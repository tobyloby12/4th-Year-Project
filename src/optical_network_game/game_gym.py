from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *
import gym
import pygame, sys
from pygame.locals import *
from gym import spaces
# from stable_baselines.common.env_checker import check_env

class game_gym(gym.Env):
    '''
    Elastic Optical Network (EON) game made into an OpenAI gym environment for easier interface with RL algorithms.
    '''
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
    NUMBEROFSLOTS = 5
    SPECTRUMBOXHEIGHT = 30
    SPECTRUMBOXWIDTH = 120

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
    GREEN = (0, 255, 0)
    # idk what this is
    BGCOLOR = GRAY
    # defined variable for colouring selected and unselected requests
    colorRequest = BLACK

    def __init__(self, nodeList, linkList, requestList, user):
        
        self.nodeList = nodeList
        self.linkList = linkList
        self.requestList = requestList
        self.user = user

        self.action_space = spaces.Discrete(6)
        
        self.initialise_values()
        
        

    def initialise_values(self):
        '''
        Intial values when starting the game. This includes initializing Pygame, setting timer, initializing game display screen and requests.
        This is used when initalizing and resetting the game.
        '''
        self.requestMode = True
        self.topologyMode = False
        self.spectrumMode = False
        self.completions = []

        # initialize pygame
        pygame.init()

        # timer
        self.timer_event = pygame.USEREVENT+1
        # repeatedly create an event on the event queue every 1000ms / 1s
        pygame.time.set_timer(self.timer_event, 1000)
        self.timer = 60
        # timer for request timer bar
        self.timer2 = 60
        
        # create an object to help track time
        self.FPSCLOCK = pygame.time.Clock()
        # Initialize a window or screen for display
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        # Set the game window caption
        pygame.display.set_caption('Demo Game')
        # fill the game screen with gray
        self.DISPLAYSURF.fill(self.BLACK)
        # initialize score
        self.SCORE = 0
        # stores the requests available to the user in a list
        self.activeRequests = []
        # automatically selects the first request in the list when game starts
        self.user.selectRequest(self.requestList[0])
        # setting value to end episode
        self.done = False



    def reset(self):
        '''
        Resets the game to start state
        '''
        self.initialise_values()


    def step(self, action):
        for event in pygame.event.get():
            # If game screen is closed, Pygame is stopped
            if event.type == pygame.QUIT:
                self.endGame()
        # Updates requests and reduces timer every second
            elif event.type == self.timer_event:
                self.requestUpdate()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action = 0
                elif event.key == pygame.K_DOWN:
                    action = 1
                elif event.key == pygame.K_LEFT:
                    action = 2
                elif event.key == pygame.K_RIGHT:
                    action = 3
                elif event.key == pygame.K_RETURN:
                    action = 4
                elif event.key == pygame.K_BACKSPACE:
                    action = 5



        if self.requestMode == True:
            self.request_logic(action)
            
        elif self.topologyMode == True:
            self.topology_logic(action)
        elif self.spectrumMode == True:
            self.spectrum_logic(action)
        
        obs = pygame.surfarray.array3d(self.DISPLAYSURF)

        if (self.timer < self.requestList[-1].getTimeStart() and self.activeRequests == []) or self.timer == 0:
            self.done = True

        return obs, self.SCORE, self.done, []
    
    # def get_action(self):
        
    #     # keys = pygame.key.get_pressed()
        
    #     # if keys != None: 
    #     #     if keys[pygame.K_UP]:
    #     #         return 0
    #     #     elif keys[pygame.K_DOWN]:
    #     #         return 1
    #     #     elif keys[pygame.K_LEFT]:
    #     #         return 2
    #     #     elif keys[pygame.K_RIGHT]:
    #     #         return 3
    #     #     elif keys[pygame.K_RETURN]:
    #     #         return 4
    #     #     elif keys[pygame.K_BACKSPACE]:
    #     #         return 5
    #     #     else:
    #     #         return 6

    #     return 0
            


    def render(self):
        '''
        Renders the game display screen and updates it per FPS value set. Includes drawing topolgy, requests, spectrum, score and timer.
        '''
        # timer2 decreases per frame to allow smooth decrease of timer bar width
        self.timer2 -= 1/self.FPS
        for event in pygame.event.get():
            # If game screen is closed, Pygame is stopped
            if event.type == pygame.QUIT:
                self.endGame()
            
            
        # creating game screen
        # fill the game screen with gray
        self.DISPLAYSURF.fill(GRAY)
        # display the score on the game scren
        self.displayScore()
        # display the timer on the game scren
        self.displayTimer()

        # draw topology on the game screen
        self.drawTopologyScreen()
        # draw requests on the game screen
        self.drawRequestsScreen()
        # draw spectrums on the game screen
        self.drawSpectrumScreen()

        # Update portions of the screen for software displays (in this case the entire screen is updated)      
        pygame.display.update()
        # updates the clock once per frame
        self.FPSCLOCK.tick(self.FPS)



    def displayScore(self):
        '''
        Function to draw score on game screen.
        Used in render().
        '''
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurface = myfont.render(f'SCORE: {str(self.SCORE)}', False, WHITE)
        self.DISPLAYSURF.blit(textsurface, (self.WINDOWWIDTH/2-70, 15))



    def drawTopologyScreen(self):
        '''
        Function to draw topolgy on game screen.
        Used in render().
        '''
        # highlighting the topology space when selecting path for easier recognition
        if self.topologyMode == True:
            color = self.RED
        else:
            color = self.BLACK

        # Draw rectangle where topology is displayed in
        pygame.draw.rect(self.DISPLAYSURF, color, (self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN, \
            self.HEADER, self.NETWORKTOPOLOGYWIDTH, self.WINDOWHEIGHT - self.HEADER - self.MARGIN), 4)

        for link in self.linkList:
            link.drawLink(self.DISPLAYSURF, self.BLUE)
            link.drawSpectrum(self.DISPLAYSURF, link.getX() - self.SPECTRUMBOXWIDTH/2, link.getY() - self.SPECTRUMBOXHEIGHT/2)

        for node in self.nodeList:
            node.drawNode(self.DISPLAYSURF, self.BLUE)
        
        

    def drawRequestsScreen(self):
        '''
        Function to display requests on game screen.
        Used in render().
        '''
        # highlighting the request space when selecting requests for easier recognition
        if self.requestMode == True:
            color = self.RED
        else:
            color = self.BLACK
        
        # Draw rectangle where requests are displayed in
        pygame.draw.rect(self.DISPLAYSURF, color, (self.MARGIN, self.HEADER, self.INCOMINGREQUESTWIDTH, \
            self.WINDOWHEIGHT - self.HEADER - self.MARGIN), 4)
        
        # FOR each active request, draw a rectangle displaying the request within it
        for i, request in enumerate(self.activeRequests):
            requestBox = pygame.Rect(self.MARGIN, self.HEADER + i*(self.REQUESTHEIGHT + self.TIMERBARHEIGHT), self.INCOMINGREQUESTWIDTH, self.REQUESTHEIGHT)
            # calculate the time left before request expires
            timeLeft = request.timeLimit - (request.timeStart - self.timer2)
            # draws a rectangle that indicates the time left for the request before it expires by decreasing its length
            if timeLeft > 0:
                pygame.draw.rect(self.DISPLAYSURF, self.ORANGE, (self.MARGIN, self.HEADER + (i+1)*self.REQUESTHEIGHT + i*self.TIMERBARHEIGHT, \
                    self.INCOMINGREQUESTWIDTH*timeLeft/request.timeLimit, self.TIMERBARHEIGHT))
            # highlighting the selected request for easier recognition
            if request.getSelected() == True:
                colorRequest = self.RED
            else:
                colorRequest = self.LIGHTGRAY
            pygame.draw.rect(self.DISPLAYSURF, colorRequest, requestBox)
            pygame.font.init()
            # display source and destination node, as well as bandwidth needed for each request
            myfont = pygame.font.SysFont('Calibri', 30)
            textsurface = myfont.render(f'({request.sourceNode.getName()}, {request.destNode.getName()}, {request.bandWidth})', False, WHITE)
            text_rect = textsurface.get_rect(center=requestBox.center)
            self.DISPLAYSURF.blit(textsurface, text_rect)



    def drawSpectrumScreen(self):
        '''
        Function to draw links' spectrums on game screen. The spectrums are updated when they are allocated, and also when links are selected.
        Used in render().
        '''
        # highlighting the spectrum space when doing spectrum allocation for easier recognition
        if self.spectrumMode == True:
            color = self.RED
        else:
            color = self.BLACK
        
        # Draw rectangle where spectrums are displayed in
        spectrumBox = pygame.Rect((self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + self.MARGIN, \
            self.HEADER, self.SELECTEDLINKWIDTH, self.WINDOWHEIGHT - self.HEADER - self.MARGIN))
        pygame.draw.rect(self.DISPLAYSURF, color, spectrumBox, 4)

        # drawing spectrum selected and unselected links
        selectedLinks = []
        for entry in self.user.getLinksSelected():
            selectedLinks.append(entry[1])
        unselectedLinks = self.linkList.copy()
        for link in self.linkList:
            if link in selectedLinks:
                unselectedLinks.remove(link)
        
        # selected links text to display
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 27)
        textsurface = myfont.render(f'Selected Links:', False, self.WHITE)
        text_rect = textsurface.get_rect(center=spectrumBox.center)
        self.DISPLAYSURF.blit(textsurface, (text_rect[0], self.HEADER + self.MARGIN))
        
        # drawing selected links
        if selectedLinks != []:
            for i in range(len(selectedLinks)):
                textsurface = myfont.render(f'{selectedLinks[i].getName()}', False, self.WHITE)
                self.DISPLAYSURF.blit(textsurface, (self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + self.MARGIN + 6, \
                    self.HEADER + self.MARGIN + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5)))
                selectedLinks[i].drawSpectrum(self.DISPLAYSURF, self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + \
                    self.MARGIN + 6 + 35, self.HEADER + self.MARGIN + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5))

        # unselected links text to display
        textsurface = myfont.render(f'Unselected Links:', False, self.WHITE)
        text_rect = textsurface.get_rect(center=spectrumBox.center)
        self.DISPLAYSURF.blit(textsurface, (text_rect[0], self.HEADER + self.MARGIN + (len(selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5)))

        # drawing unselected links
        if unselectedLinks != []:
            for i in range(len(unselectedLinks)):
                textsurface = myfont.render(f'{unselectedLinks[i].getName()}', False, self.WHITE)
                self.DISPLAYSURF.blit(textsurface, (self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + self.MARGIN + 6, \
                    self.HEADER + self.MARGIN + (len(selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5) + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5)))
                unselectedLinks[i].drawSpectrum(self.DISPLAYSURF, self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + \
                    self.MARGIN + 6 + 35, self.HEADER + self.MARGIN + (len(selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5) + \
                    (i + 1)*(self.SPECTRUMBOXHEIGHT + 5))



    # drawing clock
    def displayTimer(self):
        '''
        Function to draw timer on game screen.
        Used in render().
        '''
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurface = myfont.render(f'Time: {str(self.timer)}', False, self.WHITE)
        self.DISPLAYSURF.blit(textsurface, (self.WINDOWWIDTH - 150, 15))


    def requestUpdate(self):
        '''
        Function to update the requests available to player. Adds and removes active requests.
        Also updates the timer, decreasing it by one.
        Used in render().
        '''
        # sending in requests
        # occurs every secon
        # FOR each request in the game
        for request in self.requestList:
            # IF the game timer matches the start time of the request
            # THEN the request becomes active
            if self.timer == request.timeStart:
                self.activeRequests.append(request)
        
        for request in self.activeRequests:
            # IF the game timer matches the end time of the request (calculated based on time limit of request)
            # THEN the request is considered blocked and score decreases. Request is also de-activated
            if self.timer == request.timeStart - request.timeLimit + 1:
                request.setBlock(True)
                self.SCORE -= 1
                try:
                    self.activeRequests.remove(request)
                except:
                    pass

        # sets slots to 0 when the request runs out after allocation
        for curr_request, link_list, spectrum in self.completions:
            if self.timer == curr_request.getTimeDeallocated():
                for link in link_list:
                    spectrumCopy = link[1].getSpectrum().copy()
                    for i, slot in enumerate(spectrum):
                        if slot == 1:
                            spectrumCopy[i] = 0

                    link[1].setSpectrum(spectrumCopy)

        # IF user has selected a request
        if self.user.getCurrentRequest() != None:
            # IF selected request expires before it is completed
            # THEN the links selected by the user thus far is removed and the links the user can choose is reset
            if self.timer == self.user.getCurrentRequest().timeStart - self.user.getCurrentRequest().timeLimit + 1 and self.requestMode == False:
                availableLinks = self.clearAll()
                

            # ELSE when user has selected a request that has not expired, user can still continue to service it
        # timer countsdown every second
            elif self.timer == self.user.getCurrentRequest().timeStart - self.user.getCurrentRequest().timeLimit + 1 and self.requestMode == True:
                self.user.deselectRequest()
        # decrease timer by 1
        self.timer -= 1


    def request_logic(self, action):
        # IF there are no selected requests and there are active requests
        # THEN the first indexed request in the list of active requests is selected
        # IN THE EVENT THAT selected request expires
        if self.user.getCurrentRequest() == None and self.activeRequests != []:
            self.user.selectRequest(self.activeRequests[0])
            currentRequest = self.user.getCurrentRequest()
            
        # IF there are not active requests
        # THEN do nothing
        if self.activeRequests == []:
            pass

        else:
            # define number of active requests
            activeRequestsLength = len(self.activeRequests)
            # define the request the user is currently at
            if self.user.getCurrentRequest() in self.activeRequests:
                requestIndex = self.activeRequests.index(self.user.getCurrentRequest())
            else:
                return
            # IF DOWN arrow key is pressed
            # THEN the request below the current one is selected
            if action == 1:
                # IF DOWN arrow key is pressed and it is already the last request in the list
                # THEN the first request in the list is selected
                if requestIndex == activeRequestsLength - 1:
                    requestIndex = 0
                else:
                    requestIndex += 1
                # deselects the old request and selects the new one
                self.user.deselectRequest()
                self.user.selectRequest(self.activeRequests[requestIndex])

            # IF UP arrow key is pressed
            # THEN the request above the current one is selected
            elif action == 0:
                # IF UP arrow key is pressed and it is already the first request in the list
                # THEN the last request in the list is selected
                if requestIndex == 0:
                    requestIndex = activeRequestsLength - 1
                else:
                    requestIndex -= 1
                # deselects the old request and selects the new one
                self.user.deselectRequest()
                self.user.selectRequest(self.activeRequests[requestIndex])
            
            # IF ENTER key is pressed
            # THEN the user moves to the topology space to service the request selected
            elif action == 4:
                self.requestMode = False
                self.topologyMode = True
                # user automatically starts at the source node of the request
                self.user.setCurrentNode(self.user.currentRequest.getSourceNode())
                # source node is automatically set as selected
                self.user.getCurrentNode().setSelected(True)
                # the first link and adjacent node connected to the source node (in the list) will be automatically highlighted
                self.user.getCurrentNode().getLinks()[0][0].setHighlighted(True)
                self.user.getCurrentNode().getLinks()[0][1].setHighlighted(True)
                # defines index for use in topology space
                self.index = 0


    def topology_logic(self, action):
        # IF BACKSPACE key is pressed
        if action == 5:
            # IF BACKSPACE key is pressed and the user is at the source node
            # THEN the user moves back to selecting a request, highlights will be reset
            if self.user.getCurrentNode() == self.user.getCurrentRequest().getSourceNode():
                for node in self.nodeList:
                    node.setHighlighted(False)
                    node.setSelected(False)
                for link in self.linkList:
                    link.setHighlighted(False)
                    link.setSelected(False)
                self.requestMode = True
                self.topologyMode = False
            # IF BACKSPACE key is pressed and the user is not at the source node
            # THEN the user moves back to previous node
            else:
                # define previous node and link pair from selected links list
                previous = self.user.getLinksSelected()[-1]
                # deselects the current node user is at
                self.user.getCurrentNode().setSelected(False)
                # selects the pervious node user was at
                self.user.setCurrentNode(previous[0])

                # deselects the link user chose to get to the current node
                previous[1].setSelected(False)
                # removes the node and link pair from the selected links list
                self.user.getLinksSelected().remove(previous)
                
                # removing all highlights (makes it easier since only highlights will be where user is at)
                for node in self.nodeList:
                    node.setHighlighted(False)
                for link in self.linkList:
                    link.setHighlighted(False)
                # refreshes the links user can choose
                availableLinks = self.checkAvailable()
                # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
                if availableLinks != []:
                    availableLinks[self.index][0].setHighlighted(True)
                    availableLinks[self.index][1].setHighlighted(True)
        
        # ELSE IF any button except BACKSPACE is pressed
        else:
            # refreshes the links user can choose
            availableLinks = self.checkAvailable()
            
            # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
            if availableLinks != []:
                availableLinks[self.index][0].setHighlighted(True)
                availableLinks[self.index][1].setHighlighted(True)
            else:
                self.DISPLAYSURF.fill(self.RED)
                

        # IF UP arrow key is pressed
        # THEN the link above the current one is selected
        if action == 0:
            # de-highlights the current link
            availableLinks[self.index][0].setHighlighted(False)
            availableLinks[self.index][1].setHighlighted(False)
            # IF UP arrow key is pressed and it is already the highest link
            # THEN the lowest link is selected
            if self.index == 0:
                self.index = len(availableLinks) - 1
            else:
                self.index -= 1
            # highlights the current link
            availableLinks[self.index][0].setHighlighted(True)
            availableLinks[self.index][1].setHighlighted(True)

        # IF DOWN arrow key is pressed
        # THEN the link below the current one is selected
        elif action == 1:
            # de-highlights the current link
            availableLinks[self.index][0].setHighlighted(False)
            availableLinks[self.index][1].setHighlighted(False)
            # IF DOWN arrow key is pressed and it is already the lowest link
            # THEN the highest link is selected
            if self.index == len(availableLinks) - 1:
                self.index = 0
            else:
                self.index += 1
            # highlights the current link
            availableLinks[self.index][0].setHighlighted(True)
            availableLinks[self.index][1].setHighlighted(True)

        # IF ENTER key is pressed
        # THEN the user selects the link and moves to the adjacent node
        elif action == 4:
            # IF ENTER key is pressed and user has not reached the destination node
            if self.user.getCurrentNode() != self.user.getCurrentRequest().getDestNode():
                # IF the selected link does not move the user to the destination node
                # THEN the link and node is de-highlighted and set to selected,
                # user moves to the adjacent node connected to the selected link
                if availableLinks[self.index][0] != self.user.getCurrentRequest().getDestNode():
                    availableLinks[self.index][0].setHighlighted(False)
                    availableLinks[self.index][1].setHighlighted(False)
                    availableLinks[self.index][0].setSelected(True)
                    availableLinks[self.index][1].setSelected(True)
                    # current node and link selected is added to the list
                    self.user.addLink(self.user.getCurrentNode(), availableLinks[self.index][1])
                    # new current node is set to adjacent node connected to the selected link
                    self.user.setCurrentNode(availableLinks[self.index][0])
                    # index is set back to default 0 (as it is a new node)
                    self.index = 0
                    # links the user can choose are refreshed
                    availableLinks = self.checkAvailable()
                    # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
                    if availableLinks != []:
                        availableLinks[self.index][0].setHighlighted(True)
                        availableLinks[self.index][1].setHighlighted(True)
                    else:
                        # undo selection
                        # define previous node and link pair from selected links list
                        previous = self.user.getLinksSelected()[-1]
                        # deselects the current node user is at
                        self.user.getCurrentNode().setSelected(False)
                        # selects the pervious node user was at
                        self.user.setCurrentNode(previous[0])

                        # deselects the link user chose to get to the current node
                        previous[1].setSelected(False)
                        # removes the node and link pair from the selected links list
                        self.user.getLinksSelected().remove(previous)
                        
                        # removing all highlights (makes it easier since only highlights will be where user is at)
                        for node in self.nodeList:
                            node.setHighlighted(False)
                        for link in self.linkList:
                            link.setHighlighted(False)
                        # refreshes the links user can choose
                        availableLinks = self.checkAvailable()
                        availableLinks[self.index][0].setHighlighted(True)
                        availableLinks[self.index][1].setHighlighted(True)
                        self.DISPLAYSURF.fill(self.RED)

                # ELSE IF the selected link moves the user to the destination node
                # THEN the link and node is de-highlighted and set to selected,
                # user moves to the spectrum space for spectrum allocation
                else:
                    availableLinks[self.index][0].setHighlighted(False)
                    availableLinks[self.index][1].setHighlighted(False)
                    availableLinks[self.index][0].setSelected(True)
                    availableLinks[self.index][1].setSelected(True)
                    # current node and link selected is added to the list
                    self.user.addLink(self.user.getCurrentNode(), availableLinks[self.index][1])
                    self.topologyMode = False
                    self.spectrumMode = True

                    # need to include selecting first few slots automatically
                    bandwidth = self.user.getCurrentRequest().getBandwidth()
                    linksSelected = [link[1] for link in self.user.getLinksSelected()]
                    highlightedSpectrum = [0]*self.NUMBEROFSLOTS
                    for i in range(bandwidth):
                        highlightedSpectrum[i] = 1
                    for link in linksSelected:
                        link.setSpectrumHighlighted(highlightedSpectrum)
                    self.spectrumIndex = 0


    def spectrum_logic(self, action):
        # if backspace is pressed go back to topology mode
        # should go back to node before destination node
        # selected links should be deselected
        # automatically highlight links
        # removes the links from user selected links
        if action == 5:
            self.topologyMode = True
            self.spectrumMode = False

            linksSelected = [link[1] for link in self.user.getLinksSelected()]
            highlightedSpectrum = [0]*NUMBEROFSLOTS
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)

            links_selected = self.user.getLinksSelected()
            self.user.setCurrentNode(links_selected[-1][0])
            links_selected[-1][1].setSelected(False)
            self.user.getCurrentRequest().getDestNode().setSelected(False)
            availableLinks = self.checkAvailable()
            availableLinks[self.index][0].setHighlighted(True)
            availableLinks[self.index][1].setHighlighted(True)
            self.user.getLinksSelected().remove(links_selected[-1])
            

        # if left is pressed then the selected should be shifted to the left by 1 unless at the most left where it will jump to right
        elif action == 2:
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == 0:
                self.spectrumIndex = self.NUMBEROFSLOTS - bandwidth
            else:
                self.spectrumIndex -= 1
            highlightedSpectrum = [0]*5
            linksSelected = [link[1] for link in self.user.getLinksSelected()]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)


        # if right is pressed then the selected should be shifted to the right by 1 unless at the most right where it will jump to left
        elif action == 3:
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == self.NUMBEROFSLOTS - bandwidth:
                self.spectrumIndex = 0
            else:
                self.spectrumIndex += 1
            highlightedSpectrum = [0]*5
            linksSelected = [link[1] for link in self.user.getLinksSelected()]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)

        # if return is pressed, selected links should be checked for if they are valid and if they are they should be selected and links
        # should be updated
        # otherwise an error message should pop up
        elif action == 4:
            # check that there are no conflicts
            linksSelected = [link[1] for link in self.user.getLinksSelected()]
            possible = True
            for link in linksSelected:
                for i in range(self.NUMBEROFSLOTS):
                    if link.getSpectrumHighlighted()[i] == 1:
                        if link.getSpectrum()[i] == 1:
                            # create error screen
                            self.DISPLAYSURF.fill(self.RED)
                            pygame.display.update()
                            print("error")
                            possible = False
            if possible == True:
                self.completions.append((self.user.getCurrentRequest(), self.user.getLinksSelected().copy(), link.getSpectrumHighlighted().copy()))
                for link in linksSelected:
                    newSelected = [sum(x) for x in zip(link.getSpectrum(), link.getSpectrumHighlighted())]
                    link.setSpectrum(newSelected)
                    highlightedSpectrum = [0]*5
                    link.setSpectrumHighlighted(highlightedSpectrum)
                # throw back into request mode and add point and deselect highlighted spectrum, remove request
                self.SCORE += 1
                self.user.getCurrentRequest().complete()
                self.activeRequests.remove(self.user.getCurrentRequest())
                self.user.getCurrentRequest().setTimeAllocated(self.timer)
                availableLinks = self.clearAll()



    def checkAvailable(self):
        '''
        Function to check whether links have been selected and removes from possible routes.
        This means that the user will not be able to select links that have already been selected.
        Used in clearAll()
        '''
        availableLinks = []
        for entry in self.user.getCurrentNode().getLinks():
            if (entry[1].getSelected() == False or entry[0].getSelected() == False) and entry[0].getSource() == False:
                availableLinks.append(entry)
                
        return availableLinks
    
    
    def clearAll(self):
        '''
        Clears all previously selected nodes and links.
        Used in requestUpdate()
        '''
        self.user.getLinksSelected().clear()
        availableLinks = self.checkAvailable()
        # IF user has selected a request and is still trying to service the request when the request expired
        # THEN the request is deselected, progress in servicing it will be reset, 
        # user then needs to choose another request
        
        # the request is deselcted automatically since it has expired
        self.user.deselectRequest()
        # nodes and links that user has selected or is selecting will be removed
        highlighted = [0]*NUMBEROFSLOTS
        for node in self.nodeList:
            node.setHighlighted(False)
            node.setSelected(False)
        for link in self.linkList:
            link.setHighlighted(False)
            link.setSelected(False)

            link.setSpectrumHighlighted(highlighted)
        # user is returned to request mode
        self.requestMode = True
        self.topologyMode = False
        self.spectrumMode = False
        return availableLinks


    def endGame(self):
        '''
        Function to end the game by quitting Pygame and exiting system.
        Used in render()
        '''
        pygame.quit()
        sys.exit()



########################################################################################################



# creating fixed test topology
def createTestTopology():
    # testNodes
    nodeA = Node(0, 'A', 300, 200)
    nodeB = Node(1, 'B', 300, 400)
    nodeC = Node(2, 'C', 650, 200)
    nodeD = Node(3, 'D', 650, 400)
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

def main():

    nodeList, linkList = createTestTopology()
    requestList = generateRequests(nodeList, 5)
    user = User()
    eveon = game_gym(nodeList, linkList, requestList, user)
    # check_env(eveon, warn=True)
    eveon.render()
    while True:
        # action = eveon.get_action()
        action = 6
        observation, reward, done, info = eveon.step(action)
        if done == True:
            eveon.endGame()
        eveon.render()
if __name__ == '__main__':
    main()