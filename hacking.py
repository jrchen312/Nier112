#
# This file holds all of the code necessary to run the hacking minigame. 
#

from cmu_112_graphics import *
from dataclasses import make_dataclass
import math
import random
import time

PointerBullet = make_dataclass("PointerBullet", ['x', 'y', 'dx', 'dy', 'angle'])
Core = make_dataclass("Core", ['x', 'y'])
RedBullet = make_dataclass("RedBullet", ['x','y','dx', 'dy'])
Box = make_dataclass("Box", ['row', 'col', 'color', 'health', 'hit', 'frames'])


def appStarted(app):
    hackingAppStarted(app)
 

def hackingAppStarted(app):
    app.timerDelay = 20
    resetHackingGame(app)


def resetHackingGame(app):
    # Hacking:
    app.endZoneSize = app.height/5
    app.endZonePosition = app.height - app.endZoneSize

    #Pointer
    app.pointerX = app.width//2
    app.pointerY = app.endZonePosition + app.endZoneSize//2
    #app.camPos = int(app.height - app.height//5)
    app.initialY = app.pointerY
    app.pointerA = math.pi/2
    app.pointerBullets = []
    app.bulletSpeed = 15
    app.fireRate = 6
    app.firing = False
    app.j = 0

    app.pointerDirections = [0,1,2,3] #right, left, down, up
    app.pointerDir = 3
    app.pointerD = 20
    app.pointerDd = 5
    app.pointerLegal = False

    app.pointerGoal = None
    app.pointerSpeed = 40

    app.cellSize = 60 # 30
    app.cellGap = 4 # 2
    app.cols = 8
    #can have like 20 rows
    app.rows = 8
    app.boxHealth = 4
    app.stage = generateMaze(app, app.rows, app.cols)
    center = app.width/2
    app.leftX = center - (app.cellSize*app.cols + (app.cols+1)*app.cellGap)/2
    app.rightX = app.leftX + app.cols*app.cellSize + (app.cols+1) * app.cellGap
    app.railWidth = 15

    app.hackingGameOver = False
    app.hackingGameStarted = True
    app.returnToGame = False
    setHackingTime(app)

    app.coreRow = app.rows+5
    app.coreCol = app.cols//2
    app.coreHealth = 3
    app.hackingGameWon = False
    

def setHackingTime(app):
    app.startTime = time.time()
    #app.timeAvailable = 240 # needs to be generated

def generateMaze(app, rows, cols):
    #h is the health of the white boxes. can increase, but it doesn't matter. 
    h = 20
    maze = [ [0] * cols for _ in range(rows)]
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            #default should all be white boxes
            maze[row][col] = Box(row=row, col=col, color = "white", health = h, hit = False, frames = 0)
    
    #the rows that we should start building a maze from:
    starting = [num for num in range(cols)]
    col1 = random.choice(starting)
    col3 = (col1 + 2) % len(starting)
    starting.remove(col1)
    col2 = random.choice(starting)
    
    row1, row2 = 0, 0

    #maze = populatePath(app, maze, row1, col1, col3)
    maze[row1][col1] = Box(row = row1, col = col1, color = "black", health = app.boxHealth, hit = False, frames = 0)
    row1 += 1
    maze[row1][col1] = Box(row = row1, col = col1, color = "black", health = app.boxHealth, hit = False, frames = 0)
    maze, depth = populatePath(app, maze, row1, col1)

    #plus two because we spawn two boxes beforehand. (bullets)
    hitsNeeded = (depth + 2) * app.boxHealth
    #fire rate: (bullet/second)
    rate = app.timerDelay/1000 * app.fireRate * 1.82
    #result:
    app.timeAvailable = hitsNeeded * rate + 2.5
    print(app.timeAvailable)
    return maze


#populate a path recursively??
# populates a path, and returns how long the result was (depth)
# 'distantly' related to https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#Backtracking (example 1)
def populatePath(app, maze, row, col, depth = 0):
    rows, cols = len(maze), len(maze[0])
    dirs = [(1,0), (0,-1), (0,1), (-1,0), (0,-1), (0,1)]
    if row == rows -1:
        return maze, depth
        
    else:
        random.shuffle(dirs)
        for (drow, dcol) in dirs:
            newRow, newCol = row + drow, col + dcol
            if isValidMove(app, maze, newRow, newCol):
                maze[newRow][newCol] = Box(row=newRow, col=newCol, color = "black", health = app.boxHealth, hit = False, frames = 0)

                result = populatePath(app, maze, newRow, newCol, depth + 1)
                if result != None:
                    maze = result[0]
                    maze = fillInStuff(app, maze, newRow, newCol)
                    return maze, result[1]
        return None

#fills in some parts of the board. not efficient. 
def fillInStuff(app, maze, row, col):
    dirs = [(1,0), (0,-1), (0,1), (-1,0)]
    i = 0
    while i < 24:
        randomDir = random.choice(dirs)
        (drow, dcol) = randomDir
        if isValidMove(app, maze, row + drow, col + dcol):
            maze[drow+row][col+dcol] = Box(row=drow+row, col=dcol+col, color="black", health=app.boxHealth, hit = False, frames = 0)
            row, col = row + drow, col + dcol
        i += 1
    
    return maze


#Make sure that the path can only be one thick. 
def isValidMove(app, maze, row, col):
    rows = len(maze)
    cols = len(maze[0])
    if not isInMazeBounds(app, maze, row, col):
        return False

    if row == 0:
        return False
    #check that the new move is not adjacent to a black piece
    dirs = [(1,0), (0,-1), (0,1), (-1,0)]
    adjCount = 0
    for (drow, dcol) in dirs:
        newRow = row + drow
        newCol = col + dcol
        if isInMazeBounds(app, maze, newRow, newCol):
            currBlock = maze[newRow][newCol]
            if currBlock.color == "black":
                adjCount += 1
    if adjCount > 1:
        return False
    
    #check if there's already a solution:
    if row == rows - 1:
        r = rows - 1
        for c in range(cols):
            block = maze[r][c]
            if block.color == "black":
                return False
    return True


def isInMazeBounds(app, maze, row, col):
    rows = len(maze)
    cols = len(maze[0])
    if row < 0 or row >= rows or col < 0 or col >= cols:
        return False
    return True


#
# KeyPressed
#
def keyPressed(app, event):
    #totally intended double check lmao
    if app.hacking:
        if app.hackingGameStarted:
            app.hackingGameStarted = False
            setHackingTime(app)
        elif app.hackingGameOver:
            app.returnToGame = True
        elif event.key in "wasd" and app.pointerGoal == None:
            if event.key == "a":  #[0,1,2,3] #right, left, down, up
                app.pointerGoal = (app.pointerX - app.pointerSpeed, app.pointerY)
                app.pointerDir = 1
            elif event.key == "d":
                app.pointerGoal = (app.pointerX + app.pointerSpeed, app.pointerY)
                app.pointerDir = 0
            elif event.key == "s":
                app.pointerGoal = (app.pointerX, app.pointerY + app.pointerSpeed)
                app.pointerDir = 2
            elif event.key == "w":
                app.pointerGoal = (app.pointerX, app.pointerY - app.pointerSpeed)
                app.pointerDir = 3
        elif event.key == "f":
            app.firing = not app.firing
        elif event.key == 'r':
            resetHackingGame(app)

def mouseMoved(self, event):
    updatePointerAngle(self, event.x, event.y)

def mouseDragged(self, event):
    updatePointerAngle(self, event.x, event.y)

def updatePointerAngle(self, ex, ey):
    #calculate new angle
    x, y = self.pointerX, self.pointerY

    yDif = ey - y
    xDif = x - ex
    try:
        newAngle = math.atan(yDif/xDif)
    except:
        newAngle = math.atan(-yDif/.01)
    if xDif > 0:
        newAngle = newAngle + math.pi
    self.pointerA = newAngle 

def timerFired(app):
    if app.hacking and not app.hackingGameOver:
        moveBullets(app)
        removeBullets(app)
        movePointerToGoal(app)
        createBulletController(app)
        checkHackingGameOver(app)
        updateCameraPos(app)
        updateBoxes(app)
        if app.coreHealth <= 0:
            app.hackingGameOver = True
            app.hackingGameWon = True
    elif app.hackingGameOver:
        return checkReturnToGame(app)
    return None
        
#return None if hacking game is still going on.
#return True if the hacking is over, and the player won
#return False if the hacking is over, and the player lost
def checkReturnToGame(app):
    if app.returnToGame:
        if app.hackingGameWon:
            return True
        else:
            return False
    return None


def updateCameraPos(app):
    deviation = app.initialY - app.pointerY
    app.endZonePosition = app.endZonePosition + deviation
    app.pointerY = app.initialY
    if app.pointerGoal != None:
        x, y = app.pointerGoal
        y += deviation
        app.pointerGoal = x, y

def checkHackingGameOver(app):
    if (app.timeAvailable + app.startTime - time.time() < 0 and not 
                                            app.hackingGameStarted):
        app.hackingGameOver = True

def distance(x, y, x1, y1):
    return ((x-x1)**2 + (y-y1)**2)**.5

def movePointerToGoal(app):
    if app.pointerGoal != None:
        goalX, goalY = app.pointerGoal
        newX, newY = app.pointerX, app.pointerY
        dx = int(goalX - newX)
        dy = int(goalY - newY)

        if not app.pointerLegal and not isLegalPointerPosition(app, goalX, goalY):
            app.pointerLegal = True
            app.pointerGoal = firstLegalPointerPosition(app)

        elif not app.pointerLegal:
            app.pointerLegal = True

        dist = distance(app.pointerGoal[0], app.pointerGoal[1], 
                        newX,               newY)
        if dist > app.pointerSpeed//3:
            app.pointerD += app.pointerDd
        else:
            app.pointerD -= app.pointerDd
            if app.pointerD < 4:
                app.pointerD = 4
        if app.pointerDir == 0 and dx > 0:
            newX += app.pointerD
        elif app.pointerDir == 1 and dx < 0:
            newX -= app.pointerD
        elif app.pointerDir == 2 and dy >= 0:
            newY += 10
        elif app.pointerDir == 3 and dy <= 0:
            newY -= 10
        else:
            newX = app.pointerGoal[0]
            newY = app.pointerGoal[1]

        app.pointerX, app.pointerY = newX, newY

        if app.pointerGoal == (app.pointerX, app.pointerY):
            app.pointerGoal = None
            app.pointerD = 10
            app.pointerLegal = False
            
def isLegalPointerPosition(app, x, y):
    #may need to fix these magical nums here. 
    positions = [(x-13, y-18), (x+13, y-18), (x-13, y-12), (x+13, y+12)]
    for (x0, y0) in positions:
        temp = getPotentialCell(app, x0, y0)
        if temp != None:
            row, col = temp
            box = app.stage[row][col]
            if box != None and box.health > 0:
                return False
        elif x0 <= app.leftX or x0 >= app.rightX:
            return False
    return True

def firstLegalPointerPosition(app):
    x, y = app.pointerX, app.pointerY
    direction = app.pointerDir
    goalX, goalY = app.pointerGoal

    if direction == 0:
        xIncr, yIncr = -3, 0
    elif direction == 1:
        xIncr, yIncr = +3, 0
    elif direction == 2:
        xIncr, yIncr = 0, -3
    elif direction == 3:
        xIncr, yIncr = 0, +3
    for i in range(16):
        if isLegalPointerPosition(app, goalX+xIncr*i, goalY+yIncr*i):
            return (goalX+xIncr*i, goalY+yIncr*i)
    return (goalX+xIncr*i, goalY+yIncr*i)

def createBulletController(app):
    if app.firing:
        app.j += 1
        if app.j % app.fireRate == 0:
            createBullet(app)

def createBullet(app):
    x, y, angle, r2 = app.pointerX, app.pointerY, app.pointerA, 50
    dirX = x + r2 * math.cos(angle)
    dirY = y - r2 * math.sin(angle)
    dx = app.bulletSpeed * math.cos(angle)
    dy = app.bulletSpeed * math.sin(angle)
    bullet = PointerBullet(x = dirX, y = dirY, dx = dx, dy = dy, angle = angle)
    app.pointerBullets.append(bullet)

def moveBullets(app):
    for bullet in app.pointerBullets:
        x, y = bullet.x, bullet.y
        dx, dy = bullet.dx, bullet.dy
        x, y = x + dx, y - dy
        bullet.x, bullet.y = x, y

def removeBullets(app):
    i = 0
    x, y, x0, y0 = getCellBounds(app, app.coreRow, app.coreCol)
    
    while i < len(app.pointerBullets):
        bullet = app.pointerBullets[i]
        if (bullet.x < 0 or bullet.x > app.width or
            bullet.y < 0 or bullet.y > app.height):
            app.pointerBullets.pop(i)
        elif (getPotentialCell(app, bullet.x, bullet.y) != None):
            row, col = getPotentialCell(app, bullet.x, bullet.y)
            if app.stage[row][col] != None:
                app.pointerBullets.pop(i)
                #decrease health of the box
                boxHit(app, row, col)
            else:
                i += 1
        elif distance(bullet.x, bullet.y, x + (x0-x)/2, y + (y0-y)/2) < app.cellSize:
            if app.coreHealth > 0:
                app.pointerBullets.pop(i)
                app.coreHealth -= 1
            else:
                i += 1
        else:
            i += 1

def boxHit(app, row, col):
    box = app.stage[row][col]
    health = box.health
    health -= 1
    box.hit = True
    box.frames = 2
    if health <= 0:
        app.stage[row][col] = None
    else:
        box.health = health

#purpos is to blink the box if a bullet hits them.
def updateBoxes(app):
    rows, cols = len(app.stage), len(app.stage[0])
    for row in range(rows):
        for col in range(cols):
            if app.stage[row][col] != None:
                box = app.stage[row][col]
                if box.hit:
                    if box.frames <= 0:
                        box.hit = False
                    box.frames -= 1

#####
# redraw all
######
def redrawAll(app, canvas):
    if app.hacking:
        if app.hackingGameOver:
            drawMaze(app, canvas)
            drawHackingGameOver(app, canvas)
            return
        elif app.hackingGameStarted:
            drawMaze(app, canvas)
            drawHackingGameStarted(app, canvas)
            return
        drawMaze(app, canvas)
        drawPointer(app, canvas)
        drawPointerBullets(app, canvas)
        drawCore(app, canvas)

#code from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    # Don't worry about the :02x part, but for the curious,
    # it says to use hex (base 16) with two digits.
    return f'#{r:02x}{g:02x}{b:02x}'

def drawCore(app, canvas):
    if app.coreHealth > 0:
        x, y, x0, y0 = getCellBounds(app, app.coreRow, app.coreCol)
        color = rgbString(99, 90, 76)
        canvas.create_oval(x, y, x0, y0, fill = color)

def drawPointerBullets(app, canvas):
    for bullet in app.pointerBullets:
        x, y = bullet.x, bullet.y
        color = rgbString(242, 238, 218)
        canvas.create_oval(x-10, y-10, x+10, y+10, fill = color, width = 0)

def drawPointer(app, canvas):
    x = app.pointerX 
    y = app.pointerY 
    angle = app.pointerA 

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

    #draws the time remaining in the game
    timeLeft = round(app.timeAvailable + app.startTime - time.time(), 2)
    textColor = "red" if timeLeft < 5 else "black"
    timeLeft = str(timeLeft)
    canvas.create_text(x + r2, y, text = timeLeft, anchor = 'w', fill=textColor)

    #canvas.create_rectangle(x-13, y-18, x+13, y+12, fill = "red", width = 0)

def drawHackingGameOver(app, canvas):
    canvas.create_rectangle(0, app.height/3, app.width, app.height/(3/2), 
                            fill="tan")
    if app.hackingGameWon:
        canvas.create_text(app.width//2, app.height//2, fill="white",
                        text="Hacking Successful", font="arial 20 bold")
    else:
        canvas.create_text(app.width//2, app.height//2, fill="white",
                        text="Hacking Failed", font="arial 20 bold")
    canvas.create_text(app.width//2, app.height//2 + 30, fill = "white",
                       text = "Press any key to continue", 
                       font = "arial 15 bold")

def drawHackingGameStarted(app, canvas):
    canvas.create_rectangle(0, app.height/3, app.width, app.height/(3/2), 
                            fill="tan")
    canvas.create_text(app.width//2, app.height//2, fill="white",
                        text="Press any key to begin", font="arial 30 bold")

#getPotentialCell and getCellBounds are similar to 
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
#except they consider the gap between each cell. 
def getPotentialCell(app, x, y):
    width = app.leftX
    cellSize = app.cellSize
    if x < (app.leftX - app.cellGap) or x > (app.rightX + app.cellGap):
        return None
    if y > app.endZonePosition: return None
    col = int((x-app.leftX) / (app.cellSize+app.cellGap))
    
    row = int((app.endZonePosition-y) / (app.cellSize+app.cellGap))

    if row >= app.rows or row < 0 or col >= app.cols or col < 0: return None
    return row, col

def getCellBounds(app, row, col):
    width = app.rightX - app.leftX
    leftx = app.leftX + app.cellGap
    topy = app.endZonePosition
    x0 = leftx + (app.cellSize + app.cellGap) * col
    x1 = x0 + app.cellSize
    y0 = topy - (app.cellSize + app.cellGap) * (row)
    y1 = y0 - app.cellSize
    
    return x0, y0, x1, y1

def drawMaze(app, canvas):
    shift = 0
    center = app.width/2

    #draw a white stage:
    darkGrey = rgbString(60, 57, 51)
    stageColor = rgbString(202, 195, 171)
    canvas.create_rectangle(0,0,app.width, app.height, fill = stageColor)
    canvas.create_rectangle(0,0,app.leftX, app.height, fill = darkGrey, width = 0)
    canvas.create_rectangle(app.rightX,0, app.width,app.height, fill = darkGrey,
                            width = 0)

    #colors:
    whiteBox = rgbString(223, 217, 205)
    blackBox = rgbString(58, 56, 50)
    for row in range(len(app.stage)):
        for col in range(len(app.stage[0])):
            box = app.stage[row][col]
            if box != None:
                (x, y, x1, y1) = getCellBounds(app, row, col)
                color = box.color
                if color == "black":
                    color = blackBox
                else:
                    color = whiteBox
                if box.hit:
                    color = whiteBox
                    #box.hit = False mvc violation
                if box.health > 0:
                    canvas.create_rectangle(x, y-shift, x1, y1-shift, fill=color)

