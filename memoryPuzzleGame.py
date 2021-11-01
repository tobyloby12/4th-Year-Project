# taken from https://inventwithpython.com/pygame/chapter3.html

import random, pygame, sys
from pygame.locals import *

# setting FPS
FPS = 30

# setting window parameters
WINDOWWIDTH = 640 # size of window width
WINDOWHEIGHT = 480 # size of window height
REVEALSPEED = 8 # speed at which sliding boxes reveals and covers
BOXSIZE = 40 # size of box height and width
GAPSIZE = 10 # size of gaps between boxes
BOARDWIDTH = 10 # number of columns of boxes
BOARDHEIGHT = 7 # number of rows of boxes
assert (BOARDWIDTH*BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs and matchs'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH*(BOXSIZE + GAPSIZE)))/2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT*(BOXSIZE + GAPSIZE)))/2)

# setting colors
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALL_COLORS)*len(ALLSHAPES)*2 >= BOARDWIDTH*BOARDHEIGHT # checking board is small enough

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init() # starting game
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) # setting display
    mousex = 0 # storing mouse position
    mousey = 0
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores value of first box clicked

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing window
        drawboard(mainBoard, revealedBoxes)

        for event in pygame.event.get(): # handling events

            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION: # mouse motion handling
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
        
        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # mouse is on box
            if not revealedBoxes[boxx][boxy]: # highlighting over box
                drawHighlightbox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)]) # showing box on mouse click
                revealedBoxes[boxx][boxy] = True # setting box as revealed
                # handling if box is selected first or second
                if firstSelection == None:
                    firstSelection == (boxx, boxy)
                else:
                    # checking matching shapes
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)
                    if icon1shape != icon2shape or icon1color != icon2color: # if shapes dont match cover
                        pygame.time.wait(1000) # wait 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedboxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # reset board
                        mainBoard = getRandomizedBoard()
                        revealedboxes = generateRevealedBoxesData(False)

                        # show revealed board for 1 sec
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # replay start animation
                        startGameAnimation(mainBoard)
                    firstSelection = None
        # redraw screen and wait for clock tick
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard():
    # get list of all shapes and colors
    icons = []
    for color in ALLCOLOURS:
        for shape in ALL SHAPES:
            icons.append((shape, color))
    random.shuffle(icons) # randomizing icons
    numIconsUsed = int(BOARDWIDTH*BOARDHEIGHT/2) # how many icons needed
    icons = icons[:numIconsUsed] * 2 # two of each icon
    random.shuffle(icons)

    # creating board
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # deleting icons after they have been assigned
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):