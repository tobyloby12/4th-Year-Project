from optical_network_game.link import Link
from optical_network_game.node import Node
from optical_network_game.requests import *
# from optical_network_game import game_gym
from numpy import Inf
from collections import defaultdict

	
class Graph:
  
    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices
        self.paths = {}
        self.i = 0
         
        # default dictionary to store graph
        self.graph = defaultdict(list)
  
    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)
  
    '''A recursive function to print all paths from 'u' to 'd'.
    visited[] keeps track of vertices in current path.
    path[] stores actual vertices and path_index is current
    index in path[]'''
    def printAllPathsUtil(self, u, d, visited, path):
 
        # Mark the current node as visited and store in path
        visited[u]= True
        path.append(u)
 
        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            self.paths[self.i] = path.copy()
            self.i += 1
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if visited[i]== False:
                    self.printAllPathsUtil(i, d, visited, path)
                     
        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u]= False
  
  
    # Prints all paths from 's' to 'd'
    def printAllPaths(self, s, d):
 
        # Mark all the vertices as not visited
        visited =[False]*(self.V)
 
        # Create an array to store paths
        path = []
 
        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path)
  
  
  
def paths(request, nodeList, linkList):
    g = Graph(len(nodeList))
    edges = []
    for node in nodeList:
        for link in node.getLinks():
            edges.append((link[1].getNode1().getID(), link[1].getNode2().getID()))
    edges = set(edges)

    for edge in edges:
        g.addEdge(edge[0], edge[1])
        g.addEdge(edge[1], edge[0])

    s = request.getSourceNode().getID()
    d = request.getDestNode().getID()
    
    g.printAllPaths(s, d)
    sorted_keys = [k for k in sorted(g.paths, key=lambda k: len(g.paths[k]))]
    while len(sorted_keys) > 3:
        sorted_keys.pop()

    return sorted_keys, g

def create_list(sorted_keys, g, nodeList, linkList):
    available_paths = g.paths
    out = []
    for key in sorted_keys:
        nodeLinkList = []
        current_path = available_paths[key]
        for node in current_path:
            for node2 in nodeList:
                if node2.getID() == node:
                    nodeLinkList.append(node2)
        for i in range(len(current_path) - 1):
            for link in linkList:
                if (link.getNode1().getID() == current_path[i] and link.getNode2().getID() == current_path[i + 1]) \
                     or (link.getNode2().getID() == current_path[i] and link.getNode1().getID() == current_path[i + 1]):
                    nodeLinkList.append(link)
        out.append(nodeLinkList)
    return out


def createTestTopology():
    # testNodes
    nodeA = Node(0, 'A', 300, 200)
    nodeB = Node(1, 'B', 300, 400)
    nodeC = Node(2, 'C', 650, 200)
    nodeD = Node(3, 'D', 650, 400)
    # testLinks
    link1 = Link(0, nodeA, nodeB)
    link2 = Link(1, nodeB, nodeC)
    link3 = Link(2, nodeB, nodeD)
    link4 = Link(3, nodeA, nodeC)
    link5 = Link(4, nodeC, nodeD)

    nodeList = [nodeA, nodeB, nodeC, nodeD]
    linkList = [link1, link2, link3, link4, link5]

    # save the links associated to each node in a list
    for node in nodeList:
        node.setLinks(linkList)
    return nodeList, linkList

def main():
    nodeList, linkList = createTestTopology()
    requestList = generateRequests(nodeList, 30)
    print(requestList[0].toString())

    # Create a graph given in the above diagram
    sorted_keys, g = paths(requestList[0], nodeList, linkList)
    create_list(sorted_keys, g, nodeList, linkList)

if __name__ == '__main__':
    main()