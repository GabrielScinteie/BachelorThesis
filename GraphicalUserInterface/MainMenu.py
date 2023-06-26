from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog

from utils import colors
from MainWindow import app
from PlayMenu import PlayMenu


class MainMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.window_size = window_size
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GameLogic')

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play)

        self.settings_button = QPushButton('Settings', self)
        self.settings_button.clicked.connect(self.settings)

        self.puzzles_button = QPushButton("Puzzle", self)
        self.puzzles_button.clicked.connect(self.puzzle)

        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.quit)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.play_button)
        vbox.addStretch(1)
        vbox.addWidget(self.settings_button)
        vbox.addStretch(1)
        vbox.addWidget(self.puzzles_button)
        vbox.addStretch(1)
        vbox.addWidget(self.quit_button)
        vbox.addStretch(1)
        vbox.setAlignment(Qt.AlignHCenter)

        self.setLayout(vbox)

        self.setStyleSheet(f"background-color: {colors['Background']};")
        self.resize(self.window_size, self.window_size)
        self.style_buttons()

    def style_buttons(self):
        font = QtGui.QFont()
        font.setPointSize(20)  # set the font size to 20

        self.play_button.setFont(font)
        self.quit_button.setFont(font)
        self.settings_button.setFont(font)
        self.puzzles_button.setFont(font)

        style = """
        QPushButton {
            background-color: %s;
            color: %s;
        }
        QPushButton:hover {
            background-color: %s;
        }
        """ % (colors['Accent'], colors['Text'], colors['Hover'])

        self.play_button.setStyleSheet(style)
        self.quit_button.setStyleSheet(style)
        self.puzzles_button.setStyleSheet(style)
        self.settings_button.setStyleSheet(style)

        self.play_button.setFixedWidth(self.window_size // 3)
        self.quit_button.setFixedWidth(self.window_size // 3)
        self.puzzles_button.setFixedWidth(self.window_size // 3)
        self.settings_button.setFixedWidth(self.window_size // 3)

    def quit(self):
        app.quit()

    def settings(self):
        from SettingsMenu import SettingsMenu
        self.hide()

        self.settings = SettingsMenu(self.window_size)
        self.settings.show()

    def puzzle(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_path:
            with open(file_path, "r") as file:
                file_contents = file.read()
                print(file_contents)

    def play(self):
        self.hide()
        self.game = PlayMenu(self.window_size)  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
