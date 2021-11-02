class Node:
    def __init__(self, nodeID, name):
        self.nodeID = nodeID
        self.name = name
        self.links = []
        self.xpos = 0
        self.ypos = 0

    def getName(self):
        return self.name

    def getID(self):
        return self.nodeID

    def setX(self, x):
        self.xpos = x

    