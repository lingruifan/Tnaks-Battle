import pygame
import math
from Obstacle import *

# COlor default
cyan = (0,255,255)
pink = (255,0,255)

class Bullet(pygame.sprite.Sprite):
    # Model
    def __init__(self, cx, cy, angle, speed):
        pygame.sprite.Sprite.__init__(self)
        # A bullet has a position, a size, a direction, and a speed
        self.cx = cx
        self.cy = cy
        self.r = 5
        self.angle = angle
        self.speed = speed
        self.damage = 1
        
    # View
    def draw(self, screen, color=cyan):
        pygame.draw.circle(screen, color, [self.cx, self.cy], self.r)

    # Controller
    def moveBullet(self):
        # Move according to the original trajectory
        offset = 45
        self.cx += int(math.cos(math.radians(self.angle-offset))*self.speed)
        self.cy -= int(math.sin(math.radians(self.angle-offset))*self.speed)

    def collideWithBlock(self, other):
        if not isinstance(other, Block):
            return False
        else:
            dist = ((other.x + blockSize/2 - self.cx)**2 + (other.y + blockSize/2 - self.cy)**2)**0.5
            return dist <= self.r + blockSize/2
            
    def isOffscreen(self, width, height):
        # Check if the bullet has moved out of the screen.
        return (self.cx + self.r <= 0 or self.cx - self.r >= width) or \
               (self.cy + self.r <= 0 or self.cy - self.r >= height)

class SpecialBullet(Bullet):
    # Model
    def __init__(self, cx, cy, angle, speed):
        super().__init__(cx, cy, angle, speed)
        self.speed = speed * 0.9
        self.damage = 2
    # View
    def draw(self, screen):
        super().draw(screen, color=pink)
