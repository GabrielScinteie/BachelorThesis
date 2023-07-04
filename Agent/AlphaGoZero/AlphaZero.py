import os
import random
import time
from copy import deepcopy

import numpy as np
import torch
import torch.nn.functional as F
import torch.multiprocessing as mp
import pickle
import shutil
from tqdm import trange

from Agent.AlphaGoZero.MCTSAlpha import MCTSAlpha


class AlphaZero:
    def __init__(self, model, optimizer, game, args, arena):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MCTSAlpha(game, args, model)
        self.sp_storage_path = 'dataset'
        self.model_storage_path = 'learning_results'
        self.arena = arena
        self.old_model = deepcopy(self.model)
        self.old_optimizer = deepcopy(self.optimizer)

    def save_as_pickle(self, filename, data):
        folder_name = self.sp_storage_path + '/' + filename
        with open(folder_name, 'wb') as f:
            pickle.dump(data, f)

    def load_pickle(self, filename):
        folder_name = self.sp_storage_path + '/' + filename
        with open(folder_name, 'rb') as f:
            data = pickle.load(f)
        return data

    def rotate_state(self, board, action_probs):
        rotated_probs = np.concatenate((np.rot90(
            action_probs[:self.game.size * self.game.size].reshape(self.game.size, self.game.size), k=1).flatten(),
                                        action_probs[25:]))
        rotated_state = np.rot90(board, k=1)

        return rotated_state, rotated_probs

    def augment_data(self, state, action_probs):
        result = []

        rotated_state = deepcopy(state)
        rotated_board = state.board
        rotated_probs = action_probs
        result.append((rotated_state, rotated_probs))

        for i in range(3):
            rotated_state = deepcopy(rotated_state)
            rotated_board, rotated_probs = self.rotate_state(rotated_board, rotated_probs)
            rotated_state.board = rotated_board

            result.append((rotated_state, rotated_probs))

        return result

    def selfPlay(self, process_number, number_games, iteration):
        self_play_samples = []

        for _ in trange(number_games):
            state = self.game.get_initial_state()
            memory = []
            game_length = 0
            while True:
                game_length += 1

                action_probs, number_iterations = self.mcts.search(state)
                print("here")
                print(action_probs)
                augmented_data = self.augment_data(state, action_probs)

                for rotated_state in augmented_data:
                    memory.append((rotated_state[0], rotated_state[1], state.next_to_move))

                # First size * size / 2 moves we choose moves proportionally to their probabilities
                # After that we choose the best move
                if game_length < self.game.size * self.game.size / 2:
                    temperature_action_probs = action_probs ** (1 / self.args['temperature'])
                    action = np.random.choice(self.game.action_size, p=temperature_action_probs)
                else:
                    action = np.argmax(torch.tensor(action_probs))

                state = self.game.get_next_state(state, action, state.next_to_move)

                value, _, is_terminal = self.game.get_value_and_terminated(state)

                if is_terminal:
                    for hist_state, hist_action_probs, hist_player in memory:
                        hist_board = hist_state.board
                        hist_outcome = value

                        if hist_player == -1:
                            hist_board = hist_state.get_reversed_perspective()
                            hist_outcome *= -1

                        self_play_samples.append((
                            hist_board,
                            hist_action_probs,
                            hist_outcome
                        ))
                    break

        file_name = f'Iteration_{iteration}/Process_{process_number}'
        self.save_as_pickle(file_name, self_play_samples)


    def train(self, memory):
        f = open('loss.txt.txt', 'a')
        random.shuffle(memory)

        cumulated_loss.txt = 0
        batch_size = self.args['batch_size']
        for batch_starting_index in range(0, len(memory), batch_size):
            sample = memory[batch_starting_index:batch_starting_index + batch_size]
            states, policy_targets, value_targets = zip(*sample)

            states = tuple(element.reshape(1, self.game.size, self.game.size) for element in states)

            states, policy_targets, value_targets = np.array(states), np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
            states = torch.tensor(states, dtype=torch.float32, device=self.model.device)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32, device=self.model.device)
            value_targets = torch.tensor(value_targets, dtype=torch.float32, device=self.model.device)

            out_policy, out_value = self.model(states)
            policy_loss.txt = F.cross_entropy(out_policy, policy_targets)
            value_loss.txt = F.mse_loss.txt(out_value, value_targets)
            loss.txt = policy_loss.txt + value_loss.txt
            cumulated_loss.txt += loss.txt

            self.optimizer.zero_grad()
            loss.txt.backward()
            self.optimizer.step()
        
        cumulated_loss.txt /= (len(memory) // batch_size)
        f.write(str(cumulated_loss.txt) + '\n')
        f.close()

    def learn(self):
        # Curatare folder de stocare a modelelor
        if os.path.exists(self.model_storage_path):
            shutil.rmtree(self.model_storage_path)
        os.makedirs(self.model_storage_path)

        # Curatare folder unde se stocheaza datele de self-play
        if os.path.exists(self.sp_storage_path):
            shutil.rmtree(self.sp_storage_path)
        os.makedirs(self.sp_storage_path)

        no_test_games = self.args['num_selfPlay_iterations']

        for iteration in trange(self.args['num_iterations']):
            memory = []
            processes = []
            sp_games_per_process = self.args['num_selfPlay_iterations'] // self.args['num_processes']
            os.makedirs(self.sp_storage_path + '/' + 'Iteration_' + str(iteration))

            start_time = time.perf_counter()
            for process_number in range(self.args['num_processes']):
                # print(f'\nSelfplay no. {selfPlay_iteration}')
                p = mp.Process(target=self.selfPlay, args=(process_number, sp_games_per_process, iteration))
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

            end_time = time.perf_counter()
            self_play_time = round(end_time - start_time, 3)
            file_time_logs = open('time_logs', 'a')
            file_time_logs.write(f'Iteratie {iteration}:\n')
            file_time_logs.write(f'\tTime for selfplay: {self_play_time} s\n')

            # for j in range(max(iteration - 1, 0), iteration + 1):
            for j in range(iteration, iteration + 1):
                for i in range(self.args['num_processes']):
                    file_name = f'Iteration_{j}/Process_{i}'

                    memory.extend(self.load_pickle(file_name))
            print('Marime memorie: ' + str(len(memory)))

            f = open('loss.txt.txt', 'a')
            f.write(f'Iteratie: {iteration}\n')
            f.close()
            self.model.train()
            start_time = time.perf_counter()
            for epoch in range(self.args['num_epochs']):
                f = open('loss.txt.txt', 'a')
                f.write('Epoca ' + str(epoch) + ": ")
                f.close()
                self.train(memory)
            end_time = time.perf_counter()
            training_time = round(end_time - start_time, 3)
            file_time_logs.write(f'\tTime for training: {training_time} s, memory size: {len(memory)}\n')

            start_time = time.perf_counter()

            # self.last_best_model.eval()
            self.old_model.load_state_dict(torch.load(f'learning_results3/model_{iteration - 1}.pt'))
            self.old_optimizer.load_state_dict(torch.load(f'learning_results3/optimizer_{iteration - 1}.pt'))

            old_best_model, new_model, avg_game_length = self.arena.play(self.old_model, self.model,
                                                                         'model_' + str(iteration - 1),
                                                                         'model_' + str(iteration), no_test_games)
            f = open('model_iteration_progress.txt', 'a')
            if new_model <= no_test_games * 11 // 20:
                self.model.load_state_dict(torch.load(f'learning_results3/model_{iteration - 1}.pt'))
                self.optimizer.load_state_dict(torch.load(f'learning_results3/optimizer_{iteration - 1}.pt'))
                f.write(
                    f'{iteration}: old vs new - ({old_best_model} vs {new_model}) winrate_new: {round(new_model / no_test_games, 2)} ({avg_game_length}) => model NOT updated\n')
                f.close()
            else:
                f.write(
                    f'{iteration}: old vs new - ({old_best_model} vs {new_model}) winrate_new: {round(new_model / no_test_games, 2)} ({avg_game_length}) => model     updated\n')
                f.close()

            end_time = time.perf_counter()
            evaluating_time = round(end_time - start_time, 3)
            file_time_logs.write(f'\tTime for evaluating: {evaluating_time} s\n\n')
            file_time_logs.close()

            torch.save(self.model.state_dict(), f"{self.model_storage_path}/model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"{self.model_storage_path}/optimizer_{iteration}.pt")

