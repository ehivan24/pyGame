#! /usr/bin/env python

import random, os.path, math

try:
    import psyco
    psyco.full()
    pass
except ImportError:
    pass

MAJOR_VERSION = 1
MINOR_VERSION = 1
VERSION = "%s.%s" % (MAJOR_VERSION, MINOR_VERSION)
HISCOREFILE = ".alienhiscore"
try:
    hsf = open(HISCOREFILE)
    HISCORE = int(hsf.readline())
    hsf.close()
    pass
except:
    HISCORE = 0
    pass


def boss_level(l):
    if l % 5 == 0:
        return 1
    return 0

def killforlevel():
    if boss_level(LEVEL):
        return 30
    return 100


pause = 0

#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit, "Sorry, extended image module required"

SAMPLES = 880
LINES = 624
frame = 0
GAME_FONT = 'data/Colony_Wars_Grsites.ttf'
#GAME_FONT = 'data/Architext_Grsites.ttf'
#game constants
NOMINAL_MAX_SHOTS = 7
MAX_SHOTS      = NOMINAL_MAX_SHOTS      #most player bullets onscreen
RELOAD_TIME    = 10     # autoreload delay
ALIEN_ODDS     = 25     #chances a new alien appears
BOMB_ODDS      = 30    #chances a new bomb will drop
ALIEN_RELOAD   = 12     #frames between new aliens
SCREENRECT     = Rect(0, 0, SAMPLES, LINES)
ZIGZAG_PROB    = 50   # chance to zigzag
SCORE          = 0
REALSCORE      = 0
BOMB_DRIFT     = 9
BOMB_ACCEL     = 0.1
ALIEN_MAX_SPEED = 13
LEVEL           = 1
SHIPS           = 5
FIRED           = 0
HIT             = 0
GET_BY_COST     = 100
kills           = 0
escapees        = 0
flashcol        = 0
hitcol          = 0
pulse           = 0
    
def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join('data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass
    
def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join('data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print 'Warning, unable to load,', file
    return dummysound()



# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[SHIPS]
        self.rect = self.image.get_rect()
        self.reloading = 0
        self.rect.centerx = SCREENRECT.centerx
        self.rect.bottom = SCREENRECT.bottom - 1
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, lrdirection, uddirection):
        if lrdirection:
            self.facing = lrdirection
            pass

        self.rect.move_ip(lrdirection*self.speed, uddirection*self.speed)
        self.rect.top = self.rect.top + uddirection
        self.rect = self.rect.clamp(SCREENRECT)
        #self.rect.top = self.origtop - (self.rect.left/self.bounce%2)

    def gunpos(self):
        pos = self.facing*self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Boss(pygame.sprite.Sprite):
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image("boss.gif")
        self.frame = 0
        self.rect = self.image.get_rect()
        self.maxdescend = (LINES / 2) + LEVEL
        self.maxascend = 0
        self.speedx = 0
        self.speedy = LEVEL / 2
        self.hits = 25 + LEVEL * 5
        self.hitorig = self.hits
        self.rect.bottom = 0
        self.rect.centerx = SAMPLES / 2
        
        pass


    def update(self):
        self.rect.move_ip(self.speedx, self.speedy)
        if self.rect.bottom > self.maxdescend:
            self.speedy = -1
            pass
        self.frame = self.frame + 1

        if self.rect.top < 0:
            self.speedy = LEVEL / 2
            pass
        
        pass

    def damage(self, amt):
        global flashcol
        global pulse
        global REALSCORE
        es = 200
        er = es / 2
        self.hits = self.hits - amt
        if self.hits < 0:
            for i in range(0,15):
                Explosion_byxy(self.rect.centerx+random.random()*es-er,
                               self.rect.centery+random.random()*es-er)
                pass
            flashcol = 32
            pulse = 5
            REALSCORE = REALSCORE + 1000 * LEVEL
            self.kill()
            pass
        else:
            p = 100 - ((self.hits) / float(self.hitorig) * 100)
            self.image.fill(0x101010, (250-p,2,p,16))
            pass
        pass


difficulty_coeff = 0.67

class Alien(pygame.sprite.Sprite):
    animcycle = 12
    images = []
    def __init__(self):
        self.hitpoints = 1
        self.type = "A"
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        speed = range(-LEVEL, LEVEL+1)
        speed[LEVEL] = LEVEL
        self.facing = random.choice(speed)
        self.flyspeed = random.random() * ((LEVEL + 1) *difficulty_coeff) + 0.5
        self.frame = 0
        self.backjinks = 0
        self.rect.right = SAMPLES - (random.random() * SAMPLES) + self.rect.right
        self.rect = self.rect.clamp(SCREENRECT)
        self.rect.bottom = 0
    def update(self):

        global escapees
        global REALSCORE
        if LEVEL == 0: return
        self.rect.move_ip(self.facing, 0)
        self.rect.top = self.rect.top + self.flyspeed
        if int(self.flyspeed) == 0 and random.random() * 100 < LEVEL:
            self.flyspeed = random.random() * ((LEVEL + 1) *difficulty_coeff) + 0.5
            pass
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing;
            if self.rect.top > LINES:
                self.kill()
                escapees  = escapees + 1
                pass
            #self.rect = self.rect.clamp(SCREENRECT)
            pass
        if not int(random.random() * ZIGZAG_PROB):
            self.facing = -self.facing;
            pass
        if self.rect.top > LINES / 2 and LEVEL >= 7:
            if random.random() * 100 < LEVEL - 6 - self.backjinks:
                self.flyspeed = -self.flyspeed
                self.backjinks = self.backjinks + 1
                pass
            pass
        if self.rect.top < LINES / 4 and self.flyspeed < 0:
            self.flyspeed = -self.flyspeed
            pass
        self.frame = self.frame + 1
        self.image = self.images[self.frame/self.animcycle%len(self.images)]
        pass
    pass

class Cruiser(Alien):
    def __init__(self, victim):
        Alien.__init__(self)
        self.hitpoints = 5
        self.type = "C"
        self.victim = victim
        pass

    def update(self):
        Alien.update(self)
        if self.rect.top > LINES / 2:
            self.flyspeed = -self.flyspeed
            pass
        if frame % 60 == 0:
            GuidedBomb(self, self.victim)
            pass
        pass
    
    pass

class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.life = self.defaultlife
        self.center = actor.rect.center
        self.rect.center = actor.rect.center
        
        
    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life/self.animcycle%len(self.images)]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        if self.life <= 0: self.kill()


class Explosion_byxy(Explosion):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.life = self.defaultlife
        self.x = x
        self.y = y
        pass

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life/self.animcycle%len(self.images)]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        if self.life <= 0: self.kill()
        pass

    

    
class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []
    def __init__(self, pos):
        global FIRED
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos
        FIRED = FIRED + 1
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    images = []
    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.frame = 0
        self.rect.centerx = alien.rect.centerx
        self.rect.bottom = alien.rect.bottom + 5
        self.speed = LEVEL
        self.accel = BOMB_ACCEL * LEVEL * random.random()
        self.xdrift = int(random.random() * LEVEL) - ((LEVEL - 1)/2)
        

    def update(self):
        if LEVEL > 0:
            self.rect.move_ip(self.xdrift, self.speed)
            pass
        self.image = self.images[self.frame % len(self.images)]
        self.frame = self.frame + 1
        self.speed = self.speed + self.accel
        if self.rect.bottom >= LINES:
            self.kill()


class GuidedBomb(Bomb):
    "Class to fire bombs aimed at player"
    def __init__(self, boss, player):
        Bomb.__init__(self, boss)
        self.accel = 0
        self.speed = 8
        self.target = player
        self.retrack = None
        self.set_course()
        if LEVEL > 4 :
            self.retrack = 100 - LEVEL
            if self.retrack < 100:
                self.retrack = 100
                pass
            pass
        pass

    def set_course(self):
        self.xdir = self.target.rect.centerx - self.rect.centerx
        self.ydir = self.target.rect.centery - self.rect.centery
        d = math.hypot(self.xdir, self.ydir)
        self.xdir = self.xdir / d
        self.ydir = self.ydir / d
        
    def update(self):
        
        self.frame = self.frame + 1
        if self.frame > 200 and LEVEL > 0:
            self.kill()
            return
        if LEVEL == 0: self.speed = 0
        if self.retrack > 0:
            if self.frame % self.retrack == 0: self.set_course()
            pass
        
        self.speed = self.speed + self.accel
        self.rect.centerx = self.rect.centerx + (self.xdir * self.speed)
        self.rect.centery = self.rect.centery + (self.ydir * self.speed)
        self.image = self.images[self.frame % len(self.images)]
        if self.rect.bottom >= LINES:
            self.kill()
            pass
        if self.rect.top < 0:
            self.kill()
            pass
        if self.rect.left < 0:
            self.kill()
            pass
        if self.rect.right >= SAMPLES:
            self.kill()
            pass
        

class Star(pygame.sprite.Sprite):
    speedrange = 3
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pick_img()
        self.dx = 0
        self.count = 0
        self.lastlevel = 1
        self.speed = random.choice(range(1, self.speedrange + 1))
        self.image = self.images[self.imgno]
        if random.random() > 0.5:
            self.image = pygame.transform.scale(self.image, (3,3))
            pass
        self.rect = self.image.get_rect()
        self.rect.centerx = (random.random() * SAMPLES)
        self.rect.centery = (random.random() * LINES)
        
        pass

    def pick_img(self):
        self.imgno = int(random.choice(range(0,len(self.images))))
        pass

    def update(self):
        global LEVEL
        global pause
        if LEVEL == 0:
            self.dx = 0
            pass
        else:
            self.dx = LEVEL % 3 -1
            pass
        #self.imgno = self.imgno + 1
        #self.image = self.images[self.imgno % 2]
        if pause >100:
            self.rect.move_ip(self.dx*self.speed*4, self.speed*4)
            pass
        elif pause > 1:
            decel = pause/20
            self.rect.move_ip(self.dx*self.speed*decel, self.speed*decel)
            pass
        pass
        if self.rect.bottom >= LINES:
            self.rect.bottom = self.rect.bottom - LINES
            pass
        if self.rect.left <= 0:
            self.rect.right = self.rect.left + SAMPLES
            pass
        if self.rect.right > SAMPLES:
            self.rect.left = self.rect.right - SAMPLES
            pass
        pass

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)      
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.left = random.random() * SAMPLES
        self.rect.top = 0
        self.xvel = int(random.random() * 20 - 10)
        self.maxlev = LEVEL
        if self.maxlev > 8:
            self.maxlev = 8
            pass
        self.yvel = int(random.random() * 2 * self.maxlev) + 1
        self.frame = 0
        pass

    def update(self):
        if LEVEL > 0:
            self.rect.move_ip(self.xvel, self.yvel)
            # power up jinking
            if (random.random() * 200 < LEVEL):
                self.xvel = int(random.random() * 20 - 10)
                self.yvel = int(random.random() * 2 * self.maxlev) + 1
                pass
            if self.rect.top > LINES:
                self.kill()
                pass
            if self.rect.left <= 0 or self.rect.right >= SAMPLES:
                self.xvel = -self.xvel
                pass
            pass
        self.image = self.images[self.frame % len(self.images)]
        self.frame = self.frame + 1
        pass

class TeaserText(pygame.sprite.Sprite):
    def __init__(self, text,x,y,size=20,color=(0,230,230)):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(GAME_FONT, size)
        self.font.set_italic(0)
        self.color = color
        self.x = x
        self.y = y
        self.text = text
        self.update_text()
        pass

    def update_text(self):
        self.image = self.font.render(self.text, 0, self.color)
        self.rect = self.image.get_rect().move(self.x, self.y)
        pass

    def update(self):
        pass

    pass




class Score(pygame.sprite.Sprite):
    shieldsts = ["GONE", "0%", "20%", "40%", "60%", "80%", "100%"]
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(GAME_FONT, 14)
        self.font.set_italic(0)
        self.color = 255, 255, 255
        self.lastscore = -1
        self.lastships = -1
        self.update()
        self.rect = self.image.get_rect().move(10, LINES - 30)
        pass
    
    def update(self):
        global HISCORE
        if REALSCORE != self.lastscore or SHIPS != self.lastships:
            self.lastscore = REALSCORE
            self.lastships = SHIPS
            if SHIPS <= 2:
                self.color = 255, 0, 0
                pass
            elif SHIPS == 3:
                self.color = 255,255,0
                pass
            elif SHIPS == 4:
                self.color = 0,255,0
                pass
            else:
                self.color = 0,255,255
                pass
            if MAX_SHOTS > NOMINAL_MAX_SHOTS:
                rf = "  Rapid Fire!"
                pass
            else:
                rf = ""
                pass
            if HISCORE < REALSCORE:
                HISCORE = REALSCORE
                pass
            msg = "Score: %.6d SHLD: %s  LVL: %i HIGH: %.6d %s" % (
                REALSCORE, self.shieldsts[SHIPS], LEVEL, HISCORE, rf)
            self.image = self.font.render(msg, 0, self.color)
            
            pass
        pass
    pass

class Level(pygame.sprite.Sprite):
    def __init__(self, kills):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(GAME_FONT, 30)
        self.surprise = 0
        self.color = 0, 255, 255
        self.kills = kills
        self.update()
        
        pass


    def update(self):
        global REALSCORE
        if pause > 440:
            msg = "LEVEL %i COMPLETE: %s kills" % (LEVEL - 1, self.kills)
            pass
        elif pause == 440:
            self.surprise_bonus = 100 - self.kills
            if self.surprise_bonus > 0:
                self.surprise_bonus = self.surprise_bonus * (LEVEL) * 20
                msg = "Surprise Bonus: %i" % self.surprise_bonus
                REALSCORE = REALSCORE + self.surprise_bonus
                pass
            else:
                msg = "LEVEL %i COMPLETE: %s kills" % (LEVEL - 1, self.kills)
                pass
            pass
        elif pause > 200 and pause < 440:
            if self.surprise_bonus > 0:
                msg = "Surprise Bonus: %i" % self.surprise_bonus
                pass
            else:
                msg = "LEVEL %i COMPLETE: %s kills" % (LEVEL - 1, self.kills)
            pass
        elif pause < 180 and pause > 1:
            if boss_level(LEVEL):
                msg = "Level %i: MOTHER SHIP!" % LEVEL
                pass
            else:
                msg = "Get ready for Level %i!" % LEVEL
                pass
            HIT = 0
            FIRED = 0
            pass
        else:
            msg = " "
            pass
        self.image = self.font.render(msg, 0, self.color)
        self.rect = self.image.get_rect().move(10, LINES - 30)
        self.rect.centerx = SAMPLES / 2
        self.rect.centery = LINES / 2 
        pass
    pass


class GameOver(Level):
    def __init__(self):
        Level.__init__(self, 0)
        fh = open(HISCOREFILE, "w")
        fh.write("%i\n" % HISCORE)
        fh.close()
        self.font = pygame.font.Font(GAME_FONT, 50)
        self.font.set_italic(0)
        self.color = 255, 0, 0
        self.update()
        self.rect = self.image.get_rect().move(10, LINES - 30)
        self.rect.centerx = SAMPLES / 2
        self.rect.centery = LINES / 2
        self.update()
        pass

    def update(self):
        msg = "GAME OVER."
        self.image = self.font.render(msg, 0, self.color)
        pass
    pass


def teaser_screen(screen, background):
    global LEVEL
    global pause
    global frame
    frame = 1
    pause = 41
    LEVEL = 0
    if pygame.mixer:
        #music = os.path.join('data', 'jene.mod')
        #pygame.mixer.music.load(music)
        #pygame.mixer.music.play(-1)
        pass
    clock = pygame.time.Clock()
    rtn = -1
    screen.blit(background,(0,0))
    pygame.display.flip()
    pygame.display.set_gamma(1.0)
    all = pygame.sprite.RenderUpdates()
    TeaserText.containers = all
    Star.containers = all
    Boss.containers = all
    Player.containers = all
    #Cruiser.containers = all
    Alien.containers = all
    Bomb.containers = all
    GuidedBomb.containers = all
    PowerUp.containers = all
        
    for i in range(100):
        Star()
        pass
    b = Boss()
    p = Player()
    p.image = p.images[6]
    p.rect.left = 210
    s_stat = TeaserText("",170,240,10,(0,230,230))
    sta = ["", "Shield Down!" , "Shield Critical!", "Shield Low!", "Shield Damaged", "Shield Nominal", "Shield Fully Charged"]
    stc = [(0,0,0), (230,0,0), (230,0,0), (230,230,0), (0,230,0), (0,230,230), (0,230,230)]
    p.rect.bottom = 300
    c = Cruiser(p)
    c.rect.left = 685
    c.rect.bottom = 710
    a = Alien()

    a.rect.left = 1050
    a.rect.bottom = 700
    b.speedy = 0
    b.rect.left = 680
    b.rect.bottom = 470
    ts = GuidedBomb(p,p)
    s = Bomb(p)
    ts.rect.bottom = 850
    ts.rect.left = 840
    s.rect.bottom = 850
    s.rect.left = 920

    pu = PowerUp()
    pu.rect.left = 210
    pu.rect.bottom = 450
    
    top_title = TeaserText("Cosmic Assault", 80,50,50)
    TeaserText("Version %s" % VERSION, 1120,1010,10)
    sub_title = TeaserText("The Future is Retrogaming",270,115,20)
    TeaserText("The Good", 95, 200, 20, (0,230,0))
    TeaserText("The Bad", 760, 200, 20, (230,0,0))
    #TeaserText("The Ugly", 580,790, 20, (230,230,0))
    TeaserText("Copyright (C) 2006, Randy Kaelber, A Minor Game Company http://www.aminorgames.com/", 8,960,10,(192,192,192))
    TeaserText("This program is released under the GNU Public License v2.0",8, 975, 10, (192,192,192))
    TeaserText("Music: \"Je ne sais pas\" by u4ia, and...",9,990,10,(192,192,192))
    TeaserText("\"Beyond The Night\" by The Zapper and The Duellist. Trackers Rule!",9,1005,10,(192,192,192))
    TeaserText("Your Fighter Ship", 40,305,15,(0,230,0))
    TeaserText("Move your ship", 75,325,10,(230,230,230))
    TeaserText("with the arrow keys",75,340,10,(230,230,230))
    TeaserText("Press and hold space",75,355,10,(230,230,230))
    TeaserText("To fire",75,370,10,(230,230,230))

    TeaserText("Mother Ship",740,460,15,(230,0,0))
    TeaserText("Moves predictably, but", 710, 480,10,(230,230,230))
    TeaserText("fires tracking shots", 710,495,10,(230,230,230))
    TeaserText("and soaks up damage", 710,510,10,(230,230,230))
    TeaserText("like a sponge.",710,525,10,(230,230,230))
    TeaserText("Appears once every", 710,540,10,(230,230,230))
    TeaserText("five levels", 710,555,10,(230,230,230))

    TeaserText("Cruiser",650,710,15,(230,0,0))
    TeaserText("Five hits to kill and",580,730,10,(230,230,230))
    TeaserText("fires synchronized",580,745,10,(230,230,230))
    TeaserText("tracking shots at",580,760,10,(230,230,230))
    TeaserText("you",580,775,10,(230,230,230))

    TeaserText("Bomber",1000,710,15,(230,0,0))
    TeaserText("The Grunt unit", 920,730,10,(230,230,230))
    TeaserText("Drops dumb bombs", 920,745,10,(230,230,230))
    TeaserText("and moves erratically", 920,760,10,(230,230,230))
    TeaserText("one hit wonders", 920,775,10, (230,230,230))

    TeaserText("Tracking Shot",620,833,10,(230,0,0))
    TeaserText("Dumb Bomb",950,833,10,(230,0,0))
    TeaserText("Ouch.",855,855,10,(230,230,230))

    TeaserText("Power Module",80,450,15,(0,230,0))
    TeaserText("Used to recharge your",75,470,10,(230,230,230))
    TeaserText("shields when damaged.",75,485,10,(230,230,230))
    TeaserText("When your shields are",75,500,10,(230,230,230))
    TeaserText("full, power modules",75,515,10,(230,230,230))
    TeaserText("will upgrade your",75,530,10,(230,230,230))
    TeaserText("guns to rapid fire.",75,545,10,(230,230,230))
    TeaserText("Modules recovered when",75,560,10,(230,230,230))
    TeaserText("fully upgraded will",75,575,10,(230,230,230))
    TeaserText("destroy all bombers",75,590,10,(230,230,230))
    TeaserText("and seriously damage",75,605,10,(230,230,230))
    TeaserText("cruisers.",75,620,10,(230,230,230))

    TeaserText("Hints",160,660,15,(0,230,0))
    TeaserText("* Do not allow bombers to get", 5,680,10, (230,230,230))
    TeaserText("  past you. You will face fewer",5,695,10,(230,230,230))
    TeaserText("  enemies per level and score",5,710,10,(230,230,230))
    TeaserText("  more points.",5,725,10,(230,230,230))
    TeaserText("* Gather Power Modules between",5,740,10,(230,230,230))
    TeaserText("  levels to keep healthy.",5,755,10,(230,230,230))
    TeaserText("* Stay away from the edges",5,770,10,(230,230,230))
    TeaserText("  when there are many cruisers",5,785,10,(230,230,230))
    TeaserText("  active.",5,800,10,(230,230,230))
    ng_text = TeaserText("Press N for new game",10,910,16,(0,128,230))
    esc_text = TeaserText("Press Escape to quit",750,910,16,(0,128,230))

    ship_rot = 0
    cw_pos = [0,130,255]
    cvec = [+5,-5,-5]
    gamma = 1.0
    gam_reduce = 0.0
    soff = 0
    sv = 1
    while(gamma > 0.05):
        soff += sv
        if soff > 10 or soff < -10:
            sv *= -1
            pass
        
        a.rect.left = 1050 + soff
        c.rect.left = 685 - soff
        b.rect.bottom = 470 - soff
        sstat = 6 - ((ship_rot / 120) % 6)
        p.image = p.images[sstat]
        s_stat.text = sta[sstat]
        s_stat.color = stc[sstat]
        ng_text.color = (cw_pos[1],cw_pos[0],cw_pos[2])
        ng_text.update_text()
        s_stat.update_text()
        sub_title.color = (cw_pos[2],cw_pos[0],cw_pos[1])
        sub_title.update_text()
        s_stat.rect.centerx = 225
        ship_rot += 1
        for event in pygame.event.get():
            if (event.type == QUIT or
                (event.type == KEYDOWN and event.key == K_ESCAPE)):
                rtn = 0
                break
            elif event.type == KEYDOWN and event.key == K_n:
                rtn = 1
                break
            pass
        if rtn != -1: gam_reduce = .02
        keystate = pygame.key.get_pressed()
        gamma -= gam_reduce
        pygame.display.set_gamma(gamma)
        all.clear(screen, background)
        all.update()
        
        dirty = all.draw(screen)
        pygame.display.update(dirty)
        clock.tick(60)
        cw_pos = [cw_pos[0]+cvec[0], cw_pos[1]+cvec[1], cw_pos[2]+cvec[2]]
        for i in range(0,3):
            if cw_pos[i] > 255:
                cvec[i] *= -1
                cw_pos[i] = 255
                pass
            if cw_pos[i] < 0:
                cw_pos[i] = 0
                cvec[i] *= -1
                pass
            pass
        top_title.color = list(cw_pos)
        top_title.update_text()
                
        pass

    for s in all:
        s.kill()
        pass
    if pygame.mixer:
        pygame.mixer.music.fadeout(2000)
        pass
    LEVEL = 1
    pause = 0
    
    return rtn


def main(winstyle = 0):
    # Initialize pygame
    pygame.init()
    global flashcol
    global hitcol
    global pulse
    global LEVEL
    global kills
    global FIRED
    global GET_BY_COST
    global MAX_SHOTS
    global RELOAD_TIME
    global pause
    global frame
    pause = 0
    cruiser_allowed = 1
    while 1:
        if pygame.mixer and not pygame.mixer.get_init():
            print 'Warning, no sound'
            pygame.mixer = None
            pass
        # Set the display mode
        winstyle = FULLSCREEN
        bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        #print "bestdep: %i" % bestdepth
        screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

        #Load images, assign to sprite classes
        #(do this before the classes are used, after screen setup)
        img = load_image('player1.gif')
        Boss.images = [load_image('boss.gif')]
        Player.images = [load_image('player1.gif'),
                         load_image('player1.gif'),
                         load_image('player2.gif'),
                         load_image('player3.gif'),
                         load_image('player4.gif'),
                         load_image('player5.gif'),
                         load_image('player5.gif'),
                         ]
        img = load_image('powerup.gif')
        PowerUp.images = [img, pygame.transform.flip(img, 0, 1),
                          pygame.transform.flip(img, 1, 1),
                          pygame.transform.flip(img, 1, 0),
                          ]
        
        img = load_image('explosion1.gif')
        img2 = load_image('explosion2.gif')
        Explosion.images = [img2, img,
                            pygame.transform.flip(img2, 1, 1),
                            pygame.transform.flip(img, 1, 1)
                            ]
        Alien.images = load_images('newship.gif', 'newship.gif', 'newship.gif')
        Cruiser.images = load_images('newship3.gif')
        Bomb.images = [load_image('bomb1.gif'), load_image('bomb2.gif'),
                       load_image('bomb3.gif'), load_image('bomb4.gif')]
        img = load_image("guidebomb1.gif")
        GuidedBomb.images = [img,
                             pygame.transform.flip(img, 1, 0),
                             pygame.transform.flip(img,1,1),
                             pygame.transform.flip(img, 0, 1)]
        
        Shot.images = [load_image('shot.gif')]
        
        #decorate the game window
        icon = pygame.transform.scale(Alien.images[0], (32, 32))
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Space Assault')
        pygame.mouse.set_visible(0)
        
        #create the background, tile the bgd image
        bgdtile = load_image('background.jpeg')

        background = pygame.Surface(SCREENRECT.size)
        #print background.get_at((512,400))
        background.fill(0x101010)
        #print background.get_at((512,400))

        # stars
        img = load_image("star3.gif")
        Star.images = [img, load_image("star2.gif"), load_image("star1.gif"),
                       load_image("star.gif")]

        # load the sound effects
        boom_sound = load_sound('boom.wav')
        shoot_sound = load_sound('car_door.wav')
        shield_sound = load_sound("shields.wav")
        rapidfire_sound = load_sound("rapidfire.wav")
        lose_rf_sound = load_sound("loserf.wav")
        hit_sound = load_sound("punch.wav")
        smartbomb_sound = load_sound("smart.wav")
        dead_sound = load_sound("die.wav")


        if not teaser_screen(screen, background): return 0
        # Initialize Game Groups
        screen.blit(background,(0,0))
        #print screen.get_at((512,400))
        pygame.display.flip()
        aliens = pygame.sprite.Group()
        shots = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        stars = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        cruisers = pygame.sprite.Group()
        boss = pygame.sprite.Group()
        all = pygame.sprite.RenderUpdates()
        lastalien = pygame.sprite.GroupSingle()
        
        # assign default groups to each sprite class
        Player.containers = all
        PowerUp.containers = all, powerups
        Alien.containers = aliens, all, lastalien
        #Cruiser.containers = all
        Shot.containers = shots, all
        Bomb.containers = bombs, all
        GuidedBomb.containers = bombs, all
        Explosion.containers = all
        Boss.containers = all, boss
        Star.containers = all, stars
        Score.containers = all
        Level.containers = all
        # Create Some Starting Values
        global score
        global HIT
        global SHIPS
        alienreload = ALIEN_RELOAD
        kills = 0

        
        # initialize our starting sprites
        global SCORE
        global REALSCORE
        global escapees
        
        oldlevel = LEVEL
        a = Level(0)
        kills = 0
        generate = 1
        switchlevel = 0
        savekills = 0
        escapees = 0
        boss_active = 0
        last_boss_level = 0
        guided_timer = 0
        frame = 0
        player = Player()
        #Alien() #note, this 'lives' because it goes into a sprite group
        if pygame.font:
            all.add(Score())
            pass
        clock = pygame.time.Clock()
        for i in range(100):
            Star()
            pass
        if pygame.mixer:
            #music = os.path.join('data', 'beyond.s3m')
            #pygame.mixer.music.load(music)
            #pygame.mixer.music.play(-1)
            pass
        pygame.display.set_gamma(1.0)
        pause = 200
        MAX_SHOTS=NOMINAL_MAX_SHOTS
        while player.alive():
            frame += 1
            if boss_level(LEVEL):
                if boss_active == 0 and kills > 15 and last_boss_level < LEVEL:
                    boss_active = 1
                    last_boss_level = LEVEL
                    Boss()
                    guided_timer = 45 - LEVEL
                    pass
                pass
            
            
            if len(boss) == 0:
                boss_active = 0
                pass
            else:
                if guided_timer < LEVEL - 4 and guided_timer % 3 == 0:
                    gb = GuidedBomb(boss.sprites()[0], player)
                    pass
                if guided_timer <= 0:
                    #gb.rect.centery = gb.rect.centery - 50
                    guided_timer = 45 - LEVEL
                    pass
                guided_timer = guided_timer - 1
                pass

            

            if len(aliens) == 0:
                pause = pause - 1
                pass

            if a != None and pause <= 0:
                a.kill()
                generate = 1
                a = None
                pass

            if (kills >= killforlevel()) or (kills >= 20 + (escapees * 10)):
                switchlevel = 1
                generate = 0
                pass
            else:
                switchlevel = 0
                generate = 1
                pass
  
            if switchlevel == 1 and len(aliens) == 0 and boss_active == 0:
                for b in bombs:
                    b.kill()
                    pass
                savekills = kills
                kills = 0
                LEVEL = LEVEL + 1
                cruiser_allowed = LEVEL + 1
                escapees = 0
                pause = 800
                a = Level(savekills)
                switchlevel = 0
                generate = 1
                pass
            

            # get input
            for event in pygame.event.get():
                if (event.type == QUIT or
                    (event.type == KEYDOWN and event.key == K_ESCAPE)):
                    player.kill()
                pass
            keystate = pygame.key.get_pressed()
            
            # clear/erase the last drawn sprites

            if flashcol > 0 or hitcol > 0:
                bluegam = 1.0+(flashcol/5.0)
                redgam = 1.0+(hitcol/5.0)
                pygame.display.set_gamma(redgam, 1.0, bluegam)
                
                if flashcol > 0: flashcol = flashcol - 1
                if hitcol > 0: hitcol = hitcol -1
                pass
            else:
                pygame.display.set_gamma(1.0)
            if pulse > 0:
                pulse = pulse -1
                flashcol = 32
                pass
            all.clear(screen, background)
            # update all the sprites
            all.update()
            
            # handle player input
            lrdirection = keystate[K_RIGHT] - keystate[K_LEFT]
            uddirection = keystate[K_DOWN] - keystate[K_UP]
            player.move(lrdirection, uddirection)
            firing = keystate[K_SPACE]
            if pause <= 0 and player.reloading <= 0 and firing and len(shots) < MAX_SHOTS:
                Shot(player.gunpos())
                player.reloading = RELOAD_TIME 
                #shoot_sound.play()
                pass
            player.reloading = player.reloading - 1

            # Create new alien
            if len(powerups) < int(LEVEL/5) + 1 and random.random() * 600 < LEVEL - 1:
                PowerUp()
                pass
            if alienreload:
                alienreload = alienreload - 1
                pass
            elif not int(random.random() * (ALIEN_ODDS - LEVEL)):
                if (len(aliens) < LEVEL * 3) and (pause <= 0) and generate == 1:
                    if (LEVEL / 100.0 <= random.random()):
                        Alien()
                        pass
                    else:
                        if cruiser_allowed:
                            Cruiser(player)
                            cruiser_allowed -= 1
                            pass
                        else:
                            Alien()
                            pass
                        #print "Generated a cruiser"
                        pass
                    pass
                alienreload = ALIEN_RELOAD
                pass
            # Drop bombs
            if lastalien and not int(random.random() * (BOMB_ODDS - LEVEL)):
                qq = random.random()*100

                Bomb(lastalien.sprite)
                pass
            # Detect collisions
            for alien in pygame.sprite.spritecollide(player, aliens, 1):
                boom_sound.play()
                Explosion(alien)
                Explosion(player)
                REALSCORE = REALSCORE + (10 * (LEVEL / 5 + 1))
                if alien.hitpoints <= 0:
                    kills = kills + 1
                    pass
                SHIPS = SHIPS - 1
                hitcol = 16
                MAX_SHOTS = NOMINAL_MAX_SHOTS
                RELOAD_TIME = 10
                player.image = player.images[SHIPS]
                hit_sound.play()
                if SHIPS == 0:
                    player.kill()
                    pass
                pass

            for bosscol in pygame.sprite.spritecollide(player, boss, 0):
                boom_sound.play()
                bosscol.damage(5)
                Explosion(player)           
                SHIPS = SHIPS - 1
                hitcol = 16
                MAX_SHOTS = NOMINAL_MAX_SHOTS
                RELOAD_TIME = 10
                
                player.image = player.images[SHIPS]
                hit_sound.play()
                if SHIPS == 0:
                    player.kill()
                    pass
                pass

            for powerup in pygame.sprite.spritecollide(player, powerups, 1):
                if SHIPS < 6:
                    SHIPS = SHIPS + 1
                    shield_sound.play()
                    pass
                else:
                    rapidfire_sound.play()
                    if MAX_SHOTS == NOMINAL_MAX_SHOTS * 2:
                        REALSCORE = REALSCORE + 10
                        # smart bomb!
                        if random.random()*1 < LEVEL:
                            flashcol = 16
                            for alien in aliens.sprites():
                                #smartbomb_sound.play()
                                Explosion(alien)
                                alien.hitpoints -= 3
                                if alien.hitpoints <= 0:
                                    kills = kills + 1
                                    alien.kill()
                                    pass
                                REALSCORE = REALSCORE + (10 * (LEVEL / 5 + 1))
                                pass
                            pass
                        pass
                    MAX_SHOTS = NOMINAL_MAX_SHOTS * 2
                    RELOAD_TIME = 5
                    pass
                pass
                    
                powerup.kill()
                player.image = player.images[SHIPS]
                pass

            bosscol = pygame.sprite.groupcollide(boss, shots, 0, 1)

            for b in bosscol.keys():
                boom_sound.play()
                #print bosscol[b]
                Explosion(bosscol[b][0])
                b.damage(1)
                
            
            for alien in pygame.sprite.groupcollide(aliens, shots, 0, 1).keys():
                boom_sound.play()
                Explosion(alien)
                alien.hitpoints -= 1
                if alien.hitpoints <= 0:
                    kills = kills + 1
                    alien.kill()
                    pass
                REALSCORE = REALSCORE + (10 * (LEVEL / 5 + 1))
                HIT = HIT + 1
                pass
            
            for bomb in pygame.sprite.spritecollide(player, bombs, 1):     
                boom_sound.play()
                Explosion(player)
                SHIPS = SHIPS - 1
                hitcol = 16
                MAX_SHOTS = NOMINAL_MAX_SHOTS
                RELOAD_TIME = 10
                player.image = player.images[SHIPS]
                Explosion(bomb)
                hit_sound.play()
                if SHIPS == 0:
                    player.kill()
                    pass
                pass
            
            # draw the scene
            dirty = all.draw(screen)
            pygame.display.update(dirty)
        
            # cap the framerate
            clock.tick(60)
            pass


        dead_sound.play()
        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
            pass
        
        a = GameOver()
        GET_BY_COST = 0
        gamma = 5.0
        for i in xrange(1000):
            if gamma > 1.0:
                pygame.display.set_gamma(gamma)
                gamma -= .05
                pass
            for event in pygame.event.get():
                if (event.type == QUIT or
                    (event.type == KEYDOWN and event.key == K_ESCAPE)):
                    return 0
                elif event.type == KEYDOWN and event.key not in (K_SPACE,K_UP,K_DOWN,K_LEFT,K_RIGHT):
                    return 1
                
                pass
            keystate = pygame.key.get_pressed()
            if keystate[K_n]:
                LEVEL           = 1
                SHIPS           = 5
                FIRED           = 0
                HIT             = 0
                REALSCORE       = 0
                GET_BY_COST     = 100
                break
            all.clear(screen, background)
            all.update()
            dirty = all.draw(screen)
            pygame.display.update(dirty)
            clock.tick(60)
            pass
        del a
        return 1

        pass
    pass


#call the "main" function if running this script
if __name__ == '__main__':
    restart = 1
    while restart:
        SHIPS = 5
        LEVEL =1
        SCORE=0
        REALSCORE=0
        flashcol = 0
        hitcol  = 0
        restart = main()
    pass
