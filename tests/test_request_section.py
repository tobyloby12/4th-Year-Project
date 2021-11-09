import pytest
from optical_network_game import main
from optical_network_game.node import Node
from optical_network_game.user import User
from optical_network_game.requests import Request
from optical_network_game.link import Link


#################################################################################
# GAMESTART
#################################################################################

# GIVEN a user has just started the game and no requests are present
# WHEN the game starts
# THEN the score and timer should be set and the current gamemode should be request,
# the game should start after the first key stroke,
# the timer should count down in seconds,
# the topology should be shown with nothing selected or highlighted,
# the spectrum should have all the links shown in the links unselected box and none in the selected box,
# when the user produces an input nothing should happen



##################################################################################
# REQUESTS FUNCTIONALITY
##################################################################################



# GIVEN the game has started and set up correctly and there are no requests present
# WHEN a new request comes in 
# THEN the requests should be put at the top of the box and it should be selected,
# else the reqeust should be put underneath the lowest request,
# the request timer should start going down and should complete within the correct time frame,
# the request should be removed when the request has finished its timer,
# the user should have the correct request selected as shown on the screen



# GIVEN the game has started and set up correctly and there are requests present
# WHEN a new request comes in 
# THEN the reqeust should be put underneath the lowest request,
# the request timer should start going down and should complete within the correct time frame,
# the request should be removed when the request has finished its timer,
# the user should have the correct request selected as shown on the screen



# GIVEN the game has started and set up correctly and multiple requests are available
# WHEN the user presses down key
# THEN it should select the below request and if the bottom request is selected already, it should select the top request, 
# the user should have the correct request selected as shown on the screen



# GIVEN the game has started and set up correctly and multiple requests are available
# WHEN the user presses down key
# THEN it should select the above request and if the top request is selected already, it should select the bottom request,
# the user should have the correct request selected as shown on the screen



# GIVEN the game has started and set up correctly and multiple requests are available
# WHEN the user presses enter
# THEN the user should move to topology mode,
# the users request selected should be correctly updated



# GIVEN the game has started and there are potential requests
# WHEN the last request times out
# THEN the game should end and the final score should be displayed
# an ending screen should be displayed