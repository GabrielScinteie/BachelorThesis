import copy
import math

import numpy as np


class NodeAlpha:
    def __init__(self, game, args, state, parent=None, action_taken=None, prior=0, visit_count=0):
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        self.prior = prior

        self.children = []
        self.expandable_moves = game.get_valid_moves(state)

        self.visit_count = visit_count
        self.value_sum = 0

    def is_fully_expanded(self):
        return len(self.children) > 0

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
        child_wins = child.value_sum

        if child.visit_count == 0:
            q_value = 0
        else:
            q_value = child_wins / child.visit_count

        return q_value + self.args['C'] * child.prior * (math.sqrt(self.visit_count) / (child.visit_count + 1))

    def expand(self, policy):
        for action, prob in enumerate(policy):
            if prob > 0:
                child_state = copy.deepcopy(self.state)
                child_state = self.game.get_next_state(child_state, action, child_state.next_to_move)

                child = NodeAlpha(self.game, self.args, child_state, self, action, prob)
                self.children.append(child)

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1

        value *= -1
        if self.parent is not None:
            self.parent.backpropagate(value)
