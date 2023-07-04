# Jucat player vs bot

import numpy as np
import torch
from matplotlib import pyplot as plt

from GameLogic.GoStateManager import GoStateManager
from Agent.AlphaGoZero.MCTSAlpha import MCTSAlpha
from Agent.AlphaGoZero.Model import ResNet
from utils import read_args


def augment_data(state, action_probs):
    rotated_probs = np.concatenate((np.rot90(action_probs[:25].reshape(5, 5), k=1).flatten(), action_probs[25:]))
    rotated_state = np.rot90(state, k=1)

    return rotated_state, rotated_probs

size = 5
go = GoStateManager(size)
state = go.get_initial_state()

device = torch.device("cpu")
model = ResNet(go, 4, 256, device)
# model.load_state_dict(torch.load('saved_model/size5/run4/model_9.pt', map_location=device))
model.load_state_dict(torch.load('learning_results3/model_45.pt', map_location=device))
print(state)

args = {
    'C': 2,
    'num_searches': 100,  # cate iteratii face algoritmul de NeuralNetwork
    'num_iterations': 100,
    'num_selfPlay_iterations': 120,  # cate jocuri se joaca per iteratie
    'num_epochs': 2,  # cate epoci de antrenare se intampla per iteratie
    'batch_size': 50,  # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
    'num_processes': 6,
    'temperature': 1,
    'dirichlet_eps': 0.3,
    'dirichlet_alpha': 0.03,
    'simulation_time' : 5
}

def read_state_from_file(puzzle_number):
    board_path = f'Puzzles/Puzzle{puzzle_number}/puzzle.txt'
    matrix = np.loadtxt(board_path)

    context_path = f'Puzzles/Puzzle{puzzle_number}/context.txt'


    player_to_move = None
    good_answers = None

    with open(context_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' : ')

            if key == 'player_to_move':
                player_to_move = int(value)
            elif key == 'good_answers':
                # Extract the tuple values from the string
                good_answers = eval(value)

    print("player_to_move:", player_to_move)
    print("good_answers:", good_answers)

    return matrix, player_to_move, good_answers

mcts = MCTSAlpha(go, args, model)

for puzzle_number in range(3, 4):
    state.board, state.next_to_move, good_answers = read_state_from_file(puzzle_number)
    state.no_moves = 50
    print(state)

    action_probs, _ = mcts.search(state)
    print(action_probs)
    valid_moves = go.get_valid_moves(state)
    action_probs *= valid_moves
    action_probs /= np.sum(action_probs)
    print(action_probs)

    action = np.argmax(action_probs)
    if action == 25:
        row_action = -1
        column_action = -1
    else:
        row_action = action // 5
        column_action = action % 5

    if (row_action, column_action) in good_answers:
        print('Raspuns corect!')
    else:
        print('Raspuns gresit!')

    print(f'Jucatorul {state.next_to_move} a facut miscarea ({row_action}, {column_action})')

    state = go.get_next_state(state, action, state.next_to_move)
    print(state)
    plt.xticks(np.arange(0, 27, 1))
    plt.bar(range(size * size + 1), action_probs)
    plt.show()

#
# while state.is_game_over() == False:
#     if state.next_to_move == player:
#         input_row = int(input('Enter row: ')) - 1
#         input_col = int(input('Enter column: ')) - 1
#
#         if input_row == -1 and input_col == -1:
#             action = size * size
#         else:
#             action = input_row * size + input_col
#
#         valid_moves = go.get_valid_moves(state)
#         print(action)
#         while action < 0 or action > size * size or valid_moves[action] != 1:
#             print('Invalid move. Try again.')
#             input_row = int(input('Enter row: ')) - 1
#             input_col = int(input('Enter column: ')) - 1
#
#             if input_row == -1 and input_col == -1:
#                 action = size * size
#             else:
#                 action = input_row * size + input_col
#
#         state = go.get_next_state(state, action, state.next_to_move)
#         print(state)
#     else:
#         action_probs = mcts.search(state)
#         valid_moves = go.get_valid_moves(state)
#         action_probs *= valid_moves
#         action_probs /= np.sum(action_probs)
#
#         action = np.argmax(action_probs)
#         print(f'Jucatorul {state.next_to_move} a facut miscarea {action}')
#
#         state = go.get_next_state(state, action, state.next_to_move)
#         print(state)
#         plt.bar(range(size * size + 1), action_probs)
#         plt.show()
# print(go.get_value_and_terminated(state))