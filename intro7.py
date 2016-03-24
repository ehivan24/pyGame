'''
Created on Feb 15, 2015

@author: edwingsantos
'''

import pygame
import time
import random
 
# pygame.locals
displayWidth = 800
displayHeight = 600

white = (255, 255, 255)
black = (0, 0, 0)
red = (200, 0, 0)
green = (0,200,0)
blue = (0,0,255)

brightRed = (255,0,0)
brightGreen = (0,255,0)

blockColor = (53, 115, 255)

pygame.init()

pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)
crashSound = pygame.mixer.Sound("data\boom.wav")

gameDisplay =  pygame.display.set_mode((displayWidth,displayHeight))


iconImage = pygame.image.load("clipart.png").convert_alpha()

pygame.display.set_icon(iconImage)
pygame.display.set_caption('A bity Racey')

raceCar =  pygame.image.load("racecar.png").convert_alpha()

carWidth = 73
tree = pygame.image.load("tree.png").convert_alpha()

clock = pygame.time.Clock()

pause = False
 
def things_dodge(count):
    font = pygame.font.SysFont(None, 25)
    text = font.render("Dodge:  " + str(count), True, black)
    gameDisplay.blit(text, (0,5))




def things(thingx, thingy, thingw, thingh, color):
    pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh] )

def messageDisplay(text):
    largeText = pygame.font.Font('freesansbold.ttf', 105)
    textSurf, textRect = textObjects(text, largeText)
    textRect.center = ((displayWidth / 2 ),(displayHeight / 2))
    gameDisplay.blit(textSurf, textRect)
    pygame.display.update()
    time.sleep(2)
    gameLoop()
     
def textObjects(text, font):
    textSurface = font.render(text, True, blue)
    return textSurface, textSurface.get_rect()       

def crash():
    crashSound.play()
    
    largeText = pygame.font.SysFont("comicsansms",115)
    TextSurf, TextRect = textObjects("You Crashed", largeText)
    TextRect.center = ((displayWidth/2),(displayHeight/2))
    gameDisplay.blit(TextSurf, TextRect)
   
    
    
    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        #gameDisplay.fill(white)
        

        button("Play Again",150,450,100,50, green, brightGreen, gameLoop)
        button("Quit",550,450,100,50, red, brightRed, quitGame)

        pygame.display.update()
        clock.tick(15)


def car(x, y):
    gameDisplay.blit(raceCar,(x,y))
    
def tree(x, y):
    gameDisplay.blit(tree,(x,y))    
    
x1 = 100 
y1 = 100

def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    #print(click)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = textObjects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)



def gameIntro():
    
    global pause
    
    intro = True
    
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        #print(event)
        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf', 100)
        
        textSurf, textRect = textObjects('A bit Racey', largeText)
        textRect.center = ((displayWidth / 2 ),(displayHeight / 2))
        gameDisplay.blit(textSurf, textRect)
        
        
        button("GO!",150,450,100,50,green,brightGreen,gameLoop)
        button("Quit",550,450,100,50,red,brightRed,quitGame)

        pygame.display.update()
        clock.tick(15)

def quitGame():
    pygame.quit()
    quit()
 
 
    
def paused():

    largeText = pygame.font.SysFont("comicsansms",115)
    TextSurf, TextRect = textObjects("Paused", largeText)
    TextRect.center = ((displayWidth/2),(displayHeight/2))
    gameDisplay.blit(TextSurf, TextRect)
   
    
    
    while pause:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        #gameDisplay.fill(white)
        

        button("Continue",150,450,100,50, green, brightGreen, unpause)
        button("Quit",550,450,100,50, red, brightRed, quitGame)

        pygame.display.update()
        clock.tick(15)
        
def unpause():
    global pause 
    pause = False

def gameLoop():
    global pause
    
    x = (displayWidth * 0.45)  
    y = (displayHeight * 0.8)
    
    x_change = 0
    
    thingStartX = random.randrange(0, displayWidth) 
    thingStartY = -600
    thingSpeed = 9
    thingWidth = 100
    thingHight = 100
    
    dodge = 0
    
    gameExit = False
    
    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -8
                if event.key == pygame.K_RIGHT:
                    x_change = 8
                if event.key == pygame.K_p:
                    pause = True
                    paused()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0
                    
                
                    
        x += x_change
        
        gameDisplay.fill(white)
        
        
        things(thingStartX, thingStartY, thingWidth, thingHight, blockColor)
        thingStartY += thingSpeed 
        
       
        car(x, y)
        
        
        things_dodge(dodge)
        
        
        #
        #Boundaries or walls
        #
        if x > displayWidth - carWidth or x < 0: 
            crash()
            
        #
        #the black coming down the screen
        #    
        
        if thingStartY > displayHeight:
            thingStartY = 0 - thingHight
            thingStartX = random.randrange(0, displayWidth) 
            dodge += 1
            thingSpeed += 1
            thingWidth += (dodge * 0.5)
            
        #
        #Mainlogic 
        #
        if y < thingStartY + thingHight :
            #print ('y cross over')
            
            if x > thingStartX and x < thingStartX + thingWidth or x + carWidth > thingStartX and x + carWidth < thingStartX+ thingWidth :
                #print ()
                crash()
        
        pygame.display.update()
        clock.tick(50)
        

gameIntro()       
gameLoop()

if __name__ == '__main__':
    pass