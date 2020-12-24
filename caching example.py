# This demos caching PhotoImages for increased speed
# when using a LOT of images (2500 here)

from cmu_112_graphics import *
import time

def make2dList(rows, cols):
    return [ ([0] * cols) for row in range(rows) ]

class MyApp(App):
    def appStarted(self):
        url = 'https://tinyurl.com/great-pitch-gif'
        self.image1 = self.loadImage(url)
        self.margin = 20
        self.rows = self.cols = 50
        self.images = make2dList(self.rows, self.cols)
        for row in range(self.rows):
            for col in range(self.cols):
                self.images[row][col] = self.scaleImage(self.image1, 0.1)
        self.counter = 0
        self.timerDelay = 1
        self.timerResult = 'Counting to 10...'
        self.useCachedImages = False
        self.resetTimer()

    def resetTimer(self):
        self.time0 = time.time()
        self.counter = 0

    def timerFired(self):
        self.counter += 1
        if (self.counter == 10):
            duration = time.time() - self.time0
            self.timerResult = f'Last time to 10: {round(duration,1)}s'
            self.useCachedImages = not self.useCachedImages
            self.resetTimer()

    # from www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCellBounds(app, row, col):
        # aka "modelToView"
        # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
        gridWidth  = app.width - 2*app.margin
        gridHeight = app.height - 2*app.margin
        columnWidth = gridWidth / app.cols
        rowHeight = gridHeight / app.rows
        x0 = app.margin + col * columnWidth
        x1 = app.margin + (col+1) * columnWidth
        y0 = app.margin + row * rowHeight
        y1 = app.margin + (row+1) * rowHeight
        return (x0, y0, x1, y1)

    def getCachedPhotoImage(self, image):
        # stores a cached version of the PhotoImage in the PIL/Pillow image
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def redrawAll(self, canvas):
        for row in range(self.rows):
            for col in range(self.cols):
                (x0, y0, x1, y1) = self.getCellBounds(row, col)
                cx, cy = (x0 + x1)/2, (y0 + y1)/2
                image = self.images[row][col]
                if (self.useCachedImages):
                    photoImage = self.getCachedPhotoImage(image)
                else:
                    photoImage = ImageTk.PhotoImage(image)
                canvas.create_image(cx, cy, image=photoImage)
        canvas.create_rectangle(self.width/2-250, self.height/2-100,
                                self.width/2+250, self.height/2+100,
                                fill='lightYellow')
        canvas.create_text(self.width/2, self.height/2-50,
                           text=f'Using cached images = {self.useCachedImages}',
                           font='Arial 30 bold')
        canvas.create_text(self.width/2, self.height/2,
                           text=self.timerResult, font='Arial 30 bold')
        canvas.create_text(self.width/2, self.height/2+50,
                           text=str(self.counter), font='Arial 30 bold')

MyApp(width=700, height=600)