import random

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import trange

from Go.MCTSAlpha import MCTSAlpha


class AlphaZero:
    def __init__(self, model, optimizer, game, args):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MCTSAlpha(game, args, model)

    def selfPlay(self):
        memory = []
        state = self.game.get_initial_state()
        while True:

            action_probs = self.mcts.search(state)

            memory.append((state, action_probs, state.next_to_move))

            action = np.random.choice(self.game.action_size, p=action_probs)

            state = self.game.get_next_state(state, action, state.next_to_move)

            value, _, is_terminal = self.game.get_value_and_terminated(state)

            if is_terminal:
                returnMemory = []
                for hist_state, hist_action_probs, hist_player in memory:
                    # If player X has to move but the state is terminal TODO cum stochez cine a castigat din starea din trecut?
                    hist_board = hist_state.board
                    hist_outcome = value

                    if hist_player == -1:
                        hist_board = hist_state.get_reversed_perspective()
                        hist_outcome *= -1

                    # Stare s, alb la mutare, alb castiga => value = -1. Board-ul trebuie inversat, deci si value = 1
                    # Stare s, alb la mutare, alb pierde => value = 1. Board-ul trebuie inversat, deci si value = -1
                    # Stare s, negru la mutare, negru castiga => value = 1
                    # Stare s, negru la mutare, negru pierde => value = -1
                    returnMemory.append((
                        hist_board,
                        hist_action_probs,
                        hist_outcome
                    ))

                # print('Lungime joc self-play: ' + str(len(returnMemory)))
                return returnMemory

    def train(self, memory):
        # TODO de inteles, copy paste
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
        for iteration in range(self.args['num_iterations']):
            memory = []

            self.model.eval()
            for selfPlay_iteration in trange(self.args['num_selfPlay_iterations']):
                # print(f'Selfplay no. {selfPlay_iteration}')
                memory += self.selfPlay()

            if iteration == self.args['num_iterations'] - 1:
                self.save_memory_in_file(memory)

            self.model.train()
            for epoch in trange(self.args['num_epochs']):
                self.train(memory)

            torch.save(self.model.state_dict(), f"model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}.pt")

    def save_memory_in_file(self, memory):
        f = open('memory.txt', 'a')
        for line in memory:
            f.write(str(line[0]) + '\n')
            f.write(str(np.argmax(line[1])) + '\n')
            f.write(str(line[2]) + '\n')
            f.write('\n')

