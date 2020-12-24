#
# This file contains all of the code for the enemy AI, and changes their animations. 
#


from cmu_112_graphics import *
import random
import math
import time

import environment
import mainCharacter

class Enemy(object):
    def __init__(self, x, y, health, hitbox):
        self.x = x
        self.y = y
        self.health = health
        self.hitbox = hitbox

        self.dy = 0
        self.ddy = -5

    def gravity(self, pos):
        if -abs(self.ddy) <= self.y - pos <= abs(self.ddy):
            self.y = pos
        if self.y < pos:
            self.dy += self.ddy
            self.y -= self.dy
            if self.y - self.dy > pos:
                adjust = pos - (self.y - self.dy)
                self.dy -= adjust
        else:
            self.dy = 0

    
    @staticmethod
    def checkIfPointInEnemy(enemies, xSize, ySize, x, y):
        for enem in enemies:
            x0 = enem.x - xSize//2 # (x0, y0) is bottom left
            x1 = enem.x + xSize//2
            y0 = enem.y
            y1 = enem.y - ySize    # (x1, y1) is top right

            if x0 < x < x1 and y1 < y < y0:
                return True
        return False

    def __repr__(self):
        return f"Enemy at {self.x},{self.y}"


"""
Bipeds are the dumbest of the dumbest (totally because i don't have time)
wait i included that in the final submission LOL
"""
class Biped(Enemy):
    maxHealth = 3
    actions = ["standLeft", "walkLeft", "attackLeft"]
    dirs = ["left"]

    def __init__(self, x, y, health, hitbox):
        super().__init__(x, y, health, hitbox)
        self.attackIndex = 0
        self.walkIndex = 0
        self.dir = "left"
        self.action = "standLeft"
        self.frame = ""
        self.maxHealth = Biped.maxHealth
        self.speed = 12

    def getHealthBar(self):
        health = self.health / Biped.maxHealth
        return health
    
    def getFrame(self, app):
        if self.action == "standLeft":
            self.frame = app.bipedAttack[-1]

        elif self.action == "attackLeft":
            self.frame = app.bipedAttack[self.attackIndex]

        elif self.action == "walkLeft":
            self.frame = app.bipedWalk[self.walkIndex]
        
        self.attackIndex = (self.attackIndex + 1) % (len(app.bipedAttack) - 1)
        self.walkIndex = (self.walkIndex + 1) % (len(app.bipedWalk))

    def setAction(self, app):
        #if character too far away, just afk
        if distance(self.x, self.y, app.mcX, app.mcY) > 700:
            self.action = "standLeft"
            return
        
        #if character is in vision, start attacking if we are close enough to MC.
        if distance(self.x, self.y, app.mcX, app.mcY) <= 100:
            self.action = "attackLeft"

            if self.attackIndex == len(app.bipedAttack) - 2:
                print('attacking')
                xSize, ySize = self.hitbox
                xPos = self.x - xSize//2 - 15
                yPos = self.y - xSize//2
                mainCharacter.checkMeleeInMC(app, xPos, yPos)
            return
        
        #else, we should just run forwards
        self.x -= self.speed
        self.action = "walkLeft"

"""
Bosses are crazy cuz because they have invulnerable phases
where they kinda just you know "sit there" Ehe. And then the go beserk and just
shoot bullets everywhere constantly without pause
"""
class Boss(Enemy):
    maxHealth = 30
    actions = ["standRight", "standLeft", "attackLeft", "attackRight"]
    dirs = ["left", "right"]

    def __init__(self, x, y, health, hitbox):
        super().__init__(x, y, health, hitbox)
        self.invulnerableFrames = 45
        self.invulnerableFrame = 45
        self.vulnerableFrames = 60
        self.vulnerableFrame = 60
        self.attackIndex = 0
        self.dir = "left"
        self.action = "standLeft"
        self.frame = ""
        self.maxHealth = Boss.maxHealth
        self.invulnerable = True
    
    def getFrame(self, app):
        if self.action == "standRight":
            self.frame = app.bossAttackRight[-1]
        elif self.action == "standLeft":
            self.frame = app.bossAttackLeft[-1]

        elif self.action == "attackRight":
            self.frame = app.bossAttackRight[self.attackIndex]
        elif self.action == "attackLeft":
            self.frame = app.bossAttackLeft[self.attackIndex]
        self.attackIndex = (self.attackIndex + 1) % (len(app.bossAttackRight) -1)
    
    def setAction(self, app):
        #if character too far away, just afk
        if distance(self.x, self.y, app.mcX, app.mcY) > 1280:
            self.invulnerableFrame = self.invulnerableFrames
            self.invulnerable = True
            if self.dir == "left":
                self.action = "standLeft"
            else:
                self.action = "standRight"
            return

        #if character is in vision, as we are vulnerable, just afk
        if not self.invulnerable:
            self.vulnerableFrame -= 1
            if self.vulnerableFrame < 0:
                self.vulnerableFrame = self.vulnerableFrames
                self.invulnerable = True
            if self.dir == "left":
                self.action = "standLeft"
            else:
                self.action = "standRight"
            return

        #if the character is in vision, and we are invulnerable, jfktm
        self.invulnerableFrame -= 1
        if self.invulnerableFrame < 0:
            self.invulnerableFrame = self.invulnerableFrames
            self.invulnerable = False
        if self.dir == "left":
            self.action = "attackLeft"
        else:
            self.action = "attackRight"

        if self.attackIndex == len(app.bossAttackRight) - 2:
            if self.dir == "left":
                x = self.x - self.hitbox[0]//2
                y = self.y - self.hitbox[1] * (3/4)
                theta = math.pi/2
            else:
                x = self.x + self.hitbox[0]//2
                y = self.y - self.hitbox[1] * (3/4)
                theta = -1.2
            Boss.createBullets(self, x, y, theta)

    def createBullets(self, x, y, theta):
        speed = 10
        angle = theta
        theta += 2.5
        while angle < theta:
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            Bullet(x, y, dx, dy)
            dtheta = random.randrange(50, 100) / 100
            angle += dtheta
            
        
    #polymorphism xd
    def getHealthBar(self):
        health = self.health / Boss.maxHealth
        return health


"""
Traits:
    Gunners "patrol" the platform that they are on (walk back and forth with some gap)
    When gunners shoot, they stop moving for a second, and then they fire a burst of bullets (red circles radius 25)
        Gunners shoot when the main character is in view, and can shoot an an angle ;)
    when the main character runs at them, gunners will try to "kite backwords" away from you
    If you're on top of them, they do not like that, and will run in a direction

"""
class Gunner(Enemy):
    maxHealth = 2
    walkingFrames = 6
    actions = ["standRight", "standLeft", "walkRight", "walkLeft", "attack"]
    dirs = ["left", "right"]

    def __init__(self, x, y, health, hitbox, patrolLength):
        super().__init__(x, y, health, hitbox)
        self.patrolLength = patrolLength
        self.right = patrolLength
        self.left = patrolLength
        self.speed = 11
        self.standingFrames = 8
        self.animationIndex = 0
        self.dir = random.choice(Gunner.dirs)
        self.action = "standRight" if self.dir == "right" else "standLeft"
        self.frame = ""
        self.attackCoolDown = 3  #attack every few seconds. 
        self.lastAttack = time.time() #time of the last attack
        self.maxHealth = Gunner.maxHealth

        self.eyeHeight = self.y #
        self.leftAttackXY = -self.hitbox[0]//2, -self.hitbox[1]//2 #(-40, -30)
        self.rightAttackXY = self.hitbox[0]//2, -self.hitbox[1]//2
        self.visionRange = 720
        self.tempAngle = 0
        
    def getHealthBar(self):
        health = self.health / Gunner.maxHealth
        return health

    def getFrame(self, leftFrames, rightFrames):
        if self.action == "standRight":
            self.frame = rightFrames[-1]
        elif self.action == "standLeft":
            self.frame = leftFrames[-1]

        elif self.action == "walkRight":
            self.frame = rightFrames[self.animationIndex]
        elif self.action == "walkLeft":
            self.frame = leftFrames[self.animationIndex]
        self.animationIndex = (self.animationIndex + 1) % Gunner.walkingFrames
    
    #given that the conditions are correct, make the robot walk right
    def walkRight(self):
        self.right -= self.speed
        self.left += self.speed
        self.x += self.speed
        self.action = "walkRight"
    
    #given that the conditions are correct, make the robot walk left. 
    def walkLeft(self):
        self.left -= self.speed
        self.right += self.speed
        self.x -= self.speed #could use different mechanism here
        self.action = "walkLeft"
    
    #this is used when the gunner needs to walk left/right. Checks if conditions are valid. 
    def walkerHelper(self):
        #this means we are walking right
        if self.dir == "right":
            if self.right - self.speed > 0:
                Gunner.walkRight(self)
            else:
                self.standingFrames -= 1
                if self.standingFrames >= 0:
                    self.action = "standRight"
                else:
                    self.dir = "left"
                    self.action = "standRight"
                    self.standingFrames = 8
        #walking left:
        elif self.dir == "left":
            if self.left - self.speed > 0:
                Gunner.walkLeft(self)
            else:
                self.standingFrames -= 1
                if self.standingFrames >= 0:
                    self.action = "standLeft"
                else:
                    self.dir = "right"
                    self.action = "standLeft"
                    self.standingFrames = 8


    #sets self.action to something
    def setAction(self, app):

        # shoot from left side (position of the "gun" of robot)
        if app.mcX - self.x < 0:
            x, y = self.leftAttackXY # 
            x, y = self.x + x, self.y + y
        else:
            x, y = self.rightAttackXY 
            x, y = self.x + x, self.y + y
        
        #if mc is not around, idle and walk around the stage. 
        if not Gunner.eyesight(self, app, x, y):  
            Gunner.walkerHelper(self)
        else:

            #if the main character is near the robot:
            if app.mcY == self.y and abs(app.mcX - self.x) < 190:
                
                #if robot needs to run left:
                if app.mcX - self.x > 0:
                    if self.left - self.speed > 0:
                        self.dir = "left"
                        self.action = "walkLeft"
                        Gunner.walkLeft(self)
                        return
                
                #the robot needs to run right:
                elif app.mcX - self.x < 0:
                    if self.right - self.speed > 0:
                        self.dir = "right"
                        self.action = "walkRight"
                        Gunner.walkRight(self)
                        return
                
            #if the attack is not on cooldown
            if time.time() - self.lastAttack > self.attackCoolDown:
                self.lastAttack = time.time()
                #x = self.x
                #y = self.eyeHeight
                angle = self.tempAngle

                #do not shoot if the angle is too high
                
                if abs(angle) > .9:
                    
                    Gunner.walkerHelper(self)
                    return
                
                if self.dir == "right" and angle > 0:
                    angle = -angle

                dx = Bullet.speed * math.cos(angle)
                dy = Bullet.speed * math.sin(angle)
                if self.dir == "left":
                    dx = -dx
                #spawn a new bullet. 
                Gunner.createBullets(self, x, y, dx, dy)

            #The attack is on cooldown
            else:
                if self.dir == "left":
                    self.action = "standLeft"

                elif self.dir == "right":
                    self.action = "standRight"

    #sprays out five bullets. 
    def createBullets(self, x, y, dx, dy):
        modifier = [(0,0),(-10, -8), (10, 10), (10, -10), (-5, 10)]
        for (x0, y0) in modifier:
            Bullet(x+x0, y+y0, dx+x0/7, dy+y0/7)

    def eyesight(self, app, x, y):
        mcSize, mcPos = app.mcSize, (app.mcX, app.mcY)
        #   COORDINATES FOR EYESIGHT FROM ENEMY.
        x1 = x
        y1 = y
        xSize, ySize = mcSize 
        x0, y0 = mcPos[0], mcPos[1] - ySize//2  
        #Calculate Distance between main character and robot. If it exceeds a threshold, return False.
        if distance(x1, y1, x0, y0) > self.visionRange:
            return False
        
        #Calculate the angle between robot and main character. 
        y = y1 - y0
        x = x0 - x1

        #prevents division by zero issues
        if x == 0:
            x = .01
        
        self.tempAngle = math.atan(y/x)

        if x0 < x1 and self.tempAngle > 0:
            #main character at right
            self.dir = "left"
            return True
        
        elif x0 > x1 and self.tempAngle < 0:
            #main character to the left
            self.dir = "right"  #changeable to a high extent
            return True

        #if a platform is blocking vision, return False
        dir = "left" if x0 < x1 else "right"
        if environment.blocked(app, self.tempAngle, x1, y1, dir):
            return False
        self.dir = dir
        return True

#each ranged unit does the same amount of damage per bullet. 
class Bullet(object):
    bullets = []
    speed = 40
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.ignore = False

        #keep track of all the bullets on the screen
        Bullet.bullets.append(self)
    
    def moveBullets(self):
        self.x += dx
        self.y += dy
    
    @staticmethod
    def removeOffscreenBullets(app):
         i = 0
         while i < len(Bullet.bullets):
            bullet = Bullet.bullets[i]
            if (bullet.x < 0 or bullet.x > app.width or bullet.y < 0 or 
                bullet.y > app.height):
                Bullet.bullets.pop(i)
            else:
                i += 1

def distance(x0, y0, x1, y1):
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

# initializes appstarted variables. loads a bunch of images. 
def createStubbies(self, number):

    self.gunnerLeft = []
    self.gunnerRight = []
    paths = ['images/gunnerWalk0.png', 'images/gunnerWalk1.png', 'images/gunnerWalk2.png', 
             'images/gunnerWalk3.png', 'images/gunnerWalk4.png', 'images/gunnerWalk5.png',
             'images/gunner.png']
    for path in paths:
        self.temp = self.loadImage(path)
        self.gunnerLeft.append(self.temp)
        self.temp = self.temp.transpose(Image.FLIP_LEFT_RIGHT)
        self.gunnerRight.append(self.temp)
    
    self.bipedWalk = []
    paths = ['images/bipedWalk0.png', 'images/bipedWalk1.png', 'images/bipedWalk2.png', 
             'images/bipedWalk3.png', 'images/bipedWalk4.png', 'images/bipedWalk5.png',
             'images/bipedWalk6.png']
    
    for path in paths:
        self.temp = self.loadImage(path)
        self.temp = self.scaleImage(self.temp, 1/2)
        self.bipedWalk.append(self.temp)
    
    self.bipedAttack = []
    paths = ['images/bipedAttack1.png', 'images/bipedAttack2.png', 'images/bipedAttack3.png', 'images/bipedAttack3.png',
             'images/bipedAttack4.png', 'images/bipedAttack4.png', 'images/bipedAttack5.png', 'images/bipedAttack5.png', 
             'images/bipedWalk0.png']
    
    for path in paths:
        self.temp = self.loadImage(path)
        self.temp = self.scaleImage(self.temp, 1/2)
        self.bipedAttack.append(self.temp)
        

    self.bossAttackLeft = []
    self.bossAttackRight = []
    paths = ['images/bossAttack1.png', 'images/bossAttack2.png', 'images/bossAttack3.png', 'images/bossStand.png']
    for path in paths:
        self.temp = self.loadImage(path)
        self.bossAttackRight.append(self.temp)
        self.temp = self.temp.transpose(Image.FLIP_LEFT_RIGHT)
        self.bossAttackLeft.append(self.temp)

    self.enemies = []


def spawnGunner(self, x, y, patrolLength):
    self.enemies.append(Gunner(x, y, Gunner.maxHealth, self.gunnerLeft[-1].size, patrolLength))

def spawnBoss(self, x, y):
    self.enemies.append(Boss(x, y, Boss.maxHealth, self.bossAttackRight[-1].size))

def spawnBiped(self, x, y):
    xSize, ySize = self.bipedAttack[-1].size
    ySize -= 20
    xSize = 82
    self.enemies.append(Biped(x, y, Biped.maxHealth, (xSize, ySize)))

def setAction(self):
    for enem in self.enemies:
        if isinstance(enem, Gunner):
            enem.setAction(self)
        elif isinstance(enem, Boss):
            enem.setAction(self)
        elif isinstance(enem, Biped):
            enem.setAction(self)

def frameSelect(self):
    for enem in self.enemies:
        if isinstance(enem, Gunner):
            enem.getFrame(self.gunnerLeft, self.gunnerRight)
        else:
            enem.getFrame(self)
    
def isBoss(self, enemy):
    if isinstance(enemy, Boss):
        return True
    return False

def clearBullets():
    Bullet.bullets = []

def removeOffScreenBullets(self):
    Bullet.removeOffscreenBullets(self)

#removes enemies if their health is below 0
def removeDeadEnemies(self):
    score = 0
    i = 0
    while i < len(self.enemies):
        enem = self.enemies[i]
        if enem.health <= 0 or enem.y >= self.height + 400:
            self.enemies.pop(i)
            if isinstance(enem, Gunner):
                score += 5
            elif isinstance(enem, Biped):
                score += 3
            else:
                score += 2
            if isinstance(enem, Boss):
                self.gameOver = True
                self.bossKilled = True
        else:
            i += 1

    return score

def gravity(self, deviation):
    
    for enem in self.enemies:
        pos = environment.getPosition(self, enem.x + deviation, enem.y)
        enem.gravity(pos)

def shiftEnemies(self, deviation):
    shift = deviation
    for enem in self.enemies:
        enem.x -= shift
    
    for bullet in Bullet.bullets:
        bullet.x -= shift

def updateBullets(self):
    i = 0
    while i < len(Bullet.bullets):
        bullet = Bullet.bullets[i]

        bullet.x += bullet.dx
        bullet.y += bullet.dy
        if mainCharacter.checkInMC(self, bullet.x, bullet.y, bullet):
            Bullet.bullets.pop(i)
        else:
            i += 1



def inHackRange(self, range):
    closestDist = range
    enemy = None
    for enem in self.enemies:
        if isinstance(enem, Boss):
            if enem.invulnerable:
                continue
        dist = distance(self.mcX, self.mcY, enem.x, enem.y)
        if dist <= closestDist:
            closestDist = dist
            enemy = enem

    if enemy != None:
        return enemy
    return None


def getCachedPhotoImage(self, image):
    # stores a cached version of the PhotoImage in the PIL/Pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def enemOnScreen(self, enemy):
    if -240 < enemy.x < self.width + 250:
        return True
    return False

def drawEnemies(self, canvas):

    for enem in self.enemies:
        xSize, ySize = enem.hitbox
        if enem.frame != "" and enemOnScreen(self, enem):
            photoImage = getCachedPhotoImage(self, enem.frame)
            canvas.create_image(enem.x, enem.y, image=photoImage, anchor = "s")
            #canvas.create_image(enem.x, enem.y, image=ImageTk.PhotoImage(enem.frame), anchor = "s")
        
        if enem.health != enem.maxHealth:
            green = enem.getHealthBar()
            rectWidth = 50
            canvas.create_rectangle(enem.x-25, enem.y - ySize - 5, 
                                    enem.x + 25, enem.y - ySize-13, 
                                    fill = "red")
            canvas.create_rectangle(enem.x-25, enem.y - ySize - 5, 
                                    enem.x - 25 + green*rectWidth, 
                                    enem.y - ySize-13, fill = "green")
        
        #hitbox
        if self.debug: 
            x10 = enem.x - xSize//2 # (x0, y0) is bottom left
            x11 = enem.x + xSize//2
            y10 = enem.y
            y11 = enem.y - ySize    # (x1, y1) is top right
            canvas.create_rectangle(x10, y10, x11, y11)
        
            #draws the line of sight for gunners (change this)
            if isinstance(enem, Gunner):
                #x, y = enem.eyesight()
                x = enem.x
                y = enem.eyeHeight
                canvas.create_line(self.mcX, self.mcY - self.mcSize[1] /2, x, y)
                canvas.create_text(x + 30, y, text=f"{enem.tempAngle}")


def drawBullets(self, canvas):
    r = 14
    for bullet in Bullet.bullets:
        canvas.create_oval(bullet.x-r, bullet.y-r, bullet.x+r, bullet.y+r, 
                           fill='red')