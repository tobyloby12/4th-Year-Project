# 4th-Year-Project

This repository contains the work done for the 4th year project on EONs in Arcade Games. It contains both the arcade game developed along with the code to train the RL agents.

The repository is split into many branches having various stages of the games development. The main branch has the original game in the main.py file and the gym converted game in the game_gym.py file.

The simplifications branch contains the simplified version of the game where the routing is done for the agent.

The dict_game branch contains the game that has been converted into a dictionary for ease of RL development. Additionally training and evaluation of the model can be found in the sw_dict_game branch.


# How to install dependancies

## For development:

- create environment
- navigate to 4th-year-project directory in a command prompt

- pip install -e .
- pip install -r requirements.txt
- pip install -r requirements_dev.txt

## For use:

- create environment
- navigate to 4th-year-project directory in a command prompt
- pip install -e .
- pip install -r requirements.txt

# How to run game

- To run the game navigate to the main.py file in src/optical_network_game
- Next run the game in the python terminal and play

# Gameplay and game rules

This game is a representation of an Elastic Optical Network (EON). On the right side there are requests coming in, which are in gray and contain 2 letters and a number. The letters represent the source node (starting point) and destination node (end point) respectively and these correspond to the names of the nodes in the center of the game screen. When the request is selected by the user, it will highlight in red. Use the up and down arrow keys to select which request you want and press return to enter the next phase of the game. 

In the center of the screen is a graph made of nodes (blue circles) and links (lines). When a request is selected the source and destination nodes in the request will be shown by the nodes being filled in with colour. When the request has been selected and enter is hit, the source node will be highlighted green and the link to select the next node will be highlighted yellow along with the corresponding link. If multiple paths are available, use the up and down arrow keys to select which path you want to take and press enter to select the path. Once you reach the destination node, the next phase of the game will begin.

The final part of the game requires the player to select the slots. These are represented on the right hand side of the game screen. The player can press the up and down keys to select which slots will be selected, and can press return to select the slots.

The objective of the game is to complete as many requests as possible and each successful request will give a point. If the request has run out of time it is considered blocked and this leads to a point being taken away from the total. At the end of the game the remaining time will be taken into consideration to add points to the score.

We hope that this game can be used for reinforcement learning purposes in elastic optical networks (EONs) and currently it is a proof of concept.
If there are any bugs or features you think should be added, please contact one of the members of the group.
