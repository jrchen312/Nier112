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

class LargeBox(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = "black"

def appStarted(self):

    #large grid:
    self.lRows = 10
    self.lCols = 10
    self.lSize = 60

    #small grid:
    self.sSize = 10
    self.sRows = self.lRows * self.lSize // self.sSize #200?
    self.sCols = self.lCols * self.lSize // self.sSize #200

    #stage (placement of a few black boxes)
    self.stage = [[None] * self.lCols for __ in range(self.lRows)]
    self.stage = generateSimpleMaze(self, self.stage)

    #etc drawing
    self.upperRightCorner = (self.width//2 - (self.lRows * self.lSize) // 2, 
                             self.height//2 - (self.lCols * self.lSize // 2))

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


def timerFired(self):
    pass


#
# model to view and view to model stuff
#
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

    


#################################################
# main
#################################################

runApp(width = 1280, height = 720)
