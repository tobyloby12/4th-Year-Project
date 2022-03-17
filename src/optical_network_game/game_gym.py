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
# from stable_baselines3 import DQN
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
        self.numSlots = len(self.linkList[0].spectrum)
        self.requestList = requestList
        self.user = user

        self.action_space = spaces.Discrete(3)
        
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

        # resetting completed in requests
        for request in self.requestList:
            request.completed = False

        # initialize pygame
        pygame.init()

        #cumulative variable storing number of links made per connection req
        self.linksmade_cum = 0

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
        self.possible = 0
        self.false_counter = 0
        self.index = 0
        self.spectrumIndex = 0

        # creating observation space for gym
        # self.observation_space = spaces.Box(
        #     low= 0,
        #     high = 255,
        #     shape= (256, 256, 3),
        #     dtype=np.uint8
        #     )
        

        self.observation_space_dict = {
            'request_bandwidth': spaces.Box(low=1, high=self.numSlots, shape = (1,), dtype = np.int8),
            'slot_selected': spaces.Box(low=0, high=self.numSlots, shape = (1,), dtype = np.int8),
            'possible': spaces.Box(low=0, high=1, shape = (1,), dtype = np.int8),
            'false_counter': spaces.Box(low=0, high=6, shape = (1,), dtype = np.int8),
            'path_length': spaces.Box(low=0, high=len(self.linkList), shape = (1,), dtype = np.int8),
            'mode': spaces.Box(low=0, high=2, shape = (1,), dtype = np.int8)
            }

        for i in range(len(self.linkList)):
            self.observation_space_dict[f'topology_link_a{i}'] = spaces.Box(low=0, high=len(self.linkList), shape = (1,), dtype = np.int8)
            self.observation_space_dict[f'topology_link_b{i}'] = spaces.Box(low=0, high=len(self.linkList), shape = (1,), dtype = np.int8)

        for i in range(len(self.linkList)):
            self.observation_space_dict[f'current_path_link{i}'] = spaces.Box(low=0, high=1, shape = (1,), dtype = np.int8)

        for i in range(len(self.linkList)):
            for j in range(self.numSlots):
                self.observation_space_dict[f'link_spectrum_{j}_{i}'] = spaces.Box(low=0, high=1, shape = (1,), dtype = np.int8)


        mins = np.array([x.low[0] for x in self.observation_space_dict.values()])
        maxs = np.array([x.high[0] for x in self.observation_space_dict.values()])
        
        self.observation_space = spaces.Box(mins, maxs, dtype=np.int8)

        graph = self.links()

        self.state = {
            'request_bandwidth': np.ones(shape=(1,), dtype=np.int8),
            'slot_selected': np.zeros(shape=(1,), dtype=np.int8),
            'possible': np.zeros(shape=(1,), dtype=np.int8),
            'false_counter': np.zeros(shape=(1,), dtype=np.int8),
            'path_length': np.ones(shape=(1,), dtype=np.int8),
            'mode': np.zeros(shape=(1,), dtype=np.int8),
            'topology': graph, 
            'current_path': np.zeros(shape=(len(self.linkList),), dtype=np.int8),
            'link_spectrum': np.zeros(shape=(len(self.linkList),len(self.linkList[0].spectrum)), dtype=np.int8)
            }
        self.info = {}

        if self.user.getCurrentRequest() != None:
            self.user.deselectRequest()

        highlighted = [0]*self.numSlots
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
        # obs = np.array(pygame.surfarray.array3d(self.DISPLAYSURF.subsurface((210, 0, 560, 600))), dtype=np.uint8)
        # obs = cv2.resize(obs, dsize=(256, 256))
        # print(obs.shape)
        obs = self.get_obs()
        return obs


    def step(self, action):
        # print(self.requestMode)
        # print(action)
        self.reward = 0
        for event in pygame.event.get():
            # If game screen is closed, Pygame is stopped
            if event.type == pygame.QUIT:
                self.endGame()
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
                # elif event.key == pygame.K_BACKSPACE:
                #     action = 3
        
        if self.requestMode == True:
            self.request_logic(action)
            mode = 0
        elif self.topologyMode == True:
            self.topology_logic(action)
            mode = 1
        elif self.spectrumMode == True:
            self.spectrum_logic(action)
            mode = 2
        
        # obs = np.array(pygame.surfarray.array3d(self.DISPLAYSURF.subsurface((210, 0, 560, 600))), dtype=np.uint8)
        # obs = cv2.resize(obs, dsize=(256, 256))
        if self.user.getCurrentRequest() != None:
            self.state['request_bandwidth'] = np.array(self.user.getCurrentRequest().getBandwidth())
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            # self.state['current_path'] = np.pad(np.array([[link.getNode1().getID(), link.getNode2().getID()] for link in linksSelected]), 
            # ((0, 5 - len(linksSelected)), (0, 0)), mode='constant')
            path_IDs = [[link.getID()] for link in linksSelected]
            current_path = np.zeros(shape=(len(self.linkList),), dtype=np.int8)
            for ID in path_IDs:
                current_path[ID] = 1
            self.state['current_path'] = current_path
            self.state['path_length'] = np.array(len(linksSelected), dtype=np.int8)
            self.state['link_spectrum'] = np.array([link.getSpectrum() for link in self.linkList])
            self.state['slot_selected'] = np.array(self.spectrumIndex)
            self.state['possible'] = np.array(self.possible)
            self.state['false_counter'] = np.array(self.false_counter, dtype=np.int8)
            self.state['mode'] = np.array(mode, dtype=np.int8)
        else:
            self.state['request_bandwidth'] = np.ones(shape=(1,), dtype=np.int8)
            self.state['current_path'] = np.zeros(shape=(len(self.linkList),), dtype=np.int8)
            self.state['path_length'] = np.ones(shape=(1,), dtype=np.int8)
            self.state['link_spectrum'] = np.array([link.getSpectrum() for link in self.linkList])
            self.state['slot_selected'] =np.zeros(shape=(1,), dtype=np.int8)
            self.state['possible'] = np.array(self.possible)
            self.state['false_counter'] = np.array([self.false_counter], dtype=np.int8)
            self.state['mode'] = np.array(mode, dtype=np.int8)

        # if action != 6:    
        #     print(self.state)

        self.cum_reward += self.reward
        if (self.timer < self.requestList[-1].getTimeStart() and self.activeRequests == []):
            self.done = True
            print('No more requests.')
        

        if self.done == True:
            
            self.reward = -(len(self.requestList) - len([request for request in self.requestList if request.completed == True]))*1000/200
            self.cum_reward += self.reward
            print(f'Total reward for this episode is {self.cum_reward*200}')
            # Calculate blocking probablity
            blocking_ratio = len([request for request in self.requestList if request.completed == True])/len(self.requestList)
            self.info['bp'] = blocking_ratio
            #avg links selected
            avg_links = self.linksmade_cum/len([request for request in self.requestList if request.completed == True]) # changed to be completed requests
            self.info['avg_length'] = avg_links
            
        obs = self.get_obs()


        return obs, self.reward*200, self.done, self.info


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
        textsurface = myfont.render(f'SCORE: {str(self.cum_reward*200)}', False, WHITE)
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
                continuous, contiguous = self.typeBlock(request)
                if contiguous == True and continuous == False:
                    print('Lack of continuous slots')
                elif contiguous == False:
                    print('Lack of contiguous slots')
                self.SCORE -= 1
                # self.reward -=200
                self.reward = -50
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
            highlightedSpectrum = [0]*self.numSlots
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0


    def topology_logic(self, action):

        # IF UP arrow key is pressed
        # THEN the link above the current one is selected
        if action == 0:

            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.numSlots
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
            highlightedSpectrum = [0]*self.numSlots
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0

        elif action == 1:

            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            highlightedSpectrum = [0]*self.numSlots
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
            highlightedSpectrum = [0]*self.numSlots
            for i in range(bandwidth):
                highlightedSpectrum[i] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)
            self.spectrumIndex = 0

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

            # maximum path length
            max_path_len = 0
            for path in self.available_paths:
                path_len = len([link for link in path if type(link) is Link])
                if path_len > max_path_len:
                    max_path_len = path_len
            

            self.reward = (max_path_len - (len(linksSelected)))*1000/200
            # adding the number of links made
            self.linksmade_cum += len(linksSelected)
            highlightedSpectrum = [0]*self.numSlots
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
        # if action == 3:

        #     for item in self.available_paths[self.index]:
        #         item.setHighlighted(True)
            
        #     for item in self.available_paths[self.index]:
        #         item.setSelected(False)

        #     self.topologyMode = True
        #     self.spectrumMode = False
            

        # if up is pressed then the selected should be shifted to the up by 1 unless at the most up where it will jump to right
        if action == 0:
            self.false_counter = 0
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == 0:
                self.spectrumIndex = self.numSlots - bandwidth
            else:
                self.spectrumIndex -= 1
            highlightedSpectrum = [0]*self.numSlots
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)


        # if right is pressed then the selected should be shifted to the right by 1 unless at the most right where it will jump to up
        elif action == 1:
            self.false_counter = 0
            bandwidth = self.user.getCurrentRequest().getBandwidth()
            if self.spectrumIndex == self.numSlots - bandwidth:
                self.spectrumIndex = 0
            else:
                self.spectrumIndex += 1
            highlightedSpectrum = [0]*self.numSlots
            linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
            for i in range(bandwidth):
                highlightedSpectrum[i + self.spectrumIndex] = 1
            for link in linksSelected:
                link.setSpectrumHighlighted(highlightedSpectrum)

        # if return is pressed, selected links should be checked for if they are valid and if they are they should be selected and links
        # should be updated
        # otherwise an error message should pop up
        linksSelected = [link for link in self.available_paths[self.index] if type(link) is Link]
        self.possible = 1
        for link in linksSelected:
            for i in range(self.numSlots):
                if link.getSpectrumHighlighted()[i] == 1:
                    if link.getSpectrum()[i] == 1:
                        self.possible = 0
        if action == 2:          
            if self.possible == 1:
                self.false_counter = 0
                self.reward = 0.5
                # self.reward -= (len(self.available_paths[self.index])*5)/200
                self.reward += int((self.user.getCurrentRequest().timeLimit \
                - (self.user.getCurrentRequest().timeStart - self.timer2))*200)/200
                self.completions.append((self.user.getCurrentRequest(), linksSelected.copy(), link.getSpectrumHighlighted().copy()))
                for link in linksSelected:
                    newSelected = [sum(x) for x in zip(link.getSpectrum(), link.getSpectrumHighlighted())]
                    link.setSpectrum(newSelected)
                    highlightedSpectrum = [0]*self.numSlots
                    link.setSpectrumHighlighted(highlightedSpectrum)
                # throw back into request mode and add point and deselect highlighted spectrum, remove request
                self.SCORE += 1
                self.user.getCurrentRequest().complete()
                self.activeRequests.remove(self.user.getCurrentRequest())
                self.user.getCurrentRequest().setTimeAllocated(self.timer)
                availableLinks = self.clearAll()
            else:
                self.reward = -0.3
                self.false_counter += 1
            
            if self.false_counter > 5:
                self.done = True
                print('Too many invalid actions.')


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
        highlighted = [0]*self.numSlots
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

    def links(self):
        edges = []
        for node in self.nodeList:
            for link in node.getLinks():
                edges.append((link[1].getNode1().getID(), link[1].getNode2().getID()))
        edges = set(edges)

        graph = np.zeros(shape=(len(self.linkList),2), dtype=np.int8)
        for i, link in enumerate(edges):
            graph[i] = link[0], link[1]

        return graph

    def get_obs(self):
        return np.concatenate(np.array([x.flatten() for x in self.state.values()], dtype=object))

    def typeBlock(self, request):
        state = self.state
        continuous = False
        contiguous = False
        # check contiguous
        for path in self.available_paths:
            inter_contiguous = True
            links = [link for link in path if type(link) is Link]
            for link in links:
                max_contiguous = 0
                for i in range(self.numSlots):
                    num_contiguous_slots = 0
                    if link.getSpectrum()[i] == 0:
                        num_contiguous_slots += 1
                    else:
                        num_contiguous_slots = 0

                    if max_contiguous <= num_contiguous_slots:
                        max_contiguous = num_contiguous_slots

                if max_contiguous < request.getBandwidth():
                    inter_contiguous = False
                        
            if inter_contiguous == True:
                contiguous = True


########
        # check continuous
        if contiguous == True:
            # finding which paths have enough spectrum and eliminating impossible paths
            non_blocked = []
            bandwidth = request.getBandwidth()
            # checking each path
            possible = False
            for available_path in self.available_paths:
                # checking all possible places where consecutive free could be
                for i in range(self.numSlots - bandwidth + 1):
                    possible = True
                    # checking through each cell in the bandwidth capacity
                    for j in range(bandwidth):
                        links = [link for link in available_path if type(link) is Link]
                        spectrum_together = [link.getSpectrum() for link in links]
                        for spectrum in spectrum_together:
                            if spectrum[i+j] != 0:
                                possible = False
                    # appending to new list which contains paths unobstructed
                    if possible == True:
                        non_blocked.append(available_path)

            if non_blocked == []:
                continuous = False
            else:
                continuous = True
        return continuous, contiguous


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
    nodeE = Node(4, 'E', 400, 100)
    # testLinks
    num_slots = 4
    link1 = Link(0, nodeA, nodeB, num_slots)
    link2 = Link(1, nodeB, nodeC, num_slots)
    link3 = Link(2, nodeB, nodeD, num_slots)
    link4 = Link(3, nodeA, nodeC, num_slots)
    link5 = Link(4, nodeC, nodeD, num_slots)
    link6 = Link(5, nodeA, nodeE, num_slots)

    nodeList = [nodeA, nodeB, nodeC, nodeD, nodeE]
    linkList = [link1, link2, link3, link4, link5, link6]
    # nodeList = [nodeA, nodeB, nodeC]
    # linkList = [link1, link2]

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
        # print(obs.shape)
        if dones == True:
            # print(eveon.cum_reward)
            # with open('info.json', 'w') as outfile:
            #     json.dump(info, outfile)

            eveon.reset()

        eveon.render()

if __name__ == '__main__':
    main()