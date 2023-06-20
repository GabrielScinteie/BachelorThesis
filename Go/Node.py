import math
import time

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
        self.results = {1: 0, -1: 0}

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
        child_wins = child.results[self.state.next_to_move]

        q_value = child_wins / child.visit_count
        return q_value + self.args['C'] * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self):
        # Take random action that hasn't been taken yet
        action = np.random.choice(np.where(self.expandable_moves == 1)[0])
        # Mark the action as being taken
        self.expandable_moves[action] = 0


        child_state = self.state.deep_copy()
        child_state = self.game.get_next_state(child_state, action, child_state.next_to_move)
        # child_state = self.game.change_perspective(child_state, player=-1)

        child = Node(self.game, self.args, child_state, self, action)
        self.children.append(child)
        return child

    def simulate(self):
        value, score, is_terminal = self.game.get_value_and_terminated(self.state)

        if is_terminal:
            return value

        rollout_state = self.state
        i = 0
        while True:
            valid_moves = self.game.get_valid_moves(rollout_state)
            action = np.random.choice(np.where(valid_moves == 1)[0])
            rollout_state = self.game.get_next_state(rollout_state, action, rollout_state.next_to_move)
            value, score, is_terminal = self.game.get_value_and_terminated(rollout_state)
            i += 1

            if is_terminal:
                return value

    def backpropagate(self, result):
        self.results[result] += 1
        self.visit_count += 1

        if self.parent is not None:
            self.parent.backpropagate(result)

