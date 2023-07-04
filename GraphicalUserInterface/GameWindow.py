from copy import deepcopy

import numpy as np
import torch
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPen, QColor, QBrush, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QGraphicsView, QGraphicsScene, \
    QGraphicsItem, QGraphicsEllipseItem, QApplication, QLabel
from matplotlib import pyplot as plt

from Agent.AlphaGoZero.MCTSAlpha import MCTSAlpha
from Agent.AlphaGoZero.Model import ResNet
from GameLogic.GoMove import GoMove
from GameLogic.GoStateManager import GoStateManager
from utils import colors
from GraphicalUserInterface.MainMenu import MainMenu
from utils import read_args


class GameWindow(QWidget):
    def __init__(self, window_size, puzzle=None):
        super().__init__()
        self.puzzle = puzzle
        self.setWindowTitle('GameLogic')
        self.window_size = window_size
        # Create the Board widget
        self.board = GoBoard(5, puzzle)
        # Create the buttons
        self.pass_button = QPushButton("Pass")
        self.pass_button.clicked.connect(self.board.pass_turn)
        self.back_to_menu_button = QPushButton("Menu")
        self.back_to_menu_button.clicked.connect(self.show_confirmation_dialog)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.board.reset_board)


        # Partea de valoare
        # self.number_label = QLabel(self)
        # font = QFont()
        # font.setPointSize(20)  # Set the desired font size
        # self.number_label.setFont(font)  # Set the font for the label
        # self.number_label.adjustSize()  # Adjust the label size to fit the text
        #
        # window_width = self.width()
        # label_width = self.number_label.width()
        # x_coordinate = (window_width - label_width) // 2  # Calculate x-coordinate for centering label
        # y_coordinate = self.height() - 50 # Set the desired y-coordinate
        #
        # self.number_label.move(x_coordinate, y_coordinate)  # Set the position of the label


        # Add the buttons to a layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pass_button)
        button_layout.addWidget(self.back_to_menu_button)
        button_layout.addWidget(self.reset_button)

        if puzzle is not None:
            self.play_bot_move_button = QPushButton("Play move")
            self.play_bot_move_button.clicked.connect(self.board.play_bot_move)

            self.help_button = QPushButton("Help")
            self.help_button.clicked.connect(self.help)

            button_layout.addWidget(self.play_bot_move_button)
            button_layout.addWidget(self.help_button)



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
    def help(self):
        popup = QMessageBox()
        popup.setWindowTitle('Explicație')
        popup.setText(self.puzzle.explanation)
        popup.setStandardButtons(QMessageBox.Ok)
        popup.exec_()

    def style_buttons(self):
        font = QtGui.QFont()
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
        self.reset_button.setStyleSheet(style)

        if self.puzzle is not None:
            font.setPointSize(12)  # set the font size to 20
            self.play_bot_move_button.setFont(font)
            self.help_button.setFont(font)

            # self.pass_button.setFixedWidth(self.window_size // 8)
            # self.back_to_menu_button.setFixedWidth(self.window_size // 8)
            # self.play_bot_move_button.setFixedWidth(self.window_size // 6)
            # self.help_button.setFixedWidth(self.window_size // 8)
            # self.reset_button.setFixedWidth(self.window_size // 8)

            self.play_bot_move_button.setStyleSheet(style)
            self.help_button.setStyleSheet(style)

        else:
            font.setPointSize(16)

        self.reset_button.setFont(font)
        self.pass_button.setFont(font)
        self.back_to_menu_button.setFont(font)



    def show_confirmation_dialog(self):
        # Create the confirmation dialog
        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle("Iesire joc")
        confirm_dialog.setText("Esti sigur ca doresti revenirea la meniul principal?")
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
    def __init__(self, board_size, puzzle):
        super().__init__()
        self.puzzle = puzzle
        self.margin = 50
        self.board_size = board_size
        self.grid_size = 110
        self.piece_size = self.grid_size / 2
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.grid_size * (self.board_size - 1), self.grid_size * (self.board_size - 1))
        self.setScene(self.scene)
        self.setFixedSize(self.grid_size * (self.board_size - 1) + 2 * self.margin,
                          self.grid_size * (self.board_size - 1) + 2 * self.margin)
        self.draw_board()
        self.go = GoStateManager(5)
        self.go_state = self.go.get_initial_state()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_game_end)
        self.timer.start(100)



        if puzzle is not None:
            # Daca este puzzle incarcam reteaua neuronala
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = ResNet(self.go, 4, 256, device=device)
            model.load_state_dict(torch.load('learning_results3/model_45.pt', map_location=device))
            args = read_args()
            self.mcts = MCTSAlpha(self.go, args, model)

            # Daca este puzzle computerul incepe. Configuram tabla si jucatorul care incepe
            self.computer_player = puzzle.next_to_move
            self.go_state.board = puzzle.board
            self.go_state.next_to_move = puzzle.next_to_move
            self.go_state.no_moves = 50
            self.current_player = 'Computer'
            self.draw_ellipses()
        else:
            self.computer_player = None
            self.current_player = 'Human'

    def play_bot_move(self):
        if self.current_player == 'Computer':
            action_probs, _ = self.mcts.search(self.go_state)
            valid_moves = self.go.get_valid_moves(self.go_state)
            action_probs *= valid_moves
            action_probs /= np.sum(action_probs)

            best_action = np.argmax(action_probs)
            action_probs = np.insert(action_probs, 0, 0)
            plt.xticks(np.arange(0, 27, 1))
            plt.bar(range(self.board_size * self.board_size + 2), action_probs)
            plt.title('Distributie probabilitati mutari')
            plt.show()

            self.go_state = self.go.get_next_state(self.go_state, best_action, self.go_state.next_to_move)

            self.clear_ellipses()
            self.draw_ellipses()

            self.current_player = 'Human'

    def reset_board(self):
        self.go_state = self.go.get_initial_state()
        self.scene.clear()
        self.draw_board()

        if self.puzzle is not None:
            self.go_state.board = self.puzzle.board
            self.go_state.no_moves = self.board_size * self.board_size
            self.go_state.next_to_move = self.puzzle.next_to_move
            self.current_player = 'Computer'
            self.draw_ellipses()

    def check_game_end(self):
        # Check if game is over
        if not self.go_state.running:
            result = self.go_state.game_result
            score = self.go_state.get_score()

            winner = 'Negru'
            if result == -1:
                winner = 'Alb'

            popup = QMessageBox()
            popup.setWindowTitle("Final joc")
            popup.setText(f'Punctaj negru: {score[0]}\nPunctaj alb:{score[1]}\n\n{winner} a castigat!')
            popup.setStandardButtons(QMessageBox.Ok)
            popup.exec_()

            self.reset_board()

    def draw_board(self):
        pen = QPen(QColor("black"), 2)
        brush = QBrush(QColor(colors['Board']))
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

    def clear_ellipses(self):
        for item in self.scene.items():
             if isinstance(item, QGraphicsEllipseItem):
                self.scene.removeItem(item)

    def pass_turn(self):
        if self.current_player == 'Human':
            move = GoMove(-1, -1, self.go_state.next_to_move)
            self.go_state.move(move)
            print('Turn has been passed')
            print(f'Current player is {self.go_state.next_to_move}')

    def draw_ellipses(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.go_state.board[row][col] != 0:
                    if self.go_state.board[row][col] == 1:
                        ellipse = QGraphicsEllipseItem(col * self.grid_size - self.piece_size / 2,
                                                       row * self.grid_size - self.piece_size / 2,
                                                       self.piece_size, self.piece_size)
                        ellipse.setPen(QPen(Qt.black))
                        ellipse.setBrush(QBrush(QColor(colors['Black'])))
                        self.scene.addItem(ellipse)
                    if self.go_state.board[row][col] == -1:
                        ellipse = QGraphicsEllipseItem(col * self.grid_size - self.piece_size / 2,
                                                       row * self.grid_size - self.piece_size / 2,
                                                       self.piece_size, self.piece_size)
                        ellipse.setPen(QPen(Qt.white))
                        ellipse.setBrush(QBrush(QColor(colors['White'])))
                        self.scene.addItem(ellipse)

    # TODO capturarea pieselor nu se face instant la punerea unei piese de catre utilizator, ci abia dupa ce se calculeaza miscarea calculatorului, trebuie schimbat
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_player == 'Human':
            pos = event.pos()
            x = pos.x()
            y = pos.y()
            result, col, row = self.determineIntersection(x, y)
            if result == True and row >= 0 and col >= 0 and row <= self.board_size and col <= self.board_size:
                move = GoMove(row, col, self.go_state.next_to_move)
                if self.go_state.is_move_legal(move):
                    # print("Coordonate: ", row, col)

                    self.go_state = self.go_state.move(move)

                    self.clear_ellipses()
                    self.draw_ellipses()

                    if self.puzzle is not None:
                        self.current_player = 'Computer'

                    # if self.second_player != 'Human':
                    #     print('Se asteaptă mutarea calculatorului!')
                    #     best_action = np.argmax(self.mcts.search(self.go_state)[0])
                    #
                    #     self.go_state = self.go.get_next_state(self.go_state, best_action, self.go_state.next_to_move)
                    #     # self.printBoard(self.go_state.board, self.board_size)
                    #     self.clear_ellipses()
                    #     self.draw_ellipses()
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
        x -= self.margin
        y -= self.margin
        initial_x = x
        initial_y = y
        x = x % self.grid_size
        y = y % self.grid_size
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
