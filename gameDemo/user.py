from requests import *
from node import *

class User:
    def __init__(self):
        self.linksSelected = []
        self.currentNode = None
        self.currentRequest = None


    def selectRequest(self, request):
        self.currentRequest = request
        source = self.currentRequest.getSourceNode()
        dest = self.currentRequest.getDestNode()
        source.setSource(True)
        dest.setDest(True)
        self.currentRequest.setSelected(True)

    def deselectRequest(self):
        source = self.currentRequest.getSourceNode()
        dest = self.currentRequest.getDestNode()
        source.setSource(False)
        dest.setDest(False)
        self.currentRequest.setSelected(False)
        self.currentRequest = None

    def getCurrentRequest(self):
        return self.currentRequest

    def setCurrentRequest(self, value):
        self.currentRequest(value)

    def getCurrentNode(self):
        return self.currentNode

    def setCurrentNode(self, value):
        self.currentNode = value

    def setLinksSelected(self, node, link):
        self.linksSelected.append((node, link))

    def getLinksSelected(self):
        return self.linksSelected