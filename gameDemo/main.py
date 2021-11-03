# importing important things
import pygame, sys
from pygame.locals import *
from node import *
from link import *
from requests import *
from user import *

WINDOWWIDTH = 1000
WINDOWHEIGHT = 600
MARGIN = 10
INCOMINGREQUESTWIDTH = 200
NETWORKTOPOLOGYWIDTH = 560
SELECTEDLINKWIDTH = 200
HEADER = 50
TIMERBARHEIGHT = 15

assert WINDOWWIDTH == INCOMINGREQUESTWIDTH + NETWORKTOPOLOGYWIDTH + SELECTEDLINKWIDTH + 4*MARGIN
FPS = 30
REQUESTHEIGHT = 40


RED = (255, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 128, 0)
LIGHTGRAY = (150, 150, 150)
BGCOLOR = GRAY
colorRequest = RED


requestMode = False
topologyMode = False
spectrumMode = False

def main():
    user = User()
    global FPSCLOCK, DISPLAYSURF, SCORE
    pygame.init()

    # timer
    timer_event = pygame.USEREVENT+1
    pygame.time.set_timer(timer_event, 1000)
    timer = 60
    timer2 = 60
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Demo Game')
    DISPLAYSURF.fill(GRAY)
    SCORE = 0

    nodeList, linkList = createTestTopology()
    requestList = generateRequests(nodeList, 5)
    activeRequests = []
    user.selectRequest(requestList[0])

    while True:
        # creating game screen
        DISPLAYSURF.fill(GRAY)
        displayScore(DISPLAYSURF, SCORE, WINDOWWIDTH, WINDOWHEIGHT)
        displayTimer(DISPLAYSURF, timer)
        # drawing topology
        drawTopologyScreen(DISPLAYSURF, linkList, nodeList)
        drawRequestsScreen(DISPLAYSURF)
        drawLinksScreen(DISPLAYSURF)
        
        displayRequest(DISPLAYSURF, activeRequests, timer2)
        timer2 -= 1/30
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # sending in requests
            elif event.type == timer_event:
                for request in requestList:
                    if timer == request.timeStart:
                        activeRequests.append(request)
                    elif timer == request.timeStart - request.timeLimit:
                        request.setBlock(True)
                        SCORE -= 1
                        activeRequests.remove(request)
                timer -= 1
            elif event.type == pygame.KEYDOWN and requestMode == True:
                # handle if none
                # find index of current selected in active requests
                # go through requests with arrow keys
                currentRequest = user.getCurrentRequest()
                if currentRequest == None and activeRequests != []:
                    user.selectRequest(activeRequest[0])
                elif activeRequests == []:
                    user.getCurrentRequest(None)
                activeRequestLength = len(activeRequests)
                requestIndex = activeRequests.index(currentRequest)
                if event.key == pygame.K_DOWN:
                    if requestIndex == activeRequestsLength - 1:
                        requestIndex = 0
                    else:
                        requestIndex += 1
                    user.deselectRequest()
                    user.selectRequest(activeRequests[requestIndex])

                if event.key == pygame.K_UP:
                    if requestIndex == 0:
                        requestIndex = activeRequestsLength - 1
                    else:
                        requestIndex -= 1
                    user.deselectRequest()
                    user.selectRequest(activeRequests[requestIndex])
                
        pygame.display.update()
        FPSCLOCK.tick(30)

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

# displays request and timers
def displayRequest(DISPLAYSURF, activeRequests, timer):
    numberOfBoxes = len(activeRequests)
    for i, request in enumerate(activeRequests):
        requestBox = pygame.Rect(MARGIN, HEADER + i*(REQUESTHEIGHT + TIMERBARHEIGHT), INCOMINGREQUESTWIDTH, REQUESTHEIGHT)
        timeLeft = request.timeLimit - (request.timeStart - timer)
        if timeLeft > 0:
            pygame.draw.rect(DISPLAYSURF, ORANGE, (MARGIN, HEADER + (i+1)*REQUESTHEIGHT + i*TIMERBARHEIGHT, INCOMINGREQUESTWIDTH*timeLeft/request.timeLimit, TIMERBARHEIGHT))
        if request.getSelected() == True:
            colorRequest == RED
        else:
            colorRequest == LIGHTGRAY
        pygame.draw.rect(DISPLAYSURF, colorRequest, requestBox)
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurface = myfont.render(f'({request.sourceNode.getName()}, {request.destNode.getName()}, {request.bandWidth})', False, WHITE)
        text_rect = textsurface.get_rect(center=requestBox.center)
        DISPLAYSURF.blit(textsurface, text_rect)
        


# creating fixed test topology
def createTestTopology():
    # testNodes
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

    for node in nodeList:
        node.setLinks(linkList)

    return nodeList, linkList


if __name__ == '__main__':
    main()