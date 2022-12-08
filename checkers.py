from copy import deepcopy
import time
import math

ansi_black = "\u001b[30m"
ansi_red = "\u001b[31m"
ansi_green = "\u001b[32m"
ansi_yellow = "\u001b[33m"
ansi_blue = "\u001b[34m"
ansi_magenta = "\u001b[35m"
ansi_cyan = "\u001b[36m"
ansi_white = "\u001b[37m"
ansi_reset = "\u001b[0m"



class Pieces:
    EMPTY = 1
    PLAYER_REGULAR = 2
    PLAYER_QUEEN = 3
    COMPUTER_REGULAR = 4
    COMPUTER_QUEEN = 5

class Node:
    def __init__(self, board, move=None, parent=None, value=None):
        self.board = board
        self.value = value
        self.move = move
        self.parent = parent

    def get_children(self, minimizing_player, mandatory_jumping):
        current_state = deepcopy(self.board)
        available_moves = []
        children_states = []
        queen_row = 0
        if minimizing_player is True:
            available_moves = Checkers.find_available_moves(current_state, mandatory_jumping)
            queen_piece = Pieces.COMPUTER_QUEEN
            queen_row = 7
        else:
            available_moves = Checkers.find_player_available_moves(current_state, mandatory_jumping)
            queen_piece = Pieces.PLAYER_QUEEN
            queen_row = 0
        for i in range(len(available_moves)):
            old_i = available_moves[i][0]
            old_j = available_moves[i][1]
            new_i = available_moves[i][2]
            new_j = available_moves[i][3]
            state = deepcopy(current_state)
            Checkers.make_a_move(state, old_i, old_j, new_i, new_j, queen_piece, queen_row)
            children_states.append(Node(state, [old_i, old_j, new_i, new_j]))
        return children_states

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_board(self):
        return self.board

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent


class Checkers:

    def __init__(self):
        self.matrix = [[], [], [], [], [], [], [], []]
        self.player_turn = True
        self.computer_pieces = 12
        self.player_pieces = 12
        self.available_moves = []
        self.mandatory_jumping = False

        for i in range(8):
            for j in range(8):
                self.matrix[i].append(Pieces.EMPTY)

        self.position_computer()
        self.position_player()


    def position_computer(self):
        for i in range(3):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.matrix[i][j] = Pieces.COMPUTER_REGULAR

    def position_player(self):
        for i in range(5, 8, 1):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.matrix[i][j] = Pieces.PLAYER_REGULAR

    def get_piece_representation(self, piece, i, j):
        pos = f"{i}{j}"
        if piece == Pieces.EMPTY:
            return "---"
        elif piece == Pieces.PLAYER_REGULAR:
            return f"b{pos}"
        elif piece == Pieces.PLAYER_QUEEN:
            return f"B{pos}"
        elif piece == Pieces.COMPUTER_REGULAR:
            return f"c{pos}"
        elif piece == Pieces.COMPUTER_QUEEN:
            return f"C{pos}"

    @staticmethod
    def is_player_piece(piece):
        return piece in (Pieces.PLAYER_REGULAR, Pieces.PLAYER_QUEEN)
    
    @staticmethod
    def is_computer_piece(piece):
        return piece in (Pieces.COMPUTER_REGULAR, Pieces.COMPUTER_QUEEN)


    def print_matrix(self):
        print()
        for row_index, row in enumerate(self.matrix):
            print(row_index, end="  |")
            for col_index, elem in enumerate(row):
                print(self.get_piece_representation(elem, row_index, col_index), end=" ")
            print()
        print()
        for j in range(8):
            if j == 0:
                j = "     0"
            print(j, end="   ")
        print("\n")

    def get_player_input(self):
        available_moves = Checkers.find_player_available_moves(self.matrix, self.mandatory_jumping)
        if len(available_moves) == 0:
            if self.computer_pieces > self.player_pieces:
                print(
                    ansi_red + "You have no moves left, and you have fewer pieces than the computer.YOU LOSE!" + ansi_reset)
                exit()
            else:
                print(ansi_yellow + "You have no available moves.\nGAME ENDED!" + ansi_reset)
                exit()
        self.player_pieces = 0
        self.computer_pieces = 0
        while True:

            coord1 = input("Which piece[i,j]: ")
            if coord1 == "":
                print(ansi_cyan + "Game ended!" + ansi_reset)
                exit()
            elif coord1 == "s":
                print(ansi_cyan + "You surrendered.\nCoward." + ansi_reset)
                exit()
            coord2 = input("Where to[i,j]:")
            if coord2 == "":
                print(ansi_cyan + "Game ended!" + ansi_reset)
                exit()
            elif coord2 == "s":
                print(ansi_cyan + "You surrendered.\nCoward." + ansi_reset)
                exit()
            old = coord1.split(",")
            new = coord2.split(",")

            if len(old) != 2 or len(new) != 2:
                print(ansi_red + "Illegal input" + ansi_reset)
            else:
                old_i = old[0]
                old_j = old[1]
                new_i = new[0]
                new_j = new[1]
                if not old_i.isdigit() or not old_j.isdigit() or not new_i.isdigit() or not new_j.isdigit():
                    print(ansi_red + "Illegal input" + ansi_reset)
                else:
                    move = [int(old_i), int(old_j), int(new_i), int(new_j)]
                    if move not in available_moves:
                        print(ansi_red + "Illegal move!" + ansi_reset)
                    else:
                        Checkers.make_a_move(self.matrix, int(old_i), int(old_j), int(new_i), int(new_j), Pieces.PLAYER_QUEEN, 0)
                        for m in range(8):
                            for n in range(8):
                                if Checkers.is_computer_piece(self.matrix[m][n]):
                                    self.computer_pieces += 1
                                elif Checkers.is_player_piece(self.matrix[m][n]):
                                    self.player_pieces += 1
                        break

    @staticmethod
    def find_available_moves(board, mandatory_jumping):
        available_moves = []
        available_jumps = []
        for m in range(8):
            for n in range(8):
                if board[m][n] == Pieces.COMPUTER_REGULAR:
                    if Checkers.check_computer_moves(board, m, n, m + 1, n + 1):
                        available_moves.append([m, n, m + 1, n + 1])
                    if Checkers.check_computer_moves(board, m, n, m + 1, n - 1):
                        available_moves.append([m, n, m + 1, n - 1])
                    if Checkers.check_computer_jumps(board, m, n, m + 1, n - 1, m + 2, n - 2):
                        available_jumps.append([m, n, m + 2, n - 2])
                    if Checkers.check_computer_jumps(board, m, n, m + 1, n + 1, m + 2, n + 2):
                        available_jumps.append([m, n, m + 2, n + 2])
                elif board[m][n] == Pieces.COMPUTER_QUEEN:
                    if Checkers.check_computer_moves(board, m, n, m + 1, n + 1):
                        available_moves.append([m, n, m + 1, n + 1])
                    if Checkers.check_computer_moves(board, m, n, m + 1, n - 1):
                        available_moves.append([m, n, m + 1, n - 1])
                    if Checkers.check_computer_moves(board, m, n, m - 1, n - 1):
                        available_moves.append([m, n, m - 1, n - 1])
                    if Checkers.check_computer_moves(board, m, n, m - 1, n + 1):
                        available_moves.append([m, n, m - 1, n + 1])
                    if Checkers.check_computer_jumps(board, m, n, m + 1, n - 1, m + 2, n - 2):
                        available_jumps.append([m, n, m + 2, n - 2])
                    if Checkers.check_computer_jumps(board, m, n, m - 1, n - 1, m - 2, n - 2):
                        available_jumps.append([m, n, m - 2, n - 2])
                    if Checkers.check_computer_jumps(board, m, n, m - 1, n + 1, m - 2, n + 2):
                        available_jumps.append([m, n, m - 2, n + 2])
                    if Checkers.check_computer_jumps(board, m, n, m + 1, n + 1, m + 2, n + 2):
                        available_jumps.append([m, n, m + 2, n + 2])
        if not mandatory_jumping:
            return [*available_jumps, *available_moves]
        else:
            return available_jumps if available_jumps else available_moves

    @staticmethod
    def check_computer_jumps(board, old_i, old_j, via_i, via_j, new_i, new_j):
        if new_i > 7 or new_i < 0:
            return False
        if new_j > 7 or new_j < 0:
            return False
        if board[via_i][via_j] == Pieces.EMPTY:
            return False
        if Checkers.is_computer_piece(board[via_i][via_j]):
            return False
        if board[new_i][new_j] != Pieces.EMPTY:
            return False
        if board[old_i][old_j] == Pieces.EMPTY:
            return False
        if Checkers.is_player_piece(board[old_i][old_j]):
            return False
        return True

    @staticmethod
    def check_computer_moves(board, old_i, old_j, new_i, new_j):

        if new_i > 7 or new_i < 0:
            return False
        if new_j > 7 or new_j < 0:
            return False
        if board[old_i][old_j] == Pieces.EMPTY:
            return False
        if board[new_i][new_j] != Pieces.EMPTY:
            return False
        if Checkers.is_player_piece(board[old_i][old_j]):
            return False
        if board[new_i][new_j] == Pieces.EMPTY:
            return True

    @staticmethod
    def calculate_heuristics(board):
        result = 0
        mine = 0
        opp = 0
        for i in range(8):
            for j in range(8):
                if Checkers.is_computer_piece(board[i][j]):
                    mine += 1

                    if board[i][j] == Pieces.COMPUTER_REGULAR:
                        result += 5
                    if board[i][j] == Pieces.COMPUTER_QUEEN:
                        result += 10
                    if i == 0 or j == 0 or i == 7 or j == 7:
                        result += 7
                    if i + 1 > 7 or j - 1 < 0 or i - 1 < 0 or j + 1 > 7:
                        continue
                    if Checkers.is_player_piece(board[i + 1][j - 1]) and board[i - 1][j + 1] == Pieces.EMPTY:
                        result -= 3
                    if Checkers.is_player_piece(board[i + 1][j + 1]) and board[i - 1][j - 1] == Pieces.EMPTY:
                        result -= 3
                    if board[i - 1][j - 1] == Pieces.PLAYER_QUEEN and board[i + 1][j + 1] == Pieces.EMPTY:
                        result -= 3

                    if board[i - 1][j + 1] == Pieces.PLAYER_QUEEN and board[i + 1][j - 1] == Pieces.EMPTY:
                        result -= 3
                    if i + 2 > 7 or i - 2 < 0:
                        continue
                    if Checkers.is_player_piece(board[i + 1][j - 1]) and board[i + 2][j - 2] == Pieces.EMPTY:
                        result += 6
                    if i + 2 > 7 or j + 2 > 7:
                        continue
                    #vidi da se vise boduje kad se pojede kraljica
                    if Checkers.is_player_piece(board[i + 1][j + 1]) and board[i + 2][j + 2] == Pieces.EMPTY:
                        result += 6

                elif Checkers.is_player_piece(board[i][j]):
                    opp += 1

        return result + (mine - opp) * 1000

    @staticmethod
    def find_player_available_moves(board, mandatory_jumping):
        available_moves = []
        available_jumps = []
        for m in range(8):
            for n in range(8):
                if board[m][n] == Pieces.PLAYER_REGULAR:
                    if Checkers.check_player_moves(board, m, n, m - 1, n - 1):
                        available_moves.append([m, n, m - 1, n - 1])
                    if Checkers.check_player_moves(board, m, n, m - 1, n + 1):
                        available_moves.append([m, n, m - 1, n + 1])
                    if Checkers.check_player_jumps(board, m, n, m - 1, n - 1, m - 2, n - 2):
                        available_jumps.append([m, n, m - 2, n - 2])
                    if Checkers.check_player_jumps(board, m, n, m - 1, n + 1, m - 2, n + 2):
                        available_jumps.append([m, n, m - 2, n + 2])
                elif board[m][n] == Pieces.PLAYER_QUEEN:
                    if Checkers.check_player_moves(board, m, n, m - 1, n - 1):
                        available_moves.append([m, n, m - 1, n - 1])
                    if Checkers.check_player_moves(board, m, n, m - 1, n + 1):
                        available_moves.append([m, n, m - 1, n + 1])
                    if Checkers.check_player_jumps(board, m, n, m - 1, n - 1, m - 2, n - 2):
                        available_jumps.append([m, n, m - 2, n - 2])
                    if Checkers.check_player_jumps(board, m, n, m - 1, n + 1, m - 2, n + 2):
                        available_jumps.append([m, n, m - 2, n + 2])
                    if Checkers.check_player_moves(board, m, n, m + 1, n - 1):
                        available_moves.append([m, n, m + 1, n - 1])
                    if Checkers.check_player_jumps(board, m, n, m + 1, n - 1, m + 2, n - 2):
                        available_jumps.append([m, n, m + 2, n - 2])
                    if Checkers.check_player_moves(board, m, n, m + 1, n + 1):
                        available_moves.append([m, n, m + 1, n + 1])
                    if Checkers.check_player_jumps(board, m, n, m + 1, n + 1, m + 2, n + 2):
                        available_jumps.append([m, n, m + 2, n + 2])
        if not mandatory_jumping:
            return [*available_jumps, *available_moves]
        else:
            return available_jumps if available_jumps else available_moves

    @staticmethod
    def check_player_moves(board, old_i, old_j, new_i, new_j):
        if new_i > 7 or new_i < 0:
            return False
        if new_j > 7 or new_j < 0:
            return False
        if board[old_i][old_j] == Pieces.EMPTY:
            return False
        if board[new_i][new_j] != Pieces.EMPTY:
            return False
        if Checkers.is_computer_piece(board[old_i][old_j]):
            return False
        if board[new_i][new_j] == Pieces.EMPTY:
            return True

    @staticmethod
    def check_player_jumps(board, old_i, old_j, via_i, via_j, new_i, new_j):
        if new_i > 7 or new_i < 0:
            return False
        if new_j > 7 or new_j < 0:
            return False
        if board[via_i][via_j] == Pieces.EMPTY:
            return False
        if Checkers.is_player_piece(board[via_i][via_j]):
            return False
        if board[new_i][new_j] != Pieces.EMPTY:
            return False
        if board[old_i][old_j] == Pieces.EMPTY:
            return False
        if Checkers.is_computer_piece(board[old_i][old_j]):
            return False
        return True

    def evaluate_states(self):
        t1 = time.time()
        current_state = Node(deepcopy(self.matrix))

        first_computer_moves = current_state.get_children(True, self.mandatory_jumping)
        if len(first_computer_moves) == 0:
            if self.player_pieces > self.computer_pieces:
                print(
                    ansi_yellow + "Computer has no available moves left, and you have more pieces left.\nYOU WIN!" + ansi_reset)
                exit()
            else:
                print(ansi_yellow + "Computer has no available moves left.\nGAME ENDED!" + ansi_reset)
                exit()
        dict = {}
        for i in range(len(first_computer_moves)):
            child = first_computer_moves[i]
            value = Checkers.minimax(child.get_board(), 4, -math.inf, math.inf, False, self.mandatory_jumping)
            dict[value] = child
        if len(dict.keys()) == 0:
            print(ansi_green + "Computer has cornered itself.\nYOU WIN!" + ansi_reset)
            exit()
        new_board = dict[max(dict)].get_board()
        move = dict[max(dict)].move
        self.matrix = new_board
        t2 = time.time()
        diff = t2 - t1
        print("Computer has moved (" + str(move[0]) + "," + str(move[1]) + ") to (" + str(move[2]) + "," + str(
            move[3]) + ").")
        print("It took him " + str(diff) + " seconds.")

    @staticmethod
    def minimax(board, depth, alpha, beta, maximizing_player, mandatory_jumping):
        if depth == 0:
            return Checkers.calculate_heuristics(board)
        current_state = Node(deepcopy(board))
        if maximizing_player is True:
            max_eval = -math.inf
            for child in current_state.get_children(True, mandatory_jumping):
                ev = Checkers.minimax(child.get_board(), depth - 1, alpha, beta, False, mandatory_jumping)
                max_eval = max(max_eval, ev)
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            current_state.set_value(max_eval)
            return max_eval
        else:
            min_eval = math.inf
            for child in current_state.get_children(False, mandatory_jumping):
                ev = Checkers.minimax(child.get_board(), depth - 1, alpha, beta, True, mandatory_jumping)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            current_state.set_value(min_eval)
            return min_eval

    @staticmethod
    def make_a_move(board, old_i, old_j, new_i, new_j, queen_piece, queen_row):
        piece = board[old_i][old_j]
        i_difference = old_i - new_i
        j_difference = old_j - new_j
        if i_difference == -2 and j_difference == 2:
            board[old_i + 1][old_j - 1] = Pieces.EMPTY

        elif i_difference == 2 and j_difference == 2:
            board[old_i - 1][old_j - 1] = Pieces.EMPTY

        elif i_difference == 2 and j_difference == -2:
            board[old_i - 1][old_j + 1] = Pieces.EMPTY

        elif i_difference == -2 and j_difference == -2:
            board[old_i + 1][old_j + 1] = Pieces.EMPTY

        if new_i == queen_row:
            piece = queen_piece
        board[old_i][old_j] = Pieces.EMPTY
        board[new_i][new_j] = piece

    def play(self):
        print(ansi_cyan + "##### WELCOME TO CHECKERS ####" + ansi_reset)
        print("\nSome basic rules:")
        print("1.You enter the coordinates in the form i,j.")
        print("2.You can quit the game at any time by pressing enter.")
        print("3.You can surrender at any time by pressing 's'.")
        print("Now that you've familiarized yourself with the rules, enjoy!")
        while True:
            answer = input("\nFirst, we need to know, is jumping mandatory?[Y/n]: ")
            if answer == "Y" or answer == "y":
                self.mandatory_jumping = True
                break
            elif answer == "N" or answer == "n":
                self.mandatory_jumping = False
                break
            elif answer == "":
                print(ansi_cyan + "Game ended!" + ansi_reset)
                exit()
            elif answer == "s":
                print(ansi_cyan + "You've surrendered before the game even started.\nPathetic." + ansi_reset)
                exit()
            else:
                print(ansi_red + "Illegal input!" + ansi_reset)
        while True:
            self.print_matrix()
            if self.player_turn is True:
                print(ansi_cyan + "\nPlayer's turn." + ansi_reset)
                self.get_player_input()
            else:
                print(ansi_cyan + "Computer's turn." + ansi_reset)
                print("Thinking...")
                self.evaluate_states()
            if self.player_pieces == 0:
                self.print_matrix()
                print(ansi_red + "You have no pieces left.\nYOU LOSE!" + ansi_reset)
                exit()
            elif self.computer_pieces == 0:
                self.print_matrix()
                print(ansi_green + "Computer has no pieces left.\nYOU WIN!" + ansi_reset)
                exit()
            elif self.computer_pieces - self.player_pieces == 7:
                wish = input("You have 7 pieces fewer than your opponent.Do you want to surrender?")
                if wish == "" or wish == "yes":
                    print(ansi_cyan + "Coward." + ansi_reset)
                    exit()
            self.player_turn = not self.player_turn


if __name__ == '__main__':
    checkers = Checkers()
    checkers.play()
