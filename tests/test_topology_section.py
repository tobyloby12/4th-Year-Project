#################################################################
# TOPOLOGY SECTION
#################################################################


# GIVEN a request has been selected and the user is now in topology mode at the source node
# WHEN the user produces an input
# THEN if the input is backspace, the user should go back to the request mode and be able to select another or the same request and 
# current selected and highlighted nodes should be deselected and dehighlighted,
# if the input is up or down, it should highlight the corresponding links and nodes according to the links relative heights,
# if the input is enter, the highlighted nodes should be selected and the next link should be highlighted if not at destination node,
# the link should be added to the user selected linkList



# GIVEN a request has been selected and the user is now in topology mode not at the source or destination node
# WHEN a user produces an input
# THEN if the input is backspace, the user should return to the previous node and currently highlighted should be cleared and previously
# selected links should be deselected and removed from users selected linked list
# if the input is up or down, it should highlight the corresponding links and nodes according to the links relative heights if
# they have not already been selected,
# if the input is enter, the highlighted nodes should be selected and the next link should be highlighted if not at destination node,
# the link should be added to the user selected linkList



# GIVEN a request has been selected and the user is now in topology mode at is about to select the destination node
# WHEN the user presses enter
# THEN the destination node should be selected along with the corresponding link, 
# the user should be put into spectrum mode,
# highlighted first necessary slots in translucent



# GIVEN a request has been selected
# WHEN a link does not have enough contiguous slots for spectrum allocation
# THEN the link should be grayed out and not able to be selected by the user