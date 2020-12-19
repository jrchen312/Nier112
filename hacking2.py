#hacking game v2

"""
Have a large grid system. this grid will contain stage elements and the border
of the area.

Have a small grid system that's like 5x5 pixels, The ai uses the smaller grid
to pathfind around the map and towards the player

Thus, the player and enemies will move around based on the small grid system
The small grid system could have an attribute that's like "Oh, this is a wall"
or something idk 

"""
from cmu_112_graphics import *
import random
import math

class LargeBox(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = "black"
    
    def __repr__(self):
        return f"box at ({self.row}, {self.col})"

def appStarted(self):
    self.timerDelay = 20
    #large grid:
    self.lRows = 10
    self.lCols = 10
    self.lSize = 60

    #small grid:
    self.sSize = 12
    self.sRows = self.lRows * self.lSize // self.sSize #200?
    self.sCols = self.lCols * self.lSize // self.sSize #200

    #stage (placement of a few black boxes)
    self.stage = [[None] * self.lCols for __ in range(self.lRows)]
    self.stage = generateSimpleMaze(self, self.stage)

    #etc drawing
    self.upperRightCorner = (self.width//2 - (self.lRows * self.lSize) // 2, 
                             self.height//2 - (self.lCols * self.lSize // 2))

    #pointer
    self.pointerRow = 0
    self.pointerCol = 0
    self.pointerAngle = math.pi/2
    self.pointerGoal = None

def generateSimpleMaze(self, matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    for row in range(rows):
        for col in range(cols):
            choice = random.randint(0,3)
            if choice == 0:
                matrix[row][col] = LargeBox(row, col)
    
    return matrix

#
# Control
#
def mousePressed(self, event):
    print(getLCell(self, event.x, event.y))

def keyPressed(self, event):
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
        #self.pointerRow += shift[0] * 3
        #self.pointerCol += shift[1] * 3

def setPointerGoal(self, shift):
    for i in range(1, 4):
        newRow, newCol = self.pointerRow + shift[0] * i, self.pointerCol + shift[1] * i
        if not isLegalPointerMove(self, (shift[0] * i,  shift[1] * i)):
            i -= 1
            break
    self.pointerGoal = shift[0] * i, shift[1] * i
    print(f"goal: {self.pointerGoal}, {i}")

def mouseMoved(self, event):
    #calculate new angle
    x0, y0, x1, y1 = getSCellBounds(self, self.pointerRow, self.pointerCol)
    x = x0 + self.sSize // 2
    y = y0 + self.sSize // 2

    yDif = event.y - y
    xDif = x - event.x
    try:
        newAngle = math.atan(yDif/xDif)
    except:
        newAngle = math.atan(-yDif/.01)
    if xDif > 0:
        newAngle = newAngle + math.pi
    self.pointerAngle = newAngle 

def timerFired(self):
    movePointer(self)


def movePointer(self):
    if self.pointerGoal != None:
        dRow, dCol = self.pointerGoal
        if dRow > 0:
            self.pointerRow += 1
            dRow -= 1
        elif dRow < 0:
            self.pointerRow -= 1
            dRow += 1
        elif dCol > 0:
            self.pointerCol += 1
            dCol -= 1
        elif dCol < 0:
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
            print(self.stage[row][col])
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
    col = (x - xShift) // self.lSize
    row = (y - yShift) // self.lSize
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
    col = (x - xShift) // self.sSize
    row = (y - yShift) // self.sSize
    return row, col
#
# View
#
def redrawAll(self, canvas):
    drawBackground(self, canvas)
    drawLGrid(self, canvas)
    drawPointer(self, canvas)
    #drawSGrid(self, canvas)

#code from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def drawBackground(self, canvas):
    darkGrey = rgbString(60, 57, 51)
    stageColor = rgbString(202, 195, 171)
    frameFactor = self.lSize * self.lRows
    canvas.create_rectangle(0,0,self.width, self.height, fill = darkGrey)
    canvas.create_rectangle(self.upperRightCorner, self.upperRightCorner[0] + frameFactor, 
                            self.upperRightCorner[1] + frameFactor, fill = stageColor)

#oh wait
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

def drawSGrid(self, canvas):
    rows, cols = self.sRows, self.sCols
    for row in range(rows):
        for col in range(cols):
            x0, y0, x1, y1 = getSCellBounds(self, row, col)
            smallShift = 0
            x0, y0, x1, y1 = x0 + smallShift, y0 + smallShift, x1 - smallShift, y1 - smallShift
            canvas.create_rectangle(x0, y0, x1, y1)

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

    canvas.create_rectangle(getSCellBounds(self, self.pointerRow, self.pointerCol), fill = "red")


#################################################
# main
#################################################

runApp(width = 1280, height = 720)
