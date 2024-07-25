import threading
from collections import deque
import RequestToolbox as RT
from Tools import verbosePrint
import urllib3
import random
from urllib.parse import urlparse
from urllib3.connectionpool import connection_from_url
import time
from WebServer import inScope

class WorkerThread(threading.Thread):
    def __init__(self, headers, queue, lock, edgelist, url, scope, level, verbose, proxy, delay, node_dict, visited):
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
        self.delay = int(delay)
        self.node_dict = node_dict
        self.visited = visited
        self.headers = headers

    '''
        Thread main function.
    '''
    def run(self):
        print('[Thread #%s]: started' % threading.get_ident())
        self.mapURLBFS(self.headers, self.scope, self.verbose, self.level, self.proxy, self.delay, self.node_dict, self.visited)
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
    def mapURLBFS(self, headers, scope, verbose, max_level, proxy, delay, node_dict, visited):
        retry_count = 0;
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

            if "logout" in next_url or "signoff" in next_url or "signout" in next_url:
                continue

            time.sleep(delay)
            
            # URL not in scope
            if not inScope(scope, next_url):
                print('[Thread #%s]: ' % (self.ident) + next_url + " is out of scope")
                continue
            

            # Make generic URL up here so we can avoid sending
            # requests if we end up skipping it
            generic_prev_url = RT.makeGeneric(prev_url)
            generic_url = RT.makeGeneric(next_url)

            # Add nodes to edge list in pretty form
            to_add_prev_url = RT.extractPresentablePath(generic_prev_url)
            to_add_next_url = RT.extractPresentablePath(generic_url)
            
            next_domain = urllib3.util.parse_url(next_url).host
            prev_domain = urllib3.util.parse_url(prev_url).host

            new_edge = ((prev_domain, to_add_prev_url), (next_domain, to_add_next_url))

            # Does the thread need to hold the lock here?
            with self.lock:
                # Generic-ify the URLs so that they can be grouped
                if new_edge in self.edge_list:
                    # Edge already exists. SKIP
                    continue
            

            # Retrieve the current URL
            print('[Thread #%s]: Attempting: %s' % (self.ident, next_url))
            try:
                if (proxy):
                    #print("[Thread #%s]: Proxying through:" % threading.get_ident()+proxy)
                    cert = 'CERT_NONE' # Certs not implemented
                    http = urllib3.ProxyManager(proxy, cert_reqs=cert)
                    resp = http.request("GET", next_url, headers=headers)

                else:
                    cert = 'CERT_NONE' # Certs not implemented
                    http = urllib3.PoolManager(cert_reqs=cert)
                    

                    path = http.request('GET', next_url).geturl()
                    conn = connection_from_url(url=next_url)
                    resp = conn.request(
                        "GET", # Request method
                        path,   # Target URL
                        headers=headers, 
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
                self.edge_list.add(new_edge)
                # Add nodes to node table to track different hosts
                domain = urllib3.util.parse_url(next_url).host
                if domain not in node_dict:
                    node_dict[domain] = []
                if to_add_next_url not in [x[0] for x in node_dict[domain]] and to_add_next_url != None:
                    node_dict[domain].append((to_add_next_url, level))
            


            # Get children
            sublinks = set(RT.getSubLinks(str_HTML, 
                                          next_url,
                                          True if 'https://' in next_url else False)
                           )

            if not sublinks:
                if (verbose):
                    print("[Thread #%s]: No sublinks on: " % threading.get_ident()+next_url)

            
            with self.lock:
                if (to_add_next_url in visited):
                    continue


            with self.lock:
            # Add children to queue
                for link in sublinks:
                    if inScope(scope, link):
                        self.queue.append((next_url, link, level+1))
                visited.append(to_add_next_url)
                    #else:
                    #print("[Thread #%s]: not adding " % threading.get_ident() + link)






class CrawlerManager():
    def __init__(self):
        self.thread_pool = []
    '''
       Start multithreaded crawl of target URL.
    '''
    def start(self, url, headers, scope, depth, verbose, proxy, thread_count, delay):
        queue = deque([(url,url,0)]) # tuple (node, level)
        lock = threading.Lock()
        edge_list = set()
        node_dict = {}

        prev_url, next_url, level = queue.popleft()

        # URL not in scope
        if not inScope(scope, next_url):
            verbosePrint(next_url + " is out of scope", verbose)
            return edge_list
        
        # Generic-ify the URLs so that they can be grouped
        generic_prev_url = RT.makeGeneric(prev_url)
        generic_url = RT.makeGeneric(url)
       
        # Retrieve the current URL
        verbosePrint("Attempting:" + url, verbose)
        try:
            if (proxy):
                print("Proxying through:"+proxy)
                cert = 'CERT_NONE' # Certs not implemented
                http = urllib3.ProxyManager(proxy, use_forwarding_for_https=True, cert_reqs=cert)
                resp = http.request("GET", next_url, headers=headers)

            else:
                http = urllib3.PoolManager()
                path = http.request('GET', next_url).geturl()
                conn = connection_from_url(url=next_url)
                resp = conn.request(
                    "GET", # Request method
                    path,   # Target URL
                    headers=headers, 
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

        to_add_next_url = urllib3.util.parse_url(generic_url).path
        if to_add_next_url == None:
            to_add_next_url = '/'
        if to_add_next_url:
            to_add_next_url = to_add_next_url.replace('#','\x23')
        domain = urllib3.util.parse_url(next_url).host

        if not domain in node_dict:
            node_dict[domain] = []
        if not (to_add_next_url, level) in node_dict[domain]:
            node_dict[domain].append((to_add_next_url, level))


        # Get children
        if 'https://' in next_url:
            ssl = True
        else:
            ssl = False
        sublinks = RT.getSubLinks(str_HTML, next_url, ssl)
        if not sublinks:
            if (verbose):
                print("No sublinks on " + next_url)

        # Add children to queue
        for link in sublinks:
            if inScope(scope, link):
                #verbosePrint(next_url + " is out of scope", verbose)
                #return edge_list
                queue.append((next_url, link, level+1))
        
        print("QUEUE:")
        print(queue)
        print("edge_list")
        print(edge_list)
        visited = []

        global thread_pool
        for i in range(thread_count):
            # Create a new worker with all the parallel needs
            worker = WorkerThread(headers, queue, lock, edge_list, url, scope, int(depth), verbose, proxy, delay, node_dict, visited)
            # Start worker crawling
            self.thread_pool.append(worker)
            worker.start()

        for t in self.thread_pool:
            t.join()

        self.thread_pool = []
        return edge_list, node_dict
