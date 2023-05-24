import numpy as np
import torch

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
            # print(f'Simularea numarul {search}')
            node = root
            # Traverse the tree by choosing the child with best UCB score at any point until I reach a node that hasn't been fully expanded
            while node.is_fully_expanded():
                node = node.select()

            # We check if we reached a terminal state
            value, score, is_terminal = self.game.get_value_and_terminated(node.state)
            # If the state is terminal then we have to change sign of value because the value is for the opponent player TODO WHY?
            if is_terminal:
                if value != root.state.next_to_move:
                    value *= -1
            else:
                # If the state is not terminal, then we expand it by taking a random action, then we simulate
                # TODO de inteles de ce pun squeeze si unsqueeze
                neutral_state_perspective = node.state
                if node.state.next_to_move == -1:
                    neutral_state_perspective.board *= -1

                policy, value = self.model(
                    torch.tensor(node.state.board).unsqueeze(0).unsqueeze(0).float()
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
