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

from Go.MCTSAlpha import MCTSAlpha


class AlphaZero:
    def __init__(self, model, optimizer, game, args, dataset_self_play_storage_path, arena):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MCTSAlpha(game, args, model)
        self.mean_length_self_play = 0
        self.sp_folder_path = dataset_self_play_storage_path
        self.arena = arena
        self.last_best_model = None
        self.last_best_optimizer = None

    def save_as_pickle(self, filename, data):
        folder_name = self.sp_folder_path + '/' + filename
        with open(folder_name, 'wb') as f:
            pickle.dump(data, f)

    def load_pickle(self, filename):
        folder_name = self.sp_folder_path + '/' + filename
        with open(folder_name, 'rb') as f:
            data = pickle.load(f)
        return data

    def augment_data(self, state, action_probs):

        rotated_action_probs = np.flip(action_probs.reshape(self.game.size, self.game.size), axis=0)
        rotated_state = np.rot90(state, k=1)

        return rotated_state, rotated_action_probs

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
        self_play_records = []

        for i in trange(number_games):
            state = self.game.get_initial_state()
            memory = []
            game_length = 0
            while True:
                game_length += 1
                # print(len(state.history_boards))
                action_probs = self.mcts.search(state)

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
                    # print(game_length)
                    for hist_state, hist_action_probs, hist_player in memory:
                        hist_board = hist_state.board
                        hist_outcome = value

                        if hist_player == -1:
                            hist_board = hist_state.get_reversed_perspective()
                            hist_outcome *= -1

                        # Stare s, alb la mutare, alb castiga => value = -1. Board-ul trebuie inversat, deci si value = 1
                        # Stare s, alb la mutare, alb pierde => value = 1. Board-ul trebuie inversat, deci si value = -1
                        # Stare s, negru la mutare, negru castiga => value = 1
                        # Stare s, negru la mutare, negru pierde => value = -1

                        self_play_records.append((
                            hist_board,
                            hist_action_probs,
                            hist_outcome
                        ))
                    break

                    # print('Lungime joc self-play: ' + str(len(returnMemory)))

        file_name = f'Iteration_{iteration}/Process_{process_number}'
        self.save_as_pickle(file_name, self_play_records)

    def train(self, memory):
        f = open('loss', 'a')
        random.shuffle(memory)
        cumulated_loss = 0

        for batchIdx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batchIdx:batchIdx+self.args['batch_size']]
            state, policy_targets, value_targets = zip(*sample)

            state = tuple(element.reshape(1, self.game.size, self.game.size) for element in state)

            state, policy_targets, value_targets = np.array(state), np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
            state = torch.tensor(state, dtype=torch.float32, device=self.model.device)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32, device=self.model.device)
            value_targets = torch.tensor(value_targets, dtype=torch.float32, device=self.model.device)

            out_policy, out_value = self.model(state)

            policy_loss = F.cross_entropy(out_policy, policy_targets)
            value_loss = F.mse_loss(out_value, value_targets)
            loss = policy_loss + value_loss
            cumulated_loss += loss

            self.optimizer.zero_grad()  # change to self.optimizer
            loss.backward()
            self.optimizer.step()  # change to self.optimizer
        
        cumulated_loss /= (len(memory) // self.args['batch_size'])
        f.write(str(cumulated_loss) + '\n')
        f.close()

    def learn(self):
        directory_path = "learning_results3"

        # DECOMENTEAZA DACA VREI SA STERGI FOLDERUL UNDE SE STOCHEAZA MODELELE
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        os.makedirs(directory_path)

        # DECOMENTEAZA DACA VREI SA STERGI FOLDERUL UNDE SE STOCHEAZA DATELE DE SELFPLAY
        if os.path.exists(self.sp_folder_path):
            shutil.rmtree(self.sp_folder_path)
        os.makedirs(self.sp_folder_path)

        no_test_games = self.args['num_selfPlay_iterations']

        for iteration in trange(self.args['num_iterations']):
            self.last_best_model, self.last_best_optimizer = deepcopy(self.model), deepcopy(self.optimizer)
            memory = []

            self.model.eval()

            processes = []
            sp_games_per_process = self.args['num_selfPlay_iterations'] // self.args['num_processes']
            os.makedirs(self.sp_folder_path + '/' + 'Iteration_' + str(iteration))

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

            self.model.train()
            f = open('loss', 'a')
            f.write(f'Iteratie: {iteration}\n')
            f.close()

            start_time = time.perf_counter()
            for epoch in range(self.args['num_epochs']):
                f = open('loss', 'a')
                f.write('Epoca ' + str(epoch) + ": ")
                f.close()
                self.train(memory)
            end_time = time.perf_counter()
            training_time = round(end_time - start_time, 3)
            file_time_logs.write(f'\tTime for training: {training_time} s, memory size: {len(memory)}\n')

            start_time = time.perf_counter()

            self.model.eval()
            self.last_best_model.eval()
            old_best_model, new_model, avg_game_length = self.arena.play(self.last_best_model, self.model, 'model_vechi', 'model_'+str(iteration), no_test_games)
            f = open('model_iteration_progress.txt', 'a')
            if new_model <= no_test_games * 11 // 20:
                self.model = self.last_best_model
                self.optimizer = self.last_best_optimizer
                f.write(f'{iteration}: old vs new - ({old_best_model} vs {new_model}) winrate_new: {round(new_model/no_test_games,2)} ({avg_game_length}) => model NOT updated\n')
                f.close()
            else:
                f.write(f'{iteration}: old vs new - ({old_best_model} vs {new_model}) winrate_new: {round(new_model/no_test_games,2)} ({avg_game_length}) => model     updated\n')
                f.close()

            end_time = time.perf_counter()
            evaluating_time = round(end_time - start_time, 3)
            file_time_logs.write(f'\tTime for evaluating: {evaluating_time} s\n\n')
            file_time_logs.close()

            torch.save(self.model.state_dict(), f"{directory_path}/model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"{directory_path}/optimizer_{iteration}.pt")

    def save_memory_in_file(self, memory):
        f = open('memory.txt', 'a')
        for line in memory:
            f.write(str(line[0]) + '\n')
            f.write(str(np.argmax(line[1])) + '\n')
            f.write(str(line[2]) + '\n')
            f.write('\n')

