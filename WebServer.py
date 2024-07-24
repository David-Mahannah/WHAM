import itertools
from flask import Flask, request, jsonify
from flask import render_template
import datetime
from Tools import verbosePrint
from GraphHandling import *
import urllib3
import re
from ApplicationState import State


class WebServer:
    def __init__(self, crawler_manager):
        self.crawler_manager = crawler_manager
        self.graph = None
        self.state = None

    def create_app(self, test_config=None):
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)

        @app.route('/')
        def hello():
            return render_template('app.html')


        @app.route('/api/state', methods=['POST', 'GET'])
        def applicationState():
            # Retrieve the application state
            if request.method == 'GET':
                return jsonify(self.state), 200

            # Update the application state
            elif request.method == 'POST':
                self.state = request.get_json()
                return jsonify({"Message":"State successfully updated."}), 200
            else:
                # Error 405 - Method not allowed
                return jsonify({"Message":"Method not allowed."}), 405




        @app.route('/api/graph', methods=['GET'])
        def getGraph():
            if request.method == 'GET':
                if self.graph == None:
                    return jsonify({"Message":"Failed to load previous graph data."}), 200
                response_JSON = self.graph.beautifyForJSON()
                response_JSON["Message"] = "Previous graph retrieved"
                return jsonify(response_JSON), 200
                
            else:
                # Error 405 - Method not allowed
                return jsonify({"Message":"Method not allowed."}), 405

        @app.route('/api/run', methods=['POST'])
        def run():
            if request.method == 'POST':
                self.cancel = False

                #body = request.get_json(); 

                if self.state["Target"]["URL"]["Enabled"]==True and self.state["Target"]['URL']["value"] == '':
                    return jsonify({"Message":"Target URL not provided"}), 200
                elif self.state["Target"]["Request"]["Enabled"]==True and self.state["Target"]["Request"]["value"] == '':
                    return jsonify({"Message":"Target Request not provided"}), 200


                print("Auth:", self.state["User_Roles"]["Roles"])
               

                self.graph = Graph()

                auth_dict = self.state["User_Roles"]["Roles"]
                print(auth_dict)
                if (len(auth_dict.keys()) == 0):
                    auth_dict["default_header"] = "WHAM:WHAM"
                
                print(auth_dict)

                all_edge_lists = []
                all_pairs = []

                num_users = len(auth_dict.keys())

                temp_headers = {}
                if self.state["Target"]["Request"]["Enabled"] == True:
                    req = self.state["Target"]["Request"]["value"]
                    print(req)
                    parts = req.split("\n")
                    url = re.findall("GET\s(\S*)\sHTTP", parts[0])[0]
                    url = "https://" + parts[1].replace(" ", "").split(":")[1] + url
                    for item in parts[1:]:
                        if item != '':
                            item_split = item.replace(" ","").split(":")
                            temp_headers[item_split[0]] = item_split[1]
                    print(url)
                    print(temp_headers)
                else:
                    url = self.state["Target"]["URL"]["value"]

                if self.state["Scope"]["Enabled"] == False:
                    scope = [urllib3.util.parse_url(url).host]
                else:
                    scope = self.state["Scope"]["Domain"].replace(', ', ',').split(',')


                self.graph.generateGroups(auth_dict.keys())
                
                for user in auth_dict.keys():
                    if self.cancel == True:
                        break

                    print("Running for", user)

                    headers = temp_headers

                    auth_header = auth_dict[user].replace(" ", "").split(":");
                    headers[auth_header[0]] = auth_header[1]
                    
                    proxy = None
                    if self.state["Proxy"]["Host"] != '' and self.state["Proxy"]["Enabled"] == True:
                        proxy = self.state["Proxy"]["Host"] + ':' + self.state["Proxy"]["Port"]

                    delay = 0
                    if self.state["Behavior"]["Delay"]["Enabled"] == True:
                        delay = self.state["Behavior"]["Delay"]["MS"]

                    print("SCOPE")
                    print(scope)

                    if not any(x in url for x in scope):
                        return jsonify({"Message":"Target URL is our of scope."}), 200


                    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
                    print("HEADERS: ", headers) 

                    start_time = datetime.datetime.now()
                    # Run multithreaded crawl
                    print(self.crawler_manager)
                    edge_list, node_dict = self.crawler_manager.start(url,
                                                                      headers,
                                                                      scope,
                                                                      int(self.state['Behavior']['Depth']), 
                                                                      True, 
                                                                      proxy, 
                                                                      int(self.state['Behavior']['ThreadCount']),
                                                                      delay)
                  
                    self.graph.addNodes(user,node_dict)
                    self.graph.addEdges(edge_list)

                response_JSON = self.graph.beautifyForJSON()
                response_JSON["Message"] = "Mapping complete"
                return jsonify(response_JSON), 200

            else:
                # Error 405 - Method not allowed
                return jsonify({"Message":"Method not allowed."}), 405
        

        @app.route('/api/cancel', methods=['POST'])
        def cancel():
            if request.method == 'POST':
                self.cancel = True
                data = {"Result":"Task cancelled. Partial results displayed"}
                for t in self.crawler_manager.thread_pool:
                    t.cancel()
                return jsonify({"Result":"Task cancelled. Partial results displayed"}), 200
            else:
                pass


        @app.route('/api/search', methods=['POST'])
        def search():
            if request.method == 'POST':
                body = request.get_json()
                texts = body['Text'].replace(' ', '').split(',')

                if bool(body['Negative']):
                    edge_filt = lambda x: all((text not in x[0]) and (text not in x[1]) for text in texts)
                    node_filt = lambda x: all((text not in x[0]) for text in texts)
                else:
                    edge_filt = lambda x: any((text in x[0]) or (text in x[1]) for text in texts)
                    node_filt = lambda x: any((text in x[0]) for text in texts)

                self.network_graph.setEdgeFilter(edge_filt)
                self.network_graph.setNodeFilter(node_filt)
                self.network_graph.visualize()


                return jsonify({"Message":"Filter applied."}), 200
            else:
                pass


        @app.route('/api/update_colors', methods=['POST'])
        def update_colors():
            if request.method == 'POST':
                color_dict = {}
                body = request.get_json()
                for user_group, color_hex in body.items():
                    user_tuple = tuple(user_group.replace(" ", "").split(','))
                    color_dict[user_tuple] = color_hex
                    print(user_group, color_hex)

                self.network_graph.updateColorMap(color_dict)
                self.network_graph.visualize()
                return jsonify({"Message":"Filter applied."}), 200
            else:
                pass

        return app

