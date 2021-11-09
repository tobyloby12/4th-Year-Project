#################################################################
# TOPOLOGY SECTION
#################################################################


# GIVEN a request has been selected and the user is now in topology mode at the source node
# WHEN the user presses backspace
# THEN the user should go back to the request mode and be able to select another or the same request and 
# current selected and highlighted nodes should be deselected and dehighlighted



# GIVEN a request has been selected and the user is now in topology mode at the source node
# WHEN the user presses the up arrow key
# THEN it should select the higher link and if the highest link is selected already, it should select the lowest link



# GIVEN a request has been selected and the user is now in topology mode at the source node
# WHEN the user presses the down arrow key
# THEN it should select the lower link and if the lowest link is selected already, it should select the highest link



# GIVEN a request has been selected and the user is now in topology mode at the source node and selected node is not at destination node
# WHEN the user presses enter
# THEN the highlighted node and link should be selected and the next node and link should be highlighted,
# the link should be added to the user selected linkList



# GIVEN a request has been selected and the user is now in topology mode not at the source or destination node
# WHEN a user presses backspace
# THEN the user should return to the previous node and currently highlighted should be cleared and 
# previously selected links should be deselected and removed from users selected linked list,
# the next node and link should be highlighted



# GIVEN a request has been selected and the user is now in topology mode not at the source or destination node
# WHEN the user presses the up arrow key
# THEN it should select the higher link and if the highest link is selected already, it should select the lowest link



# GIVEN a request has been selected and the user is now in topology mode not at the source or destination node
# WHEN the user presses the down arrow key
# THEN it should select the lower link and if the lowest link is selected already, it should select the highest link



# GIVEN a request has been selected and the user is now in topology mode not at the source or destination node
# WHEN the user presses enter
# THEN the highlighted nodes should be selected and the next link should be highlighted,
# the link should be added to the user selected linkList




# GIVEN a request has been selected and the user is now in topology mode at is about to select the destination node
# WHEN the user presses enter
# THEN the destination node should be selected along with the corresponding link, 
# the user should be put into spectrum mode,
# highlighted first necessary slots in translucent



# GIVEN a request has been selected
# WHEN a link does not have enough contiguous slots for spectrum allocation
# THEN the link should be grayed out and not able to be selected by the user



# GIVEN the game has started and a request is selected
# WHEN the request selected times out
# THEN it should put the user back into the request mode to select the next request,
# it should remove the request from the list
# the user should be able to select other requests,
# highlighted and selected links and nodes should be cleared and reset to baseline
# selected link list should be cleared



# GIVEN the game has started and a request is selected
# WHEN the non selected request times out
# THEN nothing should happen
