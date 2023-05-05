from copy import deepcopy
from common import TwoPlayersAbstractGameState, AbstractGameAction


class GoMove(AbstractGameAction):
    def __init__(self, row, column, player):
        self.row = row
        self.column = column
        self.player = player

    def __repr__(self):
        return "Player:{0} Row:{1} Column:{2}".format(
            self.player,
            self.row,
            self.column)

class GoGameState(TwoPlayersAbstractGameState):
    def __init__(self, state, next_to_move, win=None):
        self.size = state.size
        self.running = state.running
        self.komi = state.komi
        self.board = state.board
        self.players = state.players
        self.symbols = state.symbols
        self.next_to_move = next_to_move
        self.consecutivePass = state.consecutivePass
        self.capturedStones = state.capturedStones
        self.historyBoards = state.historyBoards
        self.win = win
        self.score = []

    def get_score(self):
        return self.score

    @property
    def game_result(self):
        # Returns 1 if black won and -1 if white won
        whiteScore = self.komi
        blackScore = 0

        capturedStonesByWhite = len(self.capturedStones[-1])
        capturedStonesByBlack = len(self.capturedStones[1])

        whiteTerritory = 0
        blackTerritory = 0

        visited = []

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 'X':
                    blackScore += 1
                if self.board[i][j] == 'O':
                    whiteScore += 1
                if self.board[i][j] == '.' and (i, j) not in visited:
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
        return len(self.get_legal_actions()) == 0 or self.running == False

    def is_move_legal(self, move):
        row = move.row
        column = move.column
        player = move.player

        if self.board[row][column] != '.':
            return False

        # Simulez mutarea
        new_board = deepcopy(self.board)
        #print(f'Valoarea lui player este {player}')
        new_board[row][column] = self.symbols[player]

        # Verific daca ultima piesa adaugata captureaza piese ale inamicului, pentru ca in acest caz ultima piesa
        # adaugata are cu siguranta cel putin o libertate
        visitedIntersections = []

        oppositePlayer = self.getOppositePlayer(player)

        neighbors = self.getValidNeighbours(row, column)
        hasLiberty = False
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if new_board[i][j] == self.symbols[oppositePlayer] and (i, j) not in visitedIntersections:
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
            self.consecutivePass += 1
            if self.consecutivePass == 2:
                self.running = False
        else:
            self.board[row][col] = self.symbols[player]
            self.tryCapture(self.board, self.capturedStones, row, col, player)
            self.historyBoards.append(deepcopy(self.board))
            self.consecutivePass = 0

        self.next_to_move = self.getOppositePlayer(self.next_to_move)

        return type(self)(deepcopy(self), self.next_to_move, self.win)

    def get_legal_actions(self):
        validMoves = []
        for row in range(self.size):
            for col in range(self.size):
                move = GoMove(row, col, self.next_to_move)
                if self.is_move_legal(move):
                    validMoves.append(move)
        validMoves.append(GoMove(-1, -1, self.next_to_move))  # Pass
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
                if self.board[newRow][newCol] == '.':
                    numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(newRow, newCol, visited,
                                                                                            numberIntersections,
                                                                                            whiteNeighbors,
                                                                                            blackNeighbors)
                elif self.board[newRow][newCol] == 'X':
                    blackNeighbors += 1
                elif self.board[newRow][newCol] == 'O':
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
                if new_board[newRow][newCol] == self.symbols[player]:
                    # print(f'Verific daca vecinul ({newRow}, {newCol}) are libertati')
                    hasLiberties = hasLiberties or self.hasLiberty(new_board, newRow, newCol, visited, groupStones,
                                                                   player)

                # Daca vecinul este un spatiu gol, atunci grupul are cel putin o libertate
                elif new_board[newRow][newCol] == '.':
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
            if board[i][j] == self.symbols[oppositePlayer] and (i, j) not in visitedIntersections:
                groupStones = []
                visited = []
                enemyGroupLiberty = self.hasLiberty(board, i, j, visited, groupStones, oppositePlayer)
                # print(f'Sunt {row},{col} si am libertati: {enemyGroupLiberty}')
                visitedIntersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci
                if not enemyGroupLiberty:
                    for (enemyRow, enemyCol) in groupStones:
                        board[enemyRow][enemyCol] = '.'
                        capturedStones[player].append((enemyRow, enemyCol))


class GoGamesManager:
    def __init__(self):
        self.games = []


class GoAPI:
    def __init__(self, size=9, komi=1):
        self.size = size
        self.running = True
        self.komi = komi
        self.board = [['.' for _ in range(size)] for _ in range(size)]
        self.players = [1, -1]
        self.symbols = {
            self.players[0]: 'X',
            self.players[1]: 'O'
        }
        self.currentPlayer = self.players[0]
        self.consecutivePass = 0
        self.capturedStones = {self.players[0]: [],
                               self.players[1]: []}
        self.historyBoards = []

    def getState(self):
        return {
            'running': self.running,
            'board': deepcopy(self.board),
            'currentPlayer': self.currentPlayer,
            'consecutivePass': self.consecutivePass,
            'capturedStones': self.capturedStones,
            'historyBoards': self.historyBoards,
            'players': self.players,
            'komi': self.komi,
            'size': self.size,
            'symbols': self.symbols
        }

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
                if self.board[newRow][newCol] == '.':
                    numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(newRow, newCol, visited,
                                                                                            numberIntersections,
                                                                                            whiteNeighbors,
                                                                                            blackNeighbors)
                elif self.board[newRow][newCol] == 'X':
                    blackNeighbors += 1
                elif self.board[newRow][newCol] == 'O':
                    whiteNeighbors += 1

        return numberIntersections, whiteNeighbors, blackNeighbors

    def getScore(self):
        whiteScore = self.komi
        blackScore = 0

        capturedStonesByWhite = len(self.capturedStones[-1])
        capturedStonesByBlack = len(self.capturedStones[1])

        whiteTerritory = 0
        blackTerritory = 0

        visited = []
        numberIntersections = 0
        whiteNeighbors = 0
        blackNeighbors = 0

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 'X':
                    blackScore += 1
                if self.board[i][j] == 'O':
                    whiteScore += 1
                if self.board[i][j] == '.' and (i, j) not in visited:
                    numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(i, j, visited, 0, 0, 0)
                    # print(f'Grupul ce-l contine pe {i} {j} are {whiteNeighbors} vecini albi, {blackNeighbors} vecini negri si are {numberIntersections} elemente')
                    if whiteNeighbors == 0:
                        # print(f'{numberIntersections} puncte pentru negru')
                        blackTerritory += numberIntersections
                    if blackNeighbors == 0:
                        # print(f'{numberIntersections} puncte pentru alb')
                        whiteTerritory += numberIntersections

        # De adaugat calcul spatii
        # print(f'Black has captured {capturedStonesByBlack} stones and has {blackTerritory} territory points')
        # print(f'White has captured {capturedStonesByWhite} stones and has {whiteTerritory} territory points')

        return blackScore + capturedStonesByBlack + blackTerritory, whiteScore + capturedStonesByWhite + whiteTerritory

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
                if new_board[newRow][newCol] == self.symbols[player]:
                    # print(f'Verific daca vecinul ({newRow}, {newCol}) are libertati')
                    hasLiberties = hasLiberties or self.hasLiberty(new_board, newRow, newCol, visited, groupStones,
                                                                   player)

                # Daca vecinul este un spatiu gol, atunci grupul are cel putin o libertate
                elif new_board[newRow][newCol] == '.':
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

    def isValidMove(self, last_move_row, last_move_col, player):
        # Simulez mutarea
        new_board = deepcopy(self.board)
        new_board[last_move_row][last_move_col] = self.symbols[player]

        # Verific daca ultima piesa adaugata captureaza piese ale inamicului, pentru ca in acest caz ultima piesa
        # adaugata are cu siguranta cel putin o libertate
        visitedIntersections = []

        oppositePlayer = self.getOppositePlayer(player)

        neighbors = self.getValidNeighbours(last_move_row, last_move_col)
        hasLiberty = False
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if new_board[i][j] == self.symbols[oppositePlayer] and (i, j) not in visitedIntersections:
                groupStones = []
                visited = []
                enemyGroupLiberty = self.hasLiberty(new_board, i, j, visited, groupStones, oppositePlayer)
                visitedIntersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci mutarea este cu siguranta una valida
                if not enemyGroupLiberty:
                    hasLiberty = True

        # Verific daca grupul creat de adaugarea ultimei pietre are libertati
        if self.hasLiberty(new_board, last_move_row, last_move_col, [], [], player):
            hasLiberty = True

        self.tryCapture(new_board,
                        {self.players[0]: [], self.players[1]: []},
                        last_move_row,
                        last_move_col,
                        player
                        )

        if hasLiberty and self.respectsKoRule(new_board):
            return True

        return False

    def getValidMoves(self, player):
        validMoves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == '.':
                    if self.isValidMove(row, col, player):
                        validMoves.append((row, col))
        #validMoves.append((-1, -1))  # Pass
        return validMoves

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
            if board[i][j] == self.symbols[oppositePlayer] and (i, j) not in visitedIntersections:
                groupStones = []
                visited = []
                enemyGroupLiberty = self.hasLiberty(board, i, j, visited, groupStones, oppositePlayer)
                # print(f'Sunt {row},{col} si am libertati: {enemyGroupLiberty}')
                visitedIntersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci
                if not enemyGroupLiberty:
                    for (enemyRow, enemyCol) in groupStones:
                        board[enemyRow][enemyCol] = '.'
                        capturedStones[player].append((enemyRow, enemyCol))

    def makeMove(self, row, col, player):
        # if self.isValidMove(row, col, player):
        if (row, col) == (-1, -1):
            self.consecutivePass += 1
            if self.consecutivePass == 2:
                self.running = False
        else:
            self.board[row][col] = self.symbols[player]
            self.tryCapture(self.board, self.capturedStones, row, col, player)
            self.historyBoards.append(deepcopy(self.board))
            # print('Istoric boards: ')
            # for previousBoard in self.historyBoards:
            #     print('Board vechi: ')
            #     printBoard(previousBoard, self.size)
            #     printBoard(self.board, self.size)
            #     print()
        self.currentPlayer = self.getOppositePlayer(self.currentPlayer)
        return True


def printBoard(board, size):
    print('  ' + ' '.join(str(i + 1) for i in range(size)))
    print_board = ''
    for i in range(size):
        print_board += str(i + 1) + ' '
        for j in range(size):
            print_board += board[i][j] + ' '
        print_board += '\n'
    print(print_board)


# size = 5
# goGame = GoAPI(size)
# state = goGame.getState()
#
# while goGame.running:
#     state = goGame.getState()
#     currentPlayer = state['currentPlayer']
#     printBoard(state['board'], size)
#     validMoves = goGame.getValidMoves(currentPlayer)
#     if len(validMoves) == 0:
#         print('Gata jocul')
#         break
#
#     print(f'Player {currentPlayer} to make a move')
#     # get user input
#     input_row = int(input('Enter row: ')) - 1
#     input_col = int(input('Enter column: ')) - 1
#     while (input_row, input_col) not in goGame.getValidMoves(currentPlayer):
#         print('Move out of matrix. Try again.')
#         input_row = int(input('Enter row: ')) - 1
#         input_col = int(input('Enter column: ')) - 1
#     goGame.makeMove(input_row, input_col, currentPlayer)
#
# print(goGame.getScore())


# size = 3
# goStartingGame = GoAPI(size)
# goGamesManager = GoGamesManager()
# goGamesManager.games.append(goStartingGame)
# i = 0
# finalBoards = []
# gamesBoards = []
# gamesState = []
# while len(goGamesManager.games):
#     currentGame = goGamesManager.games[0]
#     goGamesManager.games.pop(0)
#
#     currentState = currentGame.getState()
#     board = currentState['board']
#     currentPlayer = currentState['currentPlayer']
#     isRunning = currentState['running']
#
#     if i % 1000 == 0:
#         print(f'Iteratia {i}')
#         print(len(goGamesManager.games))
#         # printBoard(board, size)
#         # print(currentPlayer)
#         print()
#     i += 1
#
#     validMoves = currentGame.getValidMoves(currentPlayer)
#
#     if len(validMoves) == 0 or isRunning == False:  # == 1 pentru ca se poate da pass
#         if currentState['board'] not in finalBoards:
#             finalBoards.append((currentState['board'], currentGame.getScore()))
#             currentGame.running = False
#         #     print('Am gasit o configuratie finala!')
#         #     printBoard(currentState['board'], size)
#         # else:
#         #     print('Configuratia finala deja este!')
#         # print()
#     else:
#         for index, move in enumerate(validMoves):
#             newGame = deepcopy(currentGame)
#             newGame.makeMove(move[0], move[1], currentPlayer)
#             newState = newGame.getState()
#             newBoard = newState['board']
#             if newBoard not in gamesBoards:
#                 goGamesManager.games.append(newGame)
#                 gamesState.append(newState)
#                 gamesBoards.append(newBoard)
#
# print(len(finalBoards))
#
# for index, board in enumerate(finalBoards):
#     if index % 1000 == 0:
#         print(f'Configuratia {index}:')
#         print(board)
#         # printBoard(board, size)
#         # print(board)
#         print()

