import urllib3
import re
from urllib.parse import urlparse
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import argparse

f = open("output.edgelist", "w")
covered_urls = []
covered_endpoints = []


def verbosePrint(str, verbose):
    if verbose:
        print(str)

def mapURL(prev_url, url, scope, level, verbose, proxy):
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
            resp = urllib3.request("GET", url)
    except Exception as error:
        verbosePrint("Failed to retrieve: " + url, verbose)
        print(error)
        return

    if resp.status != 200:
        verbosePrint("Response contains status code: "+resp.status)
        return

    try:
        str_HTML = resp.data.decode("utf-8")
    except:
        verbosePrint("Could not read data retrieved from: " + url, verbose)
        return
    
    f.write(generic_prev_url.replace("https://" + scope, '') + " " + generic_url.replace("https://" + scope, '') + "\n")

    # Get all links without leading / and add it
    sublinks_wo_slash = list(map(lambda x : '/' + x, re.findall(r'<a[^>]*href="[^\/]([^"]*\/?[^"]+)', str_HTML)))
    # Get all links with leading /
    sublinks = re.findall(r'<a[^>]*href="(\/[^"]*\/?[^"]+)', str_HTML)
    # Join em
    sublinks += sublinks_wo_slash

    if sublinks:
        for i in sublinks:
            if i:
                mapURL(url, "https://"+scope+i, scope, level-1, verbose, proxy) 
    else:
        if (verbose):
            print("No sublinks on " + url)

    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='WHAM: Web Hacker\'s Application Mapper',
            description='Web application visualizer')

    parser.add_argument('-u', '--URL')
    parser.add_argument('-d', '--depth', type=int)
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-p', '--proxy')

    args = parser.parse_args()

    url = args.URL
    scope = urlparse(url).netloc
    mapURL(url, url, scope, args.depth, args.verbose, args.proxy)
    f.close()
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



