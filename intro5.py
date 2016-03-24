'''
Created on Feb 9, 2015

@author: edwingsantos
'''
import pygame
from pygame.locals import *
from sys import exit
from random import randint

pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    rand_col = (randint(0, 255), randint(0, 255), randint(0, 255))
    screen.lock()
    
    for _ in xrange(100):
        rand_pos = (randint(0, 639), randint(0, 479))
        screen.set_at(rand_pos, rand_col)
        rand_radius = (randint(0, 69))
        pygame.draw.rect(screen, rand_col, Rect(rand_pos, rand_pos))
        pygame.draw.circle(screen, rand_col, rand_pos, rand_radius)
    screen.unlock()
    pygame.display.update()
    
if __name__ == '__main__':
    pass