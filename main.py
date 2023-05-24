import os
import sys

import numpy as np
import torch
from matplotlib import pyplot as plt

from Go.AlphaZero import AlphaZero
from Go.MCTSAlpha import MCTSAlpha
from MCTS.Model import ResNet

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./MCTS'))
sys.path.append(os.path.abspath('./Interface'))
sys.path.append(os.path.abspath('./Go'))

from Go.Go import Go
from Go.MCTS import MCTS
from Go.Node import Node

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

size = 3
go = Go(size)
state = go.get_initial_state()

# Jucat 1v1 om la om
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

# Testare mcts pe un set de mutari
state = go.get_next_state(state, 0, state.next_to_move)
state = go.get_next_state(state, 1, state.next_to_move)
state = go.get_next_state(state, 3, state.next_to_move)
state = go.get_next_state(state, 4, state.next_to_move)
state = go.get_next_state(state, 6, state.next_to_move)

print(state)
# mcts_probs = mcts.search(state)
# action = np.argmax(mcts_probs)
#
# state = go.get_next_state(state, action, state.next_to_move)
# print(state)

# JucatMCTS
# model = ResNet(state, 4, 64)
# mctsAlpha = MCTSAlpha(go, args, model)
#
# while state.is_game_over() == False:
#     print(state)
#     print()
#     mcts_probs = mctsAlpha.search(state)
#     action = np.argmax(mcts_probs)
#     plt.bar(range(size * size + 1), mcts_probs)
#     plt.show()
#     state = go.get_next_state(state, action, state.next_to_move)

# Testare model chel
# TODO board * -1 nu e bine deoarece 0 devine -0, ele nefiind egale
tensor_state = torch.tensor(state.board * -1).unsqueeze(0).unsqueeze(0).float()
model = ResNet(state, 4, 64)
model.load_state_dict(torch.load('model_2.pt'))
policy, value = model(tensor_state)
value = value.item()
policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()

print(policy)
print(value)

plt.bar(range(size * size + 1), policy)
plt.show()




# Testat self play
# model = ResNet(go, 4, 64)
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
#
# args = {
#     'C': 2,
#     'num_searches': 60,
#     'num_iterations': 3,
#     'num_selfPlay_iterations': 10,
#     'num_epochs': 4,
#     'batch_size': 5
# }
#
# alphaZero = AlphaZero(model, optimizer, go, args)
# alphaZero.learn()


