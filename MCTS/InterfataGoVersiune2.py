from copy import copy, deepcopy

from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsItem, \
    QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox

from go import GoGameState, GoAPI, GoMove


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Menu')

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.play)

        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(QApplication.instance().quit)

        vbox = QVBoxLayout()
        vbox.addWidget(play_button)
        vbox.addWidget(quit_button)

        self.setLayout(vbox)

    def play(self):
        self.game = PlayMenu()  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
        self.hide()  # Hide the Main Menu


class PlayMenu(QWidget):
    def __init__(self):
        super().__init__()

        # Create the dropdown menus
        self.dropdown1 = QComboBox()
        self.dropdown1.addItems(['Human', 'Computer'])

        self.dropdown2 = QComboBox()
        self.dropdown2.addItems(['Human', 'Computer'])

        # Create the "Start Game" button
        self.start_button = QPushButton('Start Game')
        self.start_button.clicked.connect(self.start_game)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.back)

        # Create a layout for the dropdown menus and button
        layout = QVBoxLayout()
        layout.addWidget(self.dropdown1)
        layout.addWidget(self.dropdown2)
        layout.addWidget(self.start_button)
        layout.addWidget(self.back_button)

        # Set the layout for the main window
        self.setLayout(layout)

    def back(self):
        self.mainMenu = MainMenu()
        self.mainMenu.show()
        self.hide()

    def start_game(self):
        # Retrieve the selected options from the dropdown menus
        option1 = self.dropdown1.currentText()
        option2 = self.dropdown2.currentText()

        # Do something with the selected options (e.g. start the game with these options)
        print(f'Starting game with options: {option1}, {option2}')

        self.game = GameWidget()  # Create an instance of the Game widget
        self.game.show()  # Show the Game widget
        self.hide()  # Hide the Main Menu



# Schimbare meniu
# def play_game(self):
#     self.game = GameWidget()  # Create an instance of the Game widget
#     self.game.show()  # Show the Game widget
#     self.hide()  # Hide the Main Menu

class GameWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create the Board widget
        self.board = GoBoard(5)

        # Create the buttons
        pass_button = QPushButton("Pass")
        back_to_menu_button = QPushButton("Menu")
        button3 = QPushButton("Button 3")
        pass_button.clicked.connect(self.board.pass_turn)
        back_to_menu_button.clicked.connect(self.show_confirmation_dialog)

        # Add the buttons to a layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(pass_button)
        button_layout.addWidget(back_to_menu_button)
        button_layout.addWidget(button3)

        # Create a widget to hold the buttons
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Create a layout for the board and button widgets
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.board)
        main_layout.addWidget(button_widget)
        main_layout.setSpacing(0)

        # Set the main layout for the GameWidget
        self.setLayout(main_layout)

    def show_confirmation_dialog(self):
        # Create the confirmation dialog
        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle("Iesire joc")
        confirm_dialog.setText("Esti sigur?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Execute the confirmation dialog
        response = confirm_dialog.exec()

        # Check the user's response
        if response == QMessageBox.Yes:
            self.back_to_menu()

    def back_to_menu(self):
        self.mainMenu = MainMenu()
        self.mainMenu.show()
        self.hide()


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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mainMenu = MainMenu()
    mainMenu.show()
    sys.exit(app.exec_())
