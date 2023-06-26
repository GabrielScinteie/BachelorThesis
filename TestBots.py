import torch
from Agent.Evaluation.Arena import Arena
from GameLogic.GoStateManager import GoStateManager
from Agent.AlphaGoZero.Model import ResNet

if __name__ == '__main__':
    args = {
        'C': 2,
        'num_searches': 100,  # cate iteratii face algoritmul de NeuralNetwork
        'num_iterations': 100,
        'num_selfPlay_iterations': 60,  # cate jocuri se joaca per iteratie
        'num_epochs': 10,  # cate epoci de antrenare se intampla per iteratie
        'batch_size': 64,  # marimea batch-urilor in care se iau datele in cadrul  unei etape de antrenare
        'num_processes': 5,
        'temperature': 1,
        'dirichlet_eps': 0.3,
        'dirichlet_alpha': 0.03,
        'simulation_time': 0
    }

    size = 5
    go = GoStateManager(size)

    arena = Arena(go, args)

    device = torch.device("cpu")

    # os.remove('arena_results.txt')
    # models_folder_path = ''
    # for i in range(0, 100):
    #     for j in range(i + 1, 100):
    #         if i != j:
    #             model1 = ResNet(go, 4, 128, device=device)
    #             model2 = ResNet(go, 4, 128, device=device)
    #
    #             model1.load_state_dict(torch.load(models_folder_path + 'model_'+str(i)+'.pt', map_location=device))
    #             model2.load_state_dict(torch.load(models_folder_path + 'model_'+str(j)+'.pt', map_location=device))
    #
    #             optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
    #             optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
    #
    #             arena.play(model1, model2, 'model_'+str(i), 'model_'+str(j), 100, 'arena_results.txt')

    model1 = ResNet(go, 4, 256, device=device)
    model2 = ResNet(go, 4, 256, device=device)

    # model1.load_state_dict(torch.load('learning_results/model_3.pt'))
    # model2.load_state_dict(torch.load('learning_results/model_4_vechi.pt'))
    #
    # same = True
    # for p1, p2 in zip(model1.parameters(), model2.parameters()):
    #     if p1.data.ne(p2.data).sum() > 0:
    #         same = False
    #
    # print(same)
    # model1.load_state_dict(torch.load('learning_results3/model_4 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_5 (1).pt', map_location=device))

    model1.eval()
    model2.eval()

    # optimizer8 = torch.optim.Adam(model1.parameters(), lr=0.001)
    # optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
    # arena.play(model1, model2, 'model_4', 'model_5', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_4', 'model_5', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_5 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_6 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_5', 'model6', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_5', 'model6', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_6 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_7 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_6', 'model_7', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_6', 'model_7', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_7 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_8 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_7', 'model_8', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_7', 'model_8', 60, 'arena_results.txt')

    model1.load_state_dict(torch.load('learning_results/model_0.pt', map_location=device))
    model2.load_state_dict(torch.load('learning_results/model_1.pt', map_location=device))

    arena.play(model1, model2, 'model_0', 'model_1', args['num_selfPlay_iterations'], 'arena_results.txt')
    arena.play(model1, model2, 'model_0', 'model_1', args['num_selfPlay_iterations'], 'arena_results.txt')

    model1.load_state_dict(torch.load('learning_results/model_1.pt', map_location=device))
    model2.load_state_dict(torch.load('learning_results/model_2.pt', map_location=device))

    arena.play(model1, model2, 'model_1', 'model_2', args['num_selfPlay_iterations'], 'arena_results.txt')
    arena.play(model1, model2, 'model_1', 'model_2', args['num_selfPlay_iterations'], 'arena_results.txt')

    model1.load_state_dict(torch.load('learning_results/model_0.pt', map_location=device))
    model2.load_state_dict(torch.load('learning_results/model_1.pt', map_location=device))
    arena.play(model1, model2, 'model_0', 'model_1', args['num_selfPlay_iterations'], 'arena_results.txt')

    model1.load_state_dict(torch.load('learning_results/model_1.pt', map_location=device))
    model2.load_state_dict(torch.load('learning_results/model_2.pt', map_location=device))
    arena.play(model1, model2, 'model_1', 'model_2', args['num_selfPlay_iterations'], 'arena_results.txt')

    # model1.load_state_dict(torch.load('learning_results3/model_0 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_5 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_0', 'model_5', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_0', 'model_5', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_5 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_7 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_5', 'model_7', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_5', 'model_7', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_5 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_9 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_5', 'model_9', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_5', 'model_9', 60, 'arena_results.txt')
    #
    # model1.load_state_dict(torch.load('learning_results3/model_7 (1).pt', map_location=device))
    # model2.load_state_dict(torch.load('learning_results3/model_9 (1).pt', map_location=device))
    #
    # arena.play(model1, model2, 'model_7', 'model_9', 60, 'arena_results.txt')
    # arena.play(model1, model2, 'model_7', 'model_9', 60, 'arena_results.txt')




    # mcts1 = MCTS(go, args)
    # mcts2 = MCTSAlpha(go, args, model2)
    #
    # state = go.get_initial_state()
    # game_length = 0
    #
    # while state.is_game_over() == False:
    #     if game_length % 2 == 0:
    #         print(game_length)
    #         action_probs = mcts1.search(state)
    #     else:
    #         action_probs = mcts2.search(state)
    #     valid_moves = go.get_valid_moves(state)
    #     action_probs *= valid_moves
    #     action_probs /= np.sum(action_probs)
    #
    #     action = np.argmax(action_probs)
    #     # print(f'Jucatorul {state.next_to_move} a facut miscarea {action}')
    #
    #     state = go.get_next_state(state, action, state.next_to_move)
    #
    #     # file.write(f'Jucatorul {state.next_to_move} a facut miscarea {action}\n')
    #     # file.write(str(state))
    #     # file.write('\n')
    #     game_length += 1
    #
    # result, scores, mean_value = go.get_value_and_terminated(state)
    # print(result)
    # print(scores)
    # print(mean_value)

    # state = go.get_initial_state()

    # SELFPLAY FUNCTIONEAZA CORECT
    # device = torch.device("cpu")
    # model = ResNet(go, 4, 64, device=device)
    #model.load_state_dict(torch.load('model_4.pt', map_location=device))
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    # # num_iterations * num_selfPlay_iterations * nr_matari joc * num_searches = 3 * 20 * 100 = 6000

    # alphaZero = AlphaZero(model, optimizer, go, args)
    # memory = alphaZero.selfPlay()
    # for elem in memory:
    #     state, prob, result = elem
    #     print(state)
    #     print(result)
    #     print()