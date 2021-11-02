# creating requests
import random
from node import *
import datetime

# requests consist of source node, destination node, bandwidth, time allocated

class Request:
    def __init__(self, RequestID, SourceNode, DestNode, BandWidth, timeStart):
        # initialising parameters
        self.requestID = RequestID
        self.sourceNode = SourceNode
        self.destNode = DestNode
        self.bandWidth = BandWidth
        self.timeLimit = 15
        self.timeStart = timeStart
        self.timeDeallocated = 5
        self.completed = False
        self.timeCompleted = None
        self.blocked = False

    def toString(self):
        return f'''RequestID: {self.requestID}, SourceNode: {self.sourceNode}, DestNode: {self.destNode}, 
        BandWidth: {self.bandWidth}, Time limit: {self.timeLimit}s, Time Start: {self.timeStart}, 
        Time Deallocate: {self.timeDeallocated}'''

    # request has been completed
    def complete(self, time):
        self.completed = True
        self.timeCompleted = time
        self.timeDeallocated = time - self.timeDeallocated

    def getTimeStart(self):
        return self.timeStart

    
    def setBlock(self, block):
        self.blocked = block


def generateRequests(listOfNodes, numberOfRequests):
    requestsList = []
    nodeIDList = []
    # getting nodeIDs
    for node in listOfNodes:
        nodeIDList.append(node.getName())

    # creating requests
    for i in range(numberOfRequests):
        # random source and destinations
        source = random.choice(nodeIDList)
        destination = random.choice(nodeIDList)
        # makind sure destination and source are not the same
        while source == destination:
            destination = random.choice(nodeIDList)
        # randomising bandwidth
        bandwidth = random.randint(1, 5)
        # randomising time start
        timeStart = 60 - i*10
        # creating 
        request = Request(i, source, destination, bandwidth, timeStart)
        requestsList.append(request)
    return requestsList


def main():
    # test code

    # create nodes
    node1 = Node(0, 'A', 300, 300)
    node2 = Node(1, 'B', 300, 300)
    node3 = Node(2, 'C', 300, 300)
    node4 = Node(3, 'D', 300, 300)
    
    nodeList = [node1, node2, node3, node4]
    requestList = generateRequests(nodeList, 5)

    for request in requestList:
        print(request.toString())

if __name__ == '__main__':
    main()
