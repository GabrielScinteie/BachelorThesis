import time
from go import printBoard
class MonteCarloTreeSearch(object):

    def __init__(self, node):
        """
        MonteCarloTreeSearchNode
        Parameters
        ----------
        node : mctspy.tree.nodes.MonteCarloTreeSearchNode
        """
        self.root = node

    def best_action(self, simulations_number=None, total_simulation_seconds=None):
        """

        Parameters
        ----------
        simulations_number : int
            number of simulations performed to get the best action

        total_simulation_seconds : float
            Amount of time the algorithm has to run. Specified in seconds

        Returns
        -------

        """

        if simulations_number is None :
            assert(total_simulation_seconds is not None)
            end_time = time.time() + total_simulation_seconds
            index = 0
            while True:
                # if index % 50 == 0:
                #     print(index)
                index += 1
                v = self._tree_policy()
                reward = v.rollout()

                v.backpropagate(reward)
                if time.time() > end_time:
                    break
        else :
            for index in range(0, simulations_number):
                if index % 50 == 0:
                    print(index)
                # print(f'Simulation {index}')
                # print("##########################################################")
                v = self._tree_policy()
                # printBoard(v.state.board, 5)
                reward = v.rollout()
                # print(f'Reward:{reward}')
                # print()
                v.backpropagate(reward)
        # to select best child go for exploitation only
        print(self.root.best_child(c_param=0))
        return self.root.best_child(c_param=0.)

    def _tree_policy(self):
        """
        selects node to run rollout/playout for

        Returns
        -------

        """
        current_node = self.root
        while not current_node.is_terminal_node():
            #print(current_node.is_fully_expanded)
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node