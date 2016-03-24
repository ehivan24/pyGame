'''
Created on Feb 9, 2015

@author: edwingsantos
'''

if __name__ == '__main__':
    pass


import pygame
from pygame.locals import *
from sys import exit

background_image_filename = "SushPlate5.png"

pygame.init()
screen = pygame.display.set_mode((640, 480), RESIZABLE, 32)
pygame.display.set_caption("Hello World")
background = pygame.image.load(background_image_filename).convert()


x, y = 0,0

moveX, moveY = 0,0

while True:
    
    for event in pygame.event.get():
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
            exit()
        
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                moveX = -1
       
            elif event.key == K_RIGHT:
                moveX = +1
        
            elif event.key == K_UP:
                moveY = -1
        
            elif event.key == K_DOWN:
                moveY = +1
        
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                moveX = 0
       
            elif event.key == K_RIGHT:
                moveX = 0
        
            elif event.key == K_UP:
                moveY = 0
        
            elif event.key == K_DOWN:
                moveY = 0
                
    x += moveX
    y += moveY

    screen.fill((255, 255, 225))
    screen.blit(background, (x, y))
    pygame.display.update()




