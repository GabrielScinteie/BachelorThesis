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
        if simulations_number is None :
            end_time = time.time() + total_simulation_seconds
            while True:
                terminal_node = self._tree_policy()
                reward = terminal_node.rollout()

                terminal_node.backpropagate(reward)
                if time.time() > end_time:
                    break
        else :
            for index in range(0, simulations_number):
                v = self._tree_policy()
                reward = v.rollout()
                v.backpropagate(reward)

            time.sleep(100)

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