import numpy as np
import torch
from tqdm import trange

from Go.NodeAlpha import NodeAlpha


class MCTSAlpha:
    def __init__(self, game, args, model):
        self.game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, state):
        root = NodeAlpha(self.game, self.args, state)

        for search in range(self.args['num_searches']):
            # print(search)
            # print(f'Search no. {search}')
            # print(f'Simularea numarul {search}')
            node = root
            # Traverse the tree by choosing the child with best UCB score at any point until I reach a node that hasn't been fully expanded
            while node.is_fully_expanded():
                node = node.select()

            # We check if we reached a terminal state
            value, score, is_terminal = self.game.get_value_and_terminated(node.state)

            if is_terminal:
                # Daca in root albul muta si castiga albul => proprag 1
                # Daca in root albul muta si castiga negrul => proprag -1
                # Daca in root negrul muta si castiga negrul => propag 1
                # Daca in root negrul muta si castiga negrul => propag -1
                if value != root.state.next_to_move:
                    value = -1
                else:
                    value = 1
            else:
                # TODO de inteles de ce pun squeeze si unsqueeze
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

                value = value.item()
                node.expand(policy)

            # We backpropagate the value given by either the simulation or the terminal state
            node.backpropagate(value)

        action_probs = np.zeros(self.game.action_size)

        # The actions are as 'good' as the number of times their corresponding nodes have been traversed
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count

        # We normalize the probabilities
        action_probs /= np.sum(action_probs)
        return action_probs
