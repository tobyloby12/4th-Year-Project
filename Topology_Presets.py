import pygame
import random
import math
from optical_network_game.node import Node
from optical_network_game.link import Link

# link collision
# make sure every node can reach the network
WIDTH = 560
HEIGHT = 530
FPS = 30

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

#preset topology function
def createPresetTopology(Preset_Num):
    # Nodes
    nodeA = Node(0, 'A', 300, 200)
    nodeB = Node(1, 'B', 300, 400)
    nodeC = Node(2, 'C', 650, 200)
    nodeD = Node(3, 'D', 650, 400)
    nodeE = Node(4, 'E', 500, 200)
    nodeF = Node(5, 'F', 500, 400)
    nodeG = Node(6, 'G', 500, 300)
    nodeH = Node(7, 'H', 200, 300)
    nodeI = Node(8, 'I', 650, 300)
    nodeJ = Node(9, 'J', 200, 400)

    if Preset_Num == 1:
        #Preset 1 (Base Model Used for Link)

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

    elif Preset_Num == 2:
        #Preset 2 (Simpler Topology with Links between All nodes)

        link1 = Link(0, nodeA, nodeB)
        link2 = Link(1, nodeB, nodeC)
        link3 = Link(2, nodeB, nodeD)
        link4 = Link(3, nodeA, nodeC)
        link5 = Link(4, nodeC, nodeD)
        link6 = Link(5, nodeA, nodeD)

        nodeList = [nodeA, nodeB, nodeC, nodeD]
        linkList = [link1, link2, link3, link4, link5, link6]

        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)

    #elif Preset_Num == 3:


    #elif Preset_Num == 4:

    #elif Preset_Num == 5:

    elif Preset_Num == 6:
        #Preset 6 (Most complex Topology with all 10 nodes and various links)
        #Links


        nodeList = [nodeA, nodeB, nodeC, nodeD, nodeE, nodeF, nodeG, nodeH, nodeI, nodeJ]
        linkList = []
       
        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)



    

    return nodeList, linkList


def generatingNodes(numberOfNodes):
    nodeList = []
    temp = numberOfNodes
    for j in range(numberOfNodes//26 + 1):
        for i in range(26):
            valid = False
            while valid == False:
                x = random.randint(30, 530)
                y = random.randint(30, 500)
                if nodeList != []:
                    for node in nodeList:
                        x1 = node.getX()
                        y1 = node.getY()
                        distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
                        if distance > 150:
                            valid = True
                        else:
                            valid = False
                            break
                        print(valid, distance)
                else:
                    valid = True
            nodeList.append(Node(i, chr(j+65) + chr(i + 65), x, y))
            if len(nodeList) == numberOfNodes:
                return nodeList
    return None

def generateLinks(maxLinksPerNode, nodeList):
    linkList = []
    i = 0
    for node in nodeList:
        maxLinks = random.randint(2, maxLinksPerNode)
        nodeListCopy = nodeList.copy()
        nodeListCopy.remove(node)
        for link in linkList:
            if link.getNode1() == node:
                nodeListCopy.remove(link.getNode2())
                maxLinks -= 1
            elif link.getNode2() == node:
                nodeListCopy.remove(link.getNode1())
                maxLinks -= 1

        if maxLinks > 0:
            for j in range(maxLinks):
                linkList.append(Link(i, node, random.choice(nodeListCopy)))
                i += 1
    print(linkList)
    return linkList

def topology(nodeList):
    pass


## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Topology")
clock = pygame.time.Clock()     ## For syncing the FPS

nodeList = generatingNodes(8)
linkList = generateLinks(3, nodeList)

## Game loop
running = True
while running:

    clock.tick(FPS) 
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False


    #3 Draw/render
    screen.fill(GRAY)
    for link in linkList:
        link.drawLink(screen, BLUE)
    for node in nodeList:
        node.drawNode(screen, BLUE)
    


    pygame.display.flip()

pygame.quit()