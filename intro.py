'''
Created on Feb 9, 2015

@author: edwingsantos
'''


import pygame
from pygame.locals import *
from sys import exit

print "*" * 30
print "\tWelcome to Game 1"

print "*" * 30


backGroundFile = "SushPlate5.png"
mouseFile = "fugu.png"

pygame.init()

screen = pygame.display.set_mode((400, 280),0,32)
pygame.display.set_caption("Hello World")
background = pygame.image.load(backGroundFile).convert()
mouseCursor = pygame.image.load(mouseFile).convert_alpha()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    
    screen.blit(background, (0,0))
    x, y = pygame.mouse.get_pos()
    x -= mouseCursor.get_width() / 2
    y -= mouseCursor.get_height() /2
    screen.blit(mouseCursor, (x,y))
    
    
    
    pygame.display.update()


if __name__ == '__main__':
    pass

