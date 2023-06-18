import torch
from matplotlib import pyplot as plt

from Arena import Arena
from Go.AlphaZero import AlphaZero
from Go.Go import Go, GoMove
from Go.MCTSAlpha import MCTSAlpha
from MCTS.Model import ResNet

size = 3
go = Go(size)
state = go.get_initial_state()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model1 = ResNet(go, 4, 128, device=device)
# model.load_state_dict(torch.load('learning_results/model_99.pt', map_location=device))

optimizer1 = torch.optim.Adam(model1.parameters(), lr=0.001, weight_decay=0.0001)
# num_iterations * num_selfPlay_iterations * nr_matari joc * num_searches = 3 * 20 * 100 = 6000

model2 = ResNet(go, 4, 128, device=device)
optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001, weight_decay=0.0001)

args = {
    'C': 2,
    'num_searches': 3 * 3 * 3 * 3,  # cate iteratii face algoritmul de MCTS
    'num_iterations': 20,
    'num_selfPlay_iterations': 1200,  # cate jocuri se joaca per iteratie
    'num_epochs': 10,  # cate epoci de antrenare se intampla per iteratie
    'batch_size': 512,  # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
    'num_processes': 6,
    'temperature': 1,
    'dirichlet_eps': 0.3,
    'dirichlet_alpha': 0.03
}

dataset_path = 'dataset'
arena = Arena(go, args)
alphaZero1 = AlphaZero(model1, optimizer1, go, args, dataset_path, arena)

model1.load_state_dict(torch.load('learning_results3/model_0.pt', map_location=device))
model2.load_state_dict(torch.load('learning_results3/model_5.pt', map_location=device))

mcts1 = MCTSAlpha(go, args, model1)
mcts2 = MCTSAlpha(go, args, model2)

dataset = alphaZero1.load_pickle('Iteration_5/Process_0')

index = 1
print(dataset[index][0])
print(dataset[index][1])
print(dataset[index][2])

state = state.move(GoMove(2, 1, -1))
print(state)
action_probs1 = mcts1.search(state)
print(action_probs1)
plt.bar(range(size * size + 1), action_probs1)
plt.show()
action_probs2 = mcts2.search(state)
print(action_probs2)
plt.bar(range(size * size + 1), action_probs2)
plt.show()




