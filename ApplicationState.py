
from flask import jsonify

# Python object intended to store WHAM state in memory between refreshes
# and disk between active sessions.

class State:
    def __init__(self):
        self.target = {"URL":None,
                       "Request":None}
        self.user_roles = {"Enabled": False}
        self.scope = {"Enabled": False}
        self.proxy = {"Enabled": False,
                      "Host": None,
                      "Port": None,
                      "Certificate":None}
        self.behavior = {"Delay_Enabled":False,
                         "Depth":None,
                         "Thread_Count":None}

    def toJSON(self):
        return jsonify({"target":self.target,
                        "user_roles":self.user_roles,
                        "scope":self.scope,
                        "proxy":self.proxy,
                        "behavior":self.behavior})


    '''
    Write the state of WHAM to a JSON file for later reload using readFromFile
    '''
    def writeToFile(self):
        pass



    '''
    Read the stat of a previous WHAM project into memory
    '''
    def readFromFile(self):
        pass
