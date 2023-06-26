from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout

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

        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.quit)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.play_button)
        vbox.addStretch(1)
        vbox.addWidget(self.settings_button)
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
        self.settings_button.setStyleSheet(style)

        self.play_button.setFixedWidth(self.window_size // 3)
        self.quit_button.setFixedWidth(self.window_size // 3)
        self.settings_button.setFixedWidth(self.window_size // 3)

    def quit(self):
        app.quit()

    def settings(self):
        from SettingsMenu import SettingsMenu
        self.hide()

        self.settings = SettingsMenu(self.window_size)
        self.settings.show()

    def hideEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

    def play(self):
        self.hide()

        self.game = PlayMenu(self.window_size)  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
