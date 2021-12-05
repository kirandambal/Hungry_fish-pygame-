################################################################
## Sprite classes, to be ran from main.py. Not a functioning  ##
## program on its own!                                        ##
##                                                            ##
## written by  : KIRAN V DAMBAL                               ##
################################################################

import pygame
import random
import variables

def import_image(spritetype, imagename):
    """ (str,str) -> surface
    Import image from file and make it transparent."""
    if spritetype != "":
        sprite_surface = pygame.image.load(spritetype + "/" + imagename).convert()
        sprite_surface.set_alpha()
    else:
        sprite_surface = pygame.image.load(imagename).convert()
        sprite_surface.set_alpha()

    return sprite_surface

def random_generator(die_type,modifier=0,integer=1):
    """ (num,num,int) -> num
    Random number generator, outputs integers by default."""
    if integer == 0:
        value = random.random()*die_type + modifier
    else:
        value = int(random.random()*die_type) + int(modifier)
    return value
  

class enemy_fish(pygame.sprite.Sprite):
    """ Class for enemy fish sprites, with all enemy fish values. """
    def __init__(self, screen, spritetype, imagename,
                 position=None, velocity=(0, 0)):

        super().__init__()

        # import image, make transparent with mask
        self.screen = screen
        self.imagename = imagename
        self.image = import_image(spritetype, imagename)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.mask = pygame.mask.from_surface(self.image)

        self.fishlist = variables.fishfiles
        self.fishweights = variables.enemyweights
        self.fishnutrition = variables.enemynutrition
        wigglevalues = variables.efish_wiggle_values

        # sets default weight at zero
        self.weight = 0
        
        # random wiggle value depending on fish type
        for item in wigglevalues:
            if imagename == item:
                self.wiggle = random_generator(wigglevalues[item],5)

        #spawn fish in a random yposition, randomly on left or right screen
        self.ypos = random_generator(screen.get_size()[1]-200,100)
        spawny = [-80,screen.get_size()[0]+80]
        self.rect.right = spawny[random_generator(2,0)]
        self.rect.centery = self.ypos

        self.vx, self.vy = velocity
        #print("vx =", self.vx, "vy = ", self.vy)

        # direction of fish movement depending on spawn position
        if self.rect.center[0] > 0:
            self.vx *= -1

    def update(self,size,group,playerweight):
        """ Updates fish sprite. If fish swims off screen, sprite is killed.
        Also implements vertical wiggle movement, and death on collision
        with player if smaller than player, and returns nutrition and weight
        value."""
        self.rect.centerx += self.vx
        self.rect.centery += self.vy
        # kills sprite if goes off screen
        if self.rect.right < -100 or self.rect.left > size[0] + 100:
            self.kill()
        if self.rect.bottom < 40 or self.rect.top > size[1] + 1:
            self.kill()
        # code for y wiggle movement
        if self.rect.centery + self.wiggle < self.ypos:
            self.vy *= -1
        if self.rect.centery - self.wiggle > self.ypos:
            self.vy *= -1
        # code for death on collision + return value of weight and nutrition
        if pygame.sprite.spritecollide(
            self, group, False, pygame.sprite.collide_mask):
            self.weight = self.fishweights[self.fishlist.index(self.imagename)]
            self.nutrition = self.fishnutrition[self.fishlist.index(self.imagename)]
            if self.weight < playerweight:
                self.kill()
            return (self.weight, self.nutrition)
    
class player_fish(pygame.sprite.Sprite):
    """ Class for player fish sprite with values necessary for sprite interaction. """
    def __init__(self, screen, spritetype, imagename,
                 position=None):
        super().__init__()

        # import transparent image sprite with mask
        self.screen = screen
        self.image = import_image(spritetype, imagename)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.mask = pygame.mask.from_surface(self.image)

        # random y position
        self.ypos = random_generator(screen.get_size()[1]-150,100)

        # start weight @ 20 (allows player to eat smallest fish)
        self.weight = variables.player_fish_start_size
        self.alive = True

        self.fish_size = variables.player_fish_size

        # option to place player @ specific position, else places (100,random y)
        if position:
            self.rect.center = position
        else:
            self.rect.center = (100, self.ypos)

    def update(self,size,vyvx):
        """ Updates player fish sprite depending on directional arrow keys
        pressed. """
        vy = 0
        vx = 0
        # velocity dependent on key presses detected as an event
        if self.rect.top > 50:
            vy = vyvx[0][0]
        if self.rect.left > 2:
            vx = vyvx[1][0]
        if self.rect.bottom < size[1] - 2 and vy == 0:
            vy = vyvx[0][1]
        if self.rect.right < size[0] - 2 and vx == 0:
            vx = vyvx[1][1]
        # moves image dependent on velocity from key presses
        self.rect.center = (self.rect.center[0] + vx, self.rect.center[1] + vy)

    def enemy_collision(self,enemy_weight,enemy_nutrition):
        """ Called when collision with enemy. If enemy's weight value is less
        than player weight value, the enemy is eaten an "nutrition" is
        calculated and added to player weight. Death of player fish if enemy
        fish is larger. """
        # eats enemy if enemy weight is less than player weight
        if enemy_weight < self.weight:
            nutrition = int(random_generator(0.5,0.1,0).__round__(2)*enemy_nutrition)
            self.weight += nutrition
        # gets eaten if enemy weight is larger
        if enemy_weight > self.weight:
            self.alive = False
            self.kill()

    def update_image(self, spritetype, imagename):
        """ If player's weight reaches above a threshold, sprite image changes,
        to appropriate sprite image representation. """
        centre = self.rect.center
        self.image = import_image(spritetype, imagename)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = centre


class backgroundimage(pygame.sprite.Sprite):
    """ Class to define how the scrolling background image is displayed. """
    def __init__(self, screen, spritetype="", imagename="", position=()):
        super().__init__()

        self.screen = screen
        self.image = import_image("ui", "seabed.png")
        self.rect = self.image.get_rect()
        self.imagerepeat = False
        self.newspawned = False

        if position != (): #if position specified
            self.rect.left = position[0]
            self.rect.top = position[1]
        else:
            self.rect.left = 0 #spawn image top left at 0,0
            self.rect.top = 0

    def update(self,size):
        """ Scrolls background from right to left, maintaining loop when the
        right edge of the background sprite reaches the right edge of the
        scnree, by creating a new background image sprite. Kills background
        sprite if it goes off the left edge of the screen."""
        # scrolls background image right -> left
        self.rect.center = (self.rect.center[0] - 2, self.rect.center[1])
        # tells main to not spawn a new image
        self.imagerepeat = False
        # if statement with conditions to spawn new bg image
        if self.rect.right < (size[0] + 2) and self.newspawned == False:
            self.imagerepeat = True
            self.newspawned = True
        # if statement to kill sprite if goes off screen left
        if self.rect.right < 0:
            self.kill()
            
class menuimage(pygame.sprite.Sprite):
    """ Class to display all menu images as sprites. """
    def __init__(self, screen, spritetype="", imagename="", position = (), transparent = False):
        super().__init__()

        self.screen = screen
        self.image = import_image(spritetype, imagename)
        self.rect = self.image.get_rect()

        if transparent:
            self.image.set_colorkey(self.image.get_at((0,0)))

        if position == ():
            self.rect.left = 0 #spawn image top left at 0,0
            self.rect.top = 0
        else:
            self.rect.left = position[0]
            self.rect.top = position[1]

    def update_image(self, spritetype, imagename):
        """ If player's weight reaches above a threshold, UI image changes,
        to appropriate UI image representation. """
        centre = self.rect.center
        self.image = import_image(spritetype, imagename)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = centre
