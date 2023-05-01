import numpy as np
from collections import defaultdict
from abc import ABC, abstractmethod
from copy import deepcopy
from go import printBoard

class MonteCarloTreeSearchNode(ABC):

    def __init__(self, state, parent=None, keep_tree=False):
        """
        Parameters
        ----------
        state : mctspy.games.common.TwoPlayersAbstractGameState
        parent : MonteCarloTreeSearchNode
        """
        if not keep_tree:
            self.state = state
            self.parent = parent
            self.children = []
        else:
            self.state = state
            self.children = state.children

    @property
    @abstractmethod
    def untried_actions(self):
        """

        Returns
        -------
        list of mctspy.games.common.AbstractGameAction

        """
        pass

    @property
    @abstractmethod
    def q(self):
        pass

    @property
    @abstractmethod
    def n(self):
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def is_terminal_node(self):
        pass

    @abstractmethod
    def rollout(self):
        pass

    @abstractmethod
    def backpropagate(self, reward):
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        #print(choices_weights)
        #for child in self.children:
            #print(f'Nodul urmator are raportul win/simulari {child.q}/{child.n}:')
            #printBoard(child.state.board, 5)

        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]


class TwoPlayersGameMonteCarloTreeSearchNode(MonteCarloTreeSearchNode):

    def __init__(self, state=None, parent=None):
        super().__init__(state, parent)
        self._number_of_visits = 0.
        self._results = defaultdict(int)
        self._untried_actions = None

    @property
    def untried_actions(self):
        if self._untried_actions is None:
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @property
    def q(self):
        wins = self._results[self.parent.state.next_to_move]
        loses = self._results[-1 * self.parent.state.next_to_move]

        return wins - loses

    @property
    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self.untried_actions.pop()
        # print(action)
        next_state = deepcopy(self.state).move(action)
        child_node = TwoPlayersGameMonteCarloTreeSearchNode(
            next_state, parent=self
        )
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state
        index = 0
        #f = open('games.txt', 'a')
        while not current_rollout_state.is_game_over():
            #if index == 1:
                #printBoard(current_rollout_state.board, 5)
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = deepcopy(current_rollout_state).move(action)
            # str_game = ''
            # for i in range(len(current_rollout_state.size)):
            #     for j in range(len(current_rollout_state.size)):
            #         str_game += current_rollout_state.board[i][j]

            index += 1
        # f.write(str(current_rollout_state.game_result))
        # f.write('\n')
        # f.close()
        return current_rollout_state.game_result

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)