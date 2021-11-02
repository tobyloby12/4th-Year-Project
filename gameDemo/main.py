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
    global FPSCLOCK, DISPLAYSURF, SCORE
    pygame.init()
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Demo Game')
    DISPLAYSURF.fill(GRAY)
    SCORE = 0

    while True:
        # creating game screen
        DISPLAYSURF.fill(GRAY)
        displayScore(SCORE, WINDOWWIDTH, WINDOWHEIGHT)

        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    SCORE += 1
                elif event.key == pygame.K_DOWN:
                    try:
                        SCORE -= 1
                    except:
                        SCORE = 0
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# display score
def displayScore(score, width, height):
    pygame.font.init()
    myfont = pygame.font.SysFont('Calibri', 30)
    textsurface = myfont.render(f'SCORE: {str(score)}', False, WHITE)
    DISPLAYSURF.blit(textsurface, (width/2-70, 15))


if __name__ == '__main__':
    main()