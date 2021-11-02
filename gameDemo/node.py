############################################################
# TO DO:
# complete class by adding all getters and setters
# create method for adding links and figure out logic for it
############################################################
import pygame

GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

NODESIZE = 20
OUTLINESIZE = 4
TEXTSIZE = 25

class Node:
    def __init__(self, nodeID, name, xpos, ypos):
        self.nodeID = nodeID
        self.name = name
        self.links = []
        self.xpos = xpos
        self.ypos = ypos

    def getName(self):
        return self.name

    def getID(self):
        return self.nodeID

    # def setX(self, x):
    #     self.xpos = x

    # def setY(self, y):
    #     self.ypos = y

    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos

    def drawNode(self, display, color):
        pygame.draw.circle(display, color, (self.xpos, self.ypos), NODESIZE, OUTLINESIZE)
        pygame.draw.circle(display, GRAY, (self.xpos, self.ypos), NODESIZE - OUTLINESIZE)
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', TEXTSIZE)
        textsurface = myfont.render(f'{self.name}', False, WHITE)
        text_rect = textsurface.get_rect(center=(self.xpos, self.ypos))
        display.blit(textsurface, text_rect)