import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtCore import Qt, QSize

class Spinner(QLabel):
    def __init__(self, parent, gif_path, width=50, height=50, is_static=True):
        super().__init__(parent)
        self.setParent(parent)
        self.setFixedSize(width, height)
        self.gif_path = gif_path
        self.width = width
        self.height = height
        self.parent = parent
        self.is_static = is_static
        self.setStyleSheet("background: transparent;")
        self.spinner = None

    def start(self):
        self.center()
        if self.is_static:
            self.spinner = QPixmap(self.gif_path)
            self.setPixmap(self.spinner.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.show()
        else:
            self.spinner = QMovie(self.gif_path)
            self.spinner.setScaledSize(QSize(self.width, self.height))
            self.setMovie(self.spinner)
            self.spinner.start()
            self.show()

    def delete(self):
        if self.spinner:
            if not self.is_static:
                self.spinner.stop()
                self.spinner.deleteLater()
            self.spinner = None
            self.hide()

    def center(self):
        window_size = self.parent.size()
        spinner_size = self.sizeHint()

        x = (window_size.width() - self.width) // 2
        y = (window_size.height() - self.height) // 2
        print(x,y)

        self.move(x, y)
