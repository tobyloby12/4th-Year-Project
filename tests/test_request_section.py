import pytest


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



# GIVEN the game has started and set up correctly
# WHEN a new request comes in
# THEN if there are no requests present the requests should be put at the top of the box and it should be selected,
# else the reqeust should be put underneath the lowest request,
# the timer should start going down and should complete within the correct time frame,
# the request should be removed when the request has finished its timer,



# GIVEN the game has started and set up correctly and multiple requests are available
# WHEN the user produces an input
# THEN the game should respond accordingly; if it is a down key then the request selected should be the one before the
# arrow key was pressed unless it is the bottom one where it should return to the top, 
# if it is up then it should be the one above and if it is the top one it should go to the bottom request, 
# if it is enter then the game should move to the next stage



# GIVEN the game has started and a request is selected
# WHEN the request times out
# THEN it should put the user back into the request mode to select the next request,
# it should remove the request from the list
# the user should be able to select other requests



# GIVEN the game has started and there are potential requests
# WHEN the last request times out
# THEN the game should end and the final score should be displayed



# GIVEN 
# WHEN 
# THEN 