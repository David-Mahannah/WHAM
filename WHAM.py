import urllib3
import re
from urllib.parse import urlparse
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import argparse
import os

from flask import Flask, request, jsonify
from flask import render_template
import threading


covered_urls = []
covered_endpoints = []
worker = None


def verbosePrint(str, verbose):
    if verbose:
        print(str)

def getSubLinks(response_text, scope):
    # Get all values found in href
    href_sublinks = re.findall(r'href="([^"^\s^#]+)"', response_text)
    absolute_sublinks = []
    relative_sublinks = []
    for link in href_sublinks:
        if "https://" in link or "http://" in link:
               absolute_sublinks.append(link)
        else:
            relative_sublinks.append(link)


    r_sublinks_wo_slash = re.compile(r'([^"\/]*\/?[^"]*)')
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
        sublinks.append("https://"+scope+"/"+link)
    for link in sublinks_w_slash:
        sublinks.append("https://"+scope+link)

    return sublinks
    

def visualize(edgelist_path):
    f = open("output.edgelist", "r")
    edgelist = []
    for i in f:
        edgelist.append(i)
    #print(edgelist)
    G = nx.parse_edgelist(edgelist)

    vis = Network(height='1000px', width='100%', notebook=False, directed=True)
    vis.toggle_hide_edges_on_drag(True)
    vis.force_atlas_2based()
    #vis.show_buttons(filter_=["physics"])
    vis.from_nx(G,default_node_size=20)
    vis.write_html("static/map.html")
    #vis.show("map.html", notebook=False)



        
   
class WorkerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.cancel_event = threading.Event()

    def start(url, scope, level, verbose, proxy, fname):
        print('Thread #%s started' % self.ident)
        with open(fname, "w") as f:
            mapURLBFS(prev_url, url, scope, verbose, proxy, f)
            #mapURL(prev_url, url, scope, level, verbose, proxy, f)

    print('Thread #%s stopped' % self.ident)



    def run(self, url, scope, level, proxy, fname):
        print('Thread #%s started' % self.ident)
        with open(fname, "w") as f:
            mapURLBFS(url, scope, verbose, level, proxy, f):
            
    def cancel(self):
        print("Cancelling worker thread...")
        self.cancel_event.set()

    
    def mapURLDFS(prev_url, url, scope, level, verbose, proxy, f):
        if level == -1:
            return

        if scope not in url:
            verbosePrint(url + " is out of scope", verbose)
            return
        if (prev_url, url) in covered_urls:
            verbosePrint(url + " was already visited", verbose)
            return
        '''
        if (".jpg" in url):
            verbosePrint(url + " is an image [SKIPPING]", verbose)
            return
        '''
        covered_urls.append((prev_url, url))

        generic_prev_url = re.sub(r'\b\d+\b', '<int>', prev_url) # generic integers
        generic_prev_url = re.sub(r'=([^&]+)', r'=<param>', generic_prev_url) # generic URL parameters
        generic_url = re.sub(r'\b\d+\b', '<int>', url) # generic integers
        generic_url = re.sub(r'=([^&]+)', r'=<param>', generic_url) # generic URL parameters
        '''
        if (url in covered_endpoints):
            verbosePrint("Already crawled: "+ url + ", SKIPPING", verbose)
            return
        '''
        verbosePrint("Attempting:" + url, verbose)

        covered_endpoints.append(url)
        try:
            if (proxy):
                print("Proxy through:"+proxy)
                cert = 'CERT_NONE'
                http = urllib3.ProxyManager(proxy, use_forwarding_for_https=True, cert_reqs=cert)
                resp = http.request("GET", url)

            else:
                resp = urllib3.request("GET", url, headers={'Accept-Language':'en-US,en;q=0.5'}, redirect=False)
        except Exception as error:
            verbosePrint("Failed to retrieve: " + url, verbose)
            print(error)
            return


        try:
            str_HTML = resp.data.decode("utf-8")
        except:
            verbosePrint("Could not read data retrieved from: " + url, verbose)
            return
       
        f.write(generic_prev_url.replace("https://" + scope, '') + " " + generic_url.replace("https://" + scope, '').replace("#", '\x23') + "\n")

        # Get all links without leading / and add it
        sublinks_wo_slash = list(map(lambda x : '/' + x, re.findall(r'href="([^"\/]+\/?[^"]+)', str_HTML)))
        # Get all links with leading /
        sublinks = re.findall(r'href="(\/[^"]*\/?[^"]+)', str_HTML)
        # Join em
        sublinks += sublinks_wo_slash

        new_sublinks = []
        for link in sublinks:
            if "javascript" not in link:
                new_sublinks.append(link)

        sublinks = new_sublinks

        if not sublinks:
            if (verbose):
                print("No sublinks on " + url)


        for i in sublinks:
            if i:
                mapURL(url, "https://"+scope+i, scope, level-1, verbose, proxy, f) 


    '''
        Simplify URLs so that they are easier to compare.
        Things like IDs and Query parameters are generalized for better
        representation in the graph.
    '''
    def makeGeneric(url):
        generic_url = re.sub(r'\b\d+\b', '<int>', url) # generic integers
        generic_url = re.sub(r'=([^&]+)', r'=<param>', generic_url) # generic URL parameters
        return generic_url

    '''
        Breadth first search URL mapping.
    '''
    def mapURLBFS(url, scope, verbose, level, proxy, f):
        # Create a queue starting with our initial URL
        visited = set()
        queue = deque([(url,0)]) # tuple (node, level)
        visited.add(url)

        # This is a lazy fix for giving the first node a prev_url of itself
        next_url = url
        while queue:
            # Save the previous link
            prev_url = next_url
            # Get the next link in the queue
            next_url, level = queue.popleft()

            if self.cancel_event.is_set():
                print("Worker exiting at level: %d" % (level))
                break 

            # URL not in scope
            if scope not in next_url:
                verbosePrint(next_url + " is out of scope", verbose)
                continue
            
            # Edge already exists in graph?
            if (prev_url, next_url) in covered_urls:
                verbosePrint(url + " was already visited", verbose)
                continue

            covered_urls.append((prev_url, next_url))

            # Generic-ify the URLs so that they can be grouped
            generic_prev_url = makeGeneric(prev_url)
            generic_url = makeGeneric(url)
            
            # Retrieve the current URL
            verbosePrint("Attempting:" + url, verbose)
            try:
                if (proxy):
                    print("Proxying through:"+proxy)
                    cert = 'CERT_NONE' # Certs not implemented
                    http = urllib3.ProxyManager(proxy, use_forwarding_for_https=True, cert_reqs=cert)
                    resp = http.request("GET", url)

                else:
                    resp = urllib3.request(
                            "GET", # Request method
                            url,   # Target URL
                            headers={'Accept-Language':'en-US,en;q=0.5'}, 
                            redirect=False
                    )
            except Exception as error:
                verbosePrint("Failed to retrieve: " + url, verbose)
                print(error)
                return

            # Parse the response
            try:
                str_HTML = resp.data.decode("utf-8")
            except:
                verbosePrint("Could not read data retrieved from: " + url, verbose)
                return
           
            # Save to file
            # This is probably not the quickest but for now its easy
            # Look here for optimization
            f.write(generic_prev_url.replace("https://" + scope, '') + " "
                       + generic_url.replace("https://" + scope, '')
                                    .replace("#", '\x23') + "\n")

            # Get children
            sublinks = getSubLinks(str_HTML, scope):
            if not sublinks:
                if (verbose):
                    print("No sublinks on " + url)

            # Add children to queue
            for link in sublinks:
                if link not in visited:
                    queue.append(link, level+1)
                    visited.add(neighbor)




def start(url, scope, level, verbose, proxy, fname):
    print('Thread #%s started' % self.ident)
    with open(fname, "w") as f:
        mapURLBFS(prev_url, url, scope, verbose, proxy, f)
        #mapURL(prev_url, url, scope, level, verbose, proxy, f)
    print('Thread #%s stopped' % self.ident)

 

def create_app(test_config=None):
    # create and configure the app

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def hello():
        return render_template('app.html')


    @app.route('/api/run', methods=['POST'])
    def run():
        if request.method == 'POST':
            data = {"Result":"Success"}
            print(request.form)
            url = request.form.get('URL')
            request_HTTP = request.form.get('Request')
            proxy_host = request.form.get('ProxyHost')
            proxy_port = request.form.get('ProxyPort')
            depth = request.form.get('Depth')
            scope = request.form.get('Scope')
            print(url)
            print(request_HTTP)
            print(proxy_host)
            print(proxy_port)
            print(depth)

            stop_event = threading.Event() 
            threading.Thread(target=start, args=(stop_event, url, url, scope, int(depth), True, proxy_host+':'+proxy_port, "output.edgelist",)).start();

            # wait for all threads to exit
            for t in threading.enumerate():
                if t != threading.current_thread():
                    t.join()

            visualize('output.edgelist')
            
            global covered_urls
            global covered_endpoints
            covered_urls = []
            covered_endpoints = []

            return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data=data), 200
        else:
            # Error 405 - Method not allowed
            pass

    @app.route('api/cancel', methods=['POST'])
    def cancel():
        if request.method == 'POST':
            

    return app

if __name__ == '__main__':
    #with open ('test.txt') as f:
    #    print(getSubLinks(f.read(), "google.com"))
    '''
    parser = argparse.ArgumentParser(
            prog='WHAM: Web Hacker\'s Application Mapper',
            description='Web application visualizer')

    parser.add_argument('-u', '--URL')
    parser.add_argument('-d', '--depth', type=int)
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-p', '--proxy')
    parser.add_argument('-t', '--test')

    args = parser.parse_args()

    url = args.URL
    scope = urlparse(url).netloc

    urllib3.disable_warnings()

    with open("output.edgelist", "w") as f:
        mapURL(url, url, scope, args.depth, args.verbose, args.proxy, f)
    
    visualize('output.edgelist')
    '''
    create_app().run(debug=True)

