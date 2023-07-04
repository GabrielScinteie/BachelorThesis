from copy import deepcopy
import numpy as np
from GameLogic.GoMove import GoMove


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
        self.no_moves = 0
        self.last_board = None

    def __str__(self):
        return np.array2string(np.where(self.board == 1, 'X', np.where(self.board == 0, '.', '0')), separator='')

    def get_reversed_perspective(self):
        mask_1 = (self.board == 1)
        mask_minus_1 = (self.board == -1)
        copy_board = deepcopy(self.board)
        copy_board[mask_1] = -1
        copy_board[mask_minus_1] = 1
        return copy_board

    def get_score(self):
        return self.score

    @property
    def game_result(self):
        # Returns 1 if black won and -1 if white won
        white_score = self.komi
        black_score = 0

        captured_stones_by_white = len(self.captured_stones[-1])
        captured_stones_by_black = len(self.captured_stones[1])

        white_territory = 0
        black_territory = 0

        visited = []

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    black_score += 1
                if self.board[i][j] == -1:
                    white_score += 1
                if self.board[i][j] == 0 and (i, j) not in visited:
                    number_intersections, white_neighbors, black_neighbors = self.get_territory(i, j, visited, 0, 0, 0)
                    # print(f'Grupul ce-l contine pe {i} {j} are {white_neighbors} vecini albi, {black_neighbors} vecini negri si are {number_intersections} elemente')
                    if white_neighbors == 0:
                        # print(f'{number_intersections} puncte pentru negru')
                        black_territory += number_intersections
                    if black_neighbors == 0:
                        # print(f'{number_intersections} puncte pentru alb')
                        white_territory += number_intersections

        # print(f'Black has captured {captured_stones_by_black} stones and has {black_territory} territory points')
        # print(f'White has captured {captured_stones_by_white} stones and has {white_territory} territory points')
        black_score += captured_stones_by_black + black_territory
        white_score += captured_stones_by_white + white_territory
        self.score = [black_score, white_score]

        # print(f'Black: {black_score}, White: {white_score}')
        if black_score > white_score:
            return 1
        return -1

    def is_game_over(self):
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
        visited_intersections = []

        opposite_player = self.get_opposite_player(player)

        neighbors = self.get_valid_neighbours(row, column)
        has_liberty = False
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if new_board[i][j] == opposite_player and (i, j) not in visited_intersections:
                group_stones = []
                visited = []
                enemy_group_liberty = self.has_liberty(new_board, i, j, visited, group_stones, opposite_player)
                visited_intersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci mutarea este cu siguranta una valida
                if not enemy_group_liberty:
                    has_liberty = True

        # Verific daca grupul creat de adaugarea ultimei pietre are libertati
        if self.has_liberty(new_board, row, column, [], [], player):
            has_liberty = True

        self.try_capture(new_board,
                         {self.players[0]: [], self.players[1]: []},
                         row,
                         column,
                         player
                         )

        if has_liberty and self.respects_ko_rule(new_board):
            return True

        return False

    def move(self, move):
        self.no_moves += 1
        row = move.row
        col = move.column
        player = move.player

        if (row, col) == (-1, -1):
            self.consecutive_pass += 1
            if self.consecutive_pass == 2:
                self.running = False
        else:
            self.last_board = deepcopy(self.board)
            self.board[row][col] = player
            self.try_capture(self.board, self.captured_stones, row, col, player)
            self.consecutive_pass = 0

        # Limita de miscari
        if self.no_moves > self.size * self.size * 3:
            self.running = False

        self.next_to_move = self.get_opposite_player(self.next_to_move)

        return self

    def get_legal_actions(self):
        valid_moves = np.zeros(self.size * self.size + 1)

        for row in range(self.size):
            for col in range(self.size):
                move = GoMove(row, col, self.next_to_move)
                if self.is_move_legal(move):
                    valid_moves[row * self.size + col] = 1
        if np.sum(valid_moves) == 0 or self.no_moves > self.size * self.size / 2:
            valid_moves[-1] = 1  # Pass
        return valid_moves

    def get_territory(self, row, col, visited, number_intersections, white_neighbors, black_neighbors):
        # print(f'Sunt in get_territory si testez pozitia ({row}, {col})')
        if (row, col) in visited:
            return number_intersections, white_neighbors, black_neighbors

        # print('Incrementez numarul de intersectii')
        visited.append((row, col))

        # Teritoriul are cel putin o intersectie libera, piesa de pe pozitia curenta
        number_intersections += 1

        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]

        # Parcurg toti cei 4 vecini
        for neighbor in neighbors:
            new_row = neighbor[0]
            new_col = neighbor[1]

            if 0 <= new_row < self.size and 0 <= new_col < self.size and (new_row, new_col) not in visited:
                if self.board[new_row][new_col] == 0:
                    number_intersections, white_neighbors, black_neighbors = self.get_territory(new_row, new_col, visited,
                                                                                                number_intersections,
                                                                                                white_neighbors,
                                                                                                black_neighbors)
                elif self.board[new_row][new_col] == 1:
                    black_neighbors += 1
                elif self.board[new_row][new_col] == -1:
                    white_neighbors += 1

        return number_intersections, white_neighbors, black_neighbors

    def has_liberty(self, new_board, row, col, visited, group_stones, player):
        # Daca am vizitat deja acest nod
        if (row, col) in visited:
            return False

        # Adaug nodul curent la vizitat
        visited.append((row, col))

        # Adaug nodul curent la grupul actual
        group_stones.append((row, col))

        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        has_liberties = False

        # Parcurg toti cei 4 vecini
        for neighbor in neighbors:
            new_row = neighbor[0]
            new_col = neighbor[1]
            # Daca vecinii sunt in interiorul tablei
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                # Daca vecinul este o piesa care apartine playerului curent, atunci apelez getGroup de vecin
                if new_board[new_row][new_col] == player:
                    # print(f'Verific daca vecinul ({new_row}, {new_col}) are libertati')
                    has_liberties = has_liberties or self.has_liberty(new_board, new_row, new_col, visited, group_stones,
                                                                    player)

                # Daca vecinul este un spatiu gol, atunci grupul are cel putin o libertate
                elif new_board[new_row][new_col] == 0:
                    has_liberties = True

        return has_liberties

    def respects_ko_rule(self, new_board):
        if str(new_board) == str(self.last_board):
            # print('Nu se respecta regula Ko')
            return False

        # print('Regula Ko este respectata')
        return True

    def get_opposite_player(self, player):
        opposite_player = self.players[0]
        if player == self.players[0]:
            opposite_player = self.players[1]

        return opposite_player

    def get_valid_neighbours(self, row, col):
        dl = [-1, 0, 1, 0]
        dc = [0, 1, 0, -1]
        neighbors = []
        for i in range(4):
            neighbor_row = row + dl[i]
            neighbor_col = col + dc[i]
            if 0 <= neighbor_row < self.size and 0 <= neighbor_col < self.size:
                neighbors.append((neighbor_row, neighbor_col))

        return neighbors

    def try_capture(self, board, captured_stones, row, col, player):
        visited_intersections = []

        opposite_player = self.players[0]
        if player == self.players[0]:
            opposite_player = self.players[1]

        neighbors = self.get_valid_neighbours(row, col)
        # print(neighbors)
        for neighbor in neighbors:
            i = neighbor[0]
            j = neighbor[1]
            if board[i][j] == opposite_player and (i, j) not in visited_intersections:
                group_stones = []
                visited = []
                enemy_group_liberty = self.has_liberty(board, i, j, visited, group_stones, opposite_player)
                # print(f'Sunt {row},{col} si am libertati: {enemy_group_liberty}')
                visited_intersections.extend(visited)
                # Daca grupul inamic nu are libertati, atunci
                if not enemy_group_liberty:
                    for (enemy_row, enemy_col) in group_stones:
                        board[enemy_row][enemy_col] = 0
                        captured_stones[player].append((enemy_row, enemy_col))
