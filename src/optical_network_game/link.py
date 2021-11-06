import pygame


HIGHLIGHTYELLOW = (255, 255, 0, 255)
HIGHLIGHTGREEN = (0, 255, 0, 255)

class Link:
    def __init__(self, linkID, node1, node2):
        self.linkID = linkID
        self.node1 = node1
        self.node2 = node2
        self.spectrum = [0]*5
        self.isHighlighted = False
        self.isSelected = False
        self.xpos = (node1.getX() + node2.getX())/2
        self.ypos = (node1.getY() + node2.getY())/2


    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos

    def setHighlighted(self, value):
        self.isHighlighted = value

    def setSelected(self, value):
        self.isSelected = value

    def drawLink(self, display, color):
        if self.isHighlighted == True:
            pygame.draw.line(display, HIGHLIGHTYELLOW, (self.node1.xpos, self.node1.ypos), (self.node2.xpos, self.node2.ypos), 10)
        if self.isSelected == True:
            pygame.draw.line(display, HIGHLIGHTGREEN, (self.node1.xpos, self.node1.ypos), (self.node2.xpos, self.node2.ypos), 10)
        pygame.draw.line(display, color, (self.node1.xpos, self.node1.ypos), (self.node2.xpos, self.node2.ypos), 4)