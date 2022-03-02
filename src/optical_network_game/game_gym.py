from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *
from optical_network_game.path_finding import *
import gym
import pygame, sys
from pygame.locals import *
from gym import spaces
from stable_baselines3.common.env_checker import check_env
import numpy as np
# from stable_baselines.common.vec_env import DummyVecEnv
# from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines3 import DQN
import json
import cv2
import random

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

        self.action_space = spaces.Discrete(4)
        
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
        self.current_path = None
        self.available_paths = None

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
        self.reward = 0
        self.cum_reward = 0
        # stores the requests available to the user in a list
        self.activeRequests = []
        # automatically selects the first request in the list when game starts
        # self.user.selectRequest(self.requestList[0])
        # setting value to end episode
        self.done = False

        # creating observation space for gym
        self.observation_space = spaces.Box(
            low= 0,
            high = 255,
            shape= (256, 256, 3),
            dtype=np.uint8
            )

        # self.observation_space = spaces.Dict({
        #     'gamescreen': self.screenshot,
        #     'source': self.user.getCurrentRequest().getSourceNode().getID(), 
        #     'destination': self.user.getCurrentRequest().getDestNode().getID(), 
        #     'bandwidth': self.user.getCurrentRequest().getBandwidth(), 
        #     'timeLimit': self.user.getCurrentRequest().timeLimit - (self.user.getCurrentRequest().timeStart - self.timer2)
        #     })

        self.info = {}

        if self.user.getCurrentRequest() != None:
            self.user.deselectRequest()

        highlighted = [0]*self.NUMBEROFSLOTS
        for node in self.nodeList:
            node.setHighlighted(False)
            node.setSelected(False)
        for link in self.linkList:
            link.setHighlighted(False)
            link.setSelected(False)
            link.setSpectrumHighlighted(highlighted)
            link.setSpectrum(highlighted)
        
        self.completions = []



    def reset(self):
        '''
        Resets the game to start state
        '''
        self.initialise_values()
        obs = np.array(pygame.surfarray.array3d(self.DISPLAYSURF.subsurface((210, 0, 560, 600))), dtype=np.uint8)
        obs = cv2.resize(obs, dsize=(256, 256))
        print(obs.shape)
        return obs


    def step(self, action):
        # print(action)
        # self.reward = 0
        for event in pygame.event.get():
            # If game screen is closed, Pygame is stopped
            if event.type == pygame.QUIT:
                self.endGame()
                # comment
        # Updates requests and reduces timer every second
            elif event.type == self.timer_event:
                self.requestUpdate()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action =  0
                elif event.key == pygame.K_DOWN:
                    action = 1
                elif event.key == pygame.K_RETURN:
                    action = 2
                elif event.key == pygame.K_BACKSPACE:
                    action = 3
        if action != 4:
            self.reward -= 1
            if self.requestMode == True:
                self.request_logic(action)
            elif self.topologyMode == True:
                self.topology_logic(action)
            elif self.spectrumMode == True:
                self.spectrum_logic(action)
        
        obs = np.array(pygame.surfarray.array3d(self.DISPLAYSURF.subsurface((210, 0, 560, 600))), dtype=np.uint8)
        obs = cv2.resize(obs, dsize=(256, 256))

        if (self.timer < self.requestList[-1].getTimeStart() and self.activeRequests == []) or self.timer == 0:
        # if self.timer == 0:
            self.done = True
            print(f'Total reward for this episode is {self.reward}')

        self.info[self.timer2] = {
            'display': obs,
            'user': self.user
            }

        return obs, self.reward, self.done, self.info
    
    # def get_action(self):
        
        #  for event in pygame.event.get():
        #     # If game screen is closed, Pygame is stopped
        #     if event.type == pygame.QUIT:
        #         self.endGame()
        # # Updates requests and reduces timer every second
        #     elif event.type == self.timer_event:
        #         self.requestUpdate()

        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_UP:
        #             return 0
        #         elif event.key == pygame.K_DOWN:
        #             return 1
        #         elif event.key == pygame.K_up:
        #             return 2
        #         elif event.key == pygame.K_RIGHT:
        #             return 3
        #         elif event.key == pygame.K_RETURN:
        #             return 4
        #         elif event.key == pygame.K_BACKSPACE:
        #             return 5
        #         else:
        #             return 6


    def render(self):
        '''
        Renders the game display screen and updates it per FPS value set. Includes drawing topolgy, requests, spectrum, score and timer.
        '''
        # for event in pygame.event.get():
        #     # If game screen is closed, Pygame is stopped
        #     if event.type == pygame.QUIT:
        #         self.endGame()
            
            
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

        # timer2 decreases per frame to allow smooth decrease of timer bar width
        self.timer2 -= 1/self.FPS
        
        # updates the clock once per frame
        self.FPSCLOCK.tick(self.FPS)



    def displayScore(self):
        '''
        Function to draw score on game screen.
        Used in render().
        '''
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurface = myfont.render(f'SCORE: {str(self.reward)}', False, WHITE)
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
            # calculate the time up before request expires
            timeup = request.timeLimit - (request.timeStart - self.timer2)
            # draws a rectangle that indicates the time up for the request before it expires by decreasing its length
            if timeup > 0:
                pygame.draw.rect(self.DISPLAYSURF, self.ORANGE, (self.MARGIN, self.HEADER + (i+1)*self.REQUESTHEIGHT + i*self.TIMERBARHEIGHT, \
                    self.INCOMINGREQUESTWIDTH*timeup/request.timeLimit, self.TIMERBARHEIGHT))
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
                self.reward -=200
                # self.reward = -200
                # self.cum_reward += self.reward
                try:
                    self.activeRequests.remove(request)
                except:
                    pass

        # sets slots to 0 when the request runs out after allocation
        for curr_request, link_list, spectrum in self.completions:
            if self.timer == curr_request.getTimeDeallocated():
                for link in link_list:
                    spectrumCopy = link.getSpectrum().copy()
                    for i, slot in enumerate(spectrum):
                        if slot == 1:
                            spectrumCopy[i] = 0

                    link.setSpectrum(spectrumCopy)

        # IF user has selected a request
        if self.user.getCurrentRequest() != None:
            # IF selected request expires before it is completed
            # THEN the links selected by the user thus far is removed and the links the user can choose is reset
            if self.timer == self.user.getCurrentRequest().timeStart - self.user.getCurrentRequest().timeLimit + 1 and self.requestMode == False:
                self.clearAll()
                

            # ELSE when user has selected a request that has not expired, user can still continue to service it
        # timer countsdown every second
            elif self.timer == self.user.getCurrentRequest().timeStart - self.user.getCurrentRequest().timeLimit + 1 and self.requestMode == True:
                self.user.deselectRequest()
        # decrease timer by 1
        self.timer -= 1
        self.timer2 = self.timer
        if self.user.getCurrentRequest() == None:
            if self.activeRequests != []:
                self.user.selectRequest(self.activeRequests[0])
            

    def request_logic(self, action):
        
        # IF there are no selected requests and there are active requests
        # THEN the first indexed request in the list of active requests is selected
        # IN THE EVENT THAT selected request expires
        # if self.user.getCurrentRequest() == None and self.activeRequests != []:
        #     self.user.selectRequest(self.activeRequests[0])
            
        # IF there are not active requests
        # THEN do nothing
        if self.activeRequests == []:
            pass

        else:
            
            self.requestMode = False
            self.topologyMode = True
            # user automatically starts at the source node of the request
            self.user.selectRequest(self.activeRequests[0])
            
            sorted_keys, g = paths(self.user.currentRequest, self.nodeList, self.linkList)
            self.available_paths = create_list(sorted_keys, g, self.nodeList, self.linkList)
            self.index = random.randint(0, len(self.available_paths) - 1)
            self.current_path = self.available_paths[self.index].copy()
            for item in self.current_path:
                item.setHighlighted(True)

            # need to include selecting first few slots automatically
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0
            
            # self.user.setCurrentNode(self.user.currentRequest.getSourceNode())
            # source node is automatically set as selected
            # self.user.getCurrentNode().setSelected(True)
            # the first link and adjacent node connected to the source node (in the list) will be automatically highlighted
            # self.user.getCurrentNode().getLinks()[0][0].setHighlighted(True)
            # self.user.getCurrentNode().getLinks()[0][1].setHighlighted(True)
            # defines index for use in topology space
            # self.index = 0


    def topology_logic(self, action):
        # IF BACKSPACE key is pressed
        # if action == 3:
            
        #     # IF BACKSPACE key is pressed and the user is at the source node
        #     # THEN the user moves back to selecting a request, highlights will be reset
        #     if self.user.getCurrentNode() == self.user.getCurrentRequest().getSourceNode():
        #         for node in self.nodeList:
        #             node.setHighlighted(False)
        #             node.setSelected(False)
        #         for link in self.linkList:
        #             link.setHighlighted(False)
        #             link.setSelected(False)
        #         self.requestMode = True
        #         self.topologyMode = False

        #         # self.reward = -1
        #         # self.cum_reward += self.reward
        #     # IF BACKSPACE key is pressed and the user is not at the source node
        #     # THEN the user moves back to previous node
        #     else:

        #         links_selected = self.user.getLinksSelected()
        #         highlightedSpectrum = [0]*NUMBEROFSLOTS
        #         links_selected[-1][1].setSpectrumHighlighted(highlightedSpectrum)

                
        #         # self.user.setCurrentNode(links_selected[-1][0])
        #         # links_selected[-1][1].setSelected(False)
        #         # self.user.getCurrentRequest().getDestNode().setSelected(False)
        #         # availableLinks = self.checkAvailable()
        #         # availableLinks[self.index][0].setHighlighted(True)
        #         # availableLinks[self.index][1].setHighlighted(True)

        #         # define previous node and link pair from selected links list
        #         previous = self.user.getLinksSelected()[-1]
        #         # deselects the current node user is at
        #         self.user.getCurrentNode().setSelected(False)
        #         # selects the pervious node user was at
        #         self.user.setCurrentNode(previous[0])

        #         # deselects the link user chose to get to the current node
        #         previous[1].setSelected(False)
        #         # removes the node and link pair from the selected links list
        #         self.user.getLinksSelected().remove(previous)
                
        #         # removing all highlights (makes it easier since only highlights will be where user is at)
        #         for node in self.nodeList:
        #             node.setHighlighted(False)
        #         for link in self.linkList:
        #             link.setHighlighted(False)
        #         # refreshes the links user can choose
        #         availableLinks = self.checkAvailable()
        #         # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
        #         if availableLinks != []:
        #             # availableLinks[self.index][0].setHighlighted(True)
        #             # availableLinks[self.index][1].setHighlighted(True)
        #             pass
                
            
        
        # # ELSE IF any button except BACKSPACE is pressed
        # else:
        #     # refreshes the links user can choose
        #     availableLinks = self.checkAvailable()
            
        #     # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
        #     if availableLinks != []:
        #         availableLinks[self.index][0].setHighlighted(True)
        #         availableLinks[self.index][1].setHighlighted(True)
        #     else:
        #         # self.DISPLAYSURF.fill(self.RED)
        #         pass
                

        # IF UP arrow key is pressed
        # THEN the link above the current one is selected
        if action == 0:

            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*NUMBEROFSLOTS
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)


            for item in self.available_paths[self.index]:
                item.setHighlighted(False)

            if self.index == 0:
                self.index = len(self.available_paths) - 1
            else:
                self.index -= 1

            for item in self.available_paths[self.index]:
                item.setHighlighted(True)

            
            # need to include selecting first few slots automatically
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0

            # # de-highlights the current link
            # availableLinks[self.index][0].setHighlighted(False)
            # availableLinks[self.index][1].setHighlighted(False)
            # # IF UP arrow key is pressed and it is already the highest link
            # # THEN the lowest link is selected
            # if self.index == 0:
            #     self.index = len(availableLinks) - 1
            # else:
            #     self.index -= 1
            # # highlights the current link
            # availableLinks[self.index][0].setHighlighted(True)
            # availableLinks[self.index][1].setHighlighted(True)

            # self.reward = -1
            # self.cum_reward += self.reward
        # IF DOWN arrow key is pressed
        # THEN the link below the current one is selected
        elif action == 1:

            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*NUMBEROFSLOTS
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            
            for item in self.available_paths[self.index]:
                item.setHighlighted(False)

            if self.index == len(self.available_paths) - 1:
                self.index = 0
            else:
                self.index += 1

            for item in self.available_paths[self.index]:
                item.setHighlighted(True)

            # need to include selecting first few slots automatically
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0

            # # de-highlights the current link
            # availableLinks[self.index][0].setHighlighted(False)
            # availableLinks[self.index][1].setHighlighted(False)
            # # IF DOWN arrow key is pressed and it is already the lowest link
            # # THEN the highest link is selected
            # if self.index == len(availableLinks) - 1:
            #     self.index = 0
            # else:
            #     self.index += 1
            # # highlights the current link
            # availableLinks[self.index][0].setHighlighted(True)
            # availableLinks[self.index][1].setHighlighted(True)

            # self.reward = -1
            # self.cum_reward += self.reward

        # IF ENTER key is pressed
        # THEN the user selects the link and moves to the adjacent node
        elif action == 2:

            for item in self.available_paths[self.index]:
                item.setHighlighted(False)
            
            for item in self.available_paths[self.index]:
                item.setSelected(True)

            self.topologyMode = False
            self.spectrumMode = True

            # need to include selecting first few slots automatically
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0
            
            self.reward -= len(self.available_paths[self.index])
            self.reward += self.user.getCurrentRequest().timeLimit - (self.user.getCurrentRequest().timeStart - self.timer2)

            # # self.reward = -1
            # # self.cum_reward += self.reward
            # # IF ENTER key is pressed and user has not reached the destination node
            # if self.user.getCurrentNode() != self.user.getCurrentRequest().getDestNode():
            #     # IF the selected link does not move the user to the destination node
            #     # THEN the link and node is de-highlighted and set to selected,
            #     # user moves to the adjacent node connected to the selected link
            #     if availableLinks[self.index][0] != self.user.getCurrentRequest().getDestNode():
            #         availableLinks[self.index][0].setHighlighted(False)
            #         availableLinks[self.index][1].setHighlighted(False)
            #         availableLinks[self.index][0].setSelected(True)
            #         availableLinks[self.index][1].setSelected(True)
            #         # current node and link selected is added to the list
            #         self.user.addLink(self.user.getCurrentNode(), availableLinks[self.index][1])
            #         # new current node is set to adjacent node connected to the selected link
            #         self.user.setCurrentNode(availableLinks[self.index][0])
            #         # index is set back to default 0 (as it is a new node)
            #         self.index = 0
            #         # links the user can choose are refreshed
            #         availableLinks = self.checkAvailable()
            #         # the first link and adjacent node connected to the current node (in the list) will be automatically highlighted
            #         if availableLinks != []:
            #             availableLinks[self.index][0].setHighlighted(True)
            #             availableLinks[self.index][1].setHighlighted(True)

            #             # need to include selecting first few slots automatically
            #             bandwidth = self.user.getCurrentRequest().getBandwidth()
            #             linksSelected = [link[1] for link in self.user.getLinksSelected()]
            #             highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            #             for i in range(bandwidth):
            #                 highlightedSpectrum[i] = 1
            #             for link in linksSelected:
            #                 link.setSpectrumHighlighted(highlightedSpectrum)
            #             self.spectrumIndex = 0

            #         else:
            #             # undo selection
            #             # define previous node and link pair from selected links list
            #             previous = self.user.getLinksSelected()[-1]
            #             # deselects the current node user is at
            #             self.user.getCurrentNode().setSelected(False)
            #             # selects the pervious node user was at
            #             self.user.setCurrentNode(previous[0])

            #             # deselects the link user chose to get to the current node
            #             previous[1].setSelected(False)
            #             # removes the node and link pair from the selected links list
            #             self.user.getLinksSelected().remove(previous)
                        
            #             # removing all highlights (makes it easier since only highlights will be where user is at)
            #             for node in self.nodeList:
            #                 node.setHighlighted(False)
            #             for link in self.linkList:
            #                 link.setHighlighted(False)
            #             # refreshes the links user can choose
            #             availableLinks = self.checkAvailable()
            #             availableLinks[self.index][0].setHighlighted(True)
            #             availableLinks[self.index][1].setHighlighted(True)
            #             # self.DISPLAYSURF.fill(self.RED)
            #             # self.reward -= 5

            #     # ELSE IF the selected link moves the user to the destination node
            #     # THEN the link and node is de-highlighted and set to selected,
            #     # user moves to the spectrum space for spectrum allocation
            #     else:
            #         availableLinks[self.index][0].setHighlighted(False)
            #         availableLinks[self.index][1].setHighlighted(False)
            #         availableLinks[self.index][0].setSelected(True)
            #         availableLinks[self.index][1].setSelected(True)
            #         # current node and link selected is added to the list
            #         self.user.addLink(self.user.getCurrentNode(), availableLinks[self.index][1])
            #         self.topologyMode = False
            #         self.spectrumMode = True

            #         # need to include selecting first few slots automatically
            #         bandwidth = self.user.getCurrentRequest().getBandwidth()
            #         linksSelected = [link[1] for link in self.user.getLinksSelected()]
            #         highlightedSpectrum = [0]*self.NUMBEROFSLOTS
            #         for i in range(bandwidth):
            #             highlightedSpectrum[i] = 1
            #         for link in linksSelected:
            #             link.setSpectrumHighlighted(highlightedSpectrum)
            #         self.spectrumIndex = 0
        
        # elif action == 2 or action == 3:
            # self.reward -= 5


    def spectrum_logic(self, action):
        # if backspace is pressed go back to topology mode
        # should go back to node before destination node
        # selected links should be deselected
        # automatically highlight links
        # removes the links from user selected links
        if action == 3:

            for item in self.available_paths[self.index]:
                item.setHighlighted(True)
            
            for item in self.available_paths[self.index]:
                item.setSelected(False)

            self.topologyMode = True
            self.spectrumMode = False


            # links_selected = self.user.getLinksSelected()
            # highlightedSpectrum = [0]*NUMBEROFSLOTS
            # links_selected[-1][1].setSpectrumHighlighted(highlightedSpectrum)

            
            # self.user.setCurrentNode(links_selected[-1][0])
            # links_selected[-1][1].setSelected(False)
            # self.user.getCurrentRequest().getDestNode().setSelected(False)
            # availableLinks = self.checkAvailable()
            # availableLinks[self.index][0].setHighlighted(True)
            # availableLinks[self.index][1].setHighlighted(True)
            # self.user.getLinksSelected().remove(links_selected[-1])

            # self.reward = -1
            # self.cum_reward += self.reward
            

        # if up is pressed then the selected should be shifted to the up by 1 unless at the most up where it will jump to right
        elif action == 0:
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == 0:
                self.spectrumIndex = self.NUMBEROFSLOTS - bandwidth
            else:
                self.spectrumIndex -= 1
            highlightedSpectrum = [0]*5
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)

            # self.reward = -1
            # self.cum_reward += self.reward


        # if right is pressed then the selected should be shifted to the right by 1 unless at the most right where it will jump to up
        elif action == 1:
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == self.NUMBEROFSLOTS - bandwidth:
                self.spectrumIndex = 0
            else:
                self.spectrumIndex += 1
            highlightedSpectrum = [0]*5
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)

            # self.reward = -1
            # self.cum_reward += self.reward

        # if return is pressed, selected links should be checked for if they are valid and if they are they should be selected and links
        # should be updated
        # otherwise an error message should pop up
        elif action == 2:
            # check that there are no conflicts
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            possible = True
            for link in linksSelected:
                for i in range(self.NUMBEROFSLOTS):
                    if link.getSpectrumHighlighted()[i] == 1:
                        if link.getSpectrum()[i] == 1:
                            # create error screen
                            # self.DISPLAYSURF.fill(self.RED)
                            # pygame.display.update()
                            # print("error")
                            possible = False
                            self.reward -= 2
                            # self.reward = -2
                            # self.cum_reward += self.reward
            if possible == True:
                self.completions.append((self.user.getCurrentRequest(), linksSelected.copy(), link.getSpectrumHighlighted().copy()))
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

                self.reward += 100
                # self.reward = 100
                # self.cum_reward += self.reward

        # elif action == 0 or action == 1:
        #     self.reward -= 5

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
        # self.user.getLinksSelected().clear()
        # availableLinks = self.checkAvailable()
        # IF user has selected a request and is still trying to service the request when the request expired
        # THEN the request is deselected, progress in servicing it will be reset, 
        # user then needs to choose another request
        
        # the request is deselcted automatically since it has expired
        self.user.deselectRequest()
        # nodes and links that user has selected or is selecting will be removed
        highlighted = [0]*self.NUMBEROFSLOTS
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
    requestList = generateRequests(nodeList, 30)

    user = User()
    eveon = game_gym(nodeList, linkList, requestList, user)

    check_env(eveon, warn=True)
    # model = DQN('MlpPolicy', eveon, verbose=1, buffer_size=100, device='cuda')
    # model.learn(total_timesteps=10000)
    # model.save("DQNEveon")

    obs = eveon.reset()
    while True :
        # action, states_ = model.predict(obs, deterministic=True)
        # action = 6
        action = 6
        obs, rewards, dones, info = eveon.step(action)
        # print(action)
        if dones == True:
            print(eveon.reward)
            # with open('info.json', 'w') as outfile:
            #     json.dump(info, outfile)

            eveon.reset()

        eveon.render()

# def main():
#     nodeList, linkList = createTestTopology()
#     requestList = generateRequests(nodeList, 5)

#     user = User()
#     eveon = game_gym(nodeList, linkList, requestList, user)

#     # check_env(eveon, warn=True)
#     # model = DQN(MlpPolicy, eveon, verbose=1)
#     # model.learn(total_timesteps=1000)

#     obs = eveon.reset()
#     while True:
#         action = eveon.get_action()
#         # action2 = model.predict(obs)
#         obs, rewards, dones, info = eveon.step(action)
#         if dones == True:
#             print(eveon.reward)
#             eveon.endGame()
#         eveon.render()

if __name__ == '__main__':
    main()