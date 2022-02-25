from optical_network_game.user import User
from optical_network_game.requests import Request
from optical_network_game.node import Node
import pytest

###############################################
# TODO

###############################################

# GIVEN parameters are correct
# WHEN there are no requests selected
# THEN there should be no nodes or links selected
def test_userCreated(createUser):
    assert createUser.linksSelected == []
    assert createUser.currentNode == None
    assert createUser.currentRequest == None

# GIVEN that there is a request
# WHEN a request is selected
# THEN the source, destination nodes are set to True, 
# the request is selected
def test_selectRequest(createUser, createRequest):
    testRequest, source, dest = createRequest
    createUser.selectRequest(testRequest)

    assert createUser.currentRequest.getSourceNode() == source
    assert createUser.currentRequest.getDestNode() == dest
    assert createUser.currentRequest.getSourceNode().isSource == True
    assert createUser.currentRequest.getDestNode().isDest == True
    assert createUser.currentRequest.isSelected == True

# GIVEN that the user has selected a request
# WHEN the request is deselected
# THEN the source, destination nodes are set to False, 
# the request is deselected,
# current request will be removed
def test_deselectRequest(createUser, createRequest):
    testRequest, source, dest = createRequest
    createUser.selectRequest(testRequest) #select the request
    createUser.deselectRequest() #deselect the request

    assert createUser.currentRequest == None
    assert source.isSource == False
    assert source.isDest == False
    assert testRequest.isSelected == False

# GIVEN that user has selected a request
# WHEN get functions are called
# THEN the correct values should be parsed
def test_userGetters(createUser, createRequest):
    testRequest, source, dest = createRequest
    createUser.selectRequest(testRequest) #select the request

    assert createUser.getCurrentRequest() == testRequest
    assert createUser.getCurrentNode() == None
    assert createUser.getLinksSelected() == []

# GIVEN that there is a request
# WHEN set functions are called
# THEN user values should change to expected values
def test_userSetters(createUser, createRequest):
    testRequest, source, dest = createRequest

    createUser.setCurrentRequest(testRequest)
    assert createUser.currentRequest == testRequest

    createUser.setCurrentNode(source)
    assert createUser.currentNode == source

# GIVEN that user has selected a request and is choosing route
# WHEN user selects links 
# THEN list of links selected should be updated
def test_addLinks(createUser, createLink):
    testLink, node1, node2 = createLink

    createUser.addLink(node1, testLink)
    assert createUser.linksSelected != []
    selectedLinks = createUser.linksSelected
    assert selectedLinks[0][0] == node1
    assert selectedLinks[0][1] == testLink

    



    