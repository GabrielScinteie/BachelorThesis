import random
import time

from GameLogic.GoStateManager import GoStateManager
from Agent.MCTS import MCTS
import numpy as np
from utils import read_args

args = read_args()

size = 3
go = GoStateManager(size)
state = go.get_initial_state()
print(args['num_searches'])
mcts = MCTS(go, args)
# print(mcts.search(state))
game_length = 0
number_games = 10
wins_mcts = 0
start_time = time.perf_counter()
for i in range(number_games):
    if i % 10 == 0:
        print(i)
    state = go.get_initial_state()
    game_length = 0
    while state.running:
        if state.next_to_move == 1:
            action = np.argmax(mcts.search(state))
        else:
            if game_length > 6:
                action = random.randint(0, 9)
            else:
                action = random.randint(1, 9)
        game_length += 1
        state = go.get_next_state(state, action, state.next_to_move)
    value, score, is_terminal = go.get_value_and_terminated(state)
    if value == 1:
        wins_mcts += 1
end_time = time.perf_counter()
print(f'MCTS a castigat {wins_mcts} din {number_games} meciuri.')
print(f'Timp: {end_time - start_time}')

