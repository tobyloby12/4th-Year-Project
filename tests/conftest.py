import pytest
from optical_network_game.node import Node

@pytest.fixture
def createNode():
    return Node(0, 'A', 200, 400)