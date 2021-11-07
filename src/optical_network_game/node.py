############################################################
# TODO:
# complete class by adding all getters and setters
# create method for adding links and figure out logic for it
############################################################
import pygame

GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
HIGHLIGHTYELLOW = (255, 255, 0, 255)
HIGHLIGHTGREEN = (0, 255, 0, 255)

NODESIZE = 20
OUTLINESIZE = 4
TEXTSIZE = 25

class Node:
    def __init__(self, nodeID, name, xpos, ypos):
        self.nodeID = nodeID
        self.name = name
        self.links = {}
        self.xpos = xpos
        self.ypos = ypos
        self.isHighlighted = False
        self.isSelected = False
        self.isSource = False
        self.isDest = False

    def getName(self):
        return self.name

    def getID(self):
        return self.nodeID

    def setX(self, x):
        self.xpos = x

    def setY(self, y):
        self.ypos = y

    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos

    def setHighlighted(self, value):
        self.isHighlighted = value

    def setSelected(self, value):
        self.isSelected = value

    # save the links associated to each node in a list
    def setLinks(self, linkList):
        for link in linkList:
            if self.name == link.node1.name:
                self.links[link.node2] = link
            elif self.name == link.node2.name:
                self.links[link.node1] = link
        # sorts links by descending order of height
        sort_links = sorted(self.links.items(), key=lambda x: x[1].getY(), reverse=False)
        self.links = sort_links

    def getLinks(self):
        return self.links

    
    def setSource(self, value):
        self.isSource = value

    def setDest(self, value):
        self.isDest = value

    def drawNode(self, display, color):
        if self.isHighlighted == True:
            pygame.draw.circle(display, HIGHLIGHTYELLOW, (self.xpos, self.ypos), NODESIZE+5)
        elif self.isSelected == True:
            pygame.draw.circle(display, HIGHLIGHTGREEN, (self.xpos, self.ypos), NODESIZE+5)
        pygame.draw.circle(display, color, (self.xpos, self.ypos), NODESIZE)
        pygame.draw.circle(display, GRAY, (self.xpos, self.ypos), NODESIZE - OUTLINESIZE)
        if self.isSource == True or self.isDest == True:
            pygame.draw.circle(display, color, (self.xpos, self.ypos), NODESIZE)
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', TEXTSIZE)
        textsurface = myfont.render(f'{self.name}', False, WHITE)
        text_rect = textsurface.get_rect(center=(self.xpos, self.ypos))
        display.blit(textsurface, text_rect)