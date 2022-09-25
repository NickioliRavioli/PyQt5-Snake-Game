import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.Qt import Qt
import random, math

# global variables
gridScale = 20
halfGridScale = int(gridScale/2)
canvasSizeWidth = 300
canvasSizeHeight = 300

class Food():
    def __init__(self):
        self.penFood = QtGui.QPen()
        self.penFood.setWidth(gridScale)
        self.penFood.setColor(QColor(250,0,0))

        self.PickLocation()


    def PickLocation(self):
        cols = int(canvasSizeWidth/gridScale)
        rows = int(canvasSizeHeight/gridScale)
        self.x = int(random.randint(0,cols-1)*gridScale)
        self.y = int(random.randint(0,rows-1)*gridScale)

    def Draw(self, painter):
        painter.setPen(self.penFood)
        painter.drawPoint(halfGridScale + self.x, halfGridScale + self.y)



class Snake():
    def __init__(self):
        self.Reset()

    def Reset(self):
        self.x = 0
        self.y = 0
        self.xSpeed = 1
        self.ySpeed = 0

        self.total = 1
        self.tail = []

        self.penHead = QtGui.QPen()
        self.penHead.setWidth(gridScale)
        self.penHead.setColor(QColor(200,200,250))

        self.penTail = QtGui.QPen()
        self.penTail.setWidth(gridScale)
        self.penTail.setColor(QColor(150,150,200))

        self.isDead = False
        self.drawSnake = True

        self.blinkCounter = 0



        #print("reset")

    def Update(self, food):
        
        if not self.isDead:
            if self.total == len(self.tail):
                for i in range(len(self.tail)-1):
                    self.tail[i] = self.tail[i+1]
            else:
                self.tail.append([self.x,self.y])
            if self.total > 0:
                self.tail[self.total-1] = [self.x,self.y]

            self.x = self.x + gridScale * self.xSpeed
            self.y = self.y + gridScale * self.ySpeed

            self.x = max(min(canvasSizeWidth-gridScale, self.x), 0)
            self.y = max(min(canvasSizeHeight-gridScale, self.y), 0)

            self.Eat(food)
            self.Death()
        
    def Distance(self, object):
       
        if type(object) == Food:
            dist = math.sqrt((object.x - self.x)**2 + (object.y - self.y)**2)
        if type(object) == list:
            dist = math.sqrt((object[0] - self.x)**2 + (object[1] - self.y)**2)
        return dist

    def Dir(self, a, b):
        self.xSpeed = a
        self.ySpeed = b

    def Eat(self, food):
        if self.Distance(food) < 2: #if distance to food is less then 2 pixels, eat
            food.PickLocation()
            self.total += 1
            #print(self.total)

    def Death(self):
        for i in range(len(self.tail)):
            if self.Distance(self.tail[i]) < 2:
                self.isDead = True
                break

    def Draw(self, painter):
        blinkspeed = 10
        if self.isDead:
            self.blinkCounter+=1
            if self.blinkCounter % blinkspeed == blinkspeed-1:
                self.drawSnake = not self.drawSnake

        if self.drawSnake:
            for i in range(len(self.tail)):
                painter.setPen(self.penTail)
                painter.drawPoint(halfGridScale + self.tail[i][0], halfGridScale + self.tail[i][1])

            painter.setPen(self.penHead)
            painter.drawPoint(halfGridScale + self.x, halfGridScale + self.y)
            #painter.drawRect(self.x, self.y, gridScale-3, gridScale-3)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()

        self.snek = Snake()
        self.food = Food()

        self.pen = QtGui.QPen()
        self.pen.setWidth(gridScale)
        self.pen.setColor(QColor(255,255,255))

        self.inGameFont = QtGui.QFont()
        self.inGameFont.setPixelSize(10);

        self.endGameFont = QtGui.QFont()
        self.endGameFont.setPixelSize(20);

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect(self.GameLoop)
        self.updateTimer.start(int(100))

        self.drawTimer = QtCore.QTimer(self)
        self.drawTimer.timeout.connect(self.draw_something)
        self.drawTimer.start(int(1000*(1/60)))
        #self.drawTimer.start(int(50))

        self.fadeCounter = 0
        self.fadetime = 60
        #self.backgroundColor = QColor(20,20,20)
        self.snakeIsDead = False


    def Blend(self, amount, maxColor, minColor):
        red = int((maxColor.red() - minColor.red()) * amount + minColor.red())
        green = int((maxColor.green() - minColor.green()) * amount + minColor.green())
        blue = int((maxColor.blue() - minColor.blue()) * amount + minColor.blue())
        output = QColor(red,green,blue)
        return output

    def BackgroundColor(self, color1, color2):

        if self.snek.isDead and self.snakeIsDead != self.snek.isDead:
            self.snakeIsDead = self.snek.isDead
            self.fadeCounter = self.fadetime
        else:
            self.snakeIsDead = self.snek.isDead

        if self.fadeCounter > 0:
            self.fadeCounter-=1


        self.backgroundColor = self.Blend(self.fadeCounter % self.fadetime / self.fadetime, color1, color2)


    def GameLoop(self):
        self.snek.Update(self.food)
        #self.draw_something()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.snek.Reset()
        elif event.key() == Qt.Key_Up:
            #print("Up")
            self.snek.Dir(0,-1)
        elif event.key() == Qt.Key_Down:
            #print("Down")
            self.snek.Dir(0,1)
        elif event.key() == Qt.Key_Left:
            #print("Left")
            self.snek.Dir(-1,0)
        elif event.key() == Qt.Key_Right:
            #print("Right")
            self.snek.Dir(1,0)

    def draw_something(self):

        self.BackgroundColor(QColor(250,20,20), QColor(20,20,20))
        canvas = QtGui.QPixmap(canvasSizeWidth, canvasSizeHeight)
        canvas.fill(self.backgroundColor)
        self.painter = QtGui.QPainter(canvas)
        self.painter.setPen(self.pen)

        self.food.Draw(self.painter)
        self.snek.Draw(self.painter)

        self.painter.setPen(self.pen)

        if self.snek.isDead:
            self.painter.setFont(self.endGameFont)
            #self.painter.fillRect(0,0,canvasSizeWidth, canvasSizeHeight, QColor(100,100,200))
            
            self.painter.drawText(0, 0, canvasSizeWidth, int(canvasSizeHeight/2), Qt.AlignCenter, "Game Over\nScore: " + str(self.snek.total))
        else:
            self.painter.setFont(self.inGameFont)
            self.painter.drawText(10,20, "Score: " + str(self.snek.total))


        self.painter.end()

        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
