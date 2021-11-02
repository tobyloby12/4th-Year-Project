import pygame
import sys
from pygame.locals import *


FPS = 30
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
pygame.init()
DISPLAYSURF = pygame.display.set_mode((500, 300))
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF.fill(WHITE)
GRAVITY = 9.81
COLLISION_COEFFICIENT = 0.9
xpos = 250
ypos = 40
pygame.draw.circle(DISPLAYSURF, BLUE, (xpos, ypos), 20, 0)
circle_velocity = 0
while True:
    DISPLAYSURF.fill(WHITE)
    
    ypos += circle_velocity + (GRAVITY/30)**2
    circle_velocity += GRAVITY/30
    if ypos > 280:
        ypos = 280
        circle_velocity = (-circle_velocity)*COLLISION_COEFFICIENT

    
    pygame.draw.circle(DISPLAYSURF, BLUE, (xpos, ypos), 20, 0)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    pygame.display.update()
    FPSCLOCK.tick(FPS)