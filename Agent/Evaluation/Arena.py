import os
import shutil
import time
from copy import copy

import numpy as np
import torch.multiprocessing as mp
from tqdm import trange

from Agent.MCTS.MCTS import MCTS
from Agent.AlphaGoZero.MCTSAlpha import MCTSAlpha


class Arena:
    def __init__(self, game, args):
        self.game = game
        self.args = copy(args)
        self.results_folder = 'arena_results'

    def read_result_from_file(self, file_path):
        f = open(file_path, 'r')
        numbers = f.readline().strip().split()
        return numbers

    # The model that is first given as param starts with black
    # If the model is None then use simple MCTS
    def play_one_game(self, model1, model2, file_path):
        if file_path is not None:
            f = open(file_path, 'a')

        if model1 != None:
            mcts1 = MCTSAlpha(self.game, self.args, model1)
        else:
            mcts1 = MCTS(self.game, self.args)

        if model2 != None:
            mcts2 = MCTSAlpha(self.game, self.args, model2)
        else:
            mcts2 = MCTS(self.game, self.args)

        state = self.game.get_initial_state()
        game_length = 0
        search_1 = 0
        search_2 = 0
        while state.is_game_over() == False:
            if game_length % 2 == 0:
                action_probs, no_iter = mcts1.search(state)
                search_1 += no_iter
            else:
                action_probs, no_iter = mcts2.search(state)
                search_2 += no_iter

            valid_moves = self.game.get_valid_moves(state)
            action_probs *= valid_moves
            action_probs /= np.sum(action_probs)

            action = np.argmax(action_probs)
            # print(f'Jucatorul {state.next_to_move} a facut miscarea {action}')

            state = self.game.get_next_state(state, action, state.next_to_move)

            # file.write(f'Jucatorul {state.next_to_move} a facut miscarea {action}\n')
            # file.write(str(state))
            # file.write('\n')
            game_length += 1

        result, scores, _ = self.game.get_value_and_terminated(state)
        # file.write(f'A castigat jucatorul {result} in {game_length} miscari cu scorurile {scores}.\n')
        if file_path is not None:
            f.close()
        return result, game_length, search_1, search_2

    def play_games(self, model1, model2, file_path, number_games, process_number):
        file_name = f'{self.results_folder}/Process_{process_number}'
        f = open(file_name, 'a')

        medium_game_length = 0
        model1_wins_number = 0
        model2_wins_number = 0

        search_1 = 0
        search_2 = 0
        for i in trange(number_games // 2):
            result, game_length, no_iter_1, no_iter_2 = self.play_one_game(model1, model2, file_path)
            search_1 += no_iter_1
            search_2 += no_iter_2
            medium_game_length += game_length
            if result == 1:
                model1_wins_number += 1
            else:
                model2_wins_number += 1

        for i in trange(number_games // 2, number_games):
            result, game_length, no_iter_2, no_iter_1 = self.play_one_game(model2, model1, file_path)
            search_1 += no_iter_1
            search_2 += no_iter_2
            medium_game_length += game_length
            if result == 1:
                model2_wins_number += 1
            else:
                model1_wins_number += 1

        medium_game_length = medium_game_length // number_games
        f.write(f'{model1_wins_number} {model2_wins_number} {medium_game_length} {search_1} {search_2}')
        f.close()

    def play(self, model1, model2, model1_name, model2_name, number_games, file_path=None):
        print(f'{model1_name} vs {model2_name}')

        if os.path.exists(self.results_folder):
            shutil.rmtree(self.results_folder)

        os.makedirs(self.results_folder)

        if file_path is not None:
            f = open(file_path, 'a')

        model1_wins_number = 0
        model2_wins_number = 0
        medium_game_length = 0

        start_time = time.perf_counter()
        processes = []
        games_per_process = number_games // self.args['num_processes']
        for process_number in range(self.args['num_processes']):
            p = mp.Process(target=self.play_games, args=(model1, model2, file_path, games_per_process, process_number))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        search_1 = 0
        search_2 = 0
        for process_number in range(self.args['num_processes']):
            model1_wins, model2_wins, game_length, no_iter_1, no_iter_2 = self.read_result_from_file(
                f'{self.results_folder}/Process_{process_number}')
            search_1 += int(no_iter_1)
            search_2 += int(no_iter_2)
            model1_wins_number += int(model1_wins)
            model2_wins_number += int(model2_wins)
            medium_game_length += int(game_length)

        medium_game_length //= self.args['num_processes']
        end_time = time.perf_counter()
        if file_path is not None:
            f.write(
                f'\n{model1_name} vs {model2_name} : {model1_wins_number} - {model2_wins_number} {round(model2_wins_number * 100 / number_games, 2)}% ({str(medium_game_length)}) timp: {round(end_time - start_time, 2)}, iteratii_1: {search_1} iteratii_2: {search_2}')
            f.close()

        return model1_wins_number, model2_wins_number, medium_game_length
