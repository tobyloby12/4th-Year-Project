import pytest
from optical_network_game.node import Node
from optical_network_game.link import Link

@pytest.fixture
def createNode():
    return Node(0, 'A', 250, 200)

