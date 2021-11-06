from optical_network_game.node import Node
from optical_network_game.link import Link
import pytest

###############################################
# TODO
# test drawNode function
###############################################

# GIVEN parameters are correct
# WHEN I create a node
# THEN the node should be create
def test_nodeCreated(createNode):
    assert createNode.nodeID == 0
    assert createNode.name == 'A'
    assert createNode.xpos == 250
    assert createNode.ypos == 200
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
    assert createNode.getX() == 250
    assert createNode.getY() == 200
    assert createNode.getLinks() == {}

# GIVEN a node is created
# WHEN set functions are called
# THEN node values should change to expected values
def test_nodeSetters(createNode):
    createNode.setX(300)
    assert createNode.xpos == 300

    createNode.setY(500)
    assert createNode.ypos == 500

    createNode.setHighlighted(True)
    assert createNode.isHighlighted == True

    createNode.setSelected(True)
    assert createNode.isSelected == True

    createNode.setSource(True)
    assert createNode.isSource == True

    createNode.setDest(True)
    assert createNode.isDest == True

# GIVEN a node is created
# WHEN setLinks is called and links are put in
# THEN setLinks should be updated and be in ypos order
def test_linkSetting():
    
    nodeA = Node(0, 'A', 250, 200)
    nodeB = Node(1, 'B', 250, 400)
    nodeC = Node(2, 'C', 600, 200)
    nodeD = Node(3, 'D', 600, 400)
    link1 = Link(0, nodeA, nodeB)
    link2 = Link(1, nodeB, nodeC)
    link3 = Link(2, nodeB, nodeD)
    link4 = Link(3, nodeA, nodeC)
    link5 = Link(4, nodeC, nodeD)

    nodeList = [nodeA, nodeB, nodeC, nodeD]
    linkList = [link1, link2, link3, link4, link5]

    nodeA.setLinks(linkList)
    # checking number of links put in successsfully
    assert len(nodeA.links) == 2
    # checking height of nodes is correct order
    assert nodeA.links[0][1].ypos <= nodeA.links[1][1].ypos
    # checking correct links put in
    assert nodeA.links[0][0].name == 'C'
    assert nodeA.links[1][0].name == 'B'