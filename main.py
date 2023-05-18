import os
import sys

import numpy as np
from matplotlib import pyplot as plt

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./MCTS'))
sys.path.append(os.path.abspath('./Interface'))
sys.path.append(os.path.abspath('./Go'))

from Go.Go import Go
from Go.MCTS import MCTS
from Go.Node import Node

size = 3
go = Go(size)
state = go.get_initial_state()

# while state.is_game_over() == False:
#     print(state)
#     input_row = int(input('Enter row: ')) - 1
#     input_col = int(input('Enter column: ')) - 1
#
#     if input_row == -1 and input_col == -1:
#         action = size * size
#     else:
#         action = input_row * size + input_col
#
#     valid_moves = go.get_valid_moves(state)
#     print(action)
#     while action < 0 or action > size * size or valid_moves[action] != 1:
#         print('Invalid move. Try again.')
#         input_row = int(input('Enter row: ')) - 1
#         input_col = int(input('Enter column: ')) - 1
#
#         if input_row == -1 and input_col == -1:
#             action = size * size
#         else:
#             action = input_row * size + input_col
#
#     state = go.get_next_state(state, action, state.next_to_move)
#
# print(go.get_value_and_terminated(state))


args = {
    'C': 1.41,
    'num_searches': 100
}

mcts = MCTS(go, args)
state = go.get_initial_state()
# state = go.get_next_state(state, 0, state.next_to_move)
# state = go.get_next_state(state, 1, state.next_to_move)
# state = go.get_next_state(state, 3, state.next_to_move)
# state = go.get_next_state(state, 4, state.next_to_move)
# state = go.get_next_state(state, 6, state.next_to_move)
#
# print(state)
# mcts_probs = mcts.search(state)
# action = np.argmax(mcts_probs)
#
# state = go.get_next_state(state, action, state.next_to_move)
# print(state)


while state.is_game_over() == False:
    print(state)
    print()
    mcts_probs = mcts.search(state)
    action = np.argmax(mcts_probs)
    plt.bar(range(size * size + 1), mcts_probs)
    plt.show()
    state = go.get_next_state(state, action, state.next_to_move)



