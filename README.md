# 4th-Year-Project

This repository contains the work done for the 4th year project on EONs in Arcade Games. It contains both the arcade game developed along with the code to train the RL agents.

In this branch, the RL agent is fed a dictionary of key values to represent the environment rather than pixel values of the game screen. The game and reward system was also modified to improve the agent training process. In particular, the routing aspect was reduced to selecting one of three precalculated shortest paths from the source to destination node of a request.


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

This game is a representation of an Elastic Optical Network (EON). On the right side there are requests coming in, which are in gray and contain 2 letters and a number. The letters represent the source node (starting point) and destination node (end point) respectively and these correspond to the names of the nodes in the center of the game screen. Incoming requests are automatically selected.

In the center of the screen is a graph made of nodes (blue circles) and links (lines). When there is an active request, a random path from the source to destination node will be highlighted. This represents one of three precalculated shortest paths. The up and down arrow keys are used to choose which path you want to take. Pressing enter selects the corresponding path and the next phase of the game will begin.

The final part of the game requires the player to select the slots. These are represented on the right hand side of the game screen. The player can press the up and down keys to select which slots will be selected, and can press return to select the slots. If the player selects slots that are already occupied (in red), this will count as an 'invalid' action and points will be deducted. Doing this more than five consecutive times will cause the game to end early. This was implemented to dissuade the RL agent from only selecting return when playing the game.

The objective of the game is to complete as many requests as possible and each successful request will give a point. If a request has run out of time it is considered blocked and this leads to a point being taken away from the total. At the end of the game the remaining time will be taken into consideration to add points to the score.
