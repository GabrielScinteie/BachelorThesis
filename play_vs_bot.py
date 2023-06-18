# Jucat player vs bot
from copy import deepcopy

import numpy as np
import torch
from matplotlib import pyplot as plt

from Go.Go import Go
from Go.MCTSAlpha import MCTSAlpha
from MCTS.Model import ResNet


def augment_data(state, action_probs):
    rotated_probs = np.concatenate((np.rot90(action_probs[:25].reshape(5, 5), k=1).flatten(), action_probs[25:]))
    rotated_state = np.rot90(state, k=1)

    return rotated_state, rotated_probs

size = 5
go = Go(size)
state = go.get_initial_state()

device = torch.device("cpu")
model = ResNet(go, 4, 128, device)
# model.load_state_dict(torch.load('saved_model/size5/run4/model_9.pt', map_location=device))
model.load_state_dict(torch.load('learning_results/model_3.pt', map_location=device))
player = 1
print(state)
args = {
    'C': 2,
    'num_searches': 25,  # cate iteratii face algoritmul de MCTS
    'num_iterations': 100,
    'num_selfPlay_iterations': 120,  # cate jocuri se joaca per iteratie
    'num_epochs': 2,  # cate epoci de antrenare se intampla per iteratie
    'batch_size': 50,  # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
    'num_processes': 6,
    'temperature': 1,
    'dirichlet_eps': 0.2,
    'dirichlet_alpha': 0.03
}
mcts = MCTSAlpha(go, args, model)

while state.is_game_over() == False:
    if state.next_to_move == player:
        input_row = int(input('Enter row: ')) - 1
        input_col = int(input('Enter column: ')) - 1

        if input_row == -1 and input_col == -1:
            action = size * size
        else:
            action = input_row * size + input_col

        valid_moves = go.get_valid_moves(state)
        print(action)
        while action < 0 or action > size * size or valid_moves[action] != 1:
            print('Invalid move. Try again.')
            input_row = int(input('Enter row: ')) - 1
            input_col = int(input('Enter column: ')) - 1

            if input_row == -1 and input_col == -1:
                action = size * size
            else:
                action = input_row * size + input_col

        state = go.get_next_state(state, action, state.next_to_move)
        print(state)
    else:
        action_probs = mcts.search(state)
        valid_moves = go.get_valid_moves(state)
        action_probs *= valid_moves
        action_probs /= np.sum(action_probs)

        action = np.argmax(action_probs)
        print(f'Jucatorul {state.next_to_move} a facut miscarea {action}')

        state = go.get_next_state(state, action, state.next_to_move)
        print(state)
        plt.bar(range(size * size + 1), action_probs)
        plt.show()
print(go.get_value_and_terminated(state))