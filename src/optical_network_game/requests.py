# creating requests
import random
from optical_network_game.node import *

# requests consist of source node, destination node, bandwidth, time allocated

class Request:
    def __init__(self, RequestID, SourceNode, DestNode, BandWidth, timeStart, hold_time):
        # initialising parameters
        self.requestID = RequestID
        self.sourceNode = SourceNode
        self.destNode = DestNode
        self.bandWidth = BandWidth
        self.timeLimit = 5
        self.timeStart = timeStart
        self.timeAllocated = 0
        self.timeDeallocated = 0
        self.completed = False
        self.blocked = False
        self.isSelected = False

        #Adding holding time variable
        self.hold_time = hold_time

    def toString(self):
        return f'''RequestID: {self.requestID}, SourceNode: {self.sourceNode.getName()}, DestNode: {self.destNode.getName()}, 
        BandWidth: {self.bandWidth}, Time limit: {self.timeLimit}s, Time Start: {self.timeStart}, 
        Time Deallocate: {self.timeDeallocated}'''

    # request has been completed
    def complete(self):
        self.completed = True

    def getTimeStart(self):
        return self.timeStart

    
    def setBlock(self, block):
        self.blocked = block

    def getSourceNode(self):
        return self.sourceNode

    def getDestNode(self):
        return self.destNode

    def setSelected(self, value):
        self.isSelected = value

    def getSelected(self):
        return self.isSelected

    def getComplete(self):
        return self.completed

    def getBlocked(self):
        return self.blocked

    def getBandwidth(self):
        return self.bandWidth

    def setTimeAllocated(self, value):
        self.timeAllocated = value
        self.timeDeallocated = value - self.hold_time

    def getTimeDeallocated(self):
        return self.timeDeallocated
    
    def getTimeStart(self):
        return self.timeStart

def generateRequests(listOfNodes, numberOfRequests):
    random.seed(42)
    requestsList = []

    # creating requests
    for i in range(numberOfRequests):
        # random source and destinations
        source = random.choice(listOfNodes)
        destination = random.choice(listOfNodes)
        # makind sure destination and source are not the same
        while source == destination:
            destination = random.choice(listOfNodes)
        # randomising bandwidth
        bandwidth = random.randint(1, 2)
        # randomising time start
        timeStart = 60 - i*1
        # creating 
        request = Request(i, source, destination, bandwidth, timeStart, hold_time=10)
        requestsList.append(request)
    return requestsList

#Making new function which can change traffic loads based on holding time and 
#mean interval of incoming requests
def generateRequests_Dynamic_Traffic(listOfNodes, numberOfRequests, req_interval, hold_time):
    '''
    Added req_interval & Hold_time in function to be albe to make 
    preset requests with respective traffic load
    '''
    random.seed(42)
    requestsList = []

    #Getting Traffic Load metric
    traffic_load=hold_time/req_interval
    print("Traffic load is: " + str(traffic_load))


    # creating requests
    for i in range(numberOfRequests):
        # random source and destinations
        source = random.choice(listOfNodes)
        destination = random.choice(listOfNodes)
        # makind sure destination and source are not the same
        while source == destination:
            destination = random.choice(listOfNodes)
        # randomising bandwidth
        bandwidth = random.randint(1, 1)
        # randomising time start
        timeStart = 60 - req_interval*1
        # creating
        # added hold_time variable for Request Class 
        request = Request(i, source, destination, bandwidth, timeStart, hold_time=hold_time)
        requestsList.append(request)
    return requestsList, traffic_load

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
