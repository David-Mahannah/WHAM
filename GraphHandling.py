
import itertools

class Graph:
    def __init__(self):
        self._edge_list = None
        self._node_list = []
        self._groups = None
        self._sites = []


        '''
        all_nodes = {
            (URL, path):{"group":[]}
        }
        '''
        self.all_nodes = {}

    def generateGroups(self, members):
        print("MEMBERS:", members)
        self._groups = {}
        temp_groups = []
        for i in range(len(members)):
            temp_groups.extend(itertools.combinations(members, i+1))

        for i, group in enumerate(temp_groups):
            self._groups[group] = i

        print("GROUPS: ", self._groups)

    def addNodes(self, user, node_dict):
        print(node_dict)
        pairs = []
        for site, node_list in node_dict.items():
            for node in node_list:
                node_key = (site, node)
                if node_key not in self.all_nodes.keys():
                    self.all_nodes[node_key] = {}
                    self.all_nodes[node_key]['group'] = [user]
                else:
                    if user not in self.all_nodes[node_key]['group']:
                        self.all_nodes[node_key]['group'].append(user)

        # All_nodes should look like:
        # = {
        #  ("https://google.com", "/sites/"):{"group":["user1", "user2", "user3", ...]},
        #  ("https://google.com","/aboutus/"):{"group":["user1", "user2"]},
        # }
        print(self.all_nodes)


    def addEdges(self, new_edge_list):
        if self._edge_list == None:
            self._edge_list = new_edge_list
        else:
            self._edge_list = list(set(self._edge_list).union(new_edge_list))

    def getGroups(self):
        return _group

    def getNodes(self):
        return self._node_list

    def getEdges(self):
        return self._edge_list

    '''
        Returns graph data a a jsonify compatible dictionary for response body
    '''
    def beautifyForJSON(self):
        id_map = {}
        
        JSON_node_list = []

        print("all nodes", self.all_nodes.items())
        for i, (key, val) in enumerate(self.all_nodes.items()):
            host, path = key
            group = val['group']
            id_map[(host, path[0])] = i
            JSON_node_list.append({"id": i,
                                   "host":host,
                                   "path":path[0],
                                   "label":path[0],
                                   "level":path[1],
                                   "user_group":group,
                                   "group":str(self._groups[tuple(group)]),
                                 })

            
        
        JSON_edge_list = []
        for edge in self._edge_list:
            JSON_edge_list.append({"from":  id_map[(edge[0][0],edge[0][1])],
                                   "to":id_map[(edge[1][0],edge[1][1])]})
        
        output = {"node_list": JSON_node_list, "edge_list": JSON_edge_list, "groups": {str(key):val for key, val in self._groups.items()}}

        return output
