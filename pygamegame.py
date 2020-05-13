#############################
# Sockets Client Demo
# by Rohan Varma
# adapted by Kyle Chin
#############################

import socket
import threading
from queue import Queue

HOST = "128.237.127.243" # put your IP address here if playing on multiple computers
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

'''
pygamegame.py
created by Lukas Peraza
 for 15-112 F15 Pygame Optional Lecture, 11/11/15
use this code in your term project if you want
- CITE IT
- you can modify it to your liking
  - BUT STILL CITE IT
- you should remove the print calls from any function you aren't using
- you might want to move the pygame.display.flip() to your redrawAll function,
    in case you don't need to update the entire display every frame (then you
    should use pygame.display.update(Rect) instead)
'''
import pygame
import time
from bombs import *
from player import *
from Obstacle import *
from bullets import *
import random
import math
from functools import reduce

####################################
# customize these functions
####################################

class PygameGame(object):
    # Initializing values. 
    def init(self):
        # General initializations. 
        self.bombs = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()
        self.playerBullets = pygame.sprite.Group()
        self.timeCounter = 0
        self.menuBg = pygame.transform.scale(pygame.image.load("bg2.png").convert_alpha(), [self.width, self.height])
        self.background = pygame.transform.scale(pygame.image.load("bg.jpg").convert_alpha(), [self.width, self.height])
        #self.music = pygame.mixer.music.load("music.wav")
        
        # Initializations for the AI mode
        self.birthX = self.width-12.5
        self.birthY = self.height-12.5
        self.aiX, self.aiY = 12.5, 12.5
        self.player = Player("Lonely", self.birthX, self.birthY)
        self.ai = AI(self.aiX, self.aiY)
        self.aiBullets = pygame.sprite.Group()
        
        # Initializations for multiplayer mode
        self.pos = [(self.width-12.5, self.height-12.5), (12.5, self.height-12.5), (self.width-12.5, 12.5), (12.5, 12.5)]
        self.others = dict()
        self.otherBullets = dict()
        self.obs = starMap(self.width, self.height)
        obsMsg = "obs %s\n" % self.doObs(self.obs)
        server.send(obsMsg.encode())
       
        # Game state initial values
        self.aiMode = False
        self.me = False
        self.othersState = dict()
        self.playerNum = 0
        
        # Button positions
        self.buttonW, self.buttonH = 200, 50
        self.first = [[200,200], [200,280], [200,360], [200,440]]
        
    # Convert elements in self.obs into integers. 
    def doObs(self, obs):
        pattern = [ ([None]*len(obs)) for row in range(len(obs)) ]
        for i in range(len(obs)):
            for j in range(len(obs)):
                if isinstance(obs[i][j], Block):
                    pattern[i][j] = obs[i][j].life
                    if isinstance(obs[i][j], Star):
                        pattern[i][j] = 9
                        
        return pattern
    
    # Change the list of integers bakc into Block objects. 
    def redoObs(self, pattern):
        obs = [ ([None]*len(pattern)) for row in range(len(pattern)) ]
        for i in range(len(pattern)):
            for j in range(len(pattern)):
                if pattern[i][j] != None:
                    if pattern[i][j] == 9:
                        obs[i][j] = Star(j*blockSize, i*blockSize)
                        obs[i][j].life = 1
                    else:
                        obs[i][j] = Block(j*blockSize, i*blockSize)
                        obs[i][j].life = pattern[i][j]
        return obs
        
    def mousePressed(self, x, y):
        # Mouse interactions on the start menu. 
        connectMsg = ""
        if (self.first[0][0] < x < self.first[0][0]+self.buttonW) and (self.first[0][1] < y < self.first[0][1]+self.buttonH):
            self.aiMode = True
        elif (self.first[1][0] < x < self.first[1][0]+self.buttonW) and (self.first[1][1] < y < self.first[1][1]+self.buttonH):
            self.playerNum = 2
            self.me = True
            connectMsg = "connecting %s\n" % self.me
        elif (self.first[2][0] < x < self.first[2][0]+self.buttonW) and (self.first[2][1] < y < self.first[2][1]+self.buttonH):
            self.playerNum = 3
            self.me = True
            connectMsg = "connecting %s\n" % self.me
        elif (self.first[3][0] < x < self.first[3][0]+self.buttonW) and (self.first[3][1] < y < self.first[3][1]+self.buttonH):
            self.playerNum = 4
            self.me = True
            connectMsg = "connecting %s\n" % self.me
        
        if (connectMsg != ""):
            print("sending: ", connectMsg,)
            server.send(connectMsg.encode())

    def mouseReleased(self, x, y):
        pass

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass
    
    # See if the area around the player is not a drawing block. 
    def neighborVacant(self, x, y):
        if (x < 0) or (x >= self.width//blockSize) or (y < 0) or (y >= self.height//blockSize):
            return False
        elif (self.obs[x][y] == None) or (isinstance(self.obs[x][y], Block) and self.obs[x][y].life > 0):
            return False
        return True
        
    def keyPressed(self, keyCode, modifier):
        dx, dy = 0, 0
        speed = 5
        # Messages
        msg1 = ""
        msg2 = ""
        msg3 = ""
        msg4 = ""
        makeBulletMsg = ""
        starMsg = ""
        addBlockMsg = ""
        # Rotate the player with direction keys. 
        if keyCode == pygame.K_q:
            degree = 90
            self.player.rotate(degree)
            msg3 = "playerRotate %d\n" % degree
        elif keyCode == pygame.K_e:
            degree = -90
            self.player.rotate(degree)
            msg3 = "playerRotate %d\n" % degree
        
        if msg3 != "":
            print("sending: ", msg3,)
            server.send(msg3.encode())
        
        # Player can make blocks around him when he kills four lives. 
        if self.player.kill >= 4:
            posX = int((self.player.cy) // blockSize)
            posY = int((self.player.cx) // blockSize)
            if keyCode == pygame.K_a and self.neighborVacant(posX, posY-1):
                self.obs[posX][posY-1].life = 1
                addBlockMsg = "addBlock %d %d\n" % (posX, posY-1)
            elif keyCode == pygame.K_d and self.neighborVacant(posX, posY+1):
                self.obs[posX][posY+1].life = 1
                addBlockMsg = "addBlock %d %d\n" % (posX, posY+1)
            elif keyCode == pygame.K_w and self.neighborVacant(posX-1, posY):
                self.obs[posX-1][posY].life = 1
                addBlockMsg = "addBlock %d %d\n" % (posX-1, posY)
            elif keyCode == pygame.K_s and self.neighborVacant(posX+1, posY):
                self.obs[posX+1][posY].life = 1
                addBlockMsg = "addBlock %d %d\n" % (posX+1, posY)
        
        if (addBlockMsg != ""):
            print("sending: ", addBlockMsg,)
            server.send(addBlockMsg.encode())
            
        # Move the player with direction keys. 
        if keyCode == pygame.K_LEFT:
            if self.player.cx + dx <= self.player.playerSize:
                dx = 0
            else:
                dx = -speed
        elif keyCode == pygame.K_RIGHT:
            if self.player.cx + self.player.playerSize + dx >= self.width:
                dx = 0
            else:
                dx = speed
        elif keyCode == pygame.K_UP:
            if self.player.cy + dy <= self.player.playerSize:
                dy = 0
            else:
                dy = -speed
        elif keyCode == pygame.K_DOWN:
            if self.player.cy + self.player.playerSize + dy >= self.height:
                dy = 0
            else:
                dy = speed
        
        self.player.move(dx, dy)
        msg1 = "playerMoved %d %d\n" % (dx, dy)
        
        if (msg1 != ""):
            print("sending: ", msg1,)
            server.send(msg1.encode())
            
        # Motions when player is blocked. 
        for row in self.obs:
            for block in row:
                if self.player.collideWithBlocks(block) and block.life > 0:
                    if isinstance(block, Star):
                        block.life = 0
                        starMsg = "star gg\n"
                        self.player.special  = True
                        msg4 = "specialBullet %s\n" % True
                    if self.player.kill < 6:
                        self.player.move(-dx, -dy)
                        msg2 = "playerMoved %d %d\n" % (-dx, -dy)
        
        if (starMsg != ""):
            print("sending: ", starMsg,)
            server.send(starMsg.encode())
        if (msg4 != ""):
            print("sending: ", msg4,)
            server.send(msg4.encode())
        if (msg2 != ""):
            print("sending: ", msg2,)
            server.send(msg2.encode())
            
        # Make a bullet.
        if keyCode == pygame.K_SPACE:
            bullet = self.player.makeBullet()
            self.playerBullets.add(bullet)
            makeBulletMsg = "makeBullet %d %d\n" % (bullet.cx, bullet.cy)
        if (makeBulletMsg != ""):
            print("sending: ", makeBulletMsg,)
            server.send(makeBulletMsg.encode())
            
    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt):
        self.timeCounter += 1
        timeDelay = 150
        timeDelayAI = 80
        # Messages
        bombMsg = ""
        missileMsg = ""
        missMoveMsg = ""
        otherhealthMsg = ""
        
        # Game process for AI mode
        if (self.aiMode == True):
            # Make bombs and their motions
            if (self.timeCounter % timeDelayAI == 0):
                thx = random.randint(0, self.width-blockSize)
                thy = random.randint(0, self.height-blockSize)
                self.bombs.add(Bombs(thx, thy))
            for bomb in self.bombs:
                if bomb.collideWithPlayer(self.player):
                    bomb.thSize = 0
                    self.player.health -= 1
            # Make special bombs and their motions
            if (self.timeCounter % timeDelayAI == 0):
                thx = random.randint(0, self.width-blockSize)
                thy = random.randint(0, self.height-blockSize)
                self.missiles.add(Missiles(thx, thy))
            for missile in self.missiles:
                missile.move(self.width, self.height)
                if missile.collideWithPlayer(self.player):
                    self.missiles.remove(missile)
                    self.player.health -= 1
            
            # Bullets motions for player
            for bullet in self.playerBullets:
                bullet.moveBullet()
                for row in self.obs:
                    for block in row:
                        if bullet.collideWithBlock(block) and block.life > 0:
                            if not isinstance(block, Star): 
                                self.playerBullets.remove(bullet)
                                block.life -= 1
                if self.ai.collideWithBullets(bullet):
                    self.ai.health -= bullet.damage
                    self.playerBullets.remove(bullet)
                elif bullet.isOffscreen(self.width, self.height):
                    self.playerBullets.remove(bullet)
            # Bullets motions for ai
            for bullet in self.aiBullets:
                bullet.moveBullet()
                for row in self.obs:
                    for block in row:
                        if bullet.collideWithBlock(block) and block.life > 0: 
                            if not isinstance(block, Star): 
                                self.aiBullets.remove(bullet)
                                block.life -= 1
                if self.player.collideWithBullets(bullet):
                    self.player.health -= bullet.damage
                    self.aiBullets.remove(bullet)
                elif bullet.isOffscreen(self.width, self.height):
                    self.aiBullets.remove(bullet)
            # AI path finding
            opposite = self.player.cy - self.ai.cy
            ajacent = self.player.cx - self.ai.cx
            if ajacent != 0:
                angle = math.atan(opposite/ajacent)
            else:
                angle = 90 if opposite > 0 else -90
            if self.ai.cx > self.player.cx:
                angle += 180
            
            dist = ((self.player.cx-self.ai.cx)**2 + (self.player.cy-self.ai.cy)**2)**0.5
            direction = random.choice([True, False])
            velocity = 3
            vx, vy = 0, 0
            # AI moves towards the player, shoots him when they're close enough
            if dist > (self.ai.playerSize + self.player.playerSize)*3:
                
                if self.timeCounter % 1 == 0:
                    if direction == True:
                        vx = velocity * math.cos(angle)
                        self.ai.chase(vx, vy)
                        
                    else:
                        vy = velocity * math.sin(angle)
                        self.ai.chase(vx, vy)
                        
            else:
                self.ai.rotate(angle)
                if self.timeCounter % 3 == 0:
                    self.aiBullets.add(self.ai.makeBullet())
            # AI will shoot around when encountered a block
            for row in self.obs:
                for block in row:
                    if self.ai.collideWithBlocks(block) and block.life > 0:
                        self.ai.chase(-vx, -vy)
                        op = self.ai.cy - (block.y + blockSize/2)
                        aj = self.ai.cx - (block.x + blockSize/2)
                        if aj != 0:
                            degree = math.degrees(math.atan(op/aj))
                        else:
                            degree = 90 if op > 0 else -90
                        self.ai.rotate(degree)
                        if self.timeCounter % 5 == 0:
                            self.aiBullets.add(self.ai.makeBullet())
        
        
        
        # Game process for multiplayer mode
        if self.me and self.otherConnected():
            # Make a bomb.
            if self.timeCounter % timeDelay == 0 and len(self.others) == self.playerNum-1:
                thx = random.randint(0, self.width-blockSize)
                thy = random.randint(0, self.height-blockSize)
                self.bombs.add(Bombs(thx, thy))
                bombMsg = "makeBomb %d %d\n" % (thx, thy)
            if (bombMsg != ""):
                print("sending: ", bombMsg,)
                server.send(bombMsg.encode())
            # When bombs hit a player. 
            for bomb in self.bombs:
                if bomb.collideWithPlayer(self.player):
                    bomb.thSize = 0
                    self.player.health -= 1
                for other in self.others:
                    if bomb.collideWithPlayer(self.others[other]):
                        bomb.thSize = 0
                        self.others[other].health -= 1
                        otherhealthMsg = "otherHealth %s 1\n" % other
            
            # Make a special bomb.
            if self.timeCounter % timeDelay == 0 and len(self.others) == self.playerNum-1:
                thx = random.randint(0, self.width-blockSize)
                thy = random.randint(0, self.height-blockSize)
                self.missiles.add(Missiles(thx, thy))
                missileMsg = "makeMissile %d %d\n" % (thx, thy)
            if (missileMsg != ""):
                print("sending: ", missileMsg,)
                server.send(missileMsg.encode())
            # When special bombs hit a player. 
            for missile in self.missiles:
                missile.move(self.width, self.height)
                if missile.collideWithPlayer(self.player):
                    self.missiles.remove(missile)
                    self.player.health -= 1
                for other in self.others:
                    if missile.collideWithPlayer(self.others[other]):
                        self.missiles.remove(missile)
                        self.others[other].health -= 1
                        otherhealthMsg = "otherHealth %s 1\n" % other
            
            # Bullets motions for self player. 
            for bullet in self.playerBullets:
                bullet.moveBullet()
                for row in self.obs:
                    for block in row:
                        if bullet.collideWithBlock(block) and block.life > 0:
                            if not isinstance(block, Star): 
                                self.playerBullets.remove(bullet)
                                block.life -= 1
                for other in self.others:
                    if self.others[other].collideWithBullets(bullet):
                        self.others[other].health -= bullet.damage
                        otherhealthMsg = "otherHealth %s %d\n" % (other, bullet.damage)
                        self.playerBullets.remove(bullet)
                        self.player.kill += 1
                if bullet.isOffscreen(self.width, self.height):
                    self.playerBullets.remove(bullet)
            
            # Bullets motions for other players. 
            for PID in self.otherBullets:
                for bullet in self.otherBullets[PID]:
                    bullet.moveBullet()
                    for row in self.obs:
                        for block in row:
                            if bullet.collideWithBlock(block) and block.life > 0:
                                if not isinstance(block, Star): 
                                    self.otherBullets[PID].remove(bullet)
                                    block.life -= 1
                    if self.player.collideWithBullets(bullet):
                        self.player.health -= bullet.damage
                        self.otherBullets[PID].remove(bullet)
                    elif bullet.isOffscreen(self.width, self.height):
                        self.otherBullets[PID].remove(bullet)
            
            # if (otherhealthMsg != ""):
            #     print("sending: ", otherhealthMsg,)
            #     server.send(otherhealthMsg.encode())
            
        #timerFired receives instructions and executes them
        while (serverMsg.qsize() > 0):
            msg = serverMsg.get(False)
            try:
                print("received: ", msg, "\n")
                msg = msg.split()
                command = msg[0]

                if (command == "myIDis"):
                    myPID = msg[1]
                    num = int(myPID[-1])
                    self.player = Player(myPID, self.pos[num][0], self.pos[num][1])
                
                elif (command == "newPlayer"):
                    newPID = msg[1]
                    num = int(newPID[-1])
                    x = self.pos[num][0]
                    y = self.pos[num][1]
                    self.others[newPID] = Player(newPID, x, y)
                    self.othersState[newPID] = False
                
                elif (command == "connecting"):
                    PID = msg[1]
                    status = bool(msg[2])
                    self.othersState[PID] = status
                        
                elif (command == "playerMoved"):
                    PID = msg[1]
                    dx = int(msg[2])
                    dy = int(msg[3])
                    self.others[PID].move(dx, dy)
                
                elif (command == "playerRotate"):
                    PID = msg[1]
                    angle = int(msg[2])
                    self.others[PID].rotate(angle)
                    
                elif (command == "specialBullet"):
                    PID = msg[1]
                    self.others[PID].special = True
                    
                elif (command == "makeBullet"):
                    PID = msg[1]
                    bull = self.others[PID].makeBullet()
                    if PID in self.otherBullets:
                        self.otherBullets[PID].add(bull)
                    else:
                        self.otherBullets[PID] = pygame.sprite.Group()
                        self.otherBullets[PID].add(bull)
                    
                elif (command == "makeBomb"):
                    PID = msg[1]
                    thx = int(msg[2])
                    thy = int(msg[3])
                    bom = Bombs(thx, thy)
                    self.bombs.add(bom)
                        
                elif (command == "makeMissile"):
                    PID = msg[1]
                    thx = int(msg[2])
                    thy = int(msg[3])
                    miss = Missiles(thx, thy)
                    self.missiles.add(miss)
                
                # elif (command == "otherHealth"):
                #     PID = msg[2]
                #     d = msg[3]
                #     if PID in self.others:
                #         self.others[PID].health -= d
                        
                elif (command == "obs"):
                    PID = msg[1]
                    obsLst = eval(reduce(lambda x, y: x + y, msg[2:]))
                    obs = self.redoObs(obsLst)
                    self.obs = obs
                
                elif (command == "star"):
                    for row in self.obs:
                        for block in row:
                            if isinstance(block, Star):
                                block.life = 0
                
                elif (command == "addBlock"):
                    x, y = int(msg[2]), int(msg[3])
                    self.obs[x][y].life = 1
                            
            except:
                print("failed")
            serverMsg.task_done()
    
    # Check if other players are connected. 
    def otherConnected(self):
        for PID in self.othersState:
            if self.othersState[PID] == False:
                return False
        return True
        
    # If other player all get 0 life, the player wins. 
    def playerWin(self):
        otherDeath = 0
        for other in self.others:
            if self.others[other].health > 0:
                return False
        return True
    
    def redrawAll(self, screen):
        black = (0,0,0)
        red = (255,0,0)
        blue = (0,0,255)
        white = (255,255,255)
        screen.blit(self.menuBg, (0, 0))
        # The start menu
        if self.me == False and self.aiMode == False:
            fontSize = 50
            font = pygame.font.SysFont(None, fontSize)
            
            # Game name
            text = font.render("Tanks Battle", True, black)
            textRect = text.get_rect()
            textRect.center = (self.width/2, self.first[0][1]-self.buttonH)
            screen.blit(text, textRect)
            
            # Button options
            text1 = font.render("AI", True, self.bgColor)
            textRect1 = text1.get_rect()
            textRect1.center = (self.width/2, self.buttonH/2+self.first[0][1])
            
            text2 = font.render("2 players", True, self.bgColor)
            textRect2 = text2.get_rect()
            textRect2.center = (self.width/2, self.buttonH/2+self.first[1][1])
            
            text3 = font.render("3 players", True, self.bgColor)
            textRect3 = text3.get_rect()
            textRect3.center = (self.width/2, self.buttonH/2+self.first[2][1])
            
            text4 = font.render("4 players", True, self.bgColor)
            textRect4 = text4.get_rect()
            textRect4.center = (self.width/2, self.buttonH/2+self.first[3][1])
            
            # draw buttons and text
            pygame.draw.rect(screen, white, [self.first[0][0], self.first[0][1], self.buttonW, self.buttonH], 5)
            screen.blit(text1, textRect1)
            pygame.draw.rect(screen, white, [self.first[1][0], self.first[1][1], self.buttonW, self.buttonH], 5)
            screen.blit(text2, textRect2)
            pygame.draw.rect(screen, white, [self.first[2][0], self.first[2][1], self.buttonW, self.buttonH], 5)
            screen.blit(text3, textRect3)
            pygame.draw.rect(screen, white, [self.first[3][0], self.first[3][1], self.buttonW, self.buttonH], 5)
            screen.blit(text4, textRect4)
        
        # Drawing and winning stratigy for AI mode
        elif self.aiMode == True:
            pygame.mixer.music.stop()
            screen.blit(self.background, (0, 0))
            self.player.draw(screen, blue)
            self.ai.draw(screen, red)
            for row in self.obs:
                for block in row:
                    if isinstance(block, Block):
                        if isinstance(block, Star):
                            block.draw(screen)
                        else:
                            block.drawBlock(screen)
            # draw bombs
            for bomb in self.bombs:
                bomb.draw(screen)
            for missile in self.missiles:
                missile.draw(screen)
            # draw bullets
            for bullet in self.playerBullets:
                bullet.draw(screen)
            for bullet in self.aiBullets:
                bullet.draw(screen)
            # winning and losing conditions    
            if self.player.health <= 0 or self.ai.health <= 0:
                fontSize = 150
                font = pygame.font.SysFont(None, fontSize)
                backgr = pygame.transform.scale(pygame.image.load("gg.jpg").convert_alpha(), [self.width, self.height])
                screen.blit(backgr, (0,0))
                if self.player.health <= 0:
                    text = font.render("You Lose", True, self.bgColor)
                    textRect = text.get_rect()
                    textRect.center = (self.width/2, self.height/2)
                    screen.blit(text, textRect)
                    
                else:
                    text = font.render("You Win!", True, self.bgColor)
                    textRect = text.get_rect()
                    textRect.center = (self.width/2, self.height/2)
                    screen.blit(text, textRect)
                    
                    
        # Drawing and winning stratigy for multiplayer mode
        elif self.me == True:
            pygame.mixer.music.stop()
            fontSize = 100
            font = pygame.font.SysFont(None, fontSize)
            text = font.render("Connecting...", True, self.bgColor)
            textRect = text.get_rect()
            textRect.center = (self.width/2, self.height/2)
            screen.blit(text, textRect)
            if self.otherConnected():
                screen.blit(self.background, (0, 0))
                # draw blocks. 
                for row in self.obs:
                    for block in row:
                        if isinstance(block, Block):
                            if isinstance(block, Star):
                                block.draw(screen)
                            else:
                                block.drawBlock(screen)
                # draw bombs
                for bomb in self.bombs:
                    bomb.draw(screen)
                for missile in self.missiles:
                    missile.draw(screen)
                # draw other players
                for playerName in self.others:
                    self.others[playerName].draw(screen, blue)
                # draw me
                self.player.draw(screen, red)
                # draw bullets
                for PID in self.otherBullets:
                    for bullet in self.otherBullets[PID]:
                        bullet.draw(screen)
                for bullet in self.playerBullets:
                    bullet.draw(screen)
                    
                # draw ending screen when game is over.
                if self.player.health <= 0 or self.playerWin():
                    fontSize = 150
                    font = pygame.font.SysFont(None, fontSize)
                    backgr = pygame.transform.scale(pygame.image.load("gg.jpg").convert_alpha(), [self.width, self.height])
                    screen.blit(backgr, (0,0))
                    if self.player.health <= 0:
                        text = font.render("You Lose", True, self.bgColor)
                        textRect = text.get_rect()
                        textRect.center = (self.width/2, self.height/2)
                        screen.blit(text, textRect)
                        
                    elif self.playerWin():
                        text = font.render("You Win!", True, self.bgColor)
                        textRect = text.get_rect()
                        textRect.center = (self.width/2, self.height/2)
                        screen.blit(text, textRect)
                       
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=600, height=600, fps=50, title="112 Pygame Game", server=None, serverMsg=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (255, 255, 255)
        self.server = server
        self.serverMsg = serverMsg
        pygame.init()

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()
        
        # call game-specific initialization
        self.init()
        playing = True
        
        pygame.mixer.music.load("Wiser.wav")
        pygame.mixer.music.play(-1)
        
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.update()

        pygame.quit()
        quit()
        
serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()


def main():
    game = PygameGame()
    game.run()

if __name__ == '__main__':
    main()