from nodes import TwoPlayersGameMonteCarloTreeSearchNode
from search import MonteCarloTreeSearch
from go import GoAPI, printBoard, GoGameState, GoMove
from copy import deepcopy

# state = np.zeros((3, 3))
# state[0][0] = 1
# state[0][2] = -1
# state[1][0] = 1
# state[2][0] = -1
# state[1][1] = 1
# state[1][2] = -1
# initial_board_state = TicTacToeGameState(state=state, next_to_move=1)
#
# root = TwoPlayersGameMonteCarloTreeSearchNode(state=initial_board_state)
# mcts = MonteCarloTreeSearch(root)
# best_node = mcts.best_action(10000)
# print(best_node.state.board)

def playGameHumanVsHuman():
    size = 3
    goInitialState = GoAPI(size)
    initial_board_state = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)

    while initial_board_state.running:
        printBoard(initial_board_state.board, size)
        input_row = int(input('Enter row: ')) - 1
        input_col = int(input('Enter column: ')) - 1

        while (input_row, input_col) not in list(map(lambda move: (move.row, move.column), initial_board_state.get_legal_actions())):
            print('Invalid move. Try again.')
            input_row = int(input('Enter row: ')) - 1
            input_col = int(input('Enter column: ')) - 1

        move = GoMove(input_row, input_col, initial_board_state.next_to_move)
        initial_board_state.move(move)

    print(initial_board_state.game_result)
    print(initial_board_state.get_score())



def playGameHumanVsComputer():
    size = 3
    goInitialState = GoAPI(size)

    initial_board_state = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)
    root = TwoPlayersGameMonteCarloTreeSearchNode(state=initial_board_state)
    mcts = MonteCarloTreeSearch(root)
    best_node = mcts.best_action(None, 5)
    new_state = best_node.state

    def find_difference_between_boards(board1, board2):
        for i in range(len(board1)):
            for j in range(len(board2)):
                if board1[i][j] != board2[i][j]:
                    return i + 1, j + 1

        return 0,0


    turn = 'Human'
    while new_state.is_game_over() == False:
        #print(f'Mutarea {index + 1}')
        printBoard(new_state.board, size)
        if turn == 'Computer':
            root = TwoPlayersGameMonteCarloTreeSearchNode(state=new_state)
            print(len(root.children))
            mcts = MonteCarloTreeSearch(root)
            best_node = mcts.best_action(None, 5)
            move = find_difference_between_boards(best_node.state.board, new_state.board)
            print(f'Am facut mutarea {move}')
            new_state = best_node.state
            turn = 'Human'
        elif turn == 'Human':
            input_row = int(input('Enter row: ')) - 1
            input_col = int(input('Enter column: ')) - 1

            while (input_row, input_col) not in list(map(lambda move: (move.row, move.column),best_node.state.get_legal_actions())):
                print('Invalid move. Try again.')
                input_row = int(input('Enter row: ')) - 1
                input_col = int(input('Enter column: ')) - 1

            move = GoMove(input_row, input_col, best_node.state.next_to_move)
            new_state = deepcopy(best_node.state).move(move)
            new_state = GoGameState(state=new_state, next_to_move=new_state.next_to_move)
            turn = 'Computer'

    print(new_state.game_result)
    print(new_state.get_score())

def generateGames():
    size = 5
    goInitialState = GoAPI(size)
    initial_board_state = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)
    root = TwoPlayersGameMonteCarloTreeSearchNode(state=initial_board_state)
    mcts = MonteCarloTreeSearch(root)
    best_node = mcts.best_action(None, 5)

def playGameComputerVsComputer():
    size = 3
    goInitialState = GoAPI(size)

    initial_board_state = GoGameState(state=goInitialState, next_to_move=goInitialState.currentPlayer)
    root = TwoPlayersGameMonteCarloTreeSearchNode(state=initial_board_state)
    mcts = MonteCarloTreeSearch(root)
    best_node = mcts.best_action(None, 10)
    new_state = best_node.state

    def find_difference_between_boards(board1, board2):
        for i in range(len(board1)):
            for j in range(len(board2)):
                if board1[i][j] != board2[i][j]:
                    return i + 1, j + 1

        return 0, 0
    # f = open('games.txt', 'a')

    while not new_state.is_game_over():
        printBoard(new_state.board, size)
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=new_state)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(None, 5)
        move = find_difference_between_boards(best_node.state.board, new_state.board)
        # f.write(f'{move[0]} {move[1]},')
        print(f'Am facut mutarea {move}')
        new_state = best_node.state
    # f.write('\n')
    print(new_state.game_result)
    print(new_state.get_score())

# generateGames()
playGameHumanVsComputer()
#playGameHumanVsHuman()