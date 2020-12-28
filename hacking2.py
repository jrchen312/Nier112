#hacking game v2

#The complexity presented matches that of a term project for 15-112.
#Though there may need to be a few more features to flush it out.
#   such as more mobs! or something idk


"""

"""
from cmu_112_graphics import *
import random
import math
import time
from queue import PriorityQueue

class LargeBox(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = "black"
    
    def __repr__(self):
        return f"box at ({self.row}, {self.col})"

class SmallBox(object):
    def __init__(self, row, col, barrier):
        self.row = row
        self.col = col
        self.barrier = barrier

        self.successors = []

        self.isOpen = False
        self.isClosed = False

        self.isStart = False
        self.isEnd = False

        self.isPath = False
    
    def getPos(self):
        return self.row, self.col
    
    def isBarrier(self):
        return self.barrier
    
    def makeOpen(self):
        self.isOpen = True
        self.isClosed = False

    def makeClosed(self):
        self.isClosed = True
        self.isOpen = False

    def makeStart(self):
        self.isStart = True
    
    def makeEnd(self):
        self.isEnd = True
    
    def makePath(self):
        self.isPath = True
    
    def reset(self):
        self.isPath = False

    def updateSuccessors(self, app):
        self.successors = []
        for (dx, dy) in [(+1,0), (-1,0), (0,+1), (0,-1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            row, col = self.row + dx, self.col + dy
            if inBounds(app, row, col) and not app.smallBoxGrid[row][col].isBarrier() and onlyOneNeighbor(app, row, col):
                self.successors.append(app.smallBoxGrid[row][col])
    
    def __lt__(self, other):
        return False
    
    def __repr__(self):
        return f"({self.row}, {self.col})"

def onlyOneNeighbor(app, row, col):
    if (abs(row) + abs(col)) < 2:
        return True
    num = 0
    for (dx, dy) in [(+1,0), (-1,0), (0,+1), (0,-1)]:
        newRow, newCol = row + dx, col + dy
        if inBounds(app, newRow, newCol):
            box = app.smallBoxGrid[newRow][newCol]
            if box.isBarrier():
                num += 1
    return True if num <= 1 else False

def inBounds(self, row, col):
    rows, cols = len(self.smallBoxGrid), len(self.smallBoxGrid[0])
    if row < 0 or row >= rows or col < 0 or col >= cols:
        return False
    return True

def h(p1, p2):
    x0, y0 = p1
    x1, y1 = p2
    #return distance(x0, y0, x1, y1)
    return max(abs(x0-x1), abs(y1-y0))

"""
vars needed
self.smallBoxGrid  (contains all of the SmallBox objects)
"""
def aStar(self, start, end):
    if self.debug:
        removePathAttribute(self)

    grid = self.smallBoxGrid
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {SmallBox: float("inf") for row in grid for SmallBox in row}
    gScore[start] = 0
    fScore = {SmallBox: float("inf") for row in grid for SmallBox in row}
    fScore[start] = h(start.getPos(), end.getPos())

    openSetHash = {start}

    while not openSet.empty():
        current = openSet.get()[2] #this is the current SmallBox that we are looking at
        openSetHash.remove(current)

        if current == end:
            #reconstruct path. this should probably be a toggle or something so we can draw it in redrawAll. or the function retraces out the path or something idk. 
            reconstructPath(self, cameFrom, end)
            return True
        
        for successor in current.successors:
            tempG = gScore[current] + 1

            if tempG < gScore[successor]: 
                cameFrom[successor] = current
                gScore[successor] = tempG
                fScore[successor] = tempG + h(successor.getPos(), end.getPos())
                if successor not in openSetHash:
                    count += 1
                    openSet.put((fScore[successor], count, successor))
                    openSetHash.add(successor)
                    successor.makeOpen()

        if current != start:
            current.makeClosed()
    return False

def reconstructPath(self, cameFrom, current):
    while current in cameFrom:
        current = cameFrom[current]
        current.makePath()
        self.reconstructedPath.append(current)
    
#only use in debug mode, as this is n^2 efficiency on a 60 long grid. 
def removePathAttribute(self):
    rows, cols = len(self.smallBoxGrid), len(self.smallBoxGrid[0])
    for row in range(rows):
        for col in range(cols):
            box = self.smallBoxGrid[row][col]
            box.reset()

class PointerBullet(object):
    def __init__(self, x, y, dx, dy, angle):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = angle
    
    def getPos(self):
        return self.x, self.y

    def __repr__(self):
        return f"bullet: {self.x}, {self.y}"

class Enemy(object):
    def __init__(self, row, col, health):
        self.row = row
        self.col = col
        self.health = health

        self.unUpdatedAngle = True
        self.agro = False
        self.angle = math.pi/2

        self.justHit = False
        self.justHitFrame = 0
        self.justHitFrames = 2
    
    def draw(self, app, canvas):
        x0, y0, x1, y1 = getSCellBounds(app, self.row, self.col)
        canvas.create_rectangle(x0, y0, x1, y1, fill = "red")

    def isDead(self):
        return True if self.health <= 0 else False
    
    def pointInEnemy(self, app, x, y):
        return False 
    
    def updateAngle(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) > Shooter.tooFar and not self.unUpdatedAngle and not self.agro:
            return
        self.unUpdatedAngle = False
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        x0, y0 = getPointerXY(app)

        yDif = y0 - y
        xDif = x - x0
        try:
            newAngle = math.atan(yDif/xDif)
        except:
            newAngle = math.atan(-yDif/.01)
        if xDif > 0:
            newAngle = newAngle + math.pi
        self.angle = newAngle 
    
    def pathFind(self, app):
        #def pathFind(self, app):
        if time.time() - self.lastSearch > self.searchTime:
            self.found = False
            self.lastSearch = time.time()
        if not self.found:
            #variable (changes every run)
            start = app.smallBoxGrid[self.row][self.col]
            start.makeStart()
            end = app.smallBoxGrid[app.pointerRow][app.pointerCol]
            end.makeEnd()
            app.reconstructedPath = []
            if not aStar(app, start, end):
                print("didn't work ")
            self.path = (app.reconstructedPath)
            self.path.reverse()
            self.found = True

    def subtractHealth(self):
        self.health -= 1
        self.justHit = True
        self.justHitFrame = self.justHitFrames
    
    def checkJustHit(self):
        if self.justHit:
            self.justHitFrame -= 1
            if self.justHitFrame < 0:
                self.justHit = False

    def fire(self, app):
        pass

class Core(Enemy):
    #maximum health 
    maxHealth = 3
    radius = 23
    bulletSpeed = 10
    angleDx = math.pi/44  #higher denominator: slower rotation

    def __init__(self, row, col):
        super().__init__(row, col, Core.maxHealth)
        self.shielded = True

        self.path = []
        self.found = False

        self.lastSearch = 0
        self.searchTime = 2
        self.moveFrame = 0
        self.moveFrames = 9  #higher is slower

        self.unUpdatedAngle = True
        self.fireRate = 5   #higher is slower. 
        self.fireFrame = 0
        self.agro = False
    
    def draw(self, app, canvas):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Core.radius
        whiteBox = rgbString(223, 217, 205)
        blackBox = "grey"
        color = whiteBox if self.justHit else blackBox
        canvas.create_oval(x-r, y-r, x+r, y+r, fill = color, width = 0)

        if self.shielded:
            r += 4
            canvas.create_oval(x-r, y-r, x+r, y+r, width = 2)
            r += 4
            canvas.create_oval(x-r, y-r, x+r, y+r, width = 2)


    def pointInEnemy(self, app, xx, yy):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r1 = Core.radius
        if distance(x, y, xx, yy) < r1:
            return True
        return False
    
    def subtractHealth(self):
        if self.shielded:
            pass
        else:
            self.health -= 1

    def updateAngle(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if not self.unUpdatedAngle:
            return
        self.unUpdatedAngle = False
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        x0, y0 = getPointerXY(app)

        yDif = y0 - y
        xDif = x - x0
        try:
            newAngle = math.atan(yDif/xDif)
        except:
            newAngle = math.atan(-yDif/.01)
        if xDif > 0:
            newAngle = newAngle + math.pi
        self.angle = newAngle 

    #TODO: CHANGE THE KILLERiNSTICT AND TOOfAR VARIABLES TO SOMETHING MORE FAIR.
    def move(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) < Shooter.killerInstinct:
            return
        elif distance(pRow, pCol, self.row, self.col) > Shooter.tooFar and not self.agro:
            return
        
        self.agro = True
        self.moveFrame = (self.moveFrame + 1) % self.moveFrames

        if self.moveFrame == 0 and self.path != None and len(self.path) > 0:
            smallBox = self.path[0]
            newRow, newCol = smallBox.getPos()
            self.path.pop(0)
            self.row, self.col = newRow, newCol

    def fire(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) < Shooter.tooFar or self.agro:
            #can fire
            self.fireFrame = (self.fireFrame+1) % self.fireRate
            if self.fireFrame == 0:
                Core.createBullets(self, app)
                self.angle += Core.angleDx
            return

    def createBullets(self, app):
        x0, y0, x1, y1 = getSCellBounds(app, self.row, self.col)
        x = x0 + app.sSize//2
        y = y0 + app.sSize//2

        angle = self.angle
        r2 = Core.radius

        dAngles = [0, -math.pi/4, math.pi/4]
        if app.numEnemies >= 4:
            dAngles = [0, -math.pi/4, math.pi/4, math.pi/2, -math.pi/2]
        for dTheta in dAngles:
            newAngle = angle + dTheta
            dirX = x + r2 * math.cos(newAngle)
            dirY = y - r2 * math.sin(newAngle)
            dx = Core.bulletSpeed * math.cos(newAngle)
            dy = Core.bulletSpeed * math.sin(newAngle)
            bullet = PointerBullet(dirX, dirY, dx, dy, newAngle)
            app.enemyBullets.append(bullet)

class Cylinder(Enemy):
    maxHealth = 3
    size = 18
    tooFar = 50
    bulletSpeed = 14
    fireRate = 25
    shieldSize = [-math.pi/4, math.pi/4]

    def __init__(self, row, col):
        super().__init__(row, col, Cylinder.maxHealth)
        self.path = []
        self.found = False

        self.fireRate = Cylinder.fireRate
        self.fireFrame = 0

        self.angles = []   # last in first out system for keeping track of the number of angles
        self.angleNum = 40 # 40   # use the angle n frames measured ago. 

        self.shielded = True

    def pointInEnemy(self, app, xx, yy):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r1 = Cylinder.size

        if self.shielded:
            try:
                theta = self.angles[0]
            except:
                theta = 3 * math.pi/2
            r10 = app.bulletSpeed/2 + 5
            x10 = x + r1 * math.cos(theta)
            y10 = y - r1 * math.sin(theta)
            if distance(xx, yy, x10, y10) < r10:
                return None

        if distance(x, y, xx, yy) < r1:
            return True
        return False
    
    def draw(self, app, canvas):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Cylinder.size
        whiteBox = rgbString(223, 217, 205)
        blackBox = rgbString(58, 56, 50)
        color = whiteBox if self.justHit else blackBox
        canvas.create_oval(x-r, y-r, x+r, y+r, fill = color, width = 0)

        #draw a shield thing if we are shielded 
        if self.shielded:
            try:
                theta = self.angles[0]
            except:
                theta = 3 * math.pi/2
            r = Cylinder.size
            #where the shield is looking at (should lag behind a tiny bit)
            r0 = r * 1.4
            x0 = x + r0 * math.cos(theta)
            y0 = y - r0 * math.sin(theta)

            x1, y1, x2, y2, x3, y3, x4, y4 = Cylinder.getHitbox(self, app)

            canvas.create_polygon(x0, y0, x1, y1, x2, y2, x0, y0, fill = "white", width = 0)

            r10 = app.bulletSpeed/2
            x10 = x + r * math.cos(theta)
            y10 = y - r * math.sin(theta)

            #draws the triangle on the opposite side. 
            """
            theta = theta + math.pi
            r0 = r * 1.4
            x0 = x + r0 * math.cos(theta)
            y0 = y - r0 * math.sin(theta)
            x1, y1, x2, y2 = Cylinder.getOppositeTriangle(self, app)
            canvas.create_polygon(x0, y0, x1, y1, x2, y2, x0, y0, fill = "white", width = 0)
            """

            #hitbox:
            #canvas.create_oval(x10- r10, y10 - r10, x10+r10, y10+r10, fill = "red", width = 0)

            #old hitbox:
            #canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill = "red")
            #direction looking in:
            #canvas.create_line(x, y, x0, y0, fill = "red", width = 3)
    def getOppositeTriangle(self, app):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Cylinder.size
        try:
            theta = self.angles[0] + math.pi
        except:
            theta = 3 * math.pi/2 + math.pi
        dtheta1 = Cylinder.shieldSize[0]
        dtheta2 = Cylinder.shieldSize[1]
        theta1 = theta + dtheta1
        theta2 = theta + dtheta2

        x1 = x + r * math.cos(theta1)
        y1 = y - r * math.sin(theta1)
        x2 = x + r * math.cos(theta2)
        y2 = y - r * math.sin(theta2)
        return x1, y1, x2, y2

    def getHitbox(self, app):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Cylinder.size
        try:
            theta = self.angles[0]
        except:
            theta = 3 * math.pi/2
        dtheta1 = Cylinder.shieldSize[0]
        dtheta2 = Cylinder.shieldSize[1]

        theta1 = theta + dtheta1
        theta2 = theta + dtheta2

        x1 = x + r * math.cos(theta1)
        y1 = y - r * math.sin(theta1)
        x2 = x + r * math.cos(theta2)
        y2 = y - r * math.sin(theta2)

        #hitbox for the shield:
        r3 = app.bulletSpeed
        dx3 = r3 * math.cos(theta)
        dy3 =  - r3 * math.sin(theta)
        x3 = x2 + dx3
        y3 = y2 + dy3
        x4 = x1 + dx3
        y4 = y1 + dy3

        return x1, y1, x2, y2, x3, y3, x4, y4


    #does not move
    def move(self, app):
        pass

    #and thus does not need to have any pathfinding or anything xD
    def pathFind(self, app):
        pass

    def fire(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) < Cylinder.tooFar:
            #can fire
            self.fireFrame = (self.fireFrame+1) % self.fireRate
            if self.fireFrame == 0:
                Cylinder.createBullets(self, app)

    def createBullets(self, app):
        x0, y0, x1, y1 = getSCellBounds(app, self.row, self.col)
        x = x0 + app.sSize//2
        y = y0 + app.sSize//2

        angle = self.angle
        r2 = Cylinder.size
    
        dThetas = [0, math.pi/2, math.pi, 3*math.pi/2]

        for dTheta in dThetas:
            newAngle = angle + dTheta
            dirX = x + r2 * math.cos(newAngle)
            dirY = y - r2 * math.sin(newAngle)
            dx = Cylinder.bulletSpeed * math.cos(newAngle)
            dy = Cylinder.bulletSpeed * math.sin(newAngle)
            bullet = PointerBullet(dirX, dirY, dx, dy, newAngle)
            app.enemyBullets.append(bullet)

    def updateAngle(self, app):
        #this can be tweaked a lot for balance. 
        #if self.fireFrame == self.fireRate - 5:

        pRow, pCol = app.pointerRow, app.pointerCol
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        x0, y0 = getPointerXY(app)

        yDif = y0 - y
        xDif = x - x0
        try:
            newAngle = math.atan(yDif/xDif)
        except:
            newAngle = math.atan(-yDif/.01)
        if xDif > 0:
            newAngle = newAngle + math.pi
        self.angle = newAngle 
        self.angles.append(newAngle)

        while len(self.angles) > self.angleNum:
            self.angles.pop(0)

class Shooter(Enemy):
    #maximum health
    maxHealth = 2
    size = 20
    killerInstinct = 20 #stops moving at this distance. 
    tooFar = 40  #max range
    bulletSpeed = 8

    def __init__(self, row, col):
        super().__init__(row, col, Shooter.maxHealth)
        self.path = []
        self.found = False

        self.lastSearch = 0
        self.searchTime = 1.5
        self.moveFrame = 0
        self.moveFrames = 4
        
        self.fireRate = 20
        self.fireFrame = 0
    
    #Checks if a X (xx) and Y (yy) are in the shooter or not. 
    def pointInEnemy(self, app, xx, yy):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Shooter.size
        r1 = r * .8
        if distance(x, y, xx, yy) < r1:
            return True
        return False

    def move(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) < Shooter.killerInstinct:
            return
        elif distance(pRow, pCol, self.row, self.col) > Shooter.tooFar and not self.agro:
            return
        
        self.agro = True
        self.moveFrame = (self.moveFrame + 1) % self.moveFrames

        if self.moveFrame == 0 and self.path != None and len(self.path) > 0:
            smallBox = self.path[0]
            newRow, newCol = smallBox.getPos()
            self.path.pop(0)
            self.row, self.col = newRow, newCol


    def fire(self, app):
        pRow, pCol = app.pointerRow, app.pointerCol
        if distance(pRow, pCol, self.row, self.col) < Shooter.tooFar or self.agro:
            #can fire
            self.fireFrame = (self.fireFrame+1) % self.fireRate
            if self.fireFrame == 0:
                Shooter.createBullet(self, app)

    def createBullet(self, app):
        x0, y0, x1, y1 = getSCellBounds(app, self.row, self.col)
        x = x0 + app.sSize//2
        y = y0 + app.sSize//2

        angle = self.angle
        r2 = Shooter.size

        dirX = x + r2 * math.cos(angle)
        dirY = y - r2 * math.sin(angle)
        dx = Shooter.bulletSpeed * math.cos(angle)
        dy = Shooter.bulletSpeed * math.sin(angle)
        bullet = PointerBullet(dirX, dirY, dx, dy, angle)
        app.enemyBullets.append(bullet)

    def draw(self, app, canvas):
        x0, y0, x1, y1  = getSCellBounds(app, self.row, self.col)
        x, y = x0 + app.sSize//2, y0 + app.sSize//2
        r = Shooter.size
        theta = self.angle
        r1 = r * .8
        #this is the hitbox
        #canvas.create_oval(x-r1, y-r1, x+r1, y+r1, fill = "red", width = 0)

        #where the shooter is looking at
        r0 = r * 1.4
        x0 = x + r0 * math.cos(theta)
        y0 = y - r0 * math.sin(theta)
        
        #first edge:
        theta1 = theta + math.pi/4
        x1 = x + r * math.cos(theta1)
        y1 = y - r * math.sin(theta1)

        #second edge:
        theta2 = theta1 + math.pi/2
        x2 = x + r * math.cos(theta2)
        y2 = y - r * math.sin(theta2)

        #third edge:
        theta3 = theta2 + math.pi/2
        x3 = x + r * math.cos(theta3)
        y3 = y - r * math.sin(theta3)

        #fourth edge:
        theta4 = theta3 + math.pi/2
        x4 = x + r * math.cos(theta4)
        y4 = y - r * math.sin(theta4)
        canvas.create_line(x, y, x4, y4, fill = "red")

        whiteBox = rgbString(223, 217, 205)
        blackBox = rgbString(58, 56, 50)
        color = whiteBox if self.justHit else blackBox
        #final product
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, fill = color, outline = "black", width = 2)


def distance(x0, y0, x1, y1):
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def appStarted(self, hard = False):
    self.timerDelay = 20
    self.debug = False
    self.gameLost = False
    #large grid:
    self.lRows = 10
    self.lCols = 10
    self.lSize = 60

    #small grid:
    self.sSize = 10
    self.sRows = self.lRows * self.lSize // self.sSize #
    self.sCols = self.lCols * self.lSize // self.sSize #

    if hard:
        self.numEnemies = 8
        self.boxRate = 20
    else:
        self.numEnemies = 2
        self.boxRate = 3 + self.numEnemies

    #pointer
    self.pointerHealth = 10
    self.maxPointerHealth = 10
    self.pointerSpeed = 4

    self.whiteBullet = self.loadImage('images/whiteBullet.png')
    self.redBullet = self.loadImage('images/redBullet.png')
    self.blueBullet = self.loadImage('images/blueBullet.png')

    self.i = 0
    self.timerStart = time.time()
    self.totalTime = 0
    # self.i, self.timerStart, self.totalTime
    resetApp(self)

def resetApp(self):
    self.numEnemies += 1
    #stage (placement of a few black boxes)
    self.stage = [[None] * self.lCols for __ in range(self.lRows)]
    self.stage = generateSimpleMaze(self, self.stage)

    #etc drawing
    self.upperRightCorner = (self.width//2  - (self.lRows * self.lSize) // 2, 
                             self.height//2 - (self.lCols * self.lSize // 2))
    self.smallBoxGrid = makeGrid(self)

    """
    #variable (changes every run)
    start = self.smallBoxGrid[0][0]
    start.makeStart()
    end = self.smallBoxGrid[self.sRows-1][self.sCols-1]
    end.makeEnd()
    """
    for row in self.smallBoxGrid:
        for smallBox in row:
            smallBox.updateSuccessors(self)
    self.reconstructedPath = []
    """
    if not aStar(self, start, end):
        print("didn't work ")
    print(self.reconstructedPath)
    """

    #pointer
    self.pointerRow = int(self.sRows - (self.lSize/self.sSize) / 2)
    self.pointerCol = self.sCols // 2
    self.pointerAngle = math.pi/2
    self.pointerGoal = None

    self.firing = False
    self.bulletSpeed = 15
    self.fireRate = 6
    self.j = 0
    self.pointerBullets = []

    self.pointerSize = 13
    

    #enemies
    self.enemies = []
    simpleGenerateEnemy(self, self.numEnemies)
    self.enemyBullets = []
    

def generateSimpleMaze(self, matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    #chance to spawn a new block
    chance = self.boxRate
    print(f"chance: {1/(chance-1)}")
    for row in range(1, rows - 1):
        for col in range(1, cols - 1):
            choice = random.randint(0, chance)
            if rows//2-1 <= row <= rows//2 and cols//2-1 <= col <= cols//2:
                pass
            elif choice == 0:
                matrix[row][col] = LargeBox(row, col)
    return matrix

def makeGrid(self):
    grid = []
    for row in range(self.sRows):
        grid.append([])
        for col in range(self.sCols):
            isBarrier = False
            x0, y0, x1, y1 = getSCellBounds(self, row, col)
            x0, y0 = x0 + self.sSize//2, y0 + self.sSize//2
            lRow, lCol = getLCell(self, x0, y0)
            if 0 <= lRow < self.lRows and 0 <= lCol < self.lCols and self.stage[lRow][lCol] != None:
                isBarrier = True
            smallBox = SmallBox(row, col, isBarrier)
            grid[row].append(smallBox)
    return grid

def simpleGenerateEnemy(self, num):
    cRow, cCol = self.sRows // 2, self.sCols // 2 
    self.enemies.append(Core(cRow, cCol))

    for i in range(num):
        row, col = -1, -1
        while not notInPiece(self, row, col):
            #generate new row, col
            row, col = random.randint(0, self.sRows), random.randint(0, self.sCols)
        #spawn new enemy
        self.enemies.append(Shooter(row, col))
    
    cylinders = 1 if num < 5 else 2
    for i in range(cylinders):
        row, col = -1, -1
        while not notInPiece(self, row, col):
            row, col = random.randint(0, self.sRows), random.randint(0, self.sCols)
        self.enemies.append(Cylinder(row, col))


def notInPiece(self, row, col):
    if 0 <= row < self.sRows and 0 <= col < self.sCols:
        x0, y0, x1, y1 = getSCellBounds(self, row, col)
        x0, y0 = x0 + self.sSize//2, y0 + self.sSize//2
        lRow, lCol = getLCell(self, x0, y0)
        if 0 <= lRow < self.lRows and 0 <= lCol < self.lCols and self.stage[lRow][lCol] == None:

            #not related to "notInPiece", but checks if enemy is too close to the enemy.
            if distance(row, col, self.pointerRow, self.pointerCol) < Shooter.killerInstinct * 2:
                return False
            return True

    return False


#
# Control
#
def mousePressed(self, event):
    self.firing = True

def mouseReleased(self, event):
    self.firing = False

def keyPressed(self, event):
    if self.gameLost:
        appStarted(self)
    if event.key in "wasd":
        if event.key == "a":
            shift = (0, -1)
        elif event.key == "d":
            shift = (0, 1)
        elif event.key == "w":
            shift = (-1, 0)
        elif event.key == "s":
            shift = (1, 0)
        else:
            shift = (0,0)
        setPointerGoal(self, (shift[0], shift[1]))
    elif event.key == "r":
        appStarted(self)
    elif event.key == "Escape":
        self.debug = not self.debug

def setPointerGoal(self, shift):
    #was range(1, 4)
    speed = self.pointerSpeed + 1
    for i in range(1, speed):
        if not isLegalPointerMove(self, (shift[0] * i,  shift[1] * i)):
            i -= 1
            break
    self.pointerGoal = shift[0] * i, shift[1] * i
    print(self.pointerGoal)
    #print(f"goal: {self.pointerGoal}, {i}")

def mouseMoved(self, event):
    updatePointerAngle(self, event.x, event.y)

def mouseDragged(self, event):
    updatePointerAngle(self, event.x, event.y)

def updatePointerAngle(self, ex, ey):
    #calculate new angle
    x, y = getPointerXY(self)

    yDif = ey - y
    xDif = x - ex
    try:
        newAngle = math.atan(yDif/xDif)
    except:
        newAngle = math.atan(-yDif/.01)
    if xDif > 0:
        newAngle = newAngle + math.pi
    self.pointerAngle = newAngle 

def getPointerXY(self):
    x0, y0, x1, y1 = getSCellBounds(self, self.pointerRow, self.pointerCol)
    x = x0 + self.sSize // 2
    y = y0 + self.sSize // 2
    return x, y

def timerFired(self):
    movePointer(self)
    createBulletController(self)
    moveBullets(self)
    removeBullets(self)
    checkBulletsInEnemy(self)
    checkBulletsInPointer(self)
    removeEnemies(self)
    updateEnemyAngle(self)
    unshieldEnemies(self)
    checkGameOver(self)
    pathFind(self)
    moveEnemies(self)
    checkEnemyFlash(self)
    enemyBulletController(self)
    timerFiredSpeed(self)

def timerFiredSpeed(self):
    #self.i, self.timerStart, self.totalTime
    ticks = 25
    if self.i == 0:
        self.totalTime = time.time() - self.timerStart
        self.timerStart = time.time()
        print(self.totalTime)
    self.i = (self.i + 1) % ticks

def enemyBulletController(self):
    for enemy in self.enemies:
        enemy.fire(self)
    for bullet in self.enemyBullets:
        x, y = bullet.x, bullet.y
        dx, dy = bullet.dx, bullet.dy
        x, y = x + dx, y - dy
        bullet.x, bullet.y = x, y


def pathFind(self):
    for enemy in self.enemies:
        #if type(enemy) == Shooter:
            enemy.pathFind(self)

def moveEnemies(self):
    for enemy in self.enemies:
        #if type(enemy) == Shooter:
            enemy.move(self)

def checkEnemyFlash(self):
    for enemy in self.enemies:
        enemy.checkJustHit()

def checkGameOver(self):
    if len(self.enemies) == 0:
        resetApp(self)
    if self.pointerHealth <= 0:
        self.gameLost = True

def unshieldEnemies(self):
    if len(self.enemies) == 1:
        enemy = self.enemies[0]
        enemy.shielded = False

def updateEnemyAngle(self):
    for enemy in self.enemies:
        enemy.updateAngle(self)

def removeEnemies(self):
    i = 0
    while i < len(self.enemies):
        enemy = self.enemies[i]
        if enemy.isDead():
            self.enemies.pop(i)
        else:
            i += 1

def checkBulletsInEnemy(self):
    #O(n^2)...
    for enemy in self.enemies:
        i = 0
        while i < len(self.pointerBullets):
            bullet = self.pointerBullets[i]
            x, y = bullet.getPos()
            result = enemy.pointInEnemy(self, x, y)
            if result == True:
                enemy.subtractHealth()
                self.pointerBullets.pop(i)
            elif result == None:
                self.pointerBullets.pop(i)
            else:
                i += 1
            """
            if enemy.pointInEnemy(self, x, y):
                #enemy.health -= 1
                enemy.subtractHealth()
                self.pointerBullets.pop(i)
            else:
                i += 1
            """

def checkBulletsInPointer(self):
    #O(n) yay
    i = 0
    while i < len(self.enemyBullets):
        bullet = self.enemyBullets[i]
        x, y = bullet.getPos()
        if pointInPointer(self, x, y):
            self.pointerHealth -= 1
            self.enemyBullets.pop(i)
        else:
            i += 1

def pointInPointer(self, x, y):
    hitbox = 23 #should be 13 mayhpas
    x0, y0 = getPointerXY(self)
    if distance(x, y, x0, y0) < hitbox:
        return True
    return False

def removeBullets(self):
    i = 0
    while i < len(self.pointerBullets):
        bullet = self.pointerBullets[i]
        x, y = bullet.getPos()
        row, col = getLCell(self, x, y)
        if 0 <= row < self.lRows and 0 <= col < self.lCols:
            if self.stage[row][col] != None:
                self.pointerBullets.pop(i)
            else:
                i += 1
        elif x < 0 or x >= self.width or y < 0 or y >= self.width:
            self.pointerBullets.pop(i)
        else:
            i += 1
    i = 0
    while i < len(self.enemyBullets):
        bullet = self.enemyBullets[i]
        x, y = bullet.getPos()
        row, col = getLCell(self, x, y)
        if 0 <= row < self.lRows and 0 <= col < self.lCols:
            if self.stage[row][col] != None:
                self.enemyBullets.pop(i)
            else:
                i += 1
        #elif x < 0 or x >= self.width or y < 0 or y >= self.width:
        #    self.enemyBullets.pop(i)
        elif row < 0 or row >= self.lRows or col < 0 or col >= self.lCols:
            self.enemyBullets.pop(i)
        else:
            i += 1

def createBulletController(self):
    if self.firing:
        self.j += 1
        if self.j % self.fireRate == 0:
            createBullet(self)

def createBullet(self):
    x0, y0, x1, y1 = getSCellBounds(self, self.pointerRow, self.pointerCol)
    x = x0 + self.sSize // 2
    y = y0 + self.sSize // 2
    angle = self.pointerAngle
    r2 = 40 #50

    dirX = x + r2 * math.cos(angle)
    dirY = y - r2 * math.sin(angle)
    dx = self.bulletSpeed * math.cos(angle)
    dy = self.bulletSpeed * math.sin(angle)
    bullet = PointerBullet(dirX, dirY, dx, dy, angle)
    self.pointerBullets.append(bullet)

def moveBullets(self):
    for bullet in self.pointerBullets:
        x, y = bullet.x, bullet.y
        dx, dy = bullet.dx, bullet.dy
        x, y = x + dx, y - dy
        bullet.x, bullet.y = x, y

def movePointer(self):
    if self.pointerGoal != None:
        dRow, dCol = self.pointerGoal
        if dRow > 0:
            self.pointerRow += 1
            dRow -= 1
            if dRow >= 1:
                self.pointerRow += 1
                dRow -= 1
        elif dRow < 0:
            self.pointerRow -= 1
            dRow += 1
            if dRow <= -1:
                self.pointerRow -= 1
                dRow += 1 
        elif dCol > 0:
            self.pointerCol += 1
            dCol -= 1
            if dCol >= 1:
                self.pointerCol += 1
                dCol -= 1
        elif dCol < 0:
            self.pointerCol -= 1
            dCol += 1
            if dCol <= -1:
                self.pointerCol -= 1
                dCol += 1
        else:
            self.pointerGoal = None
        self.pointerGoal = (dRow, dCol)
        if self.pointerGoal == (0,0):
            self.pointerGoal = None


#
# model to view and view to model stuff
#
def isLegalPointerMove(self, position):
    newRow, newCol = self.pointerRow + position[0], self.pointerCol + position[1]
    if newRow < 0 or newRow >= self.sRows or newCol < 0 or newCol >= self.sCols:
        return False
    #check if the newRow/newCol are in a stage square thignyu
    newX, newY, x1, y1 = getSCellBounds(self, newRow, newCol)
    newX, newY = newX + self.sSize // 2, newY + self.sSize // 2
    row, col = getLCell(self, newX, newY)
    if 0 <= row < self.lRows and 0 <= col < self.lCols:
        if self.stage[row][col] != None:
            return False

    #check if our hitbox is colliding with an enemy.. O(8n)
    for enemy in self.enemies:
        # 13 is the size of the hitbox.
        for dx, dy in [(-13, -13), (13, 13), (-13, 13), (13, -13), (-13, 0), (13, 0), (0, 13), (0,-13)]:
            x, y = newX + dx, newY - dy
            if enemy.pointInEnemy(self, x, y):
                return False
    #legal move, continue. 
    return True

def getLCellBounds(self, row, col):
    xShift, yShift = self.upperRightCorner
    x0 = col * self.lSize + xShift
    x1 = (col + 1) * self.lSize + xShift
    y0 = row * self.lSize + yShift
    y1 = (row + 1) * self.lSize + yShift
    return x0, y0, x1, y1

def getLCell(self, x, y):
    xShift, yShift = self.upperRightCorner
    col = int((x - xShift) // self.lSize)
    row = int((y - yShift) // self.lSize)
    return row, col

def getSCellBounds(self, row, col):
    xShift, yShift = self.upperRightCorner
    x0 = col * self.sSize + xShift
    x1 = (col + 1) * self.sSize + xShift
    y0 = row * self.sSize + yShift
    y1 = (row + 1) * self.sSize + yShift
    return x0, y0, x1, y1

def getSCell(self, x, y):
    xShift, yShift = self.upperRightCorner
    col = int((x - xShift) // self.sSize)
    row = int((y - yShift) // self.sSize)
    return row, col
#
# View
#
def redrawAll(self, canvas):
    drawBackground(self, canvas)
    drawLGrid(self, canvas)
    drawEnemies(self, canvas)
    drawPointerHealth(self, canvas)
    if not self.gameLost:
        drawPointer(self, canvas)
        drawPointerBullets(self, canvas)
        drawEnemyBullets(self, canvas)
    else:
        drawGameLost(self, canvas)
    #drawSGrid(self, canvas)
    if self.debug:
        drawSmallGrid(self, canvas)


def drawGameLost(self, canvas):
    #rectangle covering screen
    canvas.create_rectangle(0, self.height/3, self.width, self.height*2/3,
                            fill = "grey", width = 0)
    canvas.create_text(self.width//2, self.height//2 - 25, 
                            text = "Hacking Failed", font = "arial 24 bold", fill = "white")
    canvas.create_text(self.width//2, self.height//2 + 25, text= "Press any key to continue",
                        font = "arial 14 bold", fill = "white")

#code from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def drawPointerHealth(self, canvas):
    yPos = 30
    xPos = 60
    length = 150

    maxHealth = self.maxPointerHealth
    healthColor = rgbString(205, 200, 176)
    beautifulRed = rgbString(205, 102, 77)

    canvas.create_line(xPos, yPos, xPos + length, yPos, fill = beautifulRed, width = 9)
    currHealth = (self.pointerHealth/maxHealth) * length

    if currHealth >= 0:
        canvas.create_line(xPos, yPos, xPos + currHealth, yPos, fill = healthColor, width = 9)
    
    #line above everything:
    canvas.create_line(xPos, yPos + 10, xPos + length, yPos + 10, fill= healthColor, width = 2)

def drawEnemies(self, canvas):
    for enemy in self.enemies:
        enemy.draw(self, canvas)


def drawBackground(self, canvas):
    darkGrey = rgbString(60, 57, 51)
    stageColor = rgbString(202, 195, 171)
    frameFactor = self.lSize * self.lRows
    canvas.create_rectangle(0,0,self.width, self.height, fill = darkGrey)
    canvas.create_rectangle(self.upperRightCorner, self.upperRightCorner[0] + frameFactor, 
                            self.upperRightCorner[1] + frameFactor, fill = stageColor)

def drawLGrid(self, canvas):
    rows, cols = self.lRows, self.lCols
    for row in range(rows):
        for col in range(cols):
            x0, y0, x1, y1 = getLCellBounds(self, row, col)
            smallShift = 2
            x0, y0, x1, y1 = x0 + smallShift, y0 + smallShift, x1 - smallShift, y1 - smallShift
            if self.stage[row][col] != None:
                canvas.create_rectangle(x0, y0, x1, y1, fill = "black")
            else:
                #canvas.create_rectangle(x0, y0, x1, y1)
                pass

#not used 
def drawSGrid(self, canvas):
    rows, cols = self.sRows, self.sCols
    for row in range(rows):
        for col in range(cols):
            x0, y0, x1, y1 = getSCellBounds(self, row, col)
            smallShift = 0
            x0, y0, x1, y1 = x0 + smallShift, y0 + smallShift, x1 - smallShift, y1 - smallShift
            canvas.create_rectangle(x0, y0, x1, y1)

def drawSmallGrid(self, canvas):
    """
    rows, cols = len(self.smallBoxGrid), len(self.smallBoxGrid[0])
    for row in range(rows):
        for col in range(cols):
            smallBox = self.smallBoxGrid[row][col]
            if smallBox.isPath:
                x0, y0, x1, y1 = getSCellBounds(self, row, col)
                smallShift = 0
                x0, y0, x1, y1 = x0 + smallShift, y0 + smallShift, x1 - smallShift, y1 - smallShift
                canvas.create_rectangle(x0, y0, x1, y1, fill = 'red')
    """
    for enemy in self.enemies:
            boxes = enemy.path
            for box in enemy.path:
                x0, y0, x1, y1 = getSCellBounds(self, box.row, box.col)
                smallShift = 0
                x0, y0, x1, y1 = x0 + smallShift, y0 + smallShift, x1 - smallShift, y1 - smallShift
                canvas.create_rectangle(x0, y0, x1, y1, fill = 'red')

def getCachedPhotoImage(self, image):
    # stores a cached version of the PhotoImage in the PIL/Pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def drawPointerBullets(self, canvas):
    for bullet in self.pointerBullets:
        x, y = bullet.x, bullet.y
        color = rgbString(242, 238, 218)
        canvas.create_oval(x-10, y-10, x+10, y+10, fill = color, width = 0)

def drawEnemyBullets(self, canvas):
    for bullet in self.enemyBullets:
        x, y = bullet.x, bullet.y
        #2 generally | 1.2
        redColor = rgbString(205, 102, 77)
        canvas.create_oval(x-10, y-10, x+10, y+10, fill = redColor, width = 0)

        #this is 1.5 times more laggy lol. (about 3) | (1.6, unplayable)
        #photoImage = getCachedPhotoImage(self, (self.redBullet))
        #canvas.create_image(x, y, image=photoImage)

        #3.5 on average
        #canvas.create_image(x, y, image=ImageTk.PhotoImage(self.redBullet))

        #if using all 3 at the same time; ~5.5

def drawPointer(self, canvas):
    
    x0, y0, x1, y1 = getSCellBounds(self, self.pointerRow, self.pointerCol)
    x = x0 + self.sSize // 2
    y = y0 + self.sSize // 2
    angle = self.pointerAngle

    color = rgbString(250, 247, 230)
    #radius of the two small edges
    r = 20
    theta = math.pi/3
    x0, y0 = x, y
    x1, y1 = x0 + r*math.cos(angle-theta), y0 - r * math.sin(angle-theta)
    #radius of the long line
    r2 = 50
    x2, y2 = x + r2 * math.cos(angle), y - r2 * math.sin(angle)
    x3, y3 = x0 + r*math.cos(angle+theta), y0 - r * math.sin(angle+theta)
    canvas.create_line(x, y, x1, y1)
    canvas.create_line(x, y, x3, y3)
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = color, 
                          outline = "tan", width = 2)
    #little tail things (left first)
    r = 22
    theta2 = math.pi/2
    x4, y4 = x + r*math.cos(angle+theta2), y - r * math.sin(angle + theta2)
    canvas.create_line(x3, y3, x4, y4)
    x5, y5 = x + 20*math.cos(angle+math.pi), y - 20* math.sin(angle + math.pi)
    canvas.create_polygon(x3, y3, x4, y4, x5, y5, x, y, fill = color, 
                         outline = 'tan', width = 2)
    #right little tail thing
    x6, y6 = x + r*math.cos(angle-theta2), y-r*math.sin(angle - theta2)
    canvas.create_polygon(x1, y1, x6, y6, x5, y5, x, y, fill=color, 
                            outline = "tan", width = 2)

    #temp line showing where the pointer is looking
    dirX = x + r2 * math.cos(angle)
    dirY = y - r2 * math.sin(angle)
    #canvas.create_line(x, y, dirX, dirY, fill = "red")

    #black dot in middle:
    r = 5
    canvas.create_oval(x-r, y-r, x+r, y+r, fill = "black", width = 0)

    #canvas.create_rectangle(getSCellBounds(self, self.pointerRow, self.pointerCol), fill = "red")


#################################################
# main
#################################################

runApp(width = 1280, height = 720)
