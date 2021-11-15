import pygame


HIGHLIGHTYELLOW = (255, 255, 0, 255)
HIGHLIGHTGREEN = (0, 255, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
GREEN = (0, 255, 0)
NUMBEROFSLOTS = 5
SPECTRUMBOXHEIGHT = 30
SPECTRUMBOXWIDTH = 150

class Link:
    def __init__(self, linkID, node1, node2):
        self.linkID = linkID
        self.node1 = node1
        self.node2 = node2
        self.name = node1.getName() + node2.getName()
        self.spectrum = [0]*NUMBEROFSLOTS
        self.isHighlighted = False
        self.isSelected = False
        self.xpos = (node1.getX() + node2.getX())/2
        self.ypos = (node1.getY() + node2.getY())/2
        self.spectrumHighlighted = [0]*NUMBEROFSLOTS

    def getName(self):
        return self.name

    def getX(self):
        return self.xpos

    def getY(self):
        return self.ypos

    def getSpectrum(self):
        return self.spectrum

    def setSpectrum(self, value):
        self.spectrum = value

    def getSpectrumHighlighted(self):
        return self.spectrumHighlighted

    def setSpectrumHighlighted(self, value):
        self.spectrumHighlighted = value

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
        

    def drawSpectrum(self, display, x, y):
        # drawing spectrum
        spectrumBox = pygame.Rect(x, y, SPECTRUMBOXWIDTH, SPECTRUMBOXHEIGHT)
        if self.isHighlighted == True:
            pygame.draw.rect(display, HIGHLIGHTYELLOW, spectrumBox, 10)
        if self.isSelected == True:
            pygame.draw.rect(display, HIGHLIGHTGREEN, spectrumBox, 10)
        pygame.draw.rect(display, BLACK, spectrumBox, 4)
        slotWidth = SPECTRUMBOXWIDTH/NUMBEROFSLOTS
        for i in range(NUMBEROFSLOTS):
            if self.spectrum[i] == 0:
                color = GRAY
            else:
                color = RED
            slotBox = pygame.Rect(x + i*slotWidth, y, slotWidth, SPECTRUMBOXHEIGHT)
            pygame.draw.rect(display, color, slotBox)

            slotBox = pygame.Rect(x + i*slotWidth, y, slotWidth, SPECTRUMBOXHEIGHT)
            pygame.draw.rect(display, BLACK, slotBox, 4)
            if self.spectrumHighlighted[i] == 1:
                for j in range(0, SPECTRUMBOXHEIGHT, 4):
                    pygame.draw.line(display, GREEN, (x + i*slotWidth, y + j), (x + i*slotWidth + j, y))
                    pygame.draw.line(display, GREEN, (x + i*slotWidth + j, y + SPECTRUMBOXHEIGHT - 1), (x + i*slotWidth + SPECTRUMBOXHEIGHT - 1, y + j))
            else:
                pass
            