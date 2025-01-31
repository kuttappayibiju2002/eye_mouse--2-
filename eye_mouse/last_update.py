import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QRect
import pyautogui
from PIL import ImageGrab

class EyeMouse(QWidget):
    def __init__(self):
        super().__init__()

        # Global variables to store coordinates
        self.top_left = None
        self.bottom_right = None
        self.dynamic_rect = None

        # Set the window size to the full screen size
        self.screen_width = pyautogui.size()[0]
        self.screen_height = pyautogui.size()[1]

        # set the title 
        self.setWindowTitle("Python") 
  
        self.setWindowOpacity(0.2) 
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        # To remove the titlebar
        #self.setWindowFlags(Qt.FramelessWindowHint)

        # To make the window transparent
        #self.setAttribute(Qt.WA_TranslucentBackground)

        # Make window to be always on top
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Bind mouse click events to get coordinates
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if not self.top_left:
            self.top_left = (event.x(), event.y())
            self.dynamic_rect = (event.x(), event.y(), 0, 0)
            self.update()
        else:
            self.bottom_right = (event.x(), event.y())
            self.update()

    def mouseMoveEvent(self, event):
        if self.top_left and not self.bottom_right:
            x, y = event.x(), event.y()
            self.dynamic_rect = (self.top_left[0], self.top_left[1], x - self.top_left[0], y - self.top_left[1])
            self.update()

    def paintEvent(self, event):
        if self.top_left and self.bottom_right:
            x1, y1 = self.top_left
            x2, y2 = self.bottom_right

            # Draw a green rectangle on the canvas
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            painter.drawRect(QRect(x1, y1, x2 - x1, y2 - y1))
        elif self.top_left and self.dynamic_rect:
            x, y, w, h = self.dynamic_rect
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            painter.drawRect(QRect(x, y, w, h))

    def reset_coordinates(self):
        self.top_left = None
        self.bottom_right = None
        self.dynamic_rect = None
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    eye_mouse = EyeMouse()
    eye_mouse.show()
    sys.exit(app.exec_())