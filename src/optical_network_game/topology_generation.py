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
def createPresetTopology(Preset):
    '''
    Preset = ["Base", "1-link", "VSNL", "NSFnet"]
    Preset takes in a string arguement which represents the following:
    Base = Base topology originally used for training with 4 nodes and 5 links
    1-link = Topology with 4 nodes and 6 links so all nodes are connected with each other
    VSNL = Topology replicating A1 Node connections within India (referenced), 6 nodes 9 links
    NSFnet = Topology replicating NSFnet topology for US backbone, 14 nodes 21 links
    '''
    # Nodes
    #nodeA = Node(0, 'A', 300, 200)
    #nodeB = Node(1, 'B', 300, 400)
    #nodeC = Node(2, 'C', 650, 200)
    #nodeD = Node(3, 'D', 650, 400)
    #nodeE = Node(4, 'E', 500, 200)
    #nodeF = Node(5, 'F', 500, 400)
    #nodeG = Node(6, 'G', 500, 300)
    #nodeH = Node(7, 'H', 200, 300)
    #nodeI = Node(8, 'I', 650, 300)
    #nodeJ = Node(9, 'J', 200, 400)
    #nodeK = Node(10, 'K', 200, 400)
    #nodeL = Node(11, 'L', 200, 400)
    #nodeM = Node(12, 'M', 200, 400)
    #nodeN = Node(13, 'N', 200, 400)
    
    num_slots = 4

    if Preset == "Base":
        #Preset 1 (Base Model Used for Link)

        nodeA = Node(0, 'A', 300, 200)
        nodeB = Node(1, 'B', 300, 400)
        nodeC = Node(2, 'C', 650, 200)
        nodeD = Node(3, 'D', 650, 400)


        link1 = Link(0, nodeA, nodeB, num_slots)
        link2 = Link(1, nodeB, nodeC, num_slots)
        link3 = Link(2, nodeB, nodeD, num_slots)
        link4 = Link(3, nodeA, nodeC, num_slots)
        link5 = Link(4, nodeC, nodeD, num_slots)

        nodeList = [nodeA, nodeB, nodeC, nodeD]
        linkList = [link1, link2, link3, link4, link5]

        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)
        
        print("Base Topology Selected")

    elif Preset == "1-link":
        #Preset 2 (Simpler Topology with Links between All nodes)
        nodeA = Node(0, 'A', 300, 200)
        nodeB = Node(1, 'B', 300, 400)
        nodeC = Node(2, 'C', 650, 100)
        nodeD = Node(3, 'D', 650, 500)


        link1 = Link(0, nodeA, nodeB, num_slots)
        link2 = Link(1, nodeB, nodeC, num_slots)
        link3 = Link(2, nodeB, nodeD, num_slots)
        link4 = Link(3, nodeA, nodeC, num_slots)
        link5 = Link(4, nodeC, nodeD, num_slots)
        link6 = Link(5, nodeA, nodeD, num_slots)

        nodeList = [nodeA, nodeB, nodeC, nodeD]
        linkList = [link1, link2, link3, link4, link5, link6]

        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)
        
        print("1-link Topology Selected")

    #elif Preset == 3:


    #elif Preset == 4:

    elif Preset == "VSNL":

        nodeA = Node(0, 'A', 300, 300)
        nodeB = Node(1, 'B', 350, 475)
        nodeC = Node(2, 'C', 400, 100)
        nodeD = Node(3, 'D', 600, 525)
        nodeE = Node(4, 'E', 600, 150)
        nodeF = Node(5, 'F', 750, 250)

        link1 = Link(1, nodeA, nodeB, num_slots)
        link2 = Link(2, nodeA, nodeC, num_slots)
        link3 = Link(3, nodeA, nodeD, num_slots)
        link4 = Link(4, nodeA, nodeE, num_slots)
        link5 = Link(5, nodeA, nodeF, num_slots)
        link6 = Link(6, nodeB, nodeD, num_slots)
        link7 = Link(7, nodeC, nodeD, num_slots)
        link8 = Link(8, nodeD, nodeE, num_slots)
        link9 = Link(9, nodeD, nodeF, num_slots)


        nodeList = [nodeA, nodeB, nodeC, nodeD, nodeE, nodeF]
        linkList = [link1, link2, link3, link4, link5, link6, link7, link8, link9]

        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)

        print("VSNL Topology Selected")


    elif Preset == "NSFnet":
        #Preset 6 (Most complex Topology with all 10 nodes and various links)
        #Links

        #node labelling based off of the Green optical networks with availability figure in the report
        node0 = Node(0, 'A', 100, 250)
        node1 = Node(1, 'B', 150, 400)
        node2 = Node(2, 'C', 150, 100)
        node3 = Node(3, 'D', 250, 250)
        node4 = Node(4, 'E', 300, 200)
        node5 = Node(5, 'F', 300, 100)
        node6 = Node(6, 'G', 350, 300)
        node7 = Node(7, 'H', 400, 200)
        node8 = Node(8, 'I', 500, 200)
        node9 = Node(9, 'J', 450, 100)
        node10 = Node(10, 'K', 500, 400)
        node11 = Node(11, 'L', 600, 350)
        node12 = Node(12, 'M', 550, 100)
        node13 = Node(13, 'N', 650, 300)

        link1 = Link(1, node0, node1, num_slots)
        link2 = Link(2, node0, node2, num_slots)
        link3 = Link(3, node0, node3, num_slots)
        link4 = Link(4, node1, node2, num_slots)
        link5 = Link(5, node1, node7, num_slots)
        link6 = Link(6, node2, node5, num_slots)
        link7 = Link(7, node3, node4, num_slots)
        link8 = Link(8, node3, node10, num_slots)
        link9 = Link(9, node4, node5, num_slots)
        link10 = Link(10, node4, node6, num_slots)
        link11 = Link(11, node5, node9, num_slots)
        link12 = Link(12, node5, node12, num_slots)
        link13 = Link(13, node6, node7, num_slots)
        link14 = Link(14, node7, node8, num_slots)
        link15 = Link(15, node8, node9, num_slots)
        link16 = Link(16, node8, node11, num_slots)
        link17 = Link(17, node8, node13, num_slots)
        link18 = Link(18, node10, node11, num_slots)
        link19 = Link(19, node10, node13, num_slots)
        link20 = Link(20, node11, node12, num_slots)
        link21 = Link(21, node12, node13, num_slots)
        

        nodeList = [node0, node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        linkList = [link1, link2, link3, link4, link5, link6, link7, link8, link9, link10, link11, link12, link13, link14, link15, link16, link17, link18, link19, link20, link21]
       
        # save the links associated to each node in a list
        for node in nodeList:
            node.setLinks(linkList)

        print("NSFnet Topology Selected")

    return nodeList, linkList










def createTestTopology():
    
    num_slots = 4
    
    # testNodes
    nodeA = Node(0, 'A', 300, 200)
    nodeB = Node(1, 'B', 300, 400)
    nodeC = Node(2, 'C', 650, 200)
    nodeD = Node(3, 'D', 650, 400)
    # testLinks
    link1 = Link(0, nodeA, nodeB, num_slots)
    link2 = Link(1, nodeB, nodeC, num_slots)
    link3 = Link(2, nodeB, nodeD, num_slots)
    link4 = Link(3, nodeA, nodeC, num_slots)
    link5 = Link(4, nodeC, nodeD, num_slots)

    nodeList = [nodeA, nodeB, nodeC, nodeD]
    linkList = [link1, link2, link3, link4, link5]

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
#pygame.init()
#pygame.mixer.init()  ## For sound
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#pygame.display.set_caption("Topology")
#clock = pygame.time.Clock()     ## For syncing the FPS

#nodeList = generatingNodes(8)
#linkList = generateLinks(3, nodeList)

## Game loop
#running = True
#while running:
#
#    clock.tick(FPS) 
#    for event in pygame.event.get():
#        
#        if event.type == pygame.QUIT:
#            running = False
#
#
#    #3 Draw/render
#    screen.fill(GRAY)
#    for link in linkList:
#        link.drawLink(screen, BLUE)
#    for node in nodeList:
#        node.drawNode(screen, BLUE)
#    
#
#
#    pygame.display.flip()

#pygame.quit()

