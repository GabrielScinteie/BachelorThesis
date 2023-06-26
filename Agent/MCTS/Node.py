import math
import time
from copy import deepcopy

import numpy as np


class Node:
    def __init__(self, game, args, state, parent=None, action_taken=None):
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken

        self.children = []
        self.expandable_moves = game.get_valid_moves(state)

        self.visit_count = 0
        self.value_sum = 0

    def is_fully_expanded(self):
        return np.sum(self.expandable_moves) == 0 and len(self.children) > 0

    def select(self):
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb

        return best_child

    def get_ucb(self, child):
        # (q_value + 1) / 2 to map the interval (-1, 1) to (0, 1)
        q_value = ((child.value_sum / child.visit_count) + 1) / 2

        return q_value + self.args['C'] * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self):
        # Take random action that hasn't been taken yet
        action = np.random.choice(np.where(self.expandable_moves == 1)[0])
        # Mark the action as being taken
        self.expandable_moves[action] = 0

        child_state = self.state.deep_copy()
        child_state = self.game.get_next_state(child_state, action, child_state.next_to_move)

        child = Node(self.game, self.args, child_state, self, action)
        self.children.append(child)

        return child

    def simulate(self):
        # Returns the value from the point of view of the newly expanded node
        value, score, is_terminal = self.game.get_value_and_terminated(self.state)

        if is_terminal:
            # if the player to move is white, then we change the value because the value is from perspective of black
            if self.state.next_to_move == -1:
                value *= -1
            return value

        rollout_state = deepcopy(self.state)
        i = 0
        while True:
            valid_moves = self.game.get_valid_moves(rollout_state)
            action = np.random.choice(np.where(valid_moves == 1)[0])
            rollout_state = self.game.get_next_state(rollout_state, action, rollout_state.next_to_move)
            value, score, is_terminal = self.game.get_value_and_terminated(rollout_state)
            i += 1

            if is_terminal:
                # if the winner is the same as the node that started the search, return 1, otherwise return -1
                if self.state.next_to_move == value:
                    return 1
                else:
                    return -1

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1

        if self.parent is not None:
            self.parent.backpropagate(-value)

