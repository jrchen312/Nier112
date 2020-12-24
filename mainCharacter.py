#
# This code is used to control the player and run the player's animations. 
#


from cmu_112_graphics import *
import random
import environment
import math
import time
import enemy

#loads images in appStarted
def loadMCImages(self):
    self.image1 = self.loadImage('images/standing.png')
    self.image2 = self.scaleImage(self.image1, 1/5)
    self.mcStandRight = self.scaleImage(self.image1, 1/5)
    self.mcStandLeft = self.mcStandRight.transpose(Image.FLIP_LEFT_RIGHT)

    self.mcDash = self.loadImage('images/dash.png')
    self.mcDashRight = self.scaleImage(self.mcDash, 1/5)
    self.mcDashLeft = self.mcDashRight.transpose(Image.FLIP_LEFT_RIGHT)

    self.mcRight = []
    self.mcLeft = []
    paths = ['images/run1.png', 'images/run2.png', 'images/run3.png', 
            'images/run4.png', 'images/run5.png', 'images/run6.png']
    for path in paths:
        self.temp = self.loadImage(path)
        self.temp = self.scaleImage(self.temp, 1/5)
        self.mcRight.append(self.temp)
        self.temp = self.temp.transpose(Image.FLIP_LEFT_RIGHT)
        self.mcLeft.append(self.temp)
    self.mcMoveCounter = 0

    jumpPath = random.choice(paths)
    temp = self.loadImage(jumpPath)
    self.mcJumpRight = self.scaleImage(temp, 1/5)
    jumpPath = random.choice(paths)
    temp = self.loadImage(jumpPath)
    temp = self.scaleImage(temp, 1/5)
    self.mcJumpLeft = temp.transpose(Image.FLIP_LEFT_RIGHT)


    self.attackLeft = []
    self.mcAttackRight = []
    paths = ['images/attack1.png', 'images/attack2.png', 'images/attack3.png', 
            'images/attack4.png', 'images/attack5.png', 'images/attack6.png']
    for path in paths:
        self.temp = self.loadImage(path)
        self.temp = self.scaleImage(self.temp, 1/5)
        self.attackLeft.append(self.temp)
        self.temp = self.temp.transpose(Image.FLIP_LEFT_RIGHT)
        self.mcAttackRight.append(self.temp)
    self.attackCounter = 0


#Loads the main character attributes in AppStarted
def loadMCAttributes(self):
    #main character attributes
    self.mcX = self.width / 3
    self.mcY = self.height/2 + 100
    self.mcMove = "standRight"
    self.mcDir = "right"
    self.mcIdle = True
    self.mcFrames = -1
    self.mcNewPos = None
    self.mcSpeed = 81 #how far mc moves
    self.mcMovePara = self.mcSpeed/3 #how far mc moves per "tick"
    self.mcFrame = self.mcStandRight
    self.mcDash = False
    self.mcAttacked = True

    self.mcJump = False
    self.mcDoubleJump = False
    self.dy = 0 #   y velocity
    self.ddy = -6#  y acceleration

    #mcX and mcY are temp vars. 
    mcX, mcY = self.mcStandRight.size
    self.mcSize = mcX -36, mcY - 50

    #unused:
    self.dx = 0  #  x velocit8
    self.dxTime = 100   #seconds since last dx velocity measurement
    self.dxI = 2 #      measure velocity over a 2 second period. 

    self.dashCooldown = 3
    self.hackCooldown = 15
    self.lastDash = self.dashCooldown
    self.lastHack = self.hackCooldown

    self.mcHealth = 100
    self.mcMaxHealth = self.mcHealth

    self.xLimit = None


#Manages any kepressed elements that are relevant to the movement of the main character. 
def keyInput(self, event):
    self.mcIdle = False
    self.mcFrames = 3
    if event.key == "Space":
        if self.mcDir == "right":
            self.dx = self.mcSpeed/4
        else:
            self.dx = -self.mcSpeed/4
        if self.mcJump and not self.mcDoubleJump:
            #double jump mechanism
            self.dy = 15
            self.mcDoubleJump = True
        elif self.mcJump and self.mcDoubleJump:
            # we can't jump here.
            return
        self.mcFrames = 4
        self.mcMove = "jump"
        self.dy = 30
        self.mcJump = True
        return
    if event.key == "d":
        self.mcNewPos = (self.mcSpeed, 0)
        self.mcDir = "right"
    elif event.key == "a":
        self.mcNewPos = (-self.mcSpeed, 0)
        self.mcDir = "left"
        #""" Update KeyPressed if use these in the future for some reason.
        # for some reason, game lags a lot when these two keys are removed??
    elif event.key == "s":
        self.mcNewPos = (0, self.mcSpeed)
    elif event.key == "w":
        self.mcNewPos = (0, -self.mcSpeed)
        #"""
    elif event.key == "q":
        if time.time() - self.dashCooldown < self.lastDash:
            self.mcFrames = -1
            self.mcIdle = True
            return
        else:
            timeElapsed = time.time() - self.lastDash
        
        if self.mcDir == "left":
            self.mcNewPos = (-self.mcSpeed, 0)
            self.mcNewPos = checkLegalMcMove(self, 'a', self.mcNewPos)
        else:
            self.mcNewPos = (self.mcSpeed, 0)
            self.mcNewPos = checkLegalMcMove(self, 'd', self.mcNewPos)
        if self.mcNewPos != (-self.mcSpeed, 0) and self.mcNewPos != (self.mcSpeed, 0):
            self.mcFrames = -1
            self.mcIdle = True
        else:
            self.mcNewPos = None
            self.mcMove = "dash"
            self.mcDash = True
            self.lastDash = time.time()
        return
    self.mcMovePara = self.mcSpeed / 3
    self.mcNewPos = checkLegalMcMove(self, event.key, self.mcNewPos)
    

# Checks if the new MC move position is valid based on the self.mcNewPos var
# Takes in the event.key (wasd)
# Modifiesthe self.newPos and self.mcMovePara if an issue is found.
# 
# 
# #to make this work better. instead of using a self.mcNewPos var, just have 
# one of the parameters be a tuple holding the new position. we will return a tuple containing new pos instead. 
def checkLegalMcMove(self, key, mcNewPos):
    dx, dy = mcNewPos
    newX, newY = self.mcX + dx, self.mcY + dy
    mcSize = self.mcSize
    lowDx, lowDy = dx, dy
    currDx, currDy = dx, dy
    for enem in self.enemies:
        enemSize = enem.hitbox
        # used to be 
        adjust =  overlappedImages(self, enemSize, mcSize, enem.x, enem.y, newX, newY, key)
        if adjust != None:
            currDx = dx + adjust[0]
            currDy = dy + adjust[1]
            if abs(currDx + currDy) < abs(lowDx + lowDy):
                lowDx, lowDy = currDx, currDy
    #modifies self.mcMovePara every time
    self.mcMovePara = abs((lowDx + lowDy) / 3)

    #okay. uh so this checks if the mcX is going to be greater than the xLimit.
    if self.xLimit != None and newX > self.xLimit:
        self.mcX = self.xLimit - 1
        lowDx = 0
    #returns a tuple containing values with the highest adjustment
    # (with lowest mc movement)
    return (lowDx, lowDy)
    
# Determines if two images overlap with each other by checking each of the
#   four corners. (helper function)
# Takes in two tuples of the two image sizes, the coordinates of each point,
#   and the key that was pressed (wasd)
# returns an adjustment if there is a problem. 
def overlappedImages(self, imageSize, mcImageSize, x1, y1, x2, y2, key):
    xSize1, ySize1 = imageSize
    xSize2, ySize2 = mcImageSize
    #image one coordinates
    x10 = x1 - xSize1//2 # (x10, y10) is bottom left corner
    x11 = x1 + xSize1//2
    y10 = y1
    y11 = y1 - ySize1    # (x11, y11) is top right corner
    #image2 coordinates
    x20 = x2 - xSize2//2 # (x20, y20) is bottom left corner
    x21 = x2 + xSize2//2
    y20 = y2
    y21 = y2 - ySize2    # (x21, y21) is top right corner

    #checks the corners of the images to see if there is a problem.
    #Also checks the middle of the top edge of the enemy.
    if ((x20 < x10 < x21 and y20 > y11 > y21) or (x20 < x10 < x21 and y20 > y10 > y21) or
        (x20 < x11 < x21 and y20 > y11 > y21) or (x20 < x11 < x21 and y20 > y10 > y21) or
        (x20 < x10 + (x11-x10) / 2 < x21 and y20 > y11 > y21)):
        adjustment = (0,0)
        #If we are moving right:
        if key == "d":
            dist = x21 - x10 + 1
            adjustment = (-dist, 0)
        #if we are moving left:
        elif key == "a":
            dist = x20 - x11 - 1
            adjustment = (-dist, 0)
        #if we are moving down:
        elif key == "w":
            dist = y21 - y10 - 1
            adjustment = (0, -dist)
        #in case we are moving up:
        elif key == 's':
            dist = y20 - y11 + 1
            adjustment = (0, -dist)
        return adjustment
    return None


#gets the picture that needs to be drawn on the screen. Stores the picture
# in self.mcFrame.
def frameSelect(self):
    #attempts to allow for more input buffering for smoother animation
    if self.mcFrames == 1:
        self.mcIdle = True
    #stand still if the animation is finished. 
    if self.mcFrames <= -1:
        self.mcNewPos = None #questionable
        self.mcIdle = True
        self.mcDash = False
        if self.mcDir == "right":
            self.mcMove = "standRight"
            self.mcFrame = self.mcStandRight
        elif self.mcDir == "left":
            self.mcMove = "standLeft"
            self.mcFrame = self.mcStandLeft
    elif self.mcMove == "jump":
        if self.mcDir == "right":
            self.mcFrame = self.mcJumpRight
            #self.mcX += self.mcMovePara//2
        else:
            self.mcFrame = self.mcJumpLeft
            #self.mcX -= self.mcMovePara//2
        #self.mcY -= self.dy
        self.mcFrames -= 1
    #The animation isn't finished, so we need to play an animation!
    else:
        movepara = self.mcMovePara
        #if MC is moving left/down/right/up
        if self.mcNewPos != None:  
            x, y = self.mcNewPos
            
            #if we are at our destination:
            if (-3 < x < 3 and -3 < y < 3):
                self.mcNewPos = None
            # moving right
            elif x > 0:
                x -= movepara
                self.mcX += movepara
                self.mcFrame = self.mcRight[self.mcMoveCounter]
            # moving left
            elif x < 0:
                x += movepara
                self.mcX -= movepara
                self.mcFrame = self.mcLeft[self.mcMoveCounter]
            # moving down
            elif y > 0:
                y -= movepara
                self.mcY += movepara
                if self.mcDir == "right":
                    self.mcFrame = self.mcRight[self.mcMoveCounter]
                else:
                    self.mcFrame = self.mcLeft[self.mcMoveCounter]
            #moving up
            elif y < 0:
                y += movepara
                self.mcY -= movepara
                if self.mcDir == "right":
                    self.mcFrame = self.mcRight[self.mcMoveCounter]
                else:
                    self.mcFrame = self.mcLeft[self.mcMoveCounter]
            #updates self.mcNewPos
            if self.mcNewPos != None:
                self.mcNewPos = x, y
            
            #increments the image counter for the MC moving.
            self.mcMoveCounter = (1 + self.mcMoveCounter) % len(self.mcRight)

        #the character is attacking
        elif self.mcMove == "attack":
            if self.mcDir == "left":
                self.mcFrame = self.attackLeft[self.attackCounter]
            elif self.mcDir == "right":
                self.mcFrame = self.mcAttackRight[self.attackCounter]
            # check if attack hits anything on the first self.mcFrame
            if self.mcAttacked == False and self.mcFrames == 1:
                attackRange = 120
                attackHeight = -60
                if self.mcDir == "left":
                    checkEnemyHit(self, -attackRange, attackHeight)
                else:
                    checkEnemyHit(self, attackRange, attackHeight)
                self.mcAttacked = True
            self.attackCounter = (1 + self.attackCounter) % len(self.attackLeft)

        #Character is dashing
        elif self.mcMove == "dash":
            if self.mcDir == "left":
                self.mcFrame = self.mcDashLeft
                self.mcX -= movepara
            else:
                self.mcFrame = self.mcDashRight
                self.mcX += movepara
        

        self.mcFrames -= 1

def gravity(self, pos):
    newX, newY = 0, 0 #dx, dy
    newY = self.dy #30
    #if -abs(self.ddy) <= self.mcY - pos <= abs(self.ddy):
    #    self.mcY = pos
    if self.mcY < pos or newY > 0:
        self.dy += self.ddy #24
        if self.dy == 0:
            self.dy = self.ddy
        elif self.dy < -30:
            self.dy = -30
        #corrects
        if self.mcMove == "attack":
            newY /= 2
        elif self.mcMove == "dash":
            newY = 0
        
        if self.dy >= -self.ddy: #24 > 6
            newX += self.dx
            if self.mcDoubleJump:
                newX += self.dx/2
        #if the next dy brings the self.mcY location below "pos", make sure it doesn't
        #self.dy is negative
        """
        if self.mcY - self.dy > pos:
            adjust = pos - (self.mcY - self.dy)
            self.dy -= adjust
        """
        if self.mcY - newY > pos: # 680 - -24 > 700
            adjust = pos - (self.mcY - newY)
            newY -= adjust    
        
    elif -abs(self.ddy) <= self.mcY - pos <= abs(self.ddy):
        self.mcY = pos
        self.dy = 0
        self.mcDoubleJump = False
        self.mcJump = False
        newX, newY = 0, 0
    
    if newX > 0: #moving right
        key = "d"
        mcNewPos = (newX, 0)
        result = checkLegalMcMove(self, key, mcNewPos)
        newX, temp = result
    elif newX < 0: # moving left
        key = "a"
        mcNewPos = (newX, 0)
        result = checkLegalMcMove(self, key, mcNewPos)
        newX, tmep = result
    elif newY < 0:  #check if we are on top of an enemy, because we don't want to be inside of somebody. that could be awkward.
        key = "s"
        originalY = newY
        mcNewPos = (0, -newY)
        result = checkLegalMcMove(self, key, mcNewPos)
        temp, yAdjustment = result
        newY = -yAdjustment
        if originalY != -yAdjustment:
            self.mcDoubleJump = False
            self.mcJump = False
            self.mcIdle = True

    self.mcY -= newY
    self.mcX += newX
    

#deducts health from enemies if they are hit.
# Takes in the attackRange/attackHeight of the main character
def checkEnemyHit(self, attackRange, attackHeight):
    #checks if the middle or tip of the sword hits the enemy. 
    x1 = self.mcX + attackRange // 2
    y1 = self.mcY + attackHeight
    x2 = self.mcX + attackRange
    y2 = self.mcY + attackHeight
    for enem in self.enemies:
        xSize, ySize = enem.hitbox
        if (enemy.Enemy.checkIfPointInEnemy([enem], xSize, ySize, x1, y1)
        or enemy.Enemy.checkIfPointInEnemy([enem], xSize, ySize, x2, y2)):
            if enemy.isBoss(self, enem):
                if enem.invulnerable:
                    continue
            enem.health -= 1

def checkInMC(self, x, y, bullet):
    xSize, ySize = self.mcSize
    x10 = self.mcX - xSize//2 # (x0, y0) is bottom left
    x11 = self.mcX + xSize//2
    y10 = self.mcY - 40
    y11 = self.mcY - ySize + 10    # (x1, y1) is top right
    if x10 <= x <= x11 and y11 <= y <= y10:
        if not bullet.ignore:
            if time.time() - self.lastDash < 1:
                bullet.ignore = True
            else:
                self.mcHealth -= 1
                return True
    return False

def checkMeleeInMC(self, x, y):
    xSize, ySize = self.mcSize
    x10 = self.mcX - xSize//2 # (x0, y0) is bottom left
    x11 = self.mcX + xSize//2
    y10 = self.mcY - 40
    y11 = self.mcY - ySize + 10    # (x1, y1) is top right
    if x10 <= x <= x11 and y11 <= y <= y10:
        self.mcHealth -= 2

def getCachedPhotoImage(self, image):
    # stores a cached version of the PhotoImage in the PIL/Pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def drawMC(self, canvas):
    #Draws the main character
    photoImage = getCachedPhotoImage(self, self.mcFrame)
    canvas.create_image(self.mcX, self.mcY, image=photoImage, anchor = "s")
    #canvas.create_image(self.mcX, self.mcY, image=ImageTk.PhotoImage(self.mcFrame), anchor = "s")
    #hitbox
    if self.debug:
        xSize, ySize = self.mcSize
        x10 = self.mcX - xSize//2 # (x0, y0) is bottom left
        x11 = self.mcX + xSize//2
        y10 = self.mcY - 40
        y11 = self.mcY - ySize + 10    # (x1, y1) is top right
        canvas.create_rectangle(x10, y10, x11, y11)
        if self.mcNewPos != None:
            dx, dy = self.mcNewPos
            canvas.create_rectangle(x10 + dx, y10 + dy, x11 + dx, y11 + dy, outline = 'red')
        if self.mcDash:
            canvas.create_text(10, 10, text = "dashing", anchor = 'w')

#code from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    # Don't worry about the :02x part, but for the curious,
    # it says to use hex (base 16) with two digits.
    return f'#{r:02x}{g:02x}{b:02x}'

def drawHealthBar(self, canvas):
    length = 140
    healthColor = rgbString(205, 200, 176)
    beautifulRed = rgbString(205, 102, 77)
    canvas.create_line(50, 50, 50 + length, 50, fill = beautifulRed, width = 9)
    currHealth = (self.mcHealth/self.mcMaxHealth) * length
    canvas.create_line(50, 50, 50 + currHealth, 50, fill = healthColor, width = 9)

    canvas.create_line(50, 60, 50 + length, 60, fill= healthColor, width = 2)


def drawCooldowns(self, canvas):
    boxWidth = 50
    x0 = self.width - boxWidth
    x1 = self.width - boxWidth * 2
    y0 = self.height - boxWidth
    y1 = self.height - boxWidth * 2
    color = rgbString(172, 166, 146) #darker grey peachy color
    textColor = rgbString(250, 247, 230)
    darkGrey = rgbString(60, 57, 51)

    canvas.create_oval(x0, y0, x1, y1, fill=color, width = 3, outline = darkGrey)
    canvas.create_text(x1 + boxWidth//2, y1 + boxWidth//2, text="Q", font = 
                        'arial 30 bold', fill=textColor)
    if time.time() - self.lastDash < self.dashCooldown:
        #canvas.create_rectangle(x0, y0, x1, y1, fill = "grey")
        extent = 360 * (self.dashCooldown-(time.time() - self.lastDash)/self.dashCooldown)
        canvas.create_arc(x0, y0, x1, y1, start=90, width = 0,
                                extent = extent, fill = color, outline=color)
    
    #draw's "E"
    x2 = self.width - boxWidth * 3
    x3 = self.width - boxWidth * 4
    
    canvas.create_oval(x2, y0, x3, y1, fill=color, width = 3, outline = darkGrey)
    canvas.create_text(x3 + boxWidth//2, y1 + boxWidth//2, text="E", font = 
                       "arial 30 bold", fill=textColor)
    if time.time() - self.lastHack < self.hackCooldown:
        extent = 360 * (self.hackCooldown-(time.time() - self.lastHack)/self.hackCooldown)
        canvas.create_arc(x2, y0, x3, y1, start=90, width = 0,
                                extent = extent, fill = color, outline=color)
