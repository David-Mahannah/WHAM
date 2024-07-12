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
        self.color_map = None
        self.raw_node_list = None
   
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
        



        
        #pos = nx.circular_layout(G,scale=500)
        #pos = nx.planar_layout(G)
        
        pos = nx.spring_layout(G, scale=500, k=20)

        vis = Network(width='100%',
                      height='100vh',
                      notebook=False,
                      directed=True,
                      cdn_resources='remote')
        vis.toggle_hide_edges_on_drag(True)
        #vis.force_atlas_2based()
        vis.from_nx(G,default_node_size=10)
        

        for node in vis.get_nodes():
            vis.get_node(node)['x']=pos[node][0]
            vis.get_node(node)['y']=-pos[node][1] #the minus is needed here to respect networkx y-axis convention 
            vis.get_node(node)['physics']=False


        vis.set_edge_smooth('discrete')
        vis.toggle_physics(False)
        vis.write_html("static/map.html")

    def setEdgeFilter(self, edge_filter):
        self.edge_filter = edge_filter

    def setNodeFilter(self, node_filter):
        self.node_filter = node_filter

    def setEdgeList(self, edge_list):
        self.edge_list = edge_list
    
    def setNodeList(self, node_list):
        self.node_list = node_list

    '''
        
    '''
    def parseNodeDict(self, node_dict):
        number_of_colors = len(node_dict.keys())
        color_choice = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
        
        self.node_list = []
        temp_node_list = []
        temp_node_dict = {}
        self.color_map = {}
        self.raw_node_list = []
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
            color = self.color_map[maximum]

            # For use by pyvis
            self.node_list.append((path, {"color":color}))

            # For further processing
            self.raw_node_list.append((maximum, path, {"color":color}))

        self.node_list.reverse()



    '''
    WIP
    def setDefaultColorMap(self):
        number_of_colors = len(self.node_dict.keys())
        color_choice = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)
        return
    '''

    def getColorMap(self):
        return self.color_map

    def updateColorMap(self, new_color_map):
        print('----------------------B4-------------------------------')
        print(new_color_map)
        print(self.color_map)
        print('-----------------------------------------------------------')
        for key, value in new_color_map.items():
            self.color_map[key] = value;

        print('----------------------After----------------------------------')
        print(new_color_map)
        print(self.color_map)
        print('-----------------------------------------------------------')
        self.applyColors()

    def applyColors(self):
        updated_node_list = []
        updated_raw_node_list = []
        for node in self.raw_node_list:
            if node[0] in self.color_map.keys():
                updated_raw_node_list.append((node[0], node[1], {"color":self.color_map[node[0]]}))
                updated_node_list.append((node[1], {"color":self.color_map[node[0]]}))
        self.node_list = updated_node_list
        self.raw_node_list = updated_raw_node_list
