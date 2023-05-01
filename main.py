# from copy import deepcopy
#
#
# class GoGame:
#     def __init__(self, size=9, komi=6.5):
#         self.size = size
#         self.running = True
#         self.komi = komi
#         self.board = [['.' for _ in range(size)] for _ in range(size)]
#         self.players = ['Black', 'White']
#         self.symbols = {
#             self.players[0] : 'X',
#             self.players[1] : 'O'
#         }
#         self.currentPlayer = self.players[0]
#         self.previousBoard = None
#         self.consecutivePass = 0
#         self.capturedStones = {self.players[0] : [],
#                                self.players[1] : []}
#         # self.moveHistory = []
#
#     def isRunning(self):
#         return self.running
#
#     def getOppositePlayer(self):
#         if self.currentPlayer == self.players[0]:
#             return self.players[1]
#         return self.players[0]
#
#     def makeMoveIfLegal(self, row, col):
#         # Daca mutarea este pass
#         if row == -1 and col == -1:
#             self.consecutivePass += 1
#             if self.consecutivePass == 2:
#                 self.running = False
#             return True
#         else:
#             self.consecutivePass = 0
#
#         # Daca mutarea este in interiorul tablei
#         if row < 0 or col < 0 or row >= self.size or col >= self.size:
#             print('Miscarea ar fi in afara tablei')
#             return False
#
#         # Daca intersectia este goala
#         if self.board[row][col] != '.':
#             print('Intersectia nu este libera')
#             return False
#
#         # Daca miscarea nu este suicide
#         try_board = deepcopy(self.board)
#         try_board[row][col] = self.symbols[self.currentPlayer]
#
#         capturedStones, validMove = self.tryMakeMove(try_board, row, col)
#         if validMove:
#             print('Miscarea ar fi suicidala!')
#             return False
#
#         # Daca se respecta regula ko (nu se repeta state-ul anterior)
#         if str(try_board) == str(self.previousBoard):
#             print('Nu se respecta regula ko')
#             return False
#
#         # Daca mutarea a fost legala, atunci o si execut
#         self.previousBoard = self.board
#         self.board = try_board
#         self.capturedStones[self.currentPlayer].extend(capturedStones)
#         # print('S-au capturat piesele: ')
#         # print(self.capturedStones[self.currentPlayer])
#
#         return True
#
#     def printCapturedPieces(self):
#         for playerName in self.players:
#             print(f'Playerul {playerName} a capturat piesele {self.capturedStones[playerName]}')
#
#     def tryMakeMove(self, try_board, row, col):
#         # print('Sunt in DFS-ul unde verific daca am capturat piese inamice')
#         capturedStones = []
#         visitedIntersections = []
#         for i in range(self.size):
#             for j in range(self.size):
#                 if try_board[i][j] == self.symbols[self.getOppositePlayer()] and (i, j) not in visitedIntersections:
#                     groupStones = []
#                     visited = []
#                     enemyGroupLiberty = self.dfs(try_board, i, j, visited, groupStones, self.getOppositePlayer())
#                     visitedIntersections.extend(visited)
#                     # Daca grupul inamic nu are libertati, atunci
#                     if enemyGroupLiberty == False:
#                         for (enemyRow, enemyCol) in groupStones:
#                             try_board[enemyRow][enemyCol] = '.'
#                             capturedStones.append((enemyRow, enemyCol))
#                             # print(f'Piesa ({enemyRow}, {enemyCol}) a playerului {self.currentPlayer} a fost capturata!')
#
#         # print('Sunt in DFS-ul in care verific daca piesele mele au libertati\n')
#         # Verific daca grupul creat de plasarea piesei pe row, col are libertati
#         _, hasLiberty = self.getGroupAndLiberty(try_board, row, col)
#         return capturedStones, not hasLiberty
#
#     def getGroupAndLiberty(self, try_board, row, col):
#         groupStones = []
#         visited = []
#         hasLiberties = self.dfs(try_board, row, col, visited, groupStones, self.currentPlayer)
#
#         return groupStones, hasLiberties
#
#     def getTerritory(self, row, col, visited, numberIntersections, whiteNeighbors, blackNeighbors):
#         # print(f'Sunt in getTerritory si testez pozitia ({row}, {col})')
#         if (row, col) in visited:
#             return numberIntersections, whiteNeighbors, blackNeighbors
#
#         # print('Incrementez numarul de intersectii')
#         visited.append((row, col))
#
#         # Teritoriul are cel putin o intersectie libera, piesa de pe pozitia curenta
#         numberIntersections += 1
#
#         neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
#
#         # Parcurg toti cei 4 vecini
#         for neighbor in neighbors:
#             newRow = neighbor[0]
#             newCol = neighbor[1]
#
#             if 0 <= newRow < self.size and 0 <= newCol < self.size and (newRow, newCol) not in visited:
#                 if self.board[newRow][newCol] == '.':
#                     numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(newRow, newCol, visited, numberIntersections, whiteNeighbors, blackNeighbors)
#                 elif self.board[newRow][newCol] == 'X':
#                     blackNeighbors += 1
#                 elif self.board[newRow][newCol] == 'O':
#                     whiteNeighbors += 1
#
#         return numberIntersections, whiteNeighbors, blackNeighbors
#
#     def dfs(self, try_board, row, col, visited, groupStones, player):
#         # Daca am vizitat deja acest nod
#         if (row, col) in visited:
#             return False
#
#         # Adaug nodul curent la vizitat
#         visited.append((row, col))
#
#         # Adaug nodul curent la grupul actual
#         groupStones.append((row, col))
#
#         neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
#         hasLiberties = False
#         # print(f'Sunt in ({row}, {col}) si tabla arata astfel: ')
#         # self.printBoard(try_board)
#         # print('Vecinii mei sunt: ')
#         # Parcurg toti cei 4 vecini
#         for neighbor in neighbors:
#             newRow = neighbor[0]
#             newCol = neighbor[1]
#             # print(f'({newRow}, {newCol})')
#             # Daca vecinii sunt in interiorul tablei
#             if 0 <= newRow < self.size and 0 <= newCol < self.size:
#                 # print(try_board[newRow][newCol])
#                 # print(self.symbols[player])
#                 # Daca vecinul este o piesa care apartine playerului curent, atunci apelez getGroup de vecin
#                 if try_board[newRow][newCol] == self.symbols[player]:
#                     # print(f'Verific daca vecinul ({newRow}, {newCol}) are libertati')
#                     hasLiberties = hasLiberties or self.dfs(try_board, newRow, newCol, visited, groupStones, player)
#
#                 # Daca vecinul este un spatiu gol, atunci grupul are cel putin o libertate
#                 elif try_board[newRow][newCol] == '.':
#                     hasLiberties = True
#                     # print(f'Am ca libertate pe ({newRow}, {newCol})')
#
#             # print(newRow)
#             # print(newCol)
#             # print(hasLiberties)
#             # print()
#
#         return hasLiberties
#
#     def calculateScore(self):
#         whiteScore = self.komi
#         blackScore = 0
#
#         capturedStonesByWhite = len(self.capturedStones['White'])
#         capturedStonesByBlack = len(self.capturedStones['Black'])
#
#         whiteTerritory = 0
#         blackTerritory = 0
#
#         visited = []
#         numberIntersections = 0
#         whiteNeighbors = 0
#         blackNeighbors = 0
#
#         for i in range(self.size):
#             for j in range(self.size):
#                 if self.board[i][j] == 'X':
#                     blackScore += 1
#                 if self.board[i][j] == 'O':
#                     whiteScore += 1
#                 if self.board[i][j] == '.' and (i, j) not in visited:
#                     numberIntersections, whiteNeighbors, blackNeighbors = self.getTerritory(i, j, visited, 0, 0, 0)
#                     # print(f'Grupul ce-l contine pe {i} {j} are {whiteNeighbors} vecini albi, {blackNeighbors} vecini negri si are {numberIntersections} elemente')
#                     if whiteNeighbors == 0:
#                         # print(f'{numberIntersections} puncte pentru negru')
#                         blackTerritory += numberIntersections
#                     if blackNeighbors == 0:
#                         # print(f'{numberIntersections} puncte pentru alb')
#                         whiteTerritory += numberIntersections
#
#         # De adaugat calcul spatii
#         print(f'Black has captured {capturedStonesByBlack} stones and has {blackTerritory} territory points')
#         print(f'White has captured {capturedStonesByWhite} stones and has {whiteTerritory} territory points')
#
#         return blackScore + capturedStonesByBlack + blackTerritory, whiteScore + capturedStonesByWhite + whiteTerritory
#
#     def printBoard(self, board):
#         print('  ' + ' '.join(str(i + 1) for i in range(self.size)))
#         print_board = ''
#         for i in range(self.size):
#             print_board += str(i + 1) + ' '
#             for j in range(self.size):
#                 print_board += board[i][j] + ' '
#             print_board += '\n'
#         print(print_board)
#         print()
#
#     def getCurrentPlayer(self):
#         return self.currentPlayer
#
#     def switchPlayer(self):
#         if self.players[0] == self.currentPlayer:
#             self.currentPlayer = self.players[1]
#         else:
#             self.currentPlayer = self.players[0]
#
#
# if __name__ == '__main__':
#     goGame = GoGame(5)
#     while goGame.isRunning():
#         goGame.printBoard(goGame.board)
#         print(f'Player {goGame.getCurrentPlayer()} to make a move')
#         # get user input
#         input_row = int(input('Enter row: ')) - 1
#         input_col = int(input('Enter column: ')) - 1
#         while not goGame.makeMoveIfLegal(input_row, input_col):
#             print('Illegal move. Try again.')
#             input_row = int(input('Enter row: ')) - 1
#             input_col = int(input('Enter column: ')) - 1
#         goGame.switchPlayer()
#     scores = goGame.calculateScore()
#     print('Jocul s-a incheiat!')
#     goGame.printCapturedPieces()
#     print(scores)
