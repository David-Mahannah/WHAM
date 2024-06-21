import urllib3
import re
from urllib.parse import urlparse
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import argparse


covered_urls = []
covered_endpoints = []

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
    vis.show("map.html", notebook=False)


def mapURL(prev_url, url, scope, level, verbose, proxy, f):
    if level == -1:
        return

    if scope not in url:
        verbosePrint(url + " is out of scope",verbose)
        return

    if (prev_url, url) in covered_urls:
        verbosePrint(url + " was already visited", verbose)
        return

    if (".jpg" in url):
        verbosePrint(url + " is an image [SKIPPING]", verbose)
        return

    covered_urls.append((prev_url, url))

    generic_prev_url = re.sub(r'\b\d+\b', '<int>', prev_url) # generic integers
    generic_prev_url = re.sub(r'=([^&]+)', r'=<param>', generic_prev_url) # generic URL parameters
    generic_url = re.sub(r'\b\d+\b', '<int>', url) # generic integers
    generic_url = re.sub(r'=([^&]+)', r'=<param>', generic_url) # generic URL parameters


    
    if (url in covered_endpoints):
        verbosePrint("Already crawled: "+ url + ", SKIPPING", verbose)
        return

    verbosePrint("Attempting:" + url, verbose)

    covered_endpoints.append(url)
    try:
        if (proxy):
            print("Proxy through:"+proxy)
            http = urllib3.ProxyManager(proxy, use_forwarding_for_https=True)
            resp = http.request("GET", url)

        else:
            resp = urllib3.request("GET", url, headers={'Accept-Language':'en-US,en;q=0.5'}, redirect=False)
    except Exception as error:
        verbosePrint("Failed to retrieve: " + url, verbose)
        print(error)
        return




    #if resp.status != 200:
    #    verbosePrint("Response contains status code: "+str(resp.status), verbose)
    #    return

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
            mapURL(url, "https://"+scope+i, scope, level-1, verbose, proxy) 
        

    


if __name__ == '__main__':
    with open ('test.txt') as f:
        print(getSubLinks(f.read(), "google.com"))
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

    with open("output.edgelist", "w") as f:
        mapURL(url, url, scope, args.depth, args.verbose, args.proxy, f)

    visualize('output.edgelist')

   ''' 
