import pytest
from optical_network_game.node import Node
from optical_network_game.requests import Request,generateRequests

# GIVEN a request can be created
# WHEN a request is created
# THEN the request values should be correctly setup
def test_requestCreated(createRequest):
    testRequest, node1, node2 = createRequest
    assert testRequest.requestID == 0
    assert testRequest.sourceNode == node1
    assert testRequest.destNode == node2
    assert testRequest.bandWidth == 15
    assert testRequest.timeStart == 0

# GIVEN a request is created
# WHEN getters are called
# THEN correct values are returned
def test_requestGetters(createRequest):
    testRequest, node1, node2 = createRequest
    assert testRequest.getTimeStart() == 0
    assert testRequest.getSourceNode() == node1
    assert testRequest.getDestNode() == node2

# GIVEN a request is created
# WHEN setters are called
# THEN correct values are set
def test_requestGetters(createRequest):
    testRequest, node1, node2 = createRequest
    testRequest.setBlock(True)
    assert testRequest.blocked == True
    testRequest.setSelected(True)
    assert testRequest.isSelected == True

# GIVEN a request has been completed
# WHEN the complete function is called
# THEN completed should be true, time completed should beset and time deallocated should be set
def test_completeRequest(createRequest):
    testRequest, node1, node2 = createRequest
    testRequest.complete(40)
    assert testRequest.completed == True
    assert testRequest.timeCompleted  == 40
    assert testRequest.timeDeallocated == 35

# GIVEN a list of nodes is created
# WHEN requests are generated
# THEN a list of random requests should be returned
def test_generateRequests():
    nodeA = Node(0, 'A', 250, 200)
    nodeB = Node(1, 'B', 250, 400)
    nodeC = Node(2, 'C', 600, 200)
    nodeD = Node(3, 'D', 600, 400)
    nodeList = [nodeA, nodeB, nodeC, nodeD]

    requestList = generateRequests(nodeList, 5)
    assert len(requestList) == 5
    assert type(requestList[0]) == Request