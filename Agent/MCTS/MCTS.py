import time

import numpy as np
from Agent.MCTS.Node import Node


class MCTS:
    def __init__(self, game, args):
        self.game = game
        self.args = args

    def search(self, state):
        root = Node(self.game, self.args, state)

        timing = False
        if self.args['simulation_time'] != 0:
            timing = True
            ending_time = time.time() + self.args['simulation_time']

        search = 0
        while True:
            if timing == True :
                if time.time() > ending_time:
                    # print(f'MCTS a reusit sa faca {search} iteratii in timpul stabilit!')
                    break
            elif search > self.args['num_searches']:
                # print(f'MCTS a reusit sa faca {search} iteratii in timpul stabilit!')
                break

            node = root
            # print(f'Simularea numarul {search}')
            # Traverse the tree by choosing the child with best UCB score at any point until I reach a node that hasn't been fully expanded
            while node.is_fully_expanded():
                node = node.select()

            # We check if we reached a terminal state
            value, score, is_terminal = self.game.get_value_and_terminated(node.state)
            # If it's white to move then the need to swap the sign of the value because the value is from the perspective of black

            # If the state is not terminal, then we expand it by taking a random action, then we simulate
            if is_terminal:
                if node.state.next_to_move == -1:
                    value *= -1
            else:
                node = node.expand()
                value = node.simulate()

            # We backpropagate the value given by either the simulation or the terminal state
            node.backpropagate(-value)

            search += 1

        action_probs = np.zeros(self.game.action_size)

        # The actions are as 'good' as the number of times their corresponding nodes have been traversed
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count

        # We normalize the probabilities
        action_probs /= np.sum(action_probs)

        # self.print_tree_dfs(root)

        return action_probs

    def print_tree_dfs(self, node, level=0):
        indent = '---' * level
        print(f"{indent}{node.visit_count}")

        for child in node.children:
            self.print_tree_dfs(child, level + 1)
