import pygame

class Link:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.spectrum = [0]*5

    def drawLink(self, display, color):
        pygame.draw.line(display, color, (self.node1.xpos, self.node1.ypos), (self.node2.xpos, self.node2.ypos), 4)