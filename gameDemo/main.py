# importing important things
import pygame, sys
from pygame.locals import *

WINDOWWIDTH = 1000
WINDOWHEIGHT = 600
FPS = 30

GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

BGCOLOR = GRAY


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Demo Game')
    DISPLAYSURF.fill(GRAY)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()