import urllib3
import random
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
from collections import deque
import time
from werkzeug.datastructures import ImmutableMultiDict
import datetime
import math
import RequestToolbox
from Crawler import CrawlerManager
from WebServer import WebServer

# Starting point for WHAM
if __name__ == '__main__':
    urllib3.disable_warnings()

    if os.path.exists("static/map.html"):
        os.remove("static/map.html")
    crawler_manager = CrawlerManager()
    web_server = WebServer(crawler_manager)

    port = 8000
    web_server.create_app().run(debug=True, port=port)

