import gym
from time import sleep
from IPython.display import clear_output, display
import matplotlib.pyplot as plt
import importlib
from stable_baselines3.common.env_checker import check_env

import optical_network_game.game_gym
importlib.reload(optical_network_game.game_gym)
from optical_network_game.game_gym import *

from optical_network_game.requests import *
from optical_network_game.topology_generation import *

import optical_network_game.heuristic
importlib.reload(optical_network_game.heuristic)
from optical_network_game.heuristic import *

from stable_baselines3 import DQN
import pandas as pd



#Parameters for results collection
#Holdtime = 10 to 40 (For a traffic load of 5 to 20)
#Number of connection requests = 20
num_req = 20
#request interval = 2 seconds
req_int = 2
#time limit for each connection request = 10 seconds
time_limit = req_int + 1
#bandwidth per link = 5
link_BW = 5


#setting up the VSNL topology
nodeList, linkList = createPresetTopology("VSNL", num_slots=link_BW)

#Creating list to store results
results_heuristic = []

#Outer for loop to set hold time from 10 to 40 with increments of 2 to allow for collection of traffic load from 5 to 20 with step of 1
for holdtime in range(10,41):
    
    #number of episodes flag for the inner while loop
    num_episodes = 0

    results_list = {}

    #generating request lists and game environment
    requestList = generateRequests(nodeList, numberOfRequests=num_req, req_interval=req_int, hold_time=holdtime)
    user = User()
    env = game_gym(nodeList, linkList, requestList, user, dynamic=True)
    eveon = env
    check_env(env)
    heuristic = Heuristic(linkList)
    obs = env.reset()
    
    #for each traffic load setting the game runs for 30 episodes
    while num_episodes < 30:

        action = heuristic.next_action(obs)
        obs, rewards, dones, info = env.step(action)

        if dones == True:
            print(info)

            results_list = info
            results_list['traffic_load'] = holdtime/req_int
            
            #appending the final performance results into the results list for further processing
            results_heuristic.append(info)
            env.reset()
            heuristic = Heuristic(linkList)
            num_episodes += 1
            #debug print
            #print("Episode: " + str(num_episodes))

        env.render()









#after for loop is completed, save the results list as a csv file
df_heuristic = pd.DataFrame(results_heuristic)
df_heuristic
# saving the dataframe 
#INSERT PROPER RESULTS NAME HERE
df_heuristic.to_csv('./results/new_results_heuristic.csv')

