# importing important things
import pygame, sys
from pygame.locals import *
from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *


# Buglist
# out of list request bug idk
# 

WINDOWWIDTH = 1000
WINDOWHEIGHT = 600
MARGIN = 10
INCOMINGREQUESTWIDTH = 200
NETWORKTOPOLOGYWIDTH = 560
SELECTEDLINKWIDTH = 200
HEADER = 50
TIMERBARHEIGHT = 15

assert WINDOWWIDTH == INCOMINGREQUESTWIDTH + NETWORKTOPOLOGYWIDTH + SELECTEDLINKWIDTH + 4*MARGIN
FPS = 60
REQUESTHEIGHT = 40


RED = (255, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 128, 0)
LIGHTGRAY = (150, 150, 150)
BGCOLOR = GRAY
colorRequest = BLACK



def main():
    requestMode = True
    topologyMode = False
    spectrumMode = False
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
        drawTopologyScreen(DISPLAYSURF, linkList, nodeList, topologyMode)
        drawRequestsScreen(DISPLAYSURF, requestMode)
        drawSpectrumScreen(DISPLAYSURF, spectrumMode)
        
        displayRequest(DISPLAYSURF, activeRequests, timer2)

        currentRequest = user.getCurrentRequest()
        if currentRequest == None and activeRequests != []:
            user.selectRequest(activeRequests[0])
            currentRequest = user.getCurrentRequest()

        timer2 -= 1/FPS
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
                    elif timer == request.timeStart - request.timeLimit + 1:
                        request.setBlock(True)
                        SCORE -= 1
                        activeRequests.remove(request)
                
                if user.getCurrentRequest() != None:
                    if timer == user.getCurrentRequest().timeStart - user.getCurrentRequest().timeLimit + 1:
                        user.getLinksSelected().clear()
                        availableLinks = checkAvailable(user)
                        if user.getCurrentRequest() != None and requestMode == False:
                            # go through links and deselect all
                            user.deselectRequest()
                            for node in nodeList:
                                node.setHighlighted(False)
                                node.setSelected(False)
                            for link in linkList:
                                link.setHighlighted(False)
                                link.setSelected(False)
                            requestMode = True
                            topologyMode = False
                            spectrumMode = False
                print(timer, activeRequests)
                timer -= 1
            elif event.type == pygame.KEYDOWN and requestMode == True:
                # TODO
                # create requestMode function
                # automatically select first request when request times out without pressing key
                if activeRequests == []:
                    pass
                else:
                    activeRequestsLength = len(activeRequests)
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
                    
                    if event.key == pygame.K_RETURN:
                        requestMode = False
                        topologyMode = True
                        user.setCurrentNode(user.currentRequest.getSourceNode())
                        user.getCurrentNode().setSelected(True)
                        user.getCurrentNode().getLinks()[0][0].setHighlighted(True)
                        user.getCurrentNode().getLinks()[0][1].setHighlighted(True)
                        index = 0


            elif event.type == pygame.KEYDOWN and topologyMode == True:

                if event.key == pygame.K_BACKSPACE:
                    if user.getCurrentNode() == user.getCurrentRequest().getSourceNode():
                        user.getCurrentNode().setSelected(False)
                        user.getCurrentNode().getLinks()[0][0].setHighlighted(False)
                        user.getCurrentNode().getLinks()[0][1].setHighlighted(False)
                        requestMode = True
                        topologyMode = False
                    else:
                        previous = user.getLinksSelected()[-1]
                        user.getCurrentNode().setSelected(False)
                        user.setCurrentNode(previous[0])
                        
                        previous[1].setSelected(False)
                        user.getLinksSelected().remove(previous)
                        
                        # removing all highlights
                        for node in nodeList:
                            node.setHighlighted(False)
                        for link in linkList:
                            link.setHighlighted(False)
                        availableLinks = checkAvailable(user)
                        # set default selected
                        availableLinks[index][0].setHighlighted(True)
                        availableLinks[index][1].setHighlighted(True)


                        
                else:
                    availableLinks = checkAvailable(user)
                    
                    
                    # set default selected
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                if event.key == pygame.K_UP:
                    
                    availableLinks[index][0].setHighlighted(False)
                    availableLinks[index][1].setHighlighted(False)
                    if index == 0:
                        index = len(availableLinks) - 1
                    else:
                        index -= 1
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                elif event.key == pygame.K_DOWN:
                    
                    availableLinks[index][0].setHighlighted(False)
                    availableLinks[index][1].setHighlighted(False)
                    if index == len(availableLinks) - 1:
                        index = 0
                    else:
                        index += 1
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                elif event.key == pygame.K_RETURN:
                    
                    if user.getCurrentNode() != user.getCurrentRequest().getDestNode():
                        if availableLinks[index][0] != user.getCurrentRequest().getDestNode():
                            availableLinks[index][0].setHighlighted(False)
                            availableLinks[index][1].setHighlighted(False)
                            availableLinks[index][0].setSelected(True)
                            availableLinks[index][1].setSelected(True)
                            user.addLink(user.getCurrentNode(), availableLinks[index][1])

                            user.setCurrentNode(availableLinks[index][0])
                            index = 0
                            availableLinks = checkAvailable(user)

                            availableLinks[index][0].setHighlighted(True)
                            availableLinks[index][1].setHighlighted(True)
                        else:
                            availableLinks[index][0].setHighlighted(False)
                            availableLinks[index][1].setHighlighted(False)
                            availableLinks[index][0].setSelected(True)
                            availableLinks[index][1].setSelected(True)
                            user.addLink(user.getCurrentNode(), availableLinks[index][1])
                            topologyMode = False
                            spectrumMode = True

                


                
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# display score
def displayScore(DISPLAYSURF, score, width, height):
    pygame.font.init()
    myfont = pygame.font.SysFont('Calibri', 30)
    textsurface = myfont.render(f'SCORE: {str(score)}', False, WHITE)
    DISPLAYSURF.blit(textsurface, (width/2-70, 15))

# drawing topology screen
def drawTopologyScreen(DISPLAYSURF, linkList, nodeList, topologyMode):
    if topologyMode == True:
        color = RED
    else:
        color = BLACK
    pygame.draw.rect(DISPLAYSURF, color, (MARGIN + INCOMINGREQUESTWIDTH + MARGIN, HEADER, NETWORKTOPOLOGYWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)
    for link in linkList:
        link.drawLink(DISPLAYSURF, BLUE)
    for node in nodeList:
        node.drawNode(DISPLAYSURF, BLUE)

# drawing requests screen
def drawRequestsScreen(DISPLAYSURF, requestMode):
    if requestMode == True:
        color = RED
    else:
        color = BLACK
    pygame.draw.rect(DISPLAYSURF, color, (MARGIN, HEADER, INCOMINGREQUESTWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)

# drawing links screen
def drawSpectrumScreen(DISPLAYSURF, spectrumMode):
    if spectrumMode == True:
        color = RED
    else:
        color = BLACK
    pygame.draw.rect(DISPLAYSURF, color, (MARGIN + INCOMINGREQUESTWIDTH + MARGIN + NETWORKTOPOLOGYWIDTH + MARGIN, 
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
            colorRequest = RED
        else:
            colorRequest = LIGHTGRAY
        pygame.draw.rect(DISPLAYSURF, colorRequest, requestBox)
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurface = myfont.render(f'({request.sourceNode.getName()}, {request.destNode.getName()}, {request.bandWidth})', False, WHITE)
        text_rect = textsurface.get_rect(center=requestBox.center)
        DISPLAYSURF.blit(textsurface, text_rect)
        
# checks whether links have been selected and removes from possible routes
def checkAvailable(user):
    availableLinks = user.getCurrentNode().getLinks().copy()
                            
    for link in user.getLinksSelected():
        if link in availableLinks:
            availableLinks.remove(link)
    return availableLinks


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


