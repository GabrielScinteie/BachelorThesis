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
                winner = value
                returnMemory = []
                for hist_state, hist_action_probs, hist_player in memory:
                    # If player X has to move but the state is terminal TODO cum stochez cine a castigat din starea din trecut?
                    hist_outcome = value if hist_player == winner  else -value
                    returnMemory.append((
                        hist_state,
                        hist_action_probs,
                        hist_outcome
                    ))
                return returnMemory

    def train(self, memory):
        # TODO de inteles, copy paste
        random.shuffle(memory)
        for batchIdx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batchIdx:batchIdx+self.args['batch_size']]  # Change to memory[batchIdx:batchIdx+self.args['batch_size']] in case of an error
            state, policy_targets, value_targets = zip(*sample)

            size = state[0].size
            state = tuple(element.board.reshape(1, size, size) for element in state)
            print(state)

            state, policy_targets, value_targets = np.array(state), np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
            state = torch.tensor(state, dtype=torch.float32)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32)
            value_targets = torch.tensor(value_targets, dtype=torch.float32)
            print(state.shape)
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
                memory += self.selfPlay()

            self.model.train()
            for epoch in trange(self.args['num_epochs']):
                self.train(memory)

            torch.save(self.model.state_dict(), f"model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}.pt")


