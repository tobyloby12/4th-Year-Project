import numpy as np

class Heuristic:
    def __init__(self, linkList):
        self.available_paths = []
        self.numSlots = len(linkList[0].spectrum)
        self.numLinks = len(linkList)

    def path_checker(self, state_dict):

        # finding which paths have enough spectrum and eliminating impossible paths
        non_blocked = []
        bandwidth = state_dict['request_bandwidth']
        # checking each path
        possible = False
        for available_path in self.available_paths:
            path_spectrum = []
            # updating links from state
            for i in range(len(available_path['current_path'])):
                if available_path['current_path'][i] == 1:
                    path_spectrum.append(state_dict['link_spectrum'][i])
            # checking all possible places where consecutive free could be
            for i in range(len(path_spectrum[0]) - bandwidth + 1):
                possible = True
                # checking through each cell in the bandwidth capacity
                for j in range(bandwidth):
                    for spectrum in path_spectrum:
                        if spectrum[i+j] == 1:
                            possible = False
                # appending to new list which contains paths unobstructed
                if possible == True:
                    non_blocked.append(available_path)

        # choosing shortest path
        
        min_path_length = np.inf

        # if empty list
        if non_blocked == []:
            min_path = None
        else:
            # getting smallest path with path_length
            for path in non_blocked:
                if path['path_length'] < min_path_length:
                    min_path = path
                    min_path_length = path['path_length']

        return min_path

    def to_dict(self, state):
        # function to turn state array into a dictionary for easier use
        state_dict = {'request_bandwidth': state[0],
            'slot_selected': state[1],
            'possible': state[2],
            'false_counter': state[3],
            'path_length': state[4],
            'mode': state[5],
            'topology': np.reshape(state[6:6 + self.numLinks*2], (self.numLinks,2)), 
            'current_path': state[6 + self.numLinks*2:6 + self.numLinks*2 + self.numLinks],
            'link_spectrum': np.reshape(state[6 + self.numLinks*2 + self.numLinks:6 + self.numLinks*2 + self.numLinks + self.numSlots*self.numLinks], 
            (self.numLinks, self.numSlots))
            }
        return state_dict

    def next_action(self, state):
        state_dict = self.to_dict(state)
        # request mode
        if state_dict['mode'] == 0:
            self.available_paths = []
            action = 4
            return action
        # topology mode
        elif state_dict['mode'] == 1:
            # find shortest possible path with available spectrum
            
            # go up three times to get all possible routes
            if len(self.available_paths) < 3:

                # only spectrum within the path is appended to dict
                spectrum = []
                path = state_dict['current_path']
                for i in range(len(path)):
                    if path[i] == 1:
                        spectrum.append(state_dict['link_spectrum'][i])
                
                self.available_paths.append({'current_path': path,
                'path_length': state_dict['path_length'],
                'link_spectrum': spectrum})
                action = 0
                return action

            else:
                min_path = self.path_checker(state_dict)
                if min_path == None:
                    action = 0
                elif (state_dict['current_path'] == min_path['current_path']).all():
                    action = 2
                else:
                    action = 0
                
                return action

        elif state_dict['mode'] == 2:
            # keep moving until possible is true
            if state_dict['possible'] == 1:
                action = 2
            else:
                action = 1
            return action