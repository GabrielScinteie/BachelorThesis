import numpy as np
import torch
import os
from Arena import Arena
from Go.AlphaZero import AlphaZero
from Go.Go import Go
from MCTS.Model import ResNet

if __name__ == '__main__':
    args = {
        'C': 2,
        'num_searches': 5 * 5,  # cate iteratii face algoritmul de MCTS
        'num_iterations': 100,
        'num_selfPlay_iterations': 10,  # cate jocuri se joaca per iteratie
        'num_epochs': 10,  # cate epoci de antrenare se intampla per iteratie
        'batch_size': 64,  # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
        'num_processes': 1,
        'temperature': 1,
        'dirichlet_eps': 0.3,
        'dirichlet_alpha': 0.03
    }

    size = 5
    go = Go(size)

    arena = Arena(go, args)

    device = torch.device("cpu")

    # os.remove('arena_results.txt')
    # models_folder_path = ''
    # for i in range(0, 100):
    #     for j in range(i + 1, 100):
    #         if i != j:
    #             model1 = ResNet(go, 4, 128, device=device)
    #             model2 = ResNet(go, 4, 128, device=device)
    #
    #             model1.load_state_dict(torch.load(models_folder_path + 'model_'+str(i)+'.pt', map_location=device))
    #             model2.load_state_dict(torch.load(models_folder_path + 'model_'+str(j)+'.pt', map_location=device))
    #
    #             optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
    #             optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
    #
    #             arena.play(model1, model2, 'model_'+str(i), 'model_'+str(j), 100, 'arena_results.txt')

    model1 = ResNet(go, 4, 256, device=device)
    model2 = ResNet(go, 4, 256, device=device)

    # model1.load_state_dict(torch.load('learning_results3/model_0.pt', map_location=device))
    model2.load_state_dict(torch.load('learning_results3/model_2.pt', map_location=device))

    model1.eval()
    model2.eval()

    # optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
    # optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)

    arena.play(model1, model2, 'model_0', 'model4', 10, 'arena_results.txt')

    # state = go.get_initial_state()

    # SELFPLAY FUNCTIONEAZA CORECT
    # device = torch.device("cpu")
    # model = ResNet(go, 4, 64, device=device)
    #model.load_state_dict(torch.load('model_4.pt', map_location=device))
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    # # num_iterations * num_selfPlay_iterations * nr_matari joc * num_searches = 3 * 20 * 100 = 6000

    # alphaZero = AlphaZero(model, optimizer, go, args)
    # memory = alphaZero.selfPlay()
    # for elem in memory:
    #     state, prob, result = elem
    #     print(state)
    #     print(result)
    #     print()