import os
import random
import time

import numpy as np
import torch
import torch.nn.functional as F
import torch.multiprocessing as mp
import pickle
from tqdm import trange

from Go.MCTSAlpha import MCTSAlpha


class AlphaZero:
    def __init__(self, model, optimizer, game, args, dataset_self_play_storage_path):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MCTSAlpha(game, args, model)
        self.mean_length_self_play = 0
        self.sp_folder_path = dataset_self_play_storage_path

    def save_as_pickle(self, filename, data):
        folder_name = self.sp_folder_path + '/' + filename
        with open(folder_name, 'wb') as f:
            pickle.dump(data, f)

    def load_pickle(self, filename):
        folder_name = self.sp_folder_path + '/' + filename
        with open(folder_name, 'rb') as f:
            data = pickle.load(f)
        return data

    def selfPlay(self, process_number, number_games):
        self_play_records = []

        for i in range(number_games):
            state = self.game.get_initial_state()
            memory = []
            game_length = 0
            while True:
                game_length += 1
                # print(len(state.history_boards))
                action_probs = self.mcts.search(state)

                memory.append((state, action_probs, state.next_to_move))

                action = np.random.choice(self.game.action_size, p=action_probs)

                state = self.game.get_next_state(state, action, state.next_to_move)

                value, _, is_terminal = self.game.get_value_and_terminated(state)

                if is_terminal:
                    print(game_length)
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
        file_name = f'Process_{process_number}'
        self.save_as_pickle(file_name, self_play_records)

    def train(self, memory):
        random.shuffle(memory)
        for batchIdx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batchIdx:batchIdx+self.args['batch_size']]  # Change to memory[batchIdx:batchIdx+self.args['batch_size']] in case of an error
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

            self.optimizer.zero_grad()  # change to self.optimizer
            loss.backward()
            self.optimizer.step()  # change to self.optimizer

    def learn(self):
        # f = open('mean_games_length.txt', 'a')
        for iteration in range(self.args['num_iterations']):
            # self.mean_length_self_play = 0
            memory = []

            self.model.eval()

            processes = []
            sp_games_per_process = self.args['num_selfPlay_iterations'] // self.args['num_processes']
            for process_number in range(self.args['num_processes']):
                # print(f'\nSelfplay no. {selfPlay_iteration}')
                p = mp.Process(target=self.selfPlay, args=(process_number, sp_games_per_process))
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

            for i in range(self.args['num_processes']):
                file_name = f'Process_{i}'
                memory.extend(self.load_pickle(file_name))
            print('Marime memorie(ar trebui sa fie 10' + str(len(memory)))
            # self.mean_length_self_play /= self.args['num_selfPlay_iterations']

            # f.write(f'Iteratia {iteration}: ' + str(self.mean_length_self_play))

            if iteration == self.args['num_iterations'] - 1:
                self.save_memory_in_file(memory)

            self.model.train()
            for epoch in trange(self.args['num_epochs']):
                self.train(memory)

            torch.save(self.model.state_dict(), f"model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}.pt")
        # f.close()

    def save_memory_in_file(self, memory):
        f = open('memory.txt', 'a')
        for line in memory:
            f.write(str(line[0]) + '\n')
            f.write(str(np.argmax(line[1])) + '\n')
            f.write(str(line[2]) + '\n')
            f.write('\n')

