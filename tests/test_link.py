from optical_network_game.link import Link
from optical_network_game.node import Node
import pytest

######################################
# TODO
# test drawLink function
######################################

# GIVEN parameters are correct
# WHEN I create a link
# THEN the link should be create
def test_linkCreated(createLink):
    testLink, node1, node2 = createLink
    assert testLink.linkID == 0
    assert testLink.node1 == node1
    assert testLink.node2 == node2
    assert testLink.spectrum == [0]*5
    assert testLink.isHighlighted == False
    assert testLink.isSelected == False
    assert testLink.xpos == 300
    assert testLink.ypos == 500

# GIVEN a link is created
# WHEN get functions are called
# THEN the correct values should be parsed
def test_linkGetters(createLink):
    testLink, node1, node2 = createLink
    assert testLink.getX() == 300
    assert testLink.getY() == 500

# GIVEN a link is created
# WHEN set functions are called
# THEN link values should change to expected values
def test_nodeSetters(createLink):
    testLink, node1, node2 = createLink
    testLink.setHighlighted(True)
    assert testLink.isHighlighted == True

    testLink.setSelected(True)
    assert testLink.isSelected == True