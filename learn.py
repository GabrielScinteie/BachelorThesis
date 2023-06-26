import torch

from Agent.Evaluation.Arena import Arena
from Agent.AlphaGoZero.AlphaZero import AlphaZero
from Agent.AlphaGoZero.Model import ResNet
from utils import read_args

from GameLogic.GoStateManager import GoStateManager


if __name__ == '__main__':
    size = 5
    go = GoStateManager(size)
    state = go.get_initial_state()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResNet(go, 4, 256, device=device)
    # model.load_state_dict(torch.load('learning_results3/model_3.pt', map_location=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=0.0001)
    # optimizer.load_state_dict(torch.load('learning_results3/optimizer_3.pt', map_location=device))

    args = read_args()
    arena = Arena(go, args)
    alphaZero = AlphaZero(model, optimizer, go, args, arena)
    alphaZero.learn()




