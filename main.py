import os
import sys

import numpy as np
import torch
from matplotlib import pyplot as plt

from Arena import Arena
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

if __name__ == '__main__':
    size = 5
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

    # Testare mcts pe un set de mutari
    # state = go.get_next_state(state, 0, state.next_to_move)
    # state = go.get_next_state(state, 1, state.next_to_move)
    # state = go.get_next_state(state, 3, state.next_to_move)
    # state = go.get_next_state(state, 4, state.next_to_move)
    # state = go.get_next_state(state, 6, state.next_to_move)
    # state = go.get_next_state(state, 2, state.next_to_move)
    # state = go.get_next_state(state, 7, state.next_to_move)
    # state = go.get_next_state(state, 5, state.next_to_move)
    # print(state)
    # mcts_probs = mcts.search(state)
    # action = np.argmax(mcts_probs)
    #
    # state = go.get_next_state(state, action, state.next_to_move)
    # print(state)

    # Learn
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResNet(go, 4, 256, device=device)
    model.load_state_dict(torch.load('learning_results3/model_3.pt', map_location=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=0.0001)
    optimizer.load_state_dict(torch.load('learning_results3/optimizer_3.pt', map_location=device))

    # num_iterations * num_selfPlay_iterations * nr_mutari joc * num_searches = 3 * 20 * 100 = 6000

    args = {
        'C': 2,
        'num_searches': 5 * 5 * 3, # cate iteratii face algoritmul de MCTS
        'num_iterations': 100,
        'num_selfPlay_iterations': 96, # cate jocuri se joaca per iteratie
        'num_epochs': 10, # cate epoci de antrenare se intampla per iteratie
        'batch_size': 128, # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
        'num_processes': 6,
        'temperature': 1,
        'dirichlet_eps': 0.3,
        'dirichlet_alpha': 0.03
    }

    dataset_path = 'dataset'
    arena = Arena(go, args)
    alphaZero = AlphaZero(model, optimizer, go, args, dataset_path, arena)
    # TODO vezi cum faci sa poti vedea un exemplu de joc ca sa-l analizezi
    # TODO vezi daca e rentabil sa nu mai salvezi iteratiile care nu au updatat
    # TODO incearca sa adaugi mai multe canale ca sa usurezi treaba algoritmului
    #   EXEMPLU: canal 1: valoare booleana pentru piesele tale
    #            canal 2: valoare booleana pentru piesele inamicului
    #              OPTIONAL: Canal plin de 1 sau 0 pt a explica regula komi alroitmlui

    # TODO de facut o statistica daca castiga mai des albul sau negrul
    alphaZero.learn()

    # arena = Arena(go)
    # models_folder_path = ''
    # for i in range(0, 10):
    #     for j in range(0, 10):
    #         if i != j:
    #             model1 = ResNet(go, 4, 64, device=device)
    #             model2 = ResNet(go, 4, 64, device=device)
    #
    #             model1.load_state_dict(torch.load(models_folder_path + 'model_' + str(i) + '.pt', map_location=device))
    #             model2.load_state_dict(torch.load(models_folder_path + 'model_' + str(j) + '.pt', map_location=device))
    #
    #             optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
    #             optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
    #
    #             arena.play(model1, model2, 'model_' + str(i), 'model_' + str(j), 100, 'arena_results.txt')

    # Testare
    # tensor_state = torch.tensor(state.get_reversed_perspective(), device=device).unsqueeze(0).unsqueeze(0).float()
    # model = ResNet(go, 4, 64, device)
    # model.load_state_dict(torch.load('model_4.pt', map_location=device))
    # policy, value = model(tensor_state)
    # value = value.item()
    # policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()
    # valid_moves = go.get_valid_moves(state)
    # policy *= valid_moves
    # policy /= np.sum(policy)
    # print(policy)
    # print(value)
    #
    # plt.bar(range(size * size + 1), policy)
    # plt.show()

    def computerVsComputer():
        device = torch.device("cpu")
        size = 5
        go = Go(size)
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

    # computerVsComputer()





