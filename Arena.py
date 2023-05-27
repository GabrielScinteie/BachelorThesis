import numpy as np
import torch


class Arena:
    def __init__(self, game):
        self.game = game

    # The model that is first given as param starts with black
    def play_one_game(self, model1, model2, file):
        state = self.game.get_initial_state()
        device = model1.device
        game_length = 0
        while state.is_game_over() == False:
            if state.next_to_move == -1:
                tensor_state = torch.tensor(state.get_reversed_perspective(), device=device).unsqueeze(0).unsqueeze(0).float()
                policy, value = model2(tensor_state)
            else:
                tensor_state = torch.tensor(state.board, device=device).unsqueeze(0).unsqueeze(0).float()
                policy, value = model1(tensor_state)

            policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()
            valid_moves = self.game.get_valid_moves(state)
            policy *= valid_moves
            policy /= np.sum(policy)

            action = np.random.choice(len(policy), p=policy)

            #file.write(f'Jucatorul {state.next_to_move} a facut miscarea {action}\n')
            state = self.game.get_next_state(state, action, state.next_to_move)
            #file.write(str(state))
            #file.write('\n')
            game_length += 1

        result, scores, _ = self.game.get_value_and_terminated(state)
        # file.write(f'A castigat jucatorul {result} in {game_length} miscari cu scorurile {scores}.\n')
        return result, game_length


    def play(self, model1, model2, model1_name, model2_name, number_games, folder_store_path):
        print(f'{model1_name} vs {model2_name}')
        f = open(folder_store_path, 'a')

        model1_wins_number = 0
        model2_wins_number = 0

        medium_game_length = 0
        for i in range(number_games // 2):
            # f.write(f'Game number {i}: \n')
            result, game_length = self.play_one_game(model1, model2, f)
            medium_game_length += game_length
            if result == 1:
                model1_wins_number += 1
            else:
                model2_wins_number += 1

        for i in range(number_games // 2, number_games):
            # f.write(f'Game number {i}: \n')
            result, game_length = self.play_one_game(model2, model1, f)
            medium_game_length += game_length
            if result == 1:
                model2_wins_number += 1
            else:
                model1_wins_number += 1

        medium_game_length = medium_game_length // number_games
        f.write(f'{model1_name} vs {model2_name} : {model1_wins_number} -{model2_wins_number} ({str(medium_game_length)})\n')
        f.close()
