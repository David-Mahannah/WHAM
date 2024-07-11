import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from Tools import verbosePrint
import random
import math



class NetworkGraph:
    def __init__(self, edge_list=[], node_list=[]):
        self.edge_list = edge_list
        self.node_list = node_list
        self.edge_filter = None
        self.node_filter = None
   
    '''
        Export a space separated edge list to an interactive html file.
        This file is framed inside application HTML.
    '''
    def visualize(self):
        temp_edge_list = self.edge_list
        #print("Before")
        #print(self.edge_list)
        if self.edge_filter:
            temp_edge_list = list(filter(self.edge_filter, self.edge_list))
        #print("After")
        #print(temp_edge_list)
        temp_node_list = self.node_list
        if self.node_filter:
            temp_node_list = list(filter(self.node_filter, self.node_list))

        print(temp_node_list)
        verbosePrint(temp_edge_list, True)
        G = nx.DiGraph()
        G.add_edges_from(temp_edge_list)
        G.add_nodes_from(temp_node_list)

        scale=10
        d = dict(G.degree())
        d.update((x, math.log2(y+2)*scale) for x, y in d.items())
        nx.set_node_attributes(G,d,'size')


        vis = Network(width='100%',
                      height='100vh',
                      notebook=False,
                      directed=True,
                      cdn_resources='remote')
        vis.toggle_hide_edges_on_drag(True)
        vis.force_atlas_2based()
        vis.from_nx(G,default_node_size=10)
        #vis.toggle_physics(False)
        vis.write_html("static/map.html")

    def setEdgeFilter(self, edge_filter):
        self.edge_filter = edge_filter

    def setNodeFilter(self, node_filter):
        self.node_filter = node_filter

    def setEdgeList(self, edge_list):
        self.edge_list = edge_list
    
    def setNodeList(self, node_list):
        self.node_list = node_list

    def parseNodeDict(self, node_dict):
        number_of_colors = len(node_dict.keys())
        color_choice = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]


        
        self.node_list = []
        temp_node_list = []
        temp_node_dict = {}
        self.color_map = {}
        for i, key in enumerate(node_dict.keys()):
            self.color_map[key] = color_choice[i]
            for site_key in node_dict[key].keys():
                for node_name in node_dict[key][site_key]:
                    #temp_node_list.append((len(key),node_name,{"color":color_choice[i]}))
                    if node_name not in temp_node_dict.keys():
                        temp_node_dict[node_name] = [] 
                    temp_node_dict[node_name].append(key)
                    
        for path in temp_node_dict.keys():
            maximum = temp_node_dict[path][0]
            for item in temp_node_dict[path]:
                if len(item) > len(maximum):
                    maximum = item
            self.node_list.append((path, {"color":self.color_map[maximum]}))

        self.node_list.reverse()

    def getColorMap(self):
        return self.color_map
