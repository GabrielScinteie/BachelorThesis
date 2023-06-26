from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

from utils import colors


class PlayMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle('GameLogic')
        self.window_size = window_size
        self.resize(self.window_size, self.window_size)
        self.initUI()


    def initUI(self):
        # Create the dropdown menus
        self.player_1_dropdown = QComboBox()
        self.player_1_dropdown.addItems(['Human', 'Computer'])

        self.player_2_dropdown = QComboBox()
        self.player_2_dropdown.addItems(['Human', 'Computer'])

        self.vs_label = QLabel("VS")

        choose_player_layout = QHBoxLayout()

        choose_player_layout.addStretch(1)
        choose_player_layout.addWidget(self.player_1_dropdown)
        choose_player_layout.addStretch(1)
        choose_player_layout.addWidget(self.vs_label)
        choose_player_layout.addStretch(1)
        choose_player_layout.addWidget(self.player_2_dropdown)
        choose_player_layout.addStretch(1)

        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignHCenter)

        # Create the "Start Game" button
        self.start_button = QPushButton('Start Game')
        self.start_button.clicked.connect(self.start_game)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.back)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addSpacing(100)
        buttons_layout.addWidget(self.back_button)

        # Create a layout for the dropdown menus and button
        main_layout = QVBoxLayout()

        main_layout.addStretch(1)
        main_layout.addLayout(choose_player_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch(1)

        # Set the layout for the main window
        self.setLayout(main_layout)
        self.style_buttons()

    def style_buttons(self):
        font = QtGui.QFont()
        font.setPointSize(20)  # set the font size to 20
        font_dropdown = QtGui.QFont()
        font_dropdown.setPointSize(16)  # set the font size to 20

        self.start_button.setFont(font)
        self.back_button.setFont(font)
        self.vs_label.setFont(font)
        self.player_1_dropdown.setFont(font_dropdown)
        self.player_2_dropdown.setFont(font_dropdown)

        button_style = """
        QPushButton {
            background-color: %s;
            color: %s;
        }
        QPushButton:hover {
            background-color: %s;
        }
        """ % (colors['Accent'], colors['Text'], colors['Hover'])

        dropdown_style = '''
        QComboBox QAbstractItemView {{
          background: {};
          selection-background-color: {};
        }}
        QComboBox {{
          background: {};
        }}
        '''.format(colors['Accent'], colors['Hover'], colors['Accent'])

        self.start_button.setStyleSheet(button_style)
        self.back_button.setStyleSheet(button_style)
        self.player_1_dropdown.setStyleSheet(dropdown_style)
        self.player_2_dropdown.setStyleSheet(dropdown_style)

        pallete_dropdown1 = self.player_1_dropdown.palette()
        pallete_dropdown1.setColor(pallete_dropdown1.Highlight, QColor(colors['Hover']))
        self.player_1_dropdown.setPalette(pallete_dropdown1)

        pallete_dropdown2 = self.player_2_dropdown.palette()
        pallete_dropdown2.setColor(pallete_dropdown2.Highlight, QColor(colors['Hover']))
        self.player_2_dropdown.setPalette(pallete_dropdown1)

        self.start_button.setFixedWidth(self.window_size // 3)
        self.back_button.setFixedWidth(self.window_size // 3)
        self.player_1_dropdown.setFixedWidth(self.window_size // 4)
        self.player_2_dropdown.setFixedWidth(self.window_size // 4)

    def back(self):
        from MainMenu import MainMenu
        self.hide()
        self.mainMenu = MainMenu(self.window_size)
        self.mainMenu.show()

    def start_game(self):
        from GameWindow import GameWindow
        # Retrieve the selected options from the dropdown menus
        option1 = self.player_1_dropdown.currentText()
        option2 = self.player_2_dropdown.currentText()

        # Do something with the selected options (e.g. start the game with these options)
        print(f'Starting game with options: {option1}, {option2}')

        self.hide()

        self.game = GameWindow(self.window_size, option1, option2)  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
