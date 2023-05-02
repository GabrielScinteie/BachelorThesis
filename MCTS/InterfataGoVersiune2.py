import threading
from copy import copy, deepcopy

from go import GoGameState, GoAPI, GoMove
import pyttsx3 as pyttsx3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPointF, QTimer, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsItem, \
    QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QLabel, QCheckBox
import speech_recognition as sr
import sys
import json

colors = {}
microphoneOn = False
soundOn = False

class SettingsMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle("Go")
        self.window_size = window_size
        self.resize(window_size, window_size)
        self.init_ui()

    def init_ui(self):
        # Create labels and checkboxes
        self.audio_label = QLabel("Audio")
        self.microphone_label = QLabel("Microphone")
        self.audio_checkbox = QCheckBox()
        self.microphone_checkbox = QCheckBox()

        # Setup checkboxes
        self.audio_checkbox.setChecked(soundOn)
        self.microphone_checkbox.setChecked(microphoneOn)
        self.audio_checkbox.stateChanged.connect(self.audio_checkbox_changed)
        self.microphone_checkbox.stateChanged.connect(self.microphone_checkbox_changed)

        # Create layout for labels and checkboxes
        audio_layout = QHBoxLayout()
        audio_layout.addStretch(1)
        audio_layout.addWidget(self.audio_label)
        audio_layout.addWidget(self.audio_checkbox)
        audio_layout.addStretch(1)

        microphone_layout = QHBoxLayout()
        microphone_layout.addStretch(1)
        microphone_layout.addWidget(self.microphone_label)
        microphone_layout.addWidget(self.microphone_checkbox)
        microphone_layout.addStretch(1)

        # Create back button
        self.back_button = SoundButton("Back")
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
        main_layout.addLayout(microphone_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch(2)

        # Set main layout
        self.setLayout(main_layout)
        self.style_buttons()

    def audio_checkbox_changed(self, new_state):
        global soundOn
        soundOn = new_state

    def microphone_checkbox_changed(self, new_state):
        global microphoneOn
        microphoneOn = new_state

    def back(self):
        self.hide()
        self.mainMenu = MainMenu(self.window_size)
        self.mainMenu.show()

    def style_buttons(self):
        font = QtGui.QFont()
        font.setPointSize(20)  # set the font size to 20

        self.back_button.setFont(font)
        self.microphone_label.setFont(font)
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
        self.microphone_label.setStyleSheet(style)
        self.back_button.setFixedWidth(self.window_size // 3)
        self.audio_label.setFixedWidth(self.window_size // 3)
        self.microphone_label.setFixedWidth(self.window_size // 3)


class SoundButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def enterEvent(self, event):
        if soundOn:
            t = threading.Thread(target=self.read_text)
            t.start()

    def read_text(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(self.text())
            engine.runAndWait()
        except:
            pass


def read_colors_from_file(filepath):
    global colors
    with open(filepath) as f:
        colors = json.load(f)


class MainMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.window_size = window_size
        # Audio recognition
        if microphoneOn:
            self.audioRecognition()
        self.initUI()

    def audioRecognition(self):
        self.r = sr.Recognizer()
        self.stop_listening = threading.Event()
        # start listening thread
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.start()

    def initUI(self):
        self.setWindowTitle('Go')

        self.play_button = SoundButton('Play', self)
        self.play_button.clicked.connect(self.play)

        self.settings_button = SoundButton('Settings', self)
        self.settings_button.clicked.connect(self.settings)

        self.quit_button = SoundButton('Quit', self)
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

    def listen(self):
        while not self.stop_listening.is_set():
            with sr.Microphone() as source:
                print('Say something!')
                audio = self.r.listen(source)

            try:
                text = self.r.recognize_google(audio).lower()
                print(f"You said: {text}")
                if "click button" in text:
                    if "play" in text:
                        self.play_button.click()
                    if "settings" in text:
                        self.settings_button.click()
                    if "quit" in text:
                        self.quit_button.click()

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

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
        if microphoneOn:
            self.stop_listening.set()
            app.quit()
            self.listening_thread.join()
        else:
            app.quit()

    def settings(self):
        if microphoneOn:
            self.stop_listening.set()
            self.hide()  # Hide the Main Menu
            self.listening_thread.join()
        else:
            self.hide()

        self.settings = SettingsMenu(self.window_size)
        self.settings.show()

    def hideEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

    def play(self):
        if microphoneOn:
            self.stop_listening.set()
            self.hide()  # Hide the Main Menu
            self.listening_thread.join()
        else:
            self.hide()

        self.game = PlayMenu(self.window_size)  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget


class PlayMenu(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle('Go')
        self.window_size = window_size
        self.resize(self.window_size, self.window_size)
        self.initUI()
        if microphoneOn:
            self.audioRecognition()

    def audioRecognition(self):
        self.r = sr.Recognizer()
        self.stop_listening = threading.Event()
        # start listening thread
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.start()

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
        self.start_button = SoundButton('Start Game')
        self.start_button.clicked.connect(self.start_game)

        self.back_button = SoundButton('Back')
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

    def listen(self):
        while not self.stop_listening.is_set():
            with sr.Microphone() as source:
                print('Say something!')
                audio = self.r.listen(source)
            try:
                text = self.r.recognize_google(audio).lower()
                print(f"You said: {text}")
                if "click button" in text:
                    if "start" in text:
                        self.start_button.click()
                    if "back" in text:
                        self.back_button.click()
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

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
        self.hide()
        if microphoneOn:
            self.stop_listening.set()
            self.listening_thread.join()
        self.mainMenu = MainMenu(self.window_size)
        self.mainMenu.show()


    def start_game(self):
        # Retrieve the selected options from the dropdown menus
        option1 = self.player_1_dropdown.currentText()
        option2 = self.player_2_dropdown.currentText()

        # Do something with the selected options (e.g. start the game with these options)
        print(f'Starting game with options: {option1}, {option2}')
        if microphoneOn:
            self.stop_listening.set()
            self.hide()  # Hide the Main Menu
            self.listening_thread.join()
        else:
            self.hide()

        self.game = GameWidget(self.window_size)  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget


class GameWidget(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle('Go')
        self.window_size = window_size
        # Create the Board widget
        self.board = GoBoard(5)

        # Create the buttons
        self.pass_button = SoundButton("Pass")
        self.pass_button.clicked.connect(self.board.pass_turn)
        self.back_to_menu_button = SoundButton("Menu")
        self.back_to_menu_button.clicked.connect(self.show_confirmation_dialog)

        # Add the buttons to a layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.back_to_menu_button)

        # Create a widget to hold the buttons
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Create a layout for the board and button widgets
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(self.board)
        main_layout.addWidget(button_widget)

        # Set the main layout for the GameWidget
        self.setLayout(main_layout)
        self.resize(self.window_size, self.window_size)

        self.style_buttons()

    def style_buttons(self):
        font = QtGui.QFont()
        font.setPointSize(20)  # set the font size to 20

        self.pass_button.setFont(font)
        self.back_to_menu_button.setFont(font)

        style = """
           QPushButton {
               background-color: %s;
               color: %s;
           }
           QPushButton:hover {
               background-color: %s;
           }
           """ % (colors['Accent'], colors['Text'], colors['Hover'])

        self.pass_button.setStyleSheet(style)
        self.back_to_menu_button.setStyleSheet(style)

        self.pass_button.setFixedWidth(self.window_size // 3)
        self.back_to_menu_button.setFixedWidth(self.window_size // 3)


    def show_confirmation_dialog(self):
        # Create the confirmation dialog
        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle("Iesire joc")
        confirm_dialog.setText("Esti sigur ca doresti sa abandonezi meciul?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Execute the confirmation dialog
        response = confirm_dialog.exec()

        # Check the user's response
        if response == QMessageBox.Yes:
            self.back_to_menu()

    def back_to_menu(self):
        self.hide()
        self.mainMenu = MainMenu(self.window_size)
        self.mainMenu.show()



class GoBoard(QGraphicsView):
    def __init__(self, board_size):
        super().__init__()
        self.margin = 50
        self.board_size = board_size
        self.grid_size = 80
        self.piece_size = self.grid_size / 2

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.grid_size * (self.board_size - 1), self.grid_size * (self.board_size - 1))
        self.setScene(self.scene)
        self.draw_board()
        self.setFixedSize(self.grid_size * (self.board_size - 1) + 2 * self.margin,
                          self.grid_size * (self.board_size - 1) + 2 * self.margin)

        goInitialState = GoAPI(board_size)
        self.goState = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_game_end)
        self.timer.start(100)

    def reset_board(self):
        goInitialState = GoAPI(self.board_size)
        self.goState = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)
        self.scene.clear()
        self.draw_board()

    def check_game_end(self):
        # Check if game is over
        if not self.goState.running:
            result = self.goState.game_result
            score = self.goState.get_score()

            winner = 'Negru'
            if result == '-1':
                winner = 'Alb'

            popup = QMessageBox()
            popup.setWindowTitle("Final joc")
            popup.setText(f'Punctaj negru: {score[0]}\nPunctaj alb:{score[1]}\n\n{winner} a castigat!')
            popup.setStandardButtons(QMessageBox.Ok)
            popup.exec_()

            self.reset_board()

    def draw_board(self):
        pen = QPen(QColor("black"), 2)
        brush = QBrush(QColor(139, 69, 19))
        for row in range(self.board_size - 1):
            for col in range(self.board_size - 1):
                x = col * self.grid_size
                y = row * self.grid_size
                rect = self.scene.addRect(x, y, self.grid_size, self.grid_size, pen, brush)
                rect.setFlag(QGraphicsItem.ItemIsSelectable, False)
                rect.row = row
                rect.col = col
                rect.has_piece = False
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)

    def remove_ellipse(self, row, col):
        for item in self.scene.items():
            # print(f'Trebuie sa sterg o elipsa ce se gaseste la coordonatele {col * self.grid_size + self.margin}, {row * self.grid_size + self.margin}')
            if isinstance(item, QGraphicsEllipseItem) and item.rect().contains(col * self.grid_size,
                                                                               row * self.grid_size):
                self.scene.removeItem(item)
                return True
        return False

    def find_difference_between_boards(self, old_board, new_board):
        removed = []

        for row in range(len(new_board)):
            for column in range(len(new_board)):
                if new_board[row][column] == '.' and old_board[row][column] != '.':
                    removed.append((row, column))

        return removed

    def pass_turn(self):
        move = GoMove(-1, -1, self.goState.next_to_move)
        self.goState.move(move)
        print('Turn has been passed')
        print(f'Current player is {self.goState.next_to_move}')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            x = pos.x()
            y = pos.y()
            result, col, row = self.determineIntersection(x, y)
            # print(row, col)
            if result == True and row >=0 and col >= 0 and row <= self.board_size and col <= self.board_size:
                move = GoMove(row, col, self.goState.next_to_move)
                if self.goState.is_move_legal(move):
                    print("Coordonate: ", row, col)
                    print(col * self.grid_size - self.piece_size / 2)
                    print(row * self.grid_size - self.piece_size / 2)
                    ellipse = QGraphicsEllipseItem(col * self.grid_size - self.piece_size / 2, row * self.grid_size - self.piece_size / 2,
                                                    self.piece_size, self.piece_size)
                    if self.goState.next_to_move == 1:
                        ellipse.setPen(QPen(Qt.black))
                        ellipse.setBrush(QBrush(Qt.black))
                    else:
                        ellipse.setPen(QPen(Qt.white))
                        ellipse.setBrush(QBrush(Qt.white))

                    self.scene.addItem(ellipse)

                    oldBoard = deepcopy(self.goState.board)
                    self.goState = self.goState.move(move)

                    self.printBoard(self.goState.board, self.board_size)
                    self.printBoard(oldBoard, self.board_size)
                    to_be_removed = self.find_difference_between_boards(oldBoard, self.goState.board)
                    for row, column in to_be_removed:
                        print(f'Trebuie sa sterg elipsa de la coordonatele ({row},{column})')
                        self.remove_ellipse(row, column)
                else:
                    popup = QMessageBox()
                    popup.setWindowTitle("Mutare invalida")
                    popup.setText("Mutare invalida!")
                    popup.setStandardButtons(QMessageBox.Ok)
                    popup.exec_()

    def printBoard(self, board, size):
        print('  ' + ' '.join(str(i + 1) for i in range(size)))
        print_board = ''
        for i in range(size):
            print_board += str(i + 1) + ' '
            for j in range(size):
                print_board += str(board[i][j]) + ' '
            print_board += '\n'
        print(print_board)

    def determineIntersection(self, x, y):
        print(x,y)
        x -= self.margin
        y -= self.margin
        initial_x = x
        initial_y = y
        x = x % self.grid_size
        y = y % self.grid_size
        print(x, y)
        print()
        if x > 0.75 * self.grid_size:
            if y > 0.75 * self.grid_size:
                return True, initial_x // self.grid_size + 1, initial_y // self.grid_size + 1
            if y < 0.25 * self.grid_size:
                return True, initial_x // self.grid_size + 1, initial_y // self.grid_size

        if x < 0.25 * self.grid_size:
            if y > 0.75 * self.grid_size:
                return True, initial_x // self.grid_size, initial_y // self.grid_size + 1
            if y < 0.25 * self.grid_size:
                return True, initial_x // self.grid_size, initial_y // self.grid_size

        return False, None, None

app = QApplication(sys.argv)
if __name__ == "__main__":

    window_size = 600
    read_colors_from_file('colors.json')

    mainMenu = MainMenu(window_size)
    mainMenu.show()
    sys.exit(app.exec_())
