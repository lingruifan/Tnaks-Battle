import pygame
import random

blockSize = 25

class Block(pygame.sprite.Sprite):
    
    # Model
    def __init__(self, x, y):
        self.wall = pygame.transform.scale(pygame.image.load("wall.jpg").convert_alpha(), [blockSize, blockSize])
        self.x = x
        self.y = y
        self.life = random.choice([0]*12 + [1, 2, 3, 4])
        
    # View
    def drawBlock(self, screen):
        if self.life > 0:
            screen.blit(self.wall, (self.x, self.y))

class Star(Block):
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.star = pygame.transform.scale(pygame.image.load("star.png").convert_alpha(), [blockSize, blockSize])
        self.life = 1
    def draw(self, screen):
        if self.life > 0:
            screen.blit(self.star, (self.x, self.y))

# Makes a normal map in a 2d list. 
def map(width, height):
    rows = width // blockSize
    cols = height // blockSize
    pattern = [ ([None]*cols) for row in range(rows) ]
    lst = []
    for i in range(rows):
        for j in range(cols):
            pattern[i][j] = Block(j*blockSize, i*blockSize)
            
    pattern[0][0], pattern[0][cols-1] = None, None
    pattern[rows-1][0], pattern[rows-1][cols-1] = None, None
    return pattern

# Makes the star mode map in a 2d list. 
def starMap(width, height):
    rows = width // blockSize
    cols = height // blockSize
    pattern = [ ([None]*cols) for row in range(rows) ]
    for i in range(rows):
        for j in range(cols):
            pattern[i][j] = Block(j*blockSize, i*blockSize)
    # Choose the star coordinate.
    starX = random.randint(1, len(pattern)-2)
    starY = random.randint(1, len(pattern[0])-2)
    perim = 3
    # Surround the star with blocks. 
    for i in range(starX-perim, starX+perim+1):
        if (i >= 0) and (i < rows):
            for j in range(starY-perim, starY+perim+1):
                if j >= 0 and j < cols:
                    pattern[i][j] = Block(j*blockSize, i*blockSize)
                else:
                    pass
        else:
            pass
            
    pattern[0][0], pattern[0][cols-1] = None, None
    pattern[rows-1][0], pattern[rows-1][cols-1] = None, None
    pattern[starX][starY] = Star(starY*blockSize, starX*blockSize)
    return pattern