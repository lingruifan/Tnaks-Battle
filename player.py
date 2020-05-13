import pygame
import math
from bullets import *
from Obstacle import *

# Default degree
default = 45
class Character(pygame.sprite.Sprite):
    # Model
    def __init__(self, cx, cy):
        pygame.sprite.Sprite.__init__(self)
        self.cx = cx
        self.cy = cy
        self.playerSize = 12.5
        self.angle = default
        self.health = 8
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("player.png").convert_alpha(), [blockSize, blockSize]), -90)
        
    # Controller
    def move(self, dx, dy):
        # move the player object
        self.cx += dx
        self.cy += dy
    
    def rotate(self, degree):
        # rotate the direction player's facing. 
        self.angle += degree
        self.image = pygame.transform.rotate(self.image, degree)
        
    def collideWithBlocks(self, other):
        
        if not isinstance(other, Block):
            return False
        # leftA < rightB and (topA > bottomB or topB > bottomA)
        # leftB < rightA and (topA > bottomB or topB > bottomA)
        leftA, rightA = self.cx-self.playerSize, self.cx+self.playerSize
        topA, bottomA = self.cy-self.playerSize, self.cy+self.playerSize
        leftB, rightB = other.x, other.x+blockSize
        topB, bottomB = other.y, other.y+blockSize
        if leftA >= rightB or rightA <= leftB:
            return False
        if topA >= bottomB or topB >= bottomA:
            return False
        return True
        
    def makeBullet(self):
        # Generates a bullet heading in the direction the player is facing
        x = int(self.cx + math.cos(math.radians(self.angle)))
        y = int(self.cy - math.sin(math.radians(self.angle)))
        speed = 5
        return Bullet(x, y, self.angle, speed)
        
    def collideWithBullets(self, other):
        # Check if the bullet and player overlap at all
        if not isinstance(other, Bullet):
            return False
        else:
            dist = ((other.cx - self.cx)**2 + (other.cy - self.cy)**2)**0.5
            return dist <= self.playerSize + other.r
    # View
    def draw(self, screen, color):
        cx, cy = self.cx, self.cy
        r = self.playerSize*2 / (2**0.5)
        angle = math.radians(self.angle)
        numOfPoints = 4
        angleChange = 2*math.pi/4
        points = []
        imageRect = self.image.get_rect()
        imageRect.center = (self.cx, self.cy)
        for point in range(numOfPoints):
            points.append((cx + round(r*math.cos(angle+point*angleChange), 2), 
                          cy + round(r*math.sin(angle+point*angleChange), 2)))
        font = pygame.font.SysFont(None, 25)
        text = font.render(str(self.health), True, (0,0,0))
        pygame.draw.polygon(screen, color, points)
        screen.blit(self.image, imageRect)
        screen.blit(text, (cx, cy))

class Player(Character):
    # Model
    def __init__(self, PID, cx, cy):
        super().__init__(cx, cy)
        self.PID = PID
        self.kill = 0
        self.special = False
        
    # Controller    
    def changePID(self, PID):
        # change the player ID
        self.PID = PID
    
    def makeBullet(self):
        # Generates a bullet heading in the direction the player is facing
        x = int(self.cx + math.cos(math.radians(self.angle)))
        y = int(self.cy - math.sin(math.radians(self.angle)))
        speed = 5
        if (self.special == True):
            return SpecialBullet(x, y, self.angle, speed)
        else:
            return Bullet(x, y, self.angle, speed)
    
    # View
    def draw(self, screen, color):
        super().draw(screen, color)

class AI(Character):
    
    # Controller
    def chase(self, vx, vy):
        # move the ai. 
        self.cx += vx
        self.cy += vy
    
    def rotate(self, degree):
        self.angle += degree
        
    def makeBullet(self):
        # Generates a bullet heading in the direction the player is facing
        x = int(self.cx + math.cos(math.radians(self.angle)))
        y = int(self.cy - math.sin(math.radians(self.angle)))
        speed = 5
        return Bullet(x, y, self.angle, speed)
    
    # View
    def draw(self, screen, color):
        super().draw(screen, color)