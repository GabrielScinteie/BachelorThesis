import numpy as np
import torch
import os
from Arena import Arena
from Go.AlphaZero import AlphaZero
from Go.Go import Go
from MCTS.Model import ResNet

size = 5
go = Go(size)
arena = Arena(go)

device = torch.device("cpu")
model8 = ResNet(go, 4, 64, device=device)
model9 = ResNet(go, 4, 64, device=device)

models_folder_path = './saved_model/size5/run1/'
model8.load_state_dict(torch.load('./saved_model/size5/run1/model_8.pt', map_location=device))
model9.load_state_dict(torch.load('./saved_model/size5/run1/model_9.pt', map_location=device))

optimizer8 = torch.optim.Adam(model8.parameters(), lr=0.001)
optimizer9 = torch.optim.Adam(model9.parameters(), lr=0.001)

# os.remove('arena_results.txt')
#
# for i in range(3, 10):
#     for j in range(3, 10):
#         if i != j:
#             model1 = ResNet(go, 4, 64, device=device)
#             model2 = ResNet(go, 4, 64, device=device)
#
#             model1.load_state_dict(torch.load(models_folder_path + 'model_'+str(i)+'.pt', map_location=device))
#             model2.load_state_dict(torch.load(models_folder_path + 'model_'+str(j)+'.pt', map_location=device))
#
#             optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
#             optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
#
#             arena.play(model1, model2, 'model_'+str(i), 'model_'+str(j), 20, 'arena_results.txt')

state = go.get_initial_state()

# SELFPLAY FUNCTIONEAZA CORECT
# device = torch.device("cpu")
# model = ResNet(go, 4, 64, device=device)
# #model.load_state_dict(torch.load('model_4.pt', map_location=device))
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
# # num_iterations * num_selfPlay_iterations * nr_matari joc * num_searches = 3 * 20 * 100 = 6000
# args = {
#     'C': 2,
#     'num_searches': 5, # cate iteratii face algoritmul de MCTS
#     'num_iterations': 10,
#     'num_selfPlay_iterations': 30, # cate jocuri se joaca per iteratie
#     'num_epochs': 10, # cate epoci de antrenare se intampla per iteratie
#     'batch_size': 20 # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
# }

# alphaZero = AlphaZero(model, optimizer, go, args)
# memory = alphaZero.selfPlay()
# for elem in memory:
#     state, prob, result = elem
#     print(state)
#     print(result)
#     print()