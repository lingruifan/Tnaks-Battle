import pygame
from player import *
import random

# color default
red = (255,0,0)
green = (0,255,0)

class Bombs(pygame.sprite.Sprite):
    
    # Model
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.speedX, self.speedY = 5, 5
        self.thSize = 25
    
    # Control
    def move(self):
        self.y += self.speedY
    
    def collideWithPlayer(self, other):
        # see if the bombs hit players
        if not isinstance(other, Player):
            return False
        if self.x > other.cx+other.playerSize or self.x+self.thSize < other.cx-other.playerSize:
            return False
        if self.y > other.cy+other.playerSize or self.y+self.thSize < other.cy-other.playerSize:
            return False
        return True
    
    # View
    def draw(self, screen):
        x, y = self.x, self.y
        size = self.thSize
        pygame.draw.rect(screen, red, [x, y, size, size])
        
# A special kind of bomb
class Missiles(Bombs):
    
    # Model
    def move(self, width, height):
        self.x += self.speedX
        if self.x <= 0 or self.x + self.thSize >= width:
            self.speedX = -self.speedX
            self.x += self.speedX
            
        self.y += self.speedY
        if self.y <= 0 or self.y + self.thSize >= height:
            self.speedY = -self.speedY
            self.y += self.speedY
        
    # View
    def draw(self, screen):
        x, y = self.x, self.y
        size = self.thSize
        pygame.draw.rect(screen, green, [x, y, size, size])