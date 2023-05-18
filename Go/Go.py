from copy import deepcopy

import numpy as np


class TicTacToe:
    def __init__(self):
        self.row_count = 3
        self.column_count = 3
        self.action_size = self.row_count * self.column_count

    def get_initial_state(self):
        return np.zeros((self.row_count, self.column_count))

    def get_next_state(self, state, action, player):
        row = action // self.column_count
        column = action % self.column_count
        state[row, column] = player
        return state

    def get_valid_moves(self, state):
        return (state.reshape(-1) == 0).astype(np.uint8)

    def check_win(self, state, action):
        row = action // self.column_count
        column = action % self.column_count
        player = state[row, column]

        return (
                np.sum(state[row, :]) == player * self.column_count
                or np.sum(state[:, column]) == player * self.row_count
                or np.sum(np.diag(state)) == player * self.row_count
                or np.sum(np.diag(np.flip(state, axis=0))) == player * self.row_count
        )

    def get_value_and_terminated(self, state, action):
        if self.check_win(state, action):
            return 1, True
        if np.sum(self.get_valid_moves(state)) == 0:
            return 0, True
        return 0, False

    def get_opponent(self, player):
        return -player


class Go:
    def __init__(self, size):
        self.size = size
        self.action_size = self.size * self.size + 1

    def get_initial_state(self):
        return GoState(self.size)

    def get_next_state(self, state, action, player):
        if action == self.size * self.size:
            row, column = -1, -1
        else:
            row = action // self.size
            column = action % self.size

        newState = deepcopy(state)
        newState.move(GoMove(row, column, player))

        return newState

    def get_valid_moves(self, state):
        return state.get_legal_actions()

    def get_value_and_terminated(self, state):
        # TODO nu sunt sigur de state.next_to_move aici

        if state.is_game_over() == True:
            # Exemplu output: True, 1, [15.5, 12]
            return state.game_result, state.get_score(), True
        else:
            return None, None, False

    def get_opponent(self, player):
        return -player


class GoMove:
    def __init__(self, row, column, player):
        self.row = row
        self.column = column
        self.player = player

    def __repr__(self):
        return "Player:{0} Row:{1} Column:{2}".format(
            self.player,
            self.row,
            self.column)


class GoState:
    def __init__(self, size=5, komi=1.5):
        self.size = size
        self.running = True
        self.komi = komi
        self.board = np.zeros((self.size, self.size))
        self.players = [1, -1]
        self.next_to_move = self.players[0]
        self.consecutive_pass = 0
        self.captured_stones = {self.players[0]: [], self.players[1]: []}
        self.historyBoards = []

    def __str__(self):
        return np.array2string(np.where(self.board == 1, 'X', np.where(self.board == 0, '.', '0')), separator='')

    def get_score(self):
        return self.score

    # def _convert_board_to_numbers(self):
    #     converted_matrix = []
    #     char_to_val = {'X': 1.0, '.': 0.0, 'O': -1.0}
    #     for row in self.board:
    #         converted_row = [char_to_val[char] for char in row]
    #         converted_matrix.append(converted_row)
    #
    #     return converted_matrix
    #
    # def get_encoded_state(self):
    #     encoded_state = self._convert_board_to_numbers()
    #     return encoded_state

    @property
    def game_result(self):
        # Returns 1 if black won and -1 if white won
        whiteScore = self.komi
        blackScore = 0

        capturedStonesByWhite = len(self.captured_stones[-1])
        capturedStonesByBlack = len(self.captured_stones[1])

        whiteTerritory = 0
        blackTerritory = 0

        visited = []

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    blackScore += 1
                if self.board[i][j] == -1:
                    whiteScore += 1
                if self.board[i][j] == 0 and (i, j) not in visited:
                    numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(i, j, visited, 0, 0, 0)
                    # print(f'Grupul ce-l contine pe {i} {j} are {whiteNeighbors} vecini albi, {blackNeighbors} vecini negri si are {numberIntersections} elemente')
                    if whiteNeighbors == 0:
                        # print(f'{numberIntersections} puncte pentru negru')
                        blackTerritory += numberIntersections
                    if blackNeighbors == 0:
                        # print(f'{numberIntersections} puncte pentru alb')
                        whiteTerritory += numberIntersections

        # print(f'Black has captured {capturedStonesByBlack} stones and has {blackTerritory} territory points')
        # print(f'White has captured {capturedStonesByWhite} stones and has {whiteTerritory} territory points')
        blackScore += capturedStonesByBlack + blackTerritory
        whiteScore += capturedStonesByWhite + whiteTerritory
        self.score = [blackScore, whiteScore]

        # print(f'Black: {blackScore}, White: {whiteScore}')
        if blackScore > whiteScore:
            return 1
        return -1

    def is_game_over(self):
        # TODO nu sunt sigur ca e bine
        return self.running == False

    def is_move_legal(self, move):
        row = move.row
        column = move.column
        player = move.player

        if self.board[row][column] != 0:
            return False

        # Simulez mutarea
        new_board = deepcopy(self.board)
        # print(f'Valoarea lui player este {player}')
        new_board[row][column] = player

        # Verific daca ultima piesa adaugata captureaza piese ale inamicului, pentru ca in acest caz ultima piesa
        # adaugata are cu siguranta cel putin o libertate
        visitedIntersections = []

        oppositePlayer = self.getOppositePlayer(player)

        neighbors = self.getValidNeighbours(row, column)
        hasLiberty = False
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if new_board[i][j] == oppositePlayer and (i, j) not in visitedIntersections:
                groupStones = []
                visited = []
                enemyGroupLiberty = self.hasLiberty(new_board, i, j, visited, groupStones, oppositePlayer)
                visitedIntersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci mutarea este cu siguranta una valida
                if not enemyGroupLiberty:
                    hasLiberty = True

        # Verific daca grupul creat de adaugarea ultimei pietre are libertati
        if self.hasLiberty(new_board, row, column, [], [], player):
            hasLiberty = True

        self.tryCapture(new_board,
                        {self.players[0]: [], self.players[1]: []},
                        row,
                        column,
                        player
                        )

        if hasLiberty and self.respectsKoRule(new_board):
            return True

        return False

    def move(self, move):
        row = move.row
        col = move.column
        player = move.player

        if (row, col) == (-1, -1):
            self.consecutive_pass += 1
            if self.consecutive_pass == 2:
                self.running = False
        else:
            self.board[row][col] = player
            self.tryCapture(self.board, self.captured_stones, row, col, player)
            self.historyBoards.append(deepcopy(self.board))
            self.consecutivePass = 0

        self.next_to_move = self.getOppositePlayer(self.next_to_move)

        return self

    def get_legal_actions(self):
        validMoves = np.zeros(self.size * self.size + 1)

        for row in range(self.size):
            for col in range(self.size):
                move = GoMove(row, col, self.next_to_move)
                if self.is_move_legal(move):
                    validMoves[row * self.size + col] = 1

        validMoves[-1] = 1  # Pass
        return validMoves

    def getTerritory(self, row, col, visited, numberIntersections, whiteNeighbors, blackNeighbors):
        # print(f'Sunt in getTerritory si testez pozitia ({row}, {col})')
        if (row, col) in visited:
            return numberIntersections, whiteNeighbors, blackNeighbors

        # print('Incrementez numarul de intersectii')
        visited.append((row, col))

        # Teritoriul are cel putin o intersectie libera, piesa de pe pozitia curenta
        numberIntersections += 1

        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]

        # Parcurg toti cei 4 vecini
        for neighbor in neighbors:
            newRow = neighbor[0]
            newCol = neighbor[1]

            if 0 <= newRow < self.size and 0 <= newCol < self.size and (newRow, newCol) not in visited:
                if self.board[newRow][newCol] == 0:
                    numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(newRow, newCol, visited,
                                                                                            numberIntersections,
                                                                                            whiteNeighbors,
                                                                                            blackNeighbors)
                elif self.board[newRow][newCol] == 1:
                    blackNeighbors += 1
                elif self.board[newRow][newCol] == -1:
                    whiteNeighbors += 1

        return numberIntersections, whiteNeighbors, blackNeighbors

    def hasLiberty(self, new_board, row, col, visited, groupStones, player):
        # Daca am vizitat deja acest nod
        if (row, col) in visited:
            return False

        # Adaug nodul curent la vizitat
        visited.append((row, col))

        # Adaug nodul curent la grupul actual
        groupStones.append((row, col))

        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        hasLiberties = False

        # Parcurg toti cei 4 vecini
        for neighbor in neighbors:
            newRow = neighbor[0]
            newCol = neighbor[1]
            # Daca vecinii sunt in interiorul tablei
            if 0 <= newRow < self.size and 0 <= newCol < self.size:
                # Daca vecinul este o piesa care apartine playerului curent, atunci apelez getGroup de vecin
                if new_board[newRow][newCol] == player:
                    # print(f'Verific daca vecinul ({newRow}, {newCol}) are libertati')
                    hasLiberties = hasLiberties or self.hasLiberty(new_board, newRow, newCol, visited, groupStones,
                                                                   player)

                # Daca vecinul este un spatiu gol, atunci grupul are cel putin o libertate
                elif new_board[newRow][newCol] == 0:
                    hasLiberties = True

        return hasLiberties

    def respectsKoRule(self, new_board):
        for previousBoard in self.historyBoards:
            # print('Board vechi: ')
            # printBoard(previousBoard, self.size)
            # printBoard(new_board, self.size)
            # print()
            if str(new_board) == str(previousBoard):
                # print('Nu se respecta regula Ko')
                return False

        # print('Regula Ko este respectata')
        return True

    def getOppositePlayer(self, player):
        oppositePlayer = self.players[0]
        if player == self.players[0]:
            oppositePlayer = self.players[1]

        return oppositePlayer

    def getValidNeighbours(self, row, col):
        dl = [-1, 0, 1, 0]
        dc = [0, 1, 0, -1]
        neighbors = []
        for i in range(4):
            neighbor_row = row + dl[i]
            neighbor_col = col + dc[i]
            if 0 <= neighbor_row < self.size and 0 <= neighbor_col < self.size:
                neighbors.append((neighbor_row, neighbor_col))

        return neighbors

    def tryCapture(self, board, capturedStones, row, col, player):
        visitedIntersections = []

        oppositePlayer = self.players[0]
        if player == self.players[0]:
            oppositePlayer = self.players[1]

        neighbors = self.getValidNeighbours(row, col)
        # print(neighbors)
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if board[i][j] == oppositePlayer and (i, j) not in visitedIntersections:
                groupStones = []
                visited = []
                enemyGroupLiberty = self.hasLiberty(board, i, j, visited, groupStones, oppositePlayer)
                # print(f'Sunt {row},{col} si am libertati: {enemyGroupLiberty}')
                visitedIntersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci
                if not enemyGroupLiberty:
                    for (enemyRow, enemyCol) in groupStones:
                        board[enemyRow][enemyCol] = 0
                        capturedStones[player].append((enemyRow, enemyCol))
