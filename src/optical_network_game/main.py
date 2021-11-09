# importing important things
import pygame, sys
from pygame.locals import *
from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *

######################################
# TODO
## Buglist
# out of list request bug idk
# create requestMode function
# spectrumMode functionality
# line 159 redundant user.getCurrentRequest() != None condition?
# line 269 redundant else statement since everything within it is already called in other key presses?
# line 314 redundant if statement since currentNode will never be destNode?
######################################

# set game window width and height
WINDOWWIDTH = 1000
WINDOWHEIGHT = 600
# set space between request, topology and spectrum parts of the game
MARGIN = 10
# set width of request space
INCOMINGREQUESTWIDTH = 200
# set width of topology space
NETWORKTOPOLOGYWIDTH = 560
# set width of spectrum space
SELECTEDLINKWIDTH = 200
# set space for score and timer at the top of the game screen
HEADER = 50
# set height of individual requests
REQUESTHEIGHT = 40
# set height of timer bar for individual requests
TIMERBARHEIGHT = 15

# test if width of game spaces and margin fully cover the game screen width
assert WINDOWWIDTH == INCOMINGREQUESTWIDTH + NETWORKTOPOLOGYWIDTH + SELECTEDLINKWIDTH + 4*MARGIN
# set number of frame resets per second
FPS = 30

# define colours (RED, GREEN, BLUE)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 128, 0)
LIGHTGRAY = (150, 150, 150)
# idk what this is
BGCOLOR = GRAY
# defined variable for colouring selected and unselected requests
colorRequest = BLACK



def main(nodeList, linkList, requestList, user):
    # setting values for different modes the user will be in 
    # the user will initially start by selecting a request
    requestMode = False
    topologyMode = False
    spectrumMode = False
    # # initializing User class as user
    # user = User()
    # define global variables: 
    global FPSCLOCK, DISPLAYSURF, SCORE
    # initialize pygame
    pygame.init()

    # timer
    timer_event = pygame.USEREVENT+1
    # repeatedly create an event on the event queue every 1000ms / 1s
    pygame.time.set_timer(timer_event, 1000)
    timer = 60
    # timer for request timer bar
    timer2 = 60
    
    # create an object to help track time
    FPSCLOCK = pygame.time.Clock()
    # Initialize a window or screen for display
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    # Set the game window caption
    pygame.display.set_caption('Demo Game')
    # fill the game screen with gray
    DISPLAYSURF.fill(GRAY)
    # initialize score
    SCORE = 0

    # # create a list of nodes and links using createTestTopology function
    # nodeList, linkList = createTestTopology()
    # # create requests using list of nodes and defining number of requests
    # requestList = generateRequests(nodeList, 5)
    # stores the requests available to the user in a list
    activeRequests = []
    # automatically selects the first request in the list when game starts
    user.selectRequest(requestList[0])

    while True:
        # creating game screen
        # fill the game screen with gray
        DISPLAYSURF.fill(GRAY)
        # display the score on the game scren
        displayScore(DISPLAYSURF, SCORE, WINDOWWIDTH, WINDOWHEIGHT)
        # display the timer on the game scren
        displayTimer(DISPLAYSURF, timer)

        # draw topology on the game screen
        drawTopologyScreen(DISPLAYSURF, linkList, nodeList, topologyMode)
        # draw requests space on the game screen
        drawRequestsScreen(DISPLAYSURF, requestMode)
        # draw spectrum space on the game screen
        drawSpectrumScreen(DISPLAYSURF, spectrumMode)

        # draw requests on the game screen
        displayRequest(DISPLAYSURF, activeRequests, timer2)

        # stores request selected by user
        currentRequest = user.getCurrentRequest()
        # IF there are no selected requests and there are active requests
        # THEN the first indexed request in the list of active requests is selected
        # IN THE EVENT THAT selected request expires
        if currentRequest == None and activeRequests != []:
            user.selectRequest(activeRequests[0])
            currentRequest = user.getCurrentRequest()

        # timer2 decreases per frame to allow smooth decrease of timer bar width
        timer2 -= 1/FPS
        # event handling
        for event in pygame.event.get():
            # IF user closes the game screen
            # THEN closes and halts the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # starting game only when enter is pressed
            elif event.type == pygame.KEYDOWN and (requestMode == False and topologyMode == False and spectrumMode == False):
                requestMode = True
                timer2 = 60
                
            # sending in requests
            # occurs every second
            elif event.type == timer_event and (requestMode == True or topologyMode == True or spectrumMode == True):
                # FOR each request in the game
                for request in requestList:
                    # IF the game timer matches the start time of the request
                    # THEN the request becomes active
                    if timer == request.timeStart:
                        activeRequests.append(request)
                    # IF the game timer matches the end time of the request (calculated based on time limit of request)
                    # THEN the request is considered blocked and score decreases. Request is also de-activated
                    elif timer == request.timeStart - request.timeLimit + 1:
                        request.setBlock(True)
                        SCORE -= 1
                        activeRequests.remove(request)

                # IF user has selected a request
                if user.getCurrentRequest() != None:
                    # IF selected request expires before it is completed
                    # THEN the links selected by the user thus far is removed and the links the user can choose is reset
                    if timer == user.getCurrentRequest().timeStart - user.getCurrentRequest().timeLimit + 1 and requestMode == False:
                        user.getLinksSelected().clear()
                        availableLinks = checkAvailable(user)
                        # IF user has selected a request and is still trying to service the request when the request expired
                        # THEN the request is deselected, progress in servicing it will be reset, 
                        # user then needs to choose another request
                        
                        # the request is deselcted automatically since it has expired
                        user.deselectRequest()
                        # nodes and links that user has selected or is selecting will be removed
                        for node in nodeList:
                            node.setHighlighted(False)
                            node.setSelected(False)
                        for link in linkList:
                            link.setHighlighted(False)
                            link.setSelected(False)
                        # user is returned to request mode
                        requestMode = True
                        topologyMode = False
                        spectrumMode = False
                    # ELSE when user has selected a request that has not expired, user can still continue to service it
                # timer countsdown every second
                    elif timer == user.getCurrentRequest().timeStart - user.getCurrentRequest().timeLimit + 1 and requestMode == True:
                        user.deselectRequest()
                timer -= 1

            # WHEN user presses a key while selecting a request
            elif event.type == pygame.KEYDOWN and requestMode == True:
                # IF there are not active requests
                # THEN do nothing
                if activeRequests == []:
                    pass

                else:
                    # define number of active requests
                    activeRequestsLength = len(activeRequests)
                    # define the request the user is currently at
                    if currentRequest in activeRequests:
                        requestIndex = activeRequests.index(currentRequest)
                    else:
                        break
                    # IF DOWN arrow key is pressed
                    # THEN the request below the current one is selected
                    if event.key == pygame.K_DOWN:
                        # IF DOWN arrow key is pressed and it is already the last request in the list
                        # THEN the first request in the list is selected
                        if requestIndex == activeRequestsLength - 1:
                            requestIndex = 0
                        else:
                            requestIndex += 1
                        # deselects the old request and selects the new one
                        user.deselectRequest()
                        user.selectRequest(activeRequests[requestIndex])

                    # IF UP arrow key is pressed
                    # THEN the request above the current one is selected
                    elif event.key == pygame.K_UP:
                        # IF UP arrow key is pressed and it is already the first request in the list
                        # THEN the last request in the list is selected
                        if requestIndex == 0:
                            requestIndex = activeRequestsLength - 1
                        else:
                            requestIndex -= 1
                        # deselects the old request and selects the new one
                        user.deselectRequest()
                        user.selectRequest(activeRequests[requestIndex])
                    
                    # IF ENTER key is pressed
                    # THEN the user moves to the topology space to service the request selected
                    elif event.key == pygame.K_RETURN:
                        requestMode = False
                        topologyMode = True
                        # user automatically starts at the source node of the request
                        user.setCurrentNode(user.currentRequest.getSourceNode())
                        # source node is automatically set as selected
                        user.getCurrentNode().setSelected(True)
                        # the first link and adjacent node connected to the source node (in the list) will be automatically highlighted
                        user.getCurrentNode().getLinks()[0][0].setHighlighted(True)
                        user.getCurrentNode().getLinks()[0][1].setHighlighted(True)
                        # defines index for use in topology space
                        index = 0

            # WHEN user presses a key while choosing a path in the topology
            elif event.type == pygame.KEYDOWN and topologyMode == True:
                # IF BACKSPACE key is pressed
                if event.key == pygame.K_BACKSPACE:
                    # IF BACKSPACE key is pressed and the user is at the source node
                    # THEN the user moves back to selecting a request, highlights will be reset
                    if user.getCurrentNode() == user.getCurrentRequest().getSourceNode():
                        user.getCurrentNode().setSelected(False)
                        user.getCurrentNode().getLinks()[0][0].setHighlighted(False)
                        user.getCurrentNode().getLinks()[0][1].setHighlighted(False)
                        requestMode = True
                        topologyMode = False
                    # IF BACKSPACE key is pressed and the user is not at the source node
                    # THEN the user moves back to previous node
                    else:
                        # define previous node and link pair from selected links list
                        previous = user.getLinksSelected()[-1]
                        # deselects the current node user is at
                        user.getCurrentNode().setSelected(False)
                        # selects the pervious node user was at
                        user.setCurrentNode(previous[0])

                        # deselects the link user chose to get to the current node
                        previous[1].setSelected(False)
                        # removes the node and link pair from the selected links list
                        user.getLinksSelected().remove(previous)
                        
                        # removing all highlights (makes it easier since only highlights will be where user is at)
                        for node in nodeList:
                            node.setHighlighted(False)
                        for link in linkList:
                            link.setHighlighted(False)
                        # refreshes the links user can choose
                        availableLinks = checkAvailable(user)
                        # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
                        availableLinks[index][0].setHighlighted(True)
                        availableLinks[index][1].setHighlighted(True)
                
                # ELSE IF any button except BACKSPACE is pressed
                else:
                    # refreshes the links user can choose
                    availableLinks = checkAvailable(user)
                    
                    # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                # IF UP arrow key is pressed
                # THEN the link above the current one is selected
                if event.key == pygame.K_UP:
                    # de-highlights the current link
                    availableLinks[index][0].setHighlighted(False)
                    availableLinks[index][1].setHighlighted(False)
                    # IF UP arrow key is pressed and it is already the highest link
                    # THEN the lowest link is selected
                    if index == 0:
                        index = len(availableLinks) - 1
                    else:
                        index -= 1
                    # highlights the current link
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                # IF DOWN arrow key is pressed
                # THEN the link below the current one is selected
                elif event.key == pygame.K_DOWN:
                    # de-highlights the current link
                    availableLinks[index][0].setHighlighted(False)
                    availableLinks[index][1].setHighlighted(False)
                    # IF DOWN arrow key is pressed and it is already the lowest link
                    # THEN the highest link is selected
                    if index == len(availableLinks) - 1:
                        index = 0
                    else:
                        index += 1
                    # highlights the current link
                    availableLinks[index][0].setHighlighted(True)
                    availableLinks[index][1].setHighlighted(True)

                # IF ENTER key is pressed
                # THEN the user selects the link and moves to the adjacent node
                elif event.key == pygame.K_RETURN:
                    # IF ENTER key is pressed and user has not reached the destination node
                    if user.getCurrentNode() != user.getCurrentRequest().getDestNode():
                        # IF the selected link does not move the user to the destination node
                        # THEN the link and node is de-highlighted and set to selected,
                        # user moves to the adjacent node connected to the selected link
                        if availableLinks[index][0] != user.getCurrentRequest().getDestNode():
                            availableLinks[index][0].setHighlighted(False)
                            availableLinks[index][1].setHighlighted(False)
                            availableLinks[index][0].setSelected(True)
                            availableLinks[index][1].setSelected(True)
                            # current node and link selected is added to the list
                            user.addLink(user.getCurrentNode(), availableLinks[index][1])
                            # new current node is set to adjacent node connected to the selected link
                            user.setCurrentNode(availableLinks[index][0])
                            # index is set back to default 0 (as it is a new node)
                            index = 0
                            # links the user can choose are refreshed
                            availableLinks = checkAvailable(user)
                            # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
                            availableLinks[index][0].setHighlighted(True)
                            availableLinks[index][1].setHighlighted(True)
                        # ELSE IF the selected link moves the user to the destination node
                        # THEN the link and node is de-highlighted and set to selected,
                        # user moves to the spectrum space for spectrum allocation
                        else:
                            availableLinks[index][0].setHighlighted(False)
                            availableLinks[index][1].setHighlighted(False)
                            availableLinks[index][0].setSelected(True)
                            availableLinks[index][1].setSelected(True)
                            # current node and link selected is added to the list
                            user.addLink(user.getCurrentNode(), availableLinks[index][1])
                            topologyMode = False
                            spectrumMode = True

                


        # Update portions of the screen for software displays (in this case the entire screen is updated)      
        pygame.display.update()
        # updates the clock once per frame
        FPSCLOCK.tick(FPS)

# display score
def displayScore(DISPLAYSURF, score, width, height):
    pygame.font.init()
    myfont = pygame.font.SysFont('Calibri', 30)
    textsurface = myfont.render(f'SCORE: {str(score)}', False, WHITE)
    DISPLAYSURF.blit(textsurface, (width/2-70, 15))

# drawing topology screen
def drawTopologyScreen(DISPLAYSURF, linkList, nodeList, topologyMode):
    # highlighting the topology space when selecting path for easier recognition
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
    # highlighting the request space when selecting requests for easier recognition
    if requestMode == True:
        color = RED
    else:
        color = BLACK
    pygame.draw.rect(DISPLAYSURF, color, (MARGIN, HEADER, INCOMINGREQUESTWIDTH, WINDOWHEIGHT - HEADER - MARGIN), 4)

# drawing links screen
def drawSpectrumScreen(DISPLAYSURF, spectrumMode):
    # highlighting the spectrum space when doing spectrum allocation for easier recognition
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
    numberOfBoxes = len(activeRequests) #this is not used?
    # FOR each active request, draw a rectangle displaying the request within it
    for i, request in enumerate(activeRequests):
        requestBox = pygame.Rect(MARGIN, HEADER + i*(REQUESTHEIGHT + TIMERBARHEIGHT), INCOMINGREQUESTWIDTH, REQUESTHEIGHT)
        # calculate the time left before request expires
        timeLeft = request.timeLimit - (request.timeStart - timer)
        # draws a rectangle that indicates the time left for the request before it expires by decreasing its length
        if timeLeft > 0:
            pygame.draw.rect(DISPLAYSURF, ORANGE, (MARGIN, HEADER + (i+1)*REQUESTHEIGHT + i*TIMERBARHEIGHT, INCOMINGREQUESTWIDTH*timeLeft/request.timeLimit, TIMERBARHEIGHT))
        # highlighting the selected request for easier recognition
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
# user will not be able to select links that have already been selected
def checkAvailable(user):
    # define a copied list of links connected to the current node
    availableLinks = user.getCurrentNode().getLinks().copy()


    # FOR each selected link
    # IF there is already a selected link in the list of links connected to the current node
    # THEN remove that selected link                   
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
    # testLinks
    link1 = Link(0, nodeA, nodeB)
    link2 = Link(1, nodeB, nodeC)
    link3 = Link(2, nodeB, nodeD)
    link4 = Link(3, nodeA, nodeC)
    link5 = Link(4, nodeC, nodeD)

    nodeList = [nodeA, nodeB, nodeC, nodeD]
    linkList = [link1, link2, link3, link4, link5]

    # save the links associated to each node in a list
    for node in nodeList:
        node.setLinks(linkList)
    return nodeList, linkList


if __name__ == '__main__':
    nodeList, linkList = createTestTopology()
    requestList = generateRequests(nodeList, 5)
    user = User()
    main(nodeList, linkList, requestList, user)