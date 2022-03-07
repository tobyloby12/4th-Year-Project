from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *
import gym
import pygame, sys
from pygame.locals import *
from gym import spaces
from stable_baselines3.common.env_checker import check_env
import numpy as np
# from stable_baselines.common.vec_env import DummyVecEnv
# from stable_baselines.deepq.policies import MlpPolicy

from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.evaluation import evaluate_policy
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import numpy as np
import tensorflow as tf

#from stable_baselines.common.vec_env import DummyVecEnv
#from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines3 import DQN
from stable_baselines3 import A2C
import json
import cv2

#additional code added by me just for testing
import matplotlib
import matplotlib.pyplot as plt
import torch
#importing IPython's display module to plot images
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython: from IPython import display
from itertools import count
import time
from IPython.display import clear_output
import tensorboard


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

        #ADDED also the req_num as the number of connection requests in the episode
        self.req_num = len(requestList)
        #debug
        print(self.req_num)

        #see if this changes things, setting action space to 6 actions only instead of 7 (original)
        #changed to 4
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
        
        #ADDED cumulative reward
        self.reward_sum = 0

        #ADDED connection service flag (tracks the number of connections fulfilled)
        self.req_complete = 0

        #ADDED number of links in routing
        self.num_links = 0
        
        
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
        #debug print
        #print("ACTION")
        #print(action)
        

        #TESTING THIS 
        #resetting the self.reward variable to be 0, thus for every step, the reward 
        #isnt the cumulative reward, rather the reward gained for the action state.
        self.reward = 0
        #cause the if action !=6 part sends the chosen agent action to return the reward

        for event in pygame.event.get():
            # If game screen is closed, Pygame is stopped
            if event.type == pygame.QUIT:
                self.endGame()
        # Updates requests and reduces timer every second
            elif event.type == self.timer_event:
                self.requestUpdate()

            #editing this so only 4 actions
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action =  0
                elif event.key == pygame.K_DOWN:
                    action = 1
                #elif event.key == pygame.K_LEFT:
                   #action = 2
                #elif event.key == pygame.K_RIGHT:
                    #action = 3
                elif event.key == pygame.K_RETURN:
                    #action = 4
                    action = 2
                elif event.key == pygame.K_BACKSPACE:
                    #action = 5
                    action = 3
        #if action != 4:
        if self.requestMode == True:
            self.request_logic(action)
        elif self.topologyMode == True:
            self.topology_logic(action)
        elif self.spectrumMode == True:
            self.spectrum_logic(action)
        
        obs = np.array(pygame.surfarray.array3d(self.DISPLAYSURF.subsurface((210, 0, 560, 600))), dtype=np.uint8)
        obs = cv2.resize(obs, dsize=(256, 256))

        # if (self.timer < self.requestList[-1].getTimeStart() and self.activeRequests == []) or self.timer == 0:
        if self.timer == 0:
            self.done = True
            #debug print
            print("Cumulative Reward Obtained (GAME END):")
            print(self.reward_sum)

        self.info[self.timer2] = {
            'display': obs,
            'user': self.user
            }

        #debug THIS WORKS
        #print("STEP REWARD:")
        #print(self.reward)
        #adds the reward to the cumulative reward variable
        self.reward_sum += self.reward

        #updates the score based on the cumulative reward
        #self.SCORE += self.reward

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
        #         elif event.key == pygame.K_LEFT:
        #             return 2
        #         elif event.key == pygame.K_RIGHT:
        #             return 3
        #         elif event.key == pygame.K_RETURN:
        #             return 4
        #         elif event.key == pygame.K_BACKSPACE:
        #             return 5
        #         else:
        #             return 6


    def render(self, mode = "human"):
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
            #try changing this to red?
            node.drawNode(self.DISPLAYSURF, self.RED)
        
        

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
        self.selectedLinks = []
        for entry in self.user.getLinksSelected():
            self.selectedLinks.append(entry[1])
        unselectedLinks = self.linkList.copy()
        for link in self.linkList:
            if link in self.selectedLinks:
                unselectedLinks.remove(link)
        
        # selected links text to display
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 27)
        textsurface = myfont.render(f'Selected Links:', False, self.WHITE)
        text_rect = textsurface.get_rect(center=spectrumBox.center)
        self.DISPLAYSURF.blit(textsurface, (text_rect[0], self.HEADER + self.MARGIN))
        
        # drawing selected links
        if self.selectedLinks != []:
            for i in range(len(self.selectedLinks)):
                textsurface = myfont.render(f'{self.selectedLinks[i].getName()}', False, self.WHITE)
                self.DISPLAYSURF.blit(textsurface, (self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + self.MARGIN + 6, \
                    self.HEADER + self.MARGIN + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5)))
                self.selectedLinks[i].drawSpectrum(self.DISPLAYSURF, self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + \
                    self.MARGIN + 6 + 35, self.HEADER + self.MARGIN + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5))

        # unselected links text to display
        textsurface = myfont.render(f'Unselected Links:', False, self.WHITE)
        text_rect = textsurface.get_rect(center=spectrumBox.center)
        self.DISPLAYSURF.blit(textsurface, (text_rect[0], self.HEADER + self.MARGIN + (len(self.selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5)))

        # drawing unselected links
        if unselectedLinks != []:
            for i in range(len(unselectedLinks)):
                textsurface = myfont.render(f'{unselectedLinks[i].getName()}', False, self.WHITE)
                self.DISPLAYSURF.blit(textsurface, (self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + self.MARGIN + 6, \
                    self.HEADER + self.MARGIN + (len(self.selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5) + (i + 1)*(self.SPECTRUMBOXHEIGHT + 5)))
                unselectedLinks[i].drawSpectrum(self.DISPLAYSURF, self.MARGIN + self.INCOMINGREQUESTWIDTH + self.MARGIN + self.NETWORKTOPOLOGYWIDTH + \
                    self.MARGIN + 6 + 35, self.HEADER + self.MARGIN + (len(self.selectedLinks) + 1)*(self.SPECTRUMBOXHEIGHT + 5) + \
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

                #COMMENTED OUT, TESTING SCORE PRINTOUT
                #changed to -5 from -1
                self.SCORE -= 5

                #changed to -1
                #reward expiry
                #self.reward -= 100
                self.reward -= 10
                
                #adding to the req_complete flag 
                self.req_complete += 1

                if self.req_complete == self.req_num:

                    #if the only connection expires then the episode ends
                    #debug
                    #changed this so that if the connection which expires is the final conn then the episode ends
                    print("Request Timed Out, cumulative Reward:")
                    print(self.reward_sum)
                    self.done = True

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
            
            #placeholder reward to test 
            #changed to 2 from 4
            if action == 2:
                #print("no request (enter) reward")
                #originally set to + 10
                #self.reward += 30
                
                #testing this normalised
                #self.reward += 0.3
                self.reward += 0.3

            elif action == 0 or action == 1 or action == 3: 
                #originally set to -10
                #self.reward -= 1

                #testing this normalised
                #self.reward -= 1
                self.reward -= 1

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

                #Experimenting reward function
                #unchanged
                #self.reward -= 1

                #testing this normalised
                self.reward -= 0.3

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

                #Experimenting reward function
                #unchanged
                #self.reward -= 1

                #testing this normalised
                self.reward -= 0.3
            
            # IF ENTER key is pressed
            # THEN the user moves to the topology space to service the request selected
            #changed from 4 to 2
            elif action == 2:
                #self.reward += 0
                #experimenting reward function
                #changed to +10 originally
                #changed to 20 on latest run
                #print("enter with request")
                #self.reward += 30

                #testing this normalised
                self.reward += 0.3
                
                self.requestMode = False
                self.topologyMode = True
                #set number of links value to 0 upon initiation of topology mode
                self.num_links = 0

                #adding score reward for progressing from game mode
                self.SCORE += 1

                #TESTING if agent gets reward = current cumulative reward in each mode (so basically reset to 0 or times 2 if -ve or +ve)
                #might need to change this to just adding like 20 as a one step reward if the agent passes into a new stage
                #self.reward += 100

                # user automatically starts at the source node of the request
                self.user.setCurrentNode(self.user.currentRequest.getSourceNode())
                # source node is automatically set as selected
                self.user.getCurrentNode().setSelected(True)
                # the first link and adjacent node connected to the source node (in the list) will be automatically highlighted
                self.user.getCurrentNode().getLinks()[0][0].setHighlighted(True)
                self.user.getCurrentNode().getLinks()[0][1].setHighlighted(True)
                # defines index for use in topology space
                self.index = 0

                
            #changed to only backspace (action 3)
            elif action == 3:
                #if left right or backspace pressed
                #experimenting reward function
                #changed to -10
                #self.reward -= 5
                
                #testing this normalised
                self.reward -= 1
            


    def topology_logic(self, action):
        # IF BACKSPACE key is pressed
        #changed to 3 for backspace from 5
        if action == 3:
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

                #returning to request mode action
                #experimenting reward function
                #changed to -10
                #self.reward -= 1
                #self.reward -= 10

                #testing this normalised
                self.reward -= 1

                #adding visual score screen update set to -5 first
                self.SCORE -= 5
                
            # IF BACKSPACE key is pressed and the user is not at the source node
            # THEN the user moves back to previous node
            else:
                links_selected = self.user.getLinksSelected()
                highlightedSpectrum = [0]*NUMBEROFSLOTS
                links_selected[-1][1].setSpectrumHighlighted(highlightedSpectrum)
                
                # define previous node and link pair from selected links list
                previous = self.user.getLinksSelected()[-1]
                # deselects the current node user is at
                self.user.getCurrentNode().setSelected(False)
                # selects the pervious node user was at
                self.user.setCurrentNode(previous[0])


                #experimenting reward function
                #undoing routing selection
                #set to -1
                #self.reward -= 1

                #testing this normalised
                #changed to -0.3 from -0.1
                self.reward -= 0.2

                #reducing number of links
                self.num_links -= 1


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
                # self.DISPLAYSURF.fill(self.RED)
                pass
                

        # IF UP arrow key is pressed
        # THEN the link above the current one is selected
        if action == 0:
            
            #CONDITIONAL STATEMENT TO CHECK NODE ALLOCATION
            #if the current node selected was the destination node then penalise agent for moving away
            if self.user.getCurrentNode() == self.user.getCurrentRequest().getDestNode():
                #initial reward setting
                self.reward -= 1
            #then carry on the rest of the code
            
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


            #CONDITIONAL STATEMENT TO CHECK NODE AFTER MOVEMENT
            #if the new node is the dest node then positive reward agent
            if self.user.getCurrentNode() == self.user.getCurrentRequest().getDestNode():
                self.reward += 5

            #else if the new node selected is not the destinatino node then negative reward
            elif self.user.getCurrentNode() != self.user.getCurrentRequest().getDestNode():
                #initial reward
                self.reward -= 0

            #Experimenting reward function
            #unchanged
            #self.reward -= 1

            #testing this normalised
            #changed to 0.4 from 0.5
            #self.reward += 0.4

        # IF DOWN arrow key is pressed
        # THEN the link below the current one is selected
        elif action == 1:
            
            #CONDITIONAL STATEMENT TO CHECK NODE ALLOCATION
            #if the current node selected was the destination node then penalise agent for moving away
            if self.user.getCurrentNode() == self.user.getCurrentRequest().getDestNode():
                #initial reward setting
                self.reward -= 1
            #then carry on the rest of the code
            
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

            
            #CONDITIONAL STATEMENT TO CHECK NODE AFTER MOVEMENT
            #if the new node is the dest node then positive reward agent
            if self.user.getCurrentNode() == self.user.getCurrentRequest().getDestNode():
                self.reward += 5

            #else if the new node selected is not the destinatino node then negative reward
            elif self.user.getCurrentNode() != self.user.getCurrentRequest().getDestNode():
                #initial reward
                self.reward -= 0


            #Experimenting reward function
            #unchanged
            #self.reward -= 1

            #testing this normalised
            #changed to 0.4 from 0.5
            #self.reward += 0.4

        # IF ENTER key is pressed
        # THEN the user selects the link and moves to the adjacent node
        #changed to 2 from 4 for smaller action steps
        elif action == 2:
            
            #experimenting reward function
            #commented out for now
            #self.reward += 1
            
            # IF ENTER key is pressed and user has not reached the destination node
            if self.user.getCurrentNode() != self.user.getCurrentRequest().getDestNode():
                 #routing to a non destination node
                #Experimenting reward function
                #changed to +1
                #self.reward -= 5
                #self.reward += 1

                #testing this normalised
                self.reward -= 5

                #increasing number of links
                self.num_links += 1

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

                        # need to include selecting first few slots automatically
                        bandwidth = self.user.getCurrentRequest().getBandwidth()
                        linksSelected = [link[1] for link in self.user.getLinksSelected()]
                        highlightedSpectrum = [0]*self.NUMBEROFSLOTS
                        for i in range(bandwidth):
                            highlightedSpectrum[i] = 1
                        for link in linksSelected:
                            link.setSpectrumHighlighted(highlightedSpectrum)
                        self.spectrumIndex = 0

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

                    #adding number of links to be 1 from reset value of 0
                    self.num_links += 1

                    # need to include selecting first few slots automatically
                    bandwidth = self.user.getCurrentRequest().getBandwidth()
                    linksSelected = [link[1] for link in self.user.getLinksSelected()]
                    highlightedSpectrum = [0]*self.NUMBEROFSLOTS
                    for i in range(bandwidth):
                        highlightedSpectrum[i] = 1
                    for link in linksSelected:
                        link.setSpectrumHighlighted(highlightedSpectrum)
                    self.spectrumIndex = 0
                    
                    #moving to spectrum mode

                    #CONDITIONAL REWARDS FOR NUMBER OF LINKS
                    #if the shortest route was chosen give huge reward
                    if len(linksSelected) == 1:
                        #debug print
                        #print("1 link")                       
                        #print(len(linksSelected))
                        #print(self.num_links)
                        self.reward += 10
                        self.SCORE += 5

                    #if route chosen was 2 links, give small negative reward
                    elif len(linksSelected) == 2:
                        #debug print
                        #print("2 links")
                        #print(len(linksSelected))
                        #print(self.num_links)
                        self.reward -= 50
                        self.SCORE -= 1

                    #if route chosen was greater than or equal to 3 links, give large negative reward
                    elif len(linksSelected) >= 3:
                        #debug print
                        #print("more than 3 links")
                        self.reward -= 100
                        self.SCORE -= 5


                    #Experimenting reward function
                    #added reward + 20
                    #self.reward += 30

                    #testing this normalised
                    #changed from 1 to 2
                    #self.reward += 2

                    #adding score reward for progressing from game mode
                    #changed to 4 from 2
                    #self.SCORE += 4

                    #TESTING if agent gets reward = current cumulative reward in each mode (so basically reset to 0 or times 2 if -ve or +ve)
                    #might need to change this to just adding like 20 as a one step reward if the agent passes into a new stage
                    #self.reward += 100
        
        #commented out as left and right not used anymore
        #elif action == 2 or action == 3:
            #Experimenting reward function
            #if left or right used
            #changed to -20
            #self.reward -= 5
            #self.reward -= 20

            #testing this normalised
            #self.reward -= 1


    def spectrum_logic(self, action):
        # if backspace is pressed go back to topology mode
        # should go back to node before destination node
        # selected links should be deselected
        # automatically highlight links
        # removes the links from user selected links
        #changed to 3 from 5 for new backsapce action value
        if action == 3:
            self.topologyMode = True
            self.spectrumMode = False

            #linksSelected = [link[1] for link in self.user.getLinksSelected()]
            links_selected = self.user.getLinksSelected()
            highlightedSpectrum = [0]*NUMBEROFSLOTS
            #for link in linksSelected:
            #    link.setSpectrumHighlighted(highlightedSpectrum)

            links_selected[-1][1].setSpectrumHighlighted(highlightedSpectrum)

            #links_selected = self.user.getLinksSelected()

            self.user.setCurrentNode(links_selected[-1][0])
            links_selected[-1][1].setSelected(False)
            self.user.getCurrentRequest().getDestNode().setSelected(False)
            availableLinks = self.checkAvailable()
            availableLinks[self.index][0].setHighlighted(True)
            availableLinks[self.index][1].setHighlighted(True)
            self.user.getLinksSelected().remove(links_selected[-1])

            #returning to topology mode
            #Experimenting reward function
            #changed to -20
            #self.reward -= 1
            #self.reward -= 20

            #testing this normalised
            self.reward -= 3

            #setting visual changes to the score screen set to -5 for now
            self.SCORE -= 5
            

        # if left is pressed then the selected should be shifted to the left by 1 unless at the most left where it will jump to right
        #LEFT CHANGED TO UP action is now 0 from 2
        elif action == 0:
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

            #Experimenting reward function
            #unchanged
            #self.reward -= 1

            #testing this normalised
            self.reward += 1


        # if right is pressed then the selected should be shifted to the right by 1 unless at the most right where it will jump to left
        #RIGHT CHANGED TO down action is now 1 from 2
        elif action == 1:
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
            
            #Experimenting reward function
            #unchanged
            #self.reward -= 1

            #testing this normalised
            self.reward += 1

        # if return is pressed, selected links should be checked for if they are valid and if they are they should be selected and links
        # should be updated
        # otherwise an error message should pop up
        #changed from 4 to 2 for enter
        elif action == 2:
            # check that there are no conflicts
            linksSelected = [link[1] for link in self.user.getLinksSelected()]
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
                            
                            

            if possible == True:
                self.completions.append((self.user.getCurrentRequest(), self.user.getLinksSelected().copy(), link.getSpectrumHighlighted().copy()))
                for link in linksSelected:
                    newSelected = [sum(x) for x in zip(link.getSpectrum(), link.getSpectrumHighlighted())]
                    link.setSpectrum(newSelected)
                    highlightedSpectrum = [0]*5
                    link.setSpectrumHighlighted(highlightedSpectrum)
                # throw back into request mode and add point and deselect highlighted spectrum, remove request
                
                #COMMENTED OUT, TESTING SCORE PRINTOUT
                #set to 10 from +1
                self.SCORE += 10
                
                self.user.getCurrentRequest().complete()
                self.activeRequests.remove(self.user.getCurrentRequest())
                self.user.getCurrentRequest().setTimeAllocated(self.timer)
                availableLinks = self.clearAll()

                #successful spectrum assignment (one connection serviced)
                #experimenting reward function
                #changed to + 30
                #self.reward += 100
                #self.reward += 30

                #testing this normalised
                #set to +10 from 1
                self.reward += 1
                
                #TESTING if agent gets reward = current cumulative reward in each mode (so basically reset to 0 or times 2 if -ve or +ve)
                #might need to change this to just adding like 20 as a one step reward if the agent passes into a new stage
                #self.reward += 100
                

                #adding to the req_complete flag 
                self.req_complete += 1

                if self.req_complete == self.req_num:
                    #changed so that if the number of requests is serviced then the episode ends
                    #debug
                    print("End episode, cumulative Reward:")
                    print(self.reward_sum)
                    #CHANGE THIS SO THAT IT SUCCESSFULLY ENDS THE GAME UPON CONNECTION SERVICED
                    self.done = True
            
            else:
                #invalid spectrum assignment
                #Experimenting reward function
                #changed to - 10
                #self.reward -= 5
                #self.reward -= 30

                #testing this normalised
                self.reward -= 50
                #setting such that score is minused
                self.SCORE -= 1

        #commented out as they are not used now
        #elif action == 0 or action == 1:
            #if up or down are used (irrelevant controls in this mode)
            #experimenting reward function 
            #changed to -20
            #self.reward -= 5
            #self.reward -= 20

            #testing this normalised
            #self.reward -= 1

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
    requestList = generateRequests(nodeList, 6)

    user = User()
    eveon = game_gym(nodeList, linkList, requestList, user)

    check_env(eveon, warn=True)
    model = DQN('MlpPolicy', eveon, verbose=1, buffer_size=100, device='cuda')
    model.learn(total_timesteps=25000)
    model.save("DQNEveon")

    obs = eveon.reset()
    while True :
        action, states_ = model.predict(obs, deterministic=True)
        # action = 6
        obs, rewards, dones, info = eveon.step(action)
        print(action)
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