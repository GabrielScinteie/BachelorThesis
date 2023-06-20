import numpy as np
import torch
from tqdm import trange
import time

from Go.NodeAlpha import NodeAlpha


class MCTSAlpha:
    def __init__(self, game, args, model):
        self.game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, state):
        root = NodeAlpha(self.game, self.args, state, visit_count=1)


        neutral_state_board = root.state.board
        if root.state.next_to_move == -1:
            neutral_state_board = root.state.get_reversed_perspective()
        policy, value = self.model(
            torch.tensor(neutral_state_board, device=self.model.device).unsqueeze(0).unsqueeze(0).float()
        )

        # Add random Dirichlet noise
        policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
        policy = (1 - self.args['dirichlet_eps']) * policy + self.args['dirichlet_eps'] * np.random.dirichlet([self.args['dirichlet_alpha']] * self.game.action_size)
        valid_moves = self.game.get_valid_moves(state)
        policy *= valid_moves
        policy /= np.sum(policy)
        root.expand(policy)

        for search in range(self.args['num_searches']):
            node = root

            # Traverse the tree by choosing the child with best UCB score at any point until I reach a node that hasn't been fully expanded
            while node.is_fully_expanded():
                node = node.select()

            # We check if we reached a terminal state
            value, score, is_terminal = self.game.get_value_and_terminated(node.state)

            if is_terminal:
                # value este dpdv al negrului, daca e tura albului inversez scorul final
                if node.state.next_to_move == -1:
                    value *= -1
            else:
                neutral_state_board = node.state.board
                if node.state.next_to_move == -1:
                    neutral_state_board = node.state.get_reversed_perspective()

                policy, value = self.model(
                    torch.tensor(neutral_state_board, device=self.model.device).unsqueeze(0).unsqueeze(0).float()
                )

                policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
                valid_moves = self.game.get_valid_moves(state)
                policy *= valid_moves
                policy /= np.sum(policy)

                # Valoarea este din perspectiva celui a carui tura este
                value = value.item()

                node.expand(policy)

            # We backpropagate the value given by either the simulation or the terminal state
            node.backpropagate(-value)

        action_probs = np.zeros(self.game.action_size)

        # The actions are as 'good' as the number of times their corresponding nodes have been traversed
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count

        # We normalize the probabilities
        action_probs /= np.sum(action_probs)

        return action_probs
