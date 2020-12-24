#
# This code spawns in the terrain and draws it. 
#

from cmu_112_graphics import *
import random
import math
import enemy


# appStarted variables. 
def loadStage(self):
    #background environment (720p image)
    self.environment = self.loadImage('images/environment.png')

    #Obsolete stage:
    self.margin = 25
    self.sideMargin = 150
    self.topMargin = 75 
    self.cellSize = 50 
    self.rows = (self.height - self.margin) // self.cellSize
    self.cols = (self.width - self.margin) // self.cellSize
    self.stage = [[None]*self.cols for _ in range(self.rows)]
    self.startRow = 1

    #islands:
    self.islands = []

    #2d platform system
    stage = [[(-100, self.height-200), (self.width//2, self.height-200)]]
    self.platforms = []
    self.maxPlatforms = 10
    self.platforms = generatePlatforms(self, stage, 2, 0)
    self.platformHeight = 30
    

#format: list. coord of start pos, coord of end pos
def generatePlatforms(self, stage, number, deviation):
    if len(self.platforms) > self.maxPlatforms:
        return
    #spawns more gunners than bipeds. 
    spawn = [0,1,1]
    for _ in range(number):
        
        lastCoord = stage[-1]
        y = lastCoord[0][1]
        x = lastCoord[1][0]

        if len(self.platforms) == self.maxPlatforms:
            lowerX = x + 100
            lowerY = self.height-50
            upperX = lowerX + 1280
            stage.append([(lowerX, lowerY), (upperX, lowerY)])
            enemy.spawnBoss(self, lowerX + 1000 - deviation, lowerY - 100)
            self.xLimit = lowerX + 800 - deviation
            createIslands(self, 2, lowerX, lowerY)
            return stage
        upperY = max(self.height - self.height//3, y - 130)
        lowerY = min(self.height - 50, y + 130)

        lowerX = x + 100
        upperX = x + 200

        difference = 0
        
        #the circuis and the crew and they're just passing through
        modifier = min(280, 180 + max(1, 10*len(self.platforms)))
        while difference < modifier:
            x0 = random.randint(lowerX, upperX)
            y0 = random.randint(upperY, lowerY)
            difference = abs(x - x0) + abs(y - y0)
        #how long each platform is
        length = random.randint(650, 1000)

        if y0 > y:
            createIslands(self, 2, x0, y)
        stage.append([(x0, y0),(x0 + length, y0)])

        option = random.choice(spawn)
        if option == 1:
            #length of the track that the gunner patrols.
            patrolLength = (length - 262) / 2
            enemy.spawnGunner(self, x0 + length//2 - deviation, y0 - 100, patrolLength)
        else:
            enemy.spawnBiped(self, x0 + length*(4/5) - deviation, y0 - 100)
    return stage

#Really similar to the platforms, but islands have different attributes. 
def createIslands(self, number, x, y):
    #arbitrary numbers (y should be at least 160 pixels)
    y -= random.randint(160, 170)
    x -= random.randint(80, 160)
    x0, y0 = x, y

    length = random.randint(182, 300)
    x1, y1 = x0 + length, y0
    self.islands.append([(x0, y0),(x1, y1)])
    x0, y0 = x1, y1-random.randint(140, 170)

    for __ in range(number):
        length = random.randint(182, 300)
        x1, y1 = x0 + length, y0
        if y0 > 200:
            self.islands.append([(x0, y0),(x1, y1)])
            self.islands.append([(x0-length*2.7, y0+ 10), (x0-length*1.5, y0+10)])

        x0, y0 = x1, y1-random.randint(140, 170)


def generateNewTerrain(self, deviation):
    #first, check if we need new terrain
    lastCoord = self.platforms[-1]
    x = lastCoord[1][0]
    if x - deviation < self.width * 2:
        newPlatforms = generatePlatforms(self, self.platforms, 1, deviation)
        if newPlatforms != None:
            self.platforms = newPlatforms


# returns the y-position of the platform closest to the character.
def getPosition(self, x, y):
    height = self.height + 500
    for i in range(len(self.platforms)):
        coord1 = self.platforms[i][0]
        coord2 = self.platforms[i][1]
        if coord1[0] <= x <= coord2[0] and y <= coord1[1] + self.platformHeight:
            #character is on one of the platforms:
            if coord1[1] - y < height:
                height = coord1[1]
    for i in range(len(self.islands)):
        coord1 = self.islands[i][0]
        coord2 = self.islands[i][1]
        if coord1[0] <= x <= coord2[0] and y <= coord1[1] + self.platformHeight:
            if coord1[1] - y < height:
                height = coord1[1]

    if height != self.height + 500:
        return height
    return self.height + 500

#takes in the MyApp object, and traits of the enemy, including:
# angle, x0 position, y0 position, and the direction of the robot with respect
# to the main character ('left' or 'right')
#Returns True if a platform is blocking the sight, and False if there isn't. 
def blocked(self, angle, x0, y0, direction):
    for i in range(len(self.islands)):
        coord1 = self.islands[i][0]
        x, y = coord1
        coord1 = x-self.deviation, y
        coord2 = self.islands[i][1]
        x, y = coord2
        coord2 = x-self.deviation + self.platformHeight * math.cos(math.pi/3), y

        if 0 <= coord2[0] <= self.width:
            height = y0 - coord2[1]

            #tan of the angle could be zero.
            try:
                adj =  height / abs(math.tan(angle))
            except:
                adj = height / .001

            if direction == "left":
                potentialX = x0 - adj
            else:
                potentialX = x0 + adj

            #the X value is in the range of the platform's X values. 
            if coord1[0] <= potentialX <= coord2[0]:
                return True

    return False

def inScreen(app, coord1, coord2):
    x0, y0 = coord1
    x1, y1 = coord2
    if (x0 < 0 and x1 < 0) or (x0 >= app.width and x1 >= app.width):
        return False
    return True

def getCachedPhotoImage(self, image):
    # stores a cached version of the PhotoImage in the PIL/Pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def drawBackgroundImage(self, canvas):
    photoImage = getCachedPhotoImage(self, (self.environment))
    canvas.create_image(self.width/2, self.height/2, image=photoImage)

def drawBackground(self, canvas, defaultPos, camPos):
    shift = camPos - defaultPos

    # Draw background:
    drawBackgroundImage(self, canvas)

    for i in range(len(self.platforms)):
        platformHeight = self.platformHeight
        coord1 = self.platforms[i][0]
        coord2 = self.platforms[i][1]
        x0, y0 = coord1
        coord1 = (x0 - shift, y0)
        x, y = coord2
        x -= shift
        coord2 = (x, y)
        #canvas.create_line(coord1, coord2) (decrease lag)
        if inScreen(self, coord1, coord2):
            canvas.create_rectangle(coord1, x, y + platformHeight, fill = 'green')

            x1 = x + platformHeight * math.cos(math.pi/3)
            y1 = y - platformHeight * math.sin(math.pi/3)
            canvas.create_polygon(x, y, x1, y1, x1, y1+platformHeight, x, 
                                y+platformHeight, fill='light green', 
                                outline='black')
            x10, y10 = coord1
            x11 = x10 + platformHeight * math.cos(math.pi/3)
            y11 = y10 - platformHeight * math.sin(math.pi/3)
            canvas.create_polygon(x, y, x1, y1, x11, y11, x10, y10, 
                                fill = "light green", outline="black")

    darkYellow = rgbString(204,204,0)
    lightYellow = rgbString(255,255,153)
    for i in range(len(self.islands)):
        coord1 = self.islands[i][0]
        coord2 = self.islands[i][1]
        x0, y0 = coord1
        coord1 = (x0 - shift, y0)
        x, y = coord2
        x -= shift
        coord2 = (x, y)

        if inScreen(self, coord1, coord2):
            canvas.create_rectangle(coord1, x, y + platformHeight, fill = darkYellow)

            x1 = x + platformHeight * math.cos(math.pi/3)
            y1 = y - platformHeight * math.sin(math.pi/3)
            canvas.create_polygon(x, y, x1, y1, x1, y1+platformHeight, x, 
                                y+platformHeight, fill=lightYellow, 
                                outline='black')
            x10, y10 = coord1
            x11 = x10 + platformHeight * math.cos(math.pi/3)
            y11 = y10 - platformHeight * math.sin(math.pi/3)
            canvas.create_polygon(x, y, x1, y1, x11, y11, x10, y10, 
                                fill = lightYellow, outline="black")

#code from https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    # Don't worry about the :02x part, but for the curious,
    # it says to use hex (base 16) with two digits.
    return f'#{r:02x}{g:02x}{b:02x}'