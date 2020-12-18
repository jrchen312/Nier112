#
# This file contains all of the code necessary to run the splash screen.
# It also does file I/O for the leaderboards. 
#


from cmu_112_graphics import *
import copy

def initializeSplashScreen(self):
    #background environment (720p image)
    self.splashScreenBackground = self.loadImage('images/splashScreen.png')
    self.instructionScreenBackground = self.loadImage('images/instructions.png')
    self.startPos = self.width//2, self.height//2
    self.instructionsPos = self.width//2, self.height//2 + 40
    self.scoreboardPos = self.width//2, self.height//2 + 80

    height = 15
    width = 75
    self.startLine = (self.width//2-width, self.height//2+height, self.width//2+width, self.height//2+height)
    self.startLineVisible = False
    self.instructionLine = (self.width//2-width, self.height//2 + 40+height, self.width//2+width, self.height//2 + 40+height)
    self.instructionLineVisible = False
    self.scoreboardLine = (self.width//2-width, self.height//2 + 80+height, self.width//2+width, self.height//2 + 80+height)
    self.scoreboardLineVisible = False

    self.instructionScreen = False
    self.scoreboardScreen = False

    self.read = False
    (self.first, self.second, self.third, self.fourth, self.fifth) = 0,0,0,0,0


#ah
def mouseMoved(self, event):
    x, y = event.x, event.y
    if inButton(x, y, self.startLine):
        self.startLineVisible = True
        self.instructionLineVisible = False
        self.scoreboardLineVisible = False
    elif inButton(x,y,self.instructionLine):
        self.instructionLineVisible = True
        self.startLineVisible = False
        self.scoreboardLineVisible = False
    elif inButton(x, y, self.scoreboardLine):
        self.scoreboardLineVisible = True
        self.startLineVisible = False
        self.instructionLineVisible = False
    else:
        self.startLineVisible = False
        self.instructionLineVisible = False
        self.scoreboardLineVisible = False

def mousePressed(self, event):
    x, y = event.x, event.y
    if inButton(x, y, self.startLine):
        self.splashScreen = False
    elif inButton(x, y, self.instructionLine):
        self.instructionScreen = True
        self.scoreboardScreen = False
    elif inButton(x, y, self.scoreboardLine):
        self.scoreboardScreen = True
        self.instructionScreen = False
        leaderboardValues(self)
        

def keyPressed(self, event):
    self.instructionScreen = False
    self.scoreboardScreen = False

def inButton(x, y, button):
    x0, y0, x1, y1 = button
    y0 -= 30 #height*2
    if x0 <= x <= x1 and y0 < y < y1:
        return True
    return False

#This code is mostly copied from my hack112 (mysterious hamsters) project.
def leaderboardValues(self):
        old = readFile("leaderboards.txt")
        new = old + f",{self.score}"
        writeFile("leaderboards.txt", new)
        leaders = new.split(",")
        leaders = [int(num) for num in leaders if len(num) > 0]
        while len(leaders) < 5:
            leaders.append(0)
        leaders.sort()
        self.first = leaders[-1]
        self.second = leaders[-2]
        self.third = leaders[-3]
        self.fourth = leaders[-4]
        self.fifth = leaders[-5]

# From: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


#drawing

def drawSplashScreen(self, canvas):
    canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(self.splashScreenBackground))
    if self.instructionScreen:
        instructionScreen(self, canvas)
    elif self.scoreboardScreen:
        scoreboardScreen(self, canvas)
    else:
        splashScreen(self, canvas)
    


def instructionScreen(self, canvas):
    canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(self.instructionScreenBackground))
    

    #wow, 
def scoreboardScreen(self, canvas):
    canvas.create_text(self.width//2, self.height//2 - 30, font = "calibri 20",
                        text = "Scoreboard:", fill = "white")
    canvas.create_text(self.width//2, self.height//2, font = "calibri 15",
                            text = f"1. {self.first}", fill = "white")
    canvas.create_text(self.width//2, self.height//2 + 25, font = "calibri 15",
                        text = f"2. {self.second}", fill = "white")
    canvas.create_text(self.width//2, self.height//2 + 50, font = "calibri 15",
                        text = f"3. {self.third}", fill = "white")
    canvas.create_text(self.width//2, self.height//2 + 75, font = "calibri 15",
                        text = f"2. {self.fourth}", fill = "white")
    canvas.create_text(self.width//2, self.height//2 + 100, font = "calibri 15",
                        text = f"3. {self.fifth}", fill = "white")

def splashScreen(self, canvas):
    
    canvas.create_text(self.startPos, text="Start", font="calibri 22", fill="white")
    canvas.create_text(self.instructionsPos, text="Instructions", font = "calibri 22", fill = "white")
    canvas.create_text(self.scoreboardPos, text="Scoreboard", font = "calibri 22", fill="white")

    width = 75
    height = 15
    #canvas.create_rectangle(self.width//2-width, self.height//2-height, self.width//2+width, self.height//2+height)
    if self.startLineVisible:
        canvas.create_line(self.startLine, fill = "white", width = 2)
    if self.instructionLineVisible:
        canvas.create_line(self.instructionLine, fill="white", width = 2)
    if self.scoreboardLineVisible:
        canvas.create_line(self.scoreboardLine, fill="white", width = 2)
     