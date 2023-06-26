from copy import deepcopy

from GameLogic.GoMove import GoMove
from GameLogic.GoState import GoState


class GoStateManager:
    def __init__(self, size):
        self.size = size
        self.action_size = self.size * self.size + 1

    def get_initial_state(self):
        return GoState(self.size)

    def get_next_state(self, state, action, player):
        if action == self.size * self.size:
            row, column = -1, -1
        else:
            row = action // self.size
            column = action % self.size

        new_state = deepcopy(state)
        new_state.move(GoMove(row, column, player))

        return new_state

    def get_valid_moves(self, state):
        return state.get_legal_actions()

    def get_value_and_terminated(self, state):
        if state.is_game_over() == True:
            # Exemplu output: True, 1, [15.5, 12]
            return state.game_result, state.get_score(), True
        else:
            return None, None, False
