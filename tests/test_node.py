from optical_network_game.node import Node
import pytest


# GIVEN parameters are correct
# WHEN I create a node
# THEN the node should be create
def test_nodeCreated(createNode):
    assert createNode.nodeID == 0
    assert createNode.name == 'A'
    assert createNode.xpos == 200
    assert createNode.ypos == 400
    assert createNode.links == {}
    assert createNode.isHighlighted == False
    assert createNode.isSelected == False
    assert createNode.isSource == False
    assert createNode.isDest == False


# GIVEN a node is created
# WHEN get functions are called
# THEN the correct values should be parsed
def test_nodeGetters(createNode):
    assert createNode.getID() == 0
    assert createNode.getName() == 'A'
    assert createNode.getX() == 200
    assert createNode.getY() == 400
    assert createNode.getLinks() == {}

# GIVEN a node is created
# WHEN set functions are called
# THEN node values should change to expected values
def test_nodeSetters(createNode):
    createNode.setX(300)
    assert createNode.xpos == 300
    createNode.setY(500)
    assert createNode.ypos == 500
    createNode