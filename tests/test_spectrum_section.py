#################################################################
# SPECTRUM SECTION
#################################################################


# GIVEN the user has selected a request and has completed the route to get into spectrum node
# WHEN the user presses backspace
# THEN the user should return to the topology mode at the node before the destination node,
# the destination node and corresponding link should be deselected and removed from user selected link list
# the next link should be automatically highlighted



# GIVEN the user has selected a request and has completed the route to get into spectrum node
# WHEN the user presses left arrow key
# THEN the slots selected should shift by 1 to the left



# GIVEN the user has selected a request and has completed the route to get into spectrum node
# WHEN the user presses right arrow key
# THEN the slots selected should shift by 1 to the right



# GIVEN the user has selected a request and has completed the route to get into spectrum node and non free slots are selected
# WHEN the user presses enter
# THEN an error message should be displayed until a key is pressed



# GIVEN the user has selected a request and has completed the route to get into spectrum node and free slots are selected
# and it is not the last request
# WHEN the user presses enter
# THEN the slots should be selected and a point should be added to the score,
# the links should have the correct spectrum updated,
# the request should be marked as complete and removed,
# selected links and nodes should be cleared,
# user should be put into request mode



# GIVEN the user has selected a request and has completed the route to get into spectrum node and free slots are selected
# and it is the last request
# WHEN the user presses enter
# THEN the slots should be selected and a point should be added to the score,
# the links should have the correct spectrum updated,
# the request should be marked as complete and removed,
# selected links and nodes should be cleared,
# an end game screen shown with the final score should be displayed