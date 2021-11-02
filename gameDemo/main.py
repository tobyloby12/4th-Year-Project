# importing important things
import pygame, sys
from pygame.locals import *
from node import *
from link import *
import requests

WINDOWWIDTH = 1000
WINDOWHEIGHT = 600
MARGIN = 10
INCOMINGREQUESTWIDTH = 200
NETWORKTOPOLOGYWIDTH = 560
SELECTEDLINKWIDTH = 200
HEADER = 50
assert WINDOWWIDTH == INCOMINGREQUESTWIDTH + NETWORKTOPOLOGYWIDTH + SELECTEDLINKWIDTH + 4*MARGIN
FPS = 30



GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

BGCOLOR = GRAY

def main():
    global FPSCLOCK, DISPLAYSURF, SCORE
    pygame.init()

    # timer
    timer_event = pygame.USEREVENT+1
    pygame.time.set_timer(timer_event, 1000)
    timer = 60
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Demo Game')
    DISPLAYSURF.fill(GRAY)
    SCORE = 0

    nodeList, linkList = createTestTopology()

    while True:
        # creating game screen
        DISPLAYSURF.fill(GRAY)
        displayScore(DISPLAYSURF, SCORE, WINDOWWIDTH, WINDOWHEIGHT)
        displayTimer(DISPLAYSURF, timer)
        # drawing topology
        drawTopologyScreen(DISPLAYSURF, linkList, nodeList)
        drawRequestsScreen(DISPLAYSURF)
        drawLinksScreen(DISPLAYSURF)

        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    SCORE += 1
                elif event.key == pygame.K_DOWN:
                    try:
                        SCORE -= 1
                    except:
                        SCORE = 0
            elif event.type == timer_event:
                timer -= 1
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# display score
def displayScore(DISPLAYSURF, score, width, height):
    pygame.font.init()
    myfont = pygame.font.SysFont('Calibri', 30)
    textsurface = myfont.render(f'SCORE: {str(score)}', False, WHITE)
    DISPLAYSURF.blit(textsurface, (width/2-70, 15))

# drawing topology screen
def drawTopologyScreen(DISPLAYSURF, linkList, nodeList):
    pygame.draw.rect(DISPLAYSURF, BLACK, (MARGIN + INCOMINGREQUESTWIDTH + MARGIN, HEADER, NETWORKTOPOLOGYWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)
    for link in linkList:
        link.drawLink(DISPLAYSURF, BLUE)
    for node in nodeList:
        node.drawNode(DISPLAYSURF, BLUE)

# drawing requests screen
def drawRequestsScreen(DISPLAYSURF):
    pygame.draw.rect(DISPLAYSURF, BLACK, (MARGIN, HEADER, INCOMINGREQUESTWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)

# drawing links screen
def drawLinksScreen(DISPLAYSURF):
    pygame.draw.rect(DISPLAYSURF, BLACK, (MARGIN + INCOMINGREQUESTWIDTH + MARGIN + NETWORKTOPOLOGYWIDTH + MARGIN, 
    HEADER, SELECTEDLINKWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)

# drawing clock
def displayTimer(DISPLAYSURF, time):
    pygame.font.init()
    myfont = pygame.font.SysFont('Calibri', 30)
    textsurface = myfont.render(f'Time: {str(time)}', False, WHITE)
    DISPLAYSURF.blit(textsurface, (WINDOWWIDTH-150, 15))


# creating fixed test topology
def createTestTopology():
    # testNodes
    nodeA = Node(0, 'A', 250, 200)
    nodeB = Node(1, 'B', 250, 400)
    nodeC = Node(2, 'C', 600, 200)
    nodeD = Node(3, 'D', 600, 400)
    link1 = Link(nodeA, nodeB)
    link2 = Link(nodeB, nodeC)
    link3 = Link(nodeB, nodeD)
    link4 = Link(nodeA, nodeC)
    link5 = Link(nodeC, nodeD)

    nodeList = [nodeA, nodeB, nodeC, nodeD]
    linkList = [link1, link2, link3, link4, link5]

    return nodeList, linkList


if __name__ == '__main__':
    main()