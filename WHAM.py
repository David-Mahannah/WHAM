import urllib3
import random
import re
from urllib.parse import urlparse
from urllib3.connectionpool import connection_from_url
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import argparse
import os
import signal
from flask import Flask, request, jsonify
from flask import render_template
import threading
from collections import deque
import time
from werkzeug.datastructures import ImmutableMultiDict
import datetime
import math

thread_pool = []
visited = []
edge_list = []

def verbosePrint(stri, verbose):
    if verbose:
        print("[VERBOSE]: " + str(stri))

def getSubLinks(response_text, origin_url, ssl):
    # Get all values found in href
    host = urllib3.util.parse_url(origin_url).host
    href_sublinks = set(re.findall(r'href="([^"^\s]+)"', response_text))
    #print(href_sublinks)


    absolute_sublinks = []
    relative_sublinks = []
    for link in href_sublinks:
        if "https://" in link or "http://" in link:
               absolute_sublinks.append(link)
        else:
            relative_sublinks.append(link)


    r_sublinks_wo_slash = re.compile(r'(\.*[^"\/]*\/?[^"]*)')
    r_sublinks_w_slash = re.compile(r'(\/[^"]*\/?[^"]*)')
    sublinks_wo_slash = []
    sublinks_w_slash = []
    for link in relative_sublinks:
        # Get all links without leading / and add it
        if r_sublinks_w_slash.match(link):
            sublinks_w_slash.append(link)
        else:
            sublinks_wo_slash.append(link)

    #print("Absolute sublinks: ")
    #print(absolute_sublinks)
    #print("Relative sublinks: ")
    #print(relative_sublinks)
    #print("Sublinks with leading /: ")
    #print(sublinks_w_slash)
    #print("Sublinks without leading /: ")
    #print(sublinks_wo_slash)

    sublinks = []
    sublinks += absolute_sublinks
    for link in sublinks_wo_slash:
        if ssl:
            sublinks.append("https://"+host+"/"+link)
        else:
            sublinks.append("http://"+host+"/"+link)
    for link in sublinks_w_slash:
        if ssl:
            sublinks.append("https://"+host+link)
        else:
            sublinks.append("http://"+host+link)

    return sublinks
    
'''
    Export a space separated edge list to an interactive html file.
    This file is framed inside application HTML.
'''
def visualize(edgelist, node_dict):
    verbosePrint(edgelist, True)
    #G = nx.parse_edgelist(edgelist)
    G = nx.Graph()
    G.add_edges_from(edgelist)
    
    number_of_colors = len(node_dict.keys())
    color_choice = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]


    node_list = []
    for i, key in enumerate(node_dict.keys()):
        for node_name in node_dict[key]:
            node_list.append((node_name,{"color":color_choice[i]}))


    G.add_nodes_from(node_list)

    scale=10
    d = dict(G.degree())
    d.update((x, math.log2(y+1)*scale) for x, y in d.items())
    nx.set_node_attributes(G,d,'size')


    vis = Network(width='100%',
                  height='100vh',
                  notebook=False,
                  directed=True,
                  filter_menu=True,
                  cdn_resources='remote')
    vis.toggle_hide_edges_on_drag(True)
    vis.force_atlas_2based()
    vis.from_nx(G,default_node_size=10)
    vis.write_html("static/map.html")


'''
    Simplify URLs so that they are easier to compare.
    Things like IDs and Query parameters are generalized for better
    representation in the graph.
'''
def makeGeneric(url):
    generic_url = re.sub(r'\b\d+\b', '<int>', url) # generic integers
    generic_url = re.sub(r'=([^&]+)', r'=<param>', generic_url) # generic URL parameters
    return generic_url


def extractPresentablePath(URL):
    out = urllib3.util.parse_url(URL).path
    out = out.replace('#','\x23') if out else URL
    return out
   
class WorkerThread(threading.Thread):
    def __init__(self, queue, lock, edgelist, url, scope, level, verbose, proxy, fname, delay, node_dict):
        super().__init__()
        self.cancel_event = threading.Event()
        self.queue = queue
        self.lock = lock
        self.edge_list = edgelist
        self.url = url
        self.scope = scope
        self.level = level
        self.verbose = verbose
        self.proxy = proxy
        self.fname = fname
        self.delay = int(delay)
        self.node_dict = node_dict

    '''
        Thread main function.
    '''
    def run(self):
        print('[Thread #%s]: started' % threading.get_ident())
        with open(self.fname, "w") as f:
            self.mapURLBFS(self.scope, self.verbose, self.level, self.proxy, self.delay, self.node_dict)
        print('[Thread #%s]: stopped' % self.ident)
   
    '''
        Safely cancel threads.
    '''
    def cancel(self):
        print('[Thread #%s]: Cancel event recieved' % self.ident)
        self.cancel_event.set()
   





    '''
        Breadth first search URL mapping.
    '''
    def mapURLBFS(self, scope, verbose, max_level, proxy, delay, node_dict):
        #visited = set()
        #visited.add(url)
        retry_count = 0;
        global visited
        while 1:
            if self.cancel_event.is_set():

                print('[Thread #%s]: Received cancel signal at level: %d' % (self.ident, level))
                break 

            
            # Get the next link in the queue
            try:
                with self.lock:
                    prev_url, next_url, level = self.queue.popleft()
                retry_count = 0
            except:
                if retry_count >= 3:
                    print("Maximum retries reached. Quitting.")
                    break
                print("Failed to fetch item from queue")
                print("Retrying in 1 sec")
                time.sleep(1)
                retry_count += 1
                continue

            if (level == max_level):
                continue

            time.sleep(delay)
            

            visited.append(next_url)
            # URL not in scope
            if not any(x in next_url for x in scope):
                print('[Thread #%s]: ' % (self.ident) + next_url + " is out of scope")
                continue
            
            # Generic-ify the URLs so that they can be grouped
            generic_prev_url = makeGeneric(prev_url)
            generic_url = makeGeneric(next_url)
            
            # Retrieve the current URL
            print('[Thread #%s]: Attempting: %s' % (self.ident, next_url))
            try:
                if (proxy):
                    #print("[Thread #%s]: Proxying through:" % threading.get_ident()+proxy)
                    cert = 'CERT_NONE' # Certs not implemented
                    http = urllib3.ProxyManager(proxy, cert_reqs=cert)
                    resp = http.request("GET", next_url)

                else:
                    cert = 'CERT_NONE' # Certs not implemented
                    http = urllib3.PoolManager(cert_reqs=cert)
                    path = http.request('GET', next_url).geturl()
                    conn = connection_from_url(url=next_url)
                    resp = conn.request(
                        "GET", # Request method
                        path,   # Target URL
                        headers={'Accept-Language':'en-US,en;q=0.5'}, 
                        redirect=True
                )
            except Exception as error:
                
                print("[Thread #%s]: Failed to retrieve: " % threading.get_ident()+next_url)
                verbosePrint(error, True)
                continue

            # Parse the response
            try:
                str_HTML = resp.data.decode("utf-8")
            except:

                print("[Thread #%s]: Could not read data retrieved from: " % threading.get_ident()+next_url)
                continue
          
            # Does the thread need to hold the lock here?
            with self.lock:
                # Add nodes to edge list in pretty form
                to_add_prev_url = extractPresentablePath(generic_prev_url)
                to_add_next_url = extractPresentablePath(generic_url)
                self.edge_list.add((to_add_prev_url,to_add_next_url))

                # Add nodes to node table to track different hosts
                domain = urllib3.util.parse_url(next_url).host
                if not domain in node_dict:
                    node_dict[domain] = []
                if not to_add_next_url in node_dict[domain]:
                    node_dict[domain].append(to_add_next_url)

            # Get children
            if 'https://' in next_url:
                ssl = True
            else:
                ssl = False
            sublinks = set(getSubLinks(str_HTML, next_url, ssl))
            if not sublinks:
                if (verbose):
                    print("[Thread #%s]: No sublinks on: " % threading.get_ident()+next_url)

            with self.lock:

            # Add children to queue
                for link in sublinks:
                    if any(x in link for x in scope):
                        self.queue.append((next_url, link, level+1))
                    #else:
                    #print("[Thread #%s]: not adding " % threading.get_ident() + link)
                    #visited.add(link)



'''
   Start multithreaded crawl of target URL.
'''
def start(url, scope, depth, verbose, proxy, fname, thread_count, delay):
    queue = deque([(url,url,0)]) # tuple (node, level)
    lock = threading.Lock()
    edge_list = set()
    node_dict = {}
    global visited

    prev_url, next_url, level = queue.popleft()

    # URL not in scope
    if not any(x in next_url for x in scope):
        verbosePrint(next_url + " is out of scope", verbose)
        return edge_list
    
    # Generic-ify the URLs so that they can be grouped
    generic_prev_url = makeGeneric(prev_url)
    generic_url = makeGeneric(url)
   
    visited.append(next_url)

    # Retrieve the current URL
    verbosePrint("Attempting:" + url, verbose)
    try:
        if (proxy):
            print("Proxying through:"+proxy)
            cert = 'CERT_NONE' # Certs not implemented
            http = urllib3.ProxyManager(proxy, use_forwarding_for_https=True, cert_reqs=cert)
            resp = http.request("GET", next_url)

        else:
            http = urllib3.PoolManager()
            path = http.request('GET', next_url).geturl()
            conn = connection_from_url(url=next_url)
            resp = conn.request(
                "GET", # Request method
                path,   # Target URL
                headers={'Accept-Language':'en-US,en;q=0.5'}, 
                redirect=False
            )
    except Exception as error:
        verbosePrint("Failed to retrieve: " + next_url, verbose)
        print(error)
        return

    # Parse the response
    try:
        str_HTML = resp.data.decode("utf-8")
    except:
        verbosePrint("Could not read data retrieved from: " + next_url, verbose)
        return
  
    
    # Save to file
    #to_add_prev_url = generic_prev_url.replace("https://"+scope, '').replace("http://"+scope, '').replace('#', '\x23')
    #to_add_next_url =      generic_url.replace("https://"+scope, '').replace("http://"+scope, '').replace('#', '\x23')
    '''

    if (to_add_prev_url == ''):
        to_add_prev_url = generic_prev_url

    if (to_add_next_url == ''):
        to_add_next_url = generic_url

    edge_list.add((to_add_prev_url, to_add_next_url))
    '''

    to_add_next_url = urllib3.util.parse_url(generic_url).path
    if to_add_next_url:
        to_add_next_url = to_add_next_url.replace('#','\x23')
    domain = urllib3.util.parse_url(next_url).host

    if not domain in node_dict:
        node_dict[domain] = []
    if not to_add_next_url in node_dict[domain]:
        node_dict[domain].append(to_add_next_url)


    # Get children
    if 'https://' in next_url:
        ssl = True
    else:
        ssl = False
    sublinks = getSubLinks(str_HTML, next_url, ssl)
    if not sublinks:
        if (verbose):
            print("No sublinks on " + next_url)

    # Add children to queue
    for link in sublinks:
        if any(x in link for x in scope) and not link in visited:
            #verbosePrint(next_url + " is out of scope", verbose)
            #return edge_list
            queue.append((next_url, link, level+1))
            #visited.add(link)
    
    print("QUEUE:")
    print(queue)
    print("edge_list")
    print(edge_list)

    global thread_pool
    for i in range(thread_count):
        # Create a new worker with all the parallel needs
        worker = WorkerThread(queue, lock, edge_list, url, scope, int(depth), verbose, proxy, "output.edgelist", delay, node_dict)
        # Start worker crawling
        thread_pool.append(worker)
        worker.start()

    for t in thread_pool:
        t.join()

    thread_pool = []

    return edge_list, node_dict

    #print(edge_list)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def hello():
        return render_template('app.html')


    @app.route('/api/run', methods=['POST'])
    def run():
        if request.method == 'POST':
            body = request.get_json();
            
            if body['URL'] == '' and body["Request"] == '':
                return jsonify({"Message":"Target URL or Request not provided"}), 200
    
            proxy = None
            if body['ProxyHost'] != '' and body['ProxyHost'] != 'Disabled':
                proxy = body['ProxyHost'] + ':' + body['ProxyPort']

            delay = 0
            if body['DelayMS'] != 'Disabled':
                delay = body['DelayMS']

            scope = body['Scope'].replace(', ', ',').split(',')
            print("SCOPE")
            print(scope)
            global visited
            global edge_list

            visited = []
            start_time = datetime.datetime.now()
            # Run multithreaded crawl
            edge_list, node_dict = start(body['URL'],
                              scope,
                              int(body['Depth']), 
                              True, 
                              proxy, 
                              "output.edgelist", int(body['ThreadCount']), delay)
            
            print("NODE DICT")
            print(node_dict)

            if not edge_list:
                return jsonify({"Message":"Target URL is our of scope."}), 200
            
            stop = datetime.datetime.now()
            runtime = stop - start_time
            print("Total runtime: " + str(runtime.total_seconds() * 1000) + " msec")


            # Edge list needs to be converted to preferred format for NetworkX
            edge_list = [t for t in edge_list]
            print(edge_list)
            visualize(edge_list, node_dict)

            return jsonify({"Message":"Mapping complete."}), 200

        else:
            # Error 405 - Method not allowed
            return jsonify({"Message":"Method not allowed."}), 405
    

    @app.route('/api/cancel', methods=['POST'])
    def cancel():
        if request.method == 'POST':
            data = {"Result":"Task cancelled. Partial results displayed"}
            for t in thread_pool:
                t.cancel()
            return jsonify({"Result":"Task cancelled. Partial results displayed"}), 200
        else:
            pass

    return app

if __name__ == '__main__':
    urllib3.disable_warnings()
    create_app().run(debug=True)

