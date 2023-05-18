import numpy as np
import torch

from Node import Node


class MCTS:
    def __init__(self, game, args, model):
        self.game = game
        self.args = args
        self.model = model

    def search(self, state):
        root = Node(self.game, self.args, state)

        for search in range(self.args['num_searches']):
            node = root
            # print(f'Simularea numarul {search}')
            # Traverse the tree by choosing the child with best UCB score at any point until I reach a node that hasn't been fully expanded
            while node.is_fully_expanded():
                node = node.select()

            # We check if we reached a terminal state
            value, score, is_terminal = self.game.get_value_and_terminated(node.state)

            # If the state is not terminal, then we expand it by taking a random action, then we simulate
            if not is_terminal:
                policy, value = self.model(
                    torch.tensor(node.state.board).unsqueeze(0)
                )
                node = node.expand()
                value = node.simulate()

            # We backpropagate the value given by either the simulation or the terminal state
            node.backpropagate(value)

        action_probs = np.zeros(self.game.action_size)

        # The actions are as 'good' as the number of times their corresponding nodes have been traversed
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count

        # We normalize the probabilities
        action_probs /= np.sum(action_probs)
        return action_probs
