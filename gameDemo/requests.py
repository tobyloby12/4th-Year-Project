# creating requests
import random
from node import *

# requests consist of source node, destination node, bandwidth, time allocated

class Request:
    def __init__(self, RequestID, SourceNode, DestNode, BandWidth):
        # initialising parameters
        self.requestID = RequestID
        self.sourceNode = SourceNode
        self.destNode = DestNode
        self.bandWidth = BandWidth
        self.timeAllocated = 10

    def toString(self):
        return f'RequestID: {self.requestID}, SourceNode: {self.sourceNode}, DestNode: {self.destNode}, BandWidth: {self.bandWidth}, Time to complete: {self.timeAllocated}s'
    


def generateRequests(listOfNodes, numberOfRequests):
    requestsList = []
    nodeIDList = []
    # getting nodeIDs
    for node in listOfNodes:
        nodeIDList.append(node.getID())

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
        # creating 
        request = Request(i, source, destination, bandwidth)
        requestsList.append(request)
    return requestsList

def main():
    # test code

    # create nodes
    node1 = Node(0, 'A')
    node2 = Node(1, 'B')
    node3 = Node(2, 'C')
    node4 = Node(3, 'D')
    
    nodeList = [node1, node2, node3, node4]
    requestList = generateRequests(nodeList, 5)

    for request in requestList:
        print(request.toString())

if __name__ == '__main__':
    main()
