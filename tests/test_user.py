from optical_network_game.user import User
from optical_network_game.requests import Request
from optical_network_game.node import Node
import pytest

# GIVEN parameters are correct
# WHEN there are no requests
# THEN there should be no nodes or links selected
def test_userCreated(createUser):
    assert createUser.linksSelected == []
    assert createUser.currentNode == None
    assert createUser.currentRequest == None

# GIVEN that there is a request
# WHEN a request is selected
# THEN the source, destination nodes are set, and the request is selected
def test_selectRequest(createUser, createRequest):
    testRequest, source, dest = createRequest
    createUser.selectRequest(testRequest)
    assert createUser.currentRequest.getSourceNode() == source
    assert createUser.currentRequest.getDestNode() == dest

    



    