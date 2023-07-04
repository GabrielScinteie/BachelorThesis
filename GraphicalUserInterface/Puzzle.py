import numpy as np


class Puzzle:
    def __init__(self):
        self.board = None
        self.next_to_move = None
        self.explanation = None

    def load_from_folder(self, path):
        board_path = f'{path}/puzzle.txt'
        self.board = np.loadtxt(board_path)

        context_path = f'{path}/context.txt'

        with open(context_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(' : ')

                if key == 'player_to_move':
                    self.next_to_move = int(value)
                elif key == 'good_answers':
                    # Extract the tuple values from the string
                    self.good_answers = eval(value)
                elif key == 'explanation':
                    self.explanation = value