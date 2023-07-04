import os
import sys

import numpy as np
import torch

from Agent.Evaluation.Arena import Arena
from Agent.AlphaGoZero.AlphaZero import AlphaZero
from Agent.AlphaGoZero.Model import ResNet
from utils import read_args
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('NeuralNetwork'))
sys.path.append(os.path.abspath('GraphicalUserInterface'))
sys.path.append(os.path.abspath('GameLogic'))

from GameLogic.GoStateManager import GoStateManager

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if __name__ == '__main__':
    size = 5
    go = GoStateManager(size)
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

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResNet(go, 4, 256, device=device)
    # model.load_state_dict(torch.load('learning_results3/model_3.pt', map_location=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=0.0001)
    # optimizer.load_state_dict(torch.load('learning_results3/optimizer_3.pt', map_location=device))

    # num_iterations * num_selfPlay_iterations * nr_mutari joc * num_searches = 3 * 20 * 100 = 6000

    args = read_args()

    arena = Arena(go, args)
    alphaZero = AlphaZero(model, optimizer, go, args, arena)
    # TODO incearca sa adaugi mai multe canale ca sa usurezi treaba algoritmului
    #   EXEMPLU: canal 1: valoare booleana pentru piesele tale
    #            canal 2: valoare booleana pentru piesele inamicului
    #              OPTIONAL: Canal plin de 1 sau 0 pt a explica regula komi alroitmlui

    # TODO de facut o statistica daca castiga mai des albul sau negrul
    alphaZero.learn()

    def computerVsComputer():
        device = torch.device("cpu")
        size = 5
        go = GoStateManager(size)
        model = ResNet(go, 4, 64, device)
        # model.load_state_dict(torch.load('model_4.pt', map_location=device))
        state = go.get_initial_state()
        index = 0
        while state.is_game_over() == False:
            index += 1
            if state.next_to_move == -1:
                tensor_state = torch.tensor(state.get_reversed_perspective(), device=device).unsqueeze(0).unsqueeze(0).float()
            else:
                tensor_state = torch.tensor(state.board, device=device).unsqueeze(0).unsqueeze(0).float()

            policy, value = model(tensor_state)
            value = value.item()
            policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()
            valid_moves = go.get_valid_moves(state)
            policy *= valid_moves
            policy /= np.sum(policy)

            action = np.argmax(policy)
            print(f'Jucatorul {state.next_to_move} a facut miscarea {action}')
            state = go.get_next_state(state, action, state.next_to_move)
            print(state)
            print()
        print(index)
        print(go.get_value_and_terminated(state))





