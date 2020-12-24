#
# Main file, runs CMU 112 graphics. 
#

"""
TP2:
more complex map generation, ai for enemies to attack player, boss w/ minigame

TP3:
fix boss
improve user interface
game longer

"""
# Uses cmu_112_graphics from 
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
from cmu_112_graphics import *
import random
import math
import time
import pygame
import mainCharacter
import environment
import enemy
import hacking
import splashScreen
import copy

pygame.mixer.init()
    
class MyApp(App):
    def appStarted(self):
        self.defaultTimerDelay = 70
        self.timerDelay = self.defaultTimerDelay
        pygame.mixer.music.load("audio/cityRuins.mp3")
        pygame.mixer.music.play(-1) #loop forever. 
        
        MyApp.restartApp(self)
        
    
    def restartApp(self):
        mainCharacter.loadMCImages(self)
        
        enemy.createStubbies(self, 1)
        environment.loadStage(self)
        mainCharacter.loadMCAttributes(self)

        self.debug = False
        self.camPos = self.width // 3
        self.defaultPos = self.width // 3
        self.deviation = 0

        self.score = 0
        self.gameOver = False
        self.bossKilled = False

        self.hackRange = self.width//2
        self.hacking = False
        self.hackedEnemy = None
        self.hackingAnimationFrames = 4
        enemy.clearBullets()

        splashScreen.initializeSplashScreen(self)
        self.splashScreen = True
    
    """
    Character Movement Notes:
    - jump, double jump (4) (jump1, jump2)
    """
    ###########################################################################
    # User input
    ###########################################################################
    def mousePressed(self, event):
        if self.splashScreen:
            splashScreen.mousePressed(self, event)
            #
        elif self.mcIdle or self.mcMove == "jump":
            self.mcIdle = False
            self.mcAttacked = False
            self.mcFrames = len(self.attackLeft) - 1
            self.mcMove = "attack"
            self.attackCounter = 0

    def keyPressed(self, event):
        if self.gameOver:
            MyApp.restartApp(self)
            return
        if self.splashScreen:
            splashScreen.keyPressed(self, event)
            return
        
        if not self.hacking:
            #issue: one problem is that the player cannot hold a key down, which is bad gameplay. 
            if self.mcIdle and (event.key in "asdq" or event.key == "Space") and not self.mcDash:
                mainCharacter.keyInput(self, event)
            elif event.key == 'r':
                MyApp.restartApp(self)
            elif event.key == "Escape":
                self.debug = not self.debug
            #change to incorporate the cooldown.
            elif event.key == "e":
                #do not hack if hacking is on cd.
                if time.time() - self.hackCooldown < self.lastHack:
                    return
                self.hackedEnemy = enemy.inHackRange(self, self.hackRange)
                if self.hackedEnemy != None:
                    self.hacking = True
                    self.timerDelay = 200
                    #hacking.hackingAppStarted(self)
        #hacking
        elif self.hacking and not self.hackingAnimationFrames > 0:
            hacking.keyPressed(self, event)
    
    def mouseMoved(self, event):
        if self.splashScreen:
            splashScreen.mouseMoved(self, event)
        elif self.hacking and not self.hackingAnimationFrames > 0:
            hacking.mouseMoved(self, event)

    ###########################################################################
    def timerFired(self):
        if self.hacking:
            if MyApp.hackingTimerFired(self):
                return

        if self.splashScreen:
            return
        #we are not hacking, display the actual game:
        mainCharacter.frameSelect(self)
        self.score += enemy.removeDeadEnemies(self)


        self.deviation = self.camPos - self.defaultPos
        pos = environment.getPosition(self, self.mcX + self.deviation, self.mcY)
        mainCharacter.gravity(self, pos)
        enemy.gravity(self, self.deviation)
        enemy.setAction(self)
        enemy.frameSelect(self)
        enemy.updateBullets(self)
        enemy.removeOffScreenBullets(self)
        MyApp.updateCamPos(self)
        MyApp.checkGameover(self)

        environment.generateNewTerrain(self, self.deviation)
    
    def hackingTimerFired(self):
        if self.hacking:
            if self.hackingAnimationFrames > 0:
                self.hackingAnimationFrames -= 1
                if self.hackingAnimationFrames == 0:

                    hacking.hackingAppStarted(self)
                #(still need to play animation)
                return False

            result = hacking.timerFired(self)
            #Checks if hacking is over or not:
            if result != None:
                #if we won the hacking
                if result == True:
                    enem = self.hackedEnemy
                    enem.health -= 25
                #lost 
                else:
                    self.mcHealth -= 20
                self.hacking = False
                self.timerDelay = self.defaultTimerDelay
                self.hackingAnimationFrames = 4
                #put the skill on cooldown
                self.lastHack = time.time()
            #(skip rest of the timerFired)
            return True
        #(we aren't hacking)
        return False


    def checkGameover(self):
        if self.mcY > self.height + 400:
            self.mcHealth = 0
            self.gameOver = True
        if self.mcHealth <= 0:
            self.gameOver = True
        
        if self.gameOver and not self.read:
            self.read = True
            splashScreen.leaderboardValues(self)

    #camera mechanism is somewhat similar to cs.cmu.edu/~112/notes/notes-animations-part3.html#sidescrollerExamples
    # (sideScroller1)
    def updateCamPos(self):
        deviation = self.mcX - self.defaultPos
        self.camPos += deviation
        self.mcX = self.defaultPos
        
        enemy.shiftEnemies(self, deviation)
        if self.xLimit != None:
            self.xLimit -= deviation


    
    ###########################################################################
    def redrawAll(self, canvas):
        if self.splashScreen:
            splashScreen.drawSplashScreen(self, canvas)
            return
        if self.hacking:
            if self.hackingAnimationFrames > 0:
                pass
            else:
                hacking.redrawAll(self, canvas)
                return
        
        environment.drawBackground(self, canvas, self.defaultPos, self.camPos)
        enemy.drawEnemies(self, canvas)
        enemy.drawBullets(self, canvas)
        mainCharacter.drawMC(self, canvas)
        mainCharacter.drawCooldowns(self, canvas)
        mainCharacter.drawHealthBar(self, canvas)
        MyApp.drawScore(self, canvas)
        MyApp.drawGameOver(self, canvas)
        if self.hackingAnimationFrames > 0 and self.hacking:
            MyApp.drawTether(self, canvas)
    
    def drawTether(self, canvas):
        enem = self.hackedEnemy
        x0 = self.mcX
        y0 = self.mcY - self.mcSize[1] // 2
        x1 = enem.x
        y1 = enem.y - enem.hitbox[1] // 2
        thiccness = (4 - self.hackingAnimationFrames) * 2
        canvas.create_line(x0, y0, x1, y1, fill = "red", width = thiccness)

    def drawScore(self, canvas):
        canvas.create_text(self.width - 50, 50, text=f"Score: {self.score}", anchor = "e",
                            font = "arial 16 bold", fill = "white")

    def drawGameOver(self, canvas):
        if self.gameOver:
            canvas.create_rectangle(0, self.height/3, self.width, self.height/(3/2), 
                            fill="tan")
            canvas.create_text(self.width//2, self.height//2, fill="white",
                            text="Game Over", font="arial 20 bold")
            canvas.create_text(self.width//2, self.height//2 + 30, fill = "white",
                       text = "Press any key to continue", 
                       font = "arial 15 bold")
            if self.bossKilled:
                canvas.create_text(self.width//2, self.height//2 + 55, fill="white",
                                text="You Win!", font="arial 16 bold")
                canvas.create_text(self.width//2, self.height//2 + 80, fill = "white",
                                text=f"Score: {self.score}", font = "arial 14 bold")

MyApp(width=1280, height=720)
