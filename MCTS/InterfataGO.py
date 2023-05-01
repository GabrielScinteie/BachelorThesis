from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from go import GoAPI, GoGameState, GoMove
import sys

class Board:
    def __init__(self):
        self.matrix = [[0 for _ in range(7)] for _ in range(7)]


class Cell(QLabel):
    clicked = pyqtSignal(int, int)

    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.Piece = None
        self.setFixedSize(45, 45)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: chocolate; border: 0.5px solid black;")
        self.x = 0

    def mousePressEvent(self, event):
        self.clicked.emit(self.row, self.col)

    def paintEvent(self, event):
        print(self.x)
        self.x += 1
        super().paintEvent(event)
        if self.Piece:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(255, 0, 0))
            radius = 10
            rect = self.contentsRect()
            x = rect.center().x() - radius
            y = rect.center().y() - radius
            painter.drawEllipse(x, y, radius * 2, radius * 2)
            painter.end()


class App(QWidget):
    def __init__(self, goInitialState):
        super().__init__()
        self.title = "Grid of Clickable Cells"
        self.left = 100
        self.top = 100
        self.width = 250
        self.height = 250
        self.goState = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_grid()
        self.show()

    def create_grid(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        for row in range(self.goState.size):
            for col in range(self.goState.size):
                cell = Cell(row, col)
                self.grid.addWidget(cell, row, col)
                # Connect the clicked signal to the draw_circle slot
                cell.clicked.connect(self.draw_circle)
        self.setLayout(self.grid)

    def draw_circle(self, row, col):
        cell = self.grid.itemAtPosition(row, col).widget()
        print(row, col)
        if not cell.Piece:
            cell.Piece = self.goState.next_to_move
            self.goState.move(GoMove(row, col, self.goState.next_to_move))
            cell.update()
        # else:
        #     cell.Piece = False
        #     cell.update()
        #     self.goGame.board[row][col] = 0


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Menu')

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.play_game)

        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(QApplication.instance().quit)

        vbox = QVBoxLayout()
        vbox.addWidget(play_button)
        vbox.addWidget(quit_button)

        self.setLayout(vbox)

    def play_game(self):
        self.game = App(GoAPI(5))  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
        self.hide()  # Hide the Main Menu


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())

