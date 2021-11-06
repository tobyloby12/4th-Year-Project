import pytest
from optical_network_game.node import Node
from optical_network_game.link import Link
from optical_network_game.requests import Request
from optical_network_game.user import User

# For testing Node class
@pytest.fixture
def createNode():
    return Node(0, 'A', 250, 200)

# For testing Link class
@pytest.fixture
def createLink():
    node1 = Node(0, 'A', 200, 400)
    node2 = Node(1, 'B', 400, 600)
    return Link(0, node1, node2), node1, node2

# For testing Request class
@pytest.fixture
def createRequest():
    SourceNode = Node(0, 'A', 200, 400)
    DestNode = Node(1, 'B', 400, 600)
    return Request(0, SourceNode, DestNode, 15, 0), SourceNode, DestNode

# For testing User class
@pytest.fixture
def createUser():
    return User()
