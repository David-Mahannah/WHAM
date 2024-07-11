import re
import urllib3
import random
from urllib.parse import urlparse
from urllib3.connectionpool import connection_from_url


def getSubLinks(response_text, origin_url, ssl):
    # Get all values found in href

    #if ('.css' in origin_url):
    #    print(response_text)

    host = urllib3.util.parse_url(origin_url).host
    href_sublinks = set(re.findall(r'href="([^"^\s]+)"', response_text))

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
    if out == None:
        out = '/'
    out = out.replace('#','\x23')
    return out

