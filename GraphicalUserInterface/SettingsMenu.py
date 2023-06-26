from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QHBoxLayout, QPushButton, QVBoxLayout

from utils import colors
import utils
from MainMenu import MainMenu


class SettingsMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle("GameLogic")
        self.window_size = window_size
        self.resize(window_size, window_size)
        self.init_ui()

    def init_ui(self):
        # Create labels and checkboxes
        self.audio_label = QLabel("Audio")
        self.audio_checkbox = QCheckBox()

        # Setup checkboxes
        self.audio_checkbox.stateChanged.connect(self.audio_checkbox_changed)

        # Create layout for labels and checkboxes
        audio_layout = QHBoxLayout()
        audio_layout.addStretch(1)
        audio_layout.addWidget(self.audio_label)
        audio_layout.addWidget(self.audio_checkbox)
        audio_layout.addStretch(1)

        # Create back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch(1)

        # Create vertical layout for settings and back button
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignHCenter)

        main_layout.addStretch(2)
        main_layout.addLayout(audio_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch(2)

        # Set main layout
        self.setLayout(main_layout)
        self.style_buttons()

    def audio_checkbox_changed(self, new_state):
        utils.soundOn = new_state

    def back(self):
        self.hide()
        self.mainMenu = MainMenu(self.window_size)
        self.mainMenu.show()

    def style_buttons(self):
        font = QtGui.QFont()
        font.setPointSize(20)  # set the font size to 20

        self.back_button.setFont(font)
        self.audio_label.setFont(font)

        style = """
           QPushButton {
               background-color: %s;
               color: %s;
           }
           QPushButton:hover {
               background-color: %s;
           }
           """ % (colors['Accent'], colors['Text'], colors['Hover'])

        self.back_button.setStyleSheet(style)
        self.audio_label.setStyleSheet(style)
        self.back_button.setFixedWidth(self.window_size // 3)
        self.audio_label.setFixedWidth(self.window_size // 3)
