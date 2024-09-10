import random
import numpy as np
import pandas as pd

class MENACE:
    def __init__(self):
        self.boxes = {}  # Pudełka z koralikami dla każdego stanu gry
        self.moves_history = []  # Historia ruchów MENACE w danej grze

    def board_to_string(self, board):
        """Konwertuje planszę numpy.ndarray na czytelny ciąg znaków."""
        return str(board)

    def string_to_board(self, board_str):
        """Konwertuje ciąg znaków z powrotem na numpy.ndarray."""
        board_list = eval(board_str)  # Convert the string back to a list (dangerous in real-world code)
        return np.array(board_list)

    def make_move(self, board, available_moves):
        board_str = self.board_to_string(board)  # Convert board to string

        # Tworzenie nowego "pudełka" z koralikami, jeśli stan gry nie był wcześniej widziany
        if board_str not in self.boxes:
            num_moves = len(available_moves)
            if num_moves == 9:
                self.boxes[board_str] = {move: 4 for move in available_moves}
            elif num_moves == 8 or num_moves == 7:
                self.boxes[board_str] = {move: 3 for move in available_moves}
            elif num_moves == 6 or num_moves == 5:
                self.boxes[board_str] = {move: 2 for move in available_moves}
            else:
                self.boxes[board_str] = {move: 1 for move in available_moves}

        # Losowanie ruchu na podstawie koralików
        move = self.choose_move(board_str)

        # Zapisanie stanu gry i ruchu do historii
        self.moves_history.append((board_str, move))

        return move

    def choose_move(self, board_str):
        # Wybór ruchu na podstawie liczby koralików w "pudełku"
        moves = list(self.boxes[board_str].keys())
        weights = list(self.boxes[board_str].values())

        print(f"Dostępne ruchy dla planszy {board_str}:")
        for move, weight in zip(moves, weights):
            print(f"Ruch: {move}, Koraliki: {weight}")

        move = random.choices(moves, weights=weights)[0]
        return move

    def game_over(self, result):
        # Wynik gry (MENACE wygrało/przegrało/zremisowało)
        reward = 3 if result == "win" else (-1 if result == "lose" else 1)

        # Aktualizacja koralików dla każdej planszy, na której MENACE wykonał ruch
        for board_str, move in self.moves_history:
            self.boxes[board_str][move] = max(0, self.boxes[board_str][move] + reward)

        # Reset historii ruchów po zakończeniu gry
        self.moves_history = []

    def save_to_excel(self, file_name="menace_learning.xlsx"):
        data = []
        for board_str, moves in self.boxes.items():
            for move, beads in moves.items():
                data.append([board_str, str(move), beads])

        df = pd.DataFrame(data, columns=["Board", "Move", "Beads"])
        df.to_excel(file_name, index=False)

    def load_from_excel(self, file_name="menace_learning.xlsx"):
        df = pd.read_excel(file_name)
        for _, row in df.iterrows():
            board_str = row["Board"]
            move = eval(row["Move"])
            beads = row["Beads"]

            print(f"Wczytywanie planszy: {board_str}, Ruch: {move}, Koraliki: {beads}")

            if board_str not in self.boxes:
                self.boxes[board_str] = {}
            self.boxes[board_str][move] = beads

# Funkcje pomocnicze do gry z graczem

def check_winner(board):
    win_patterns = [
        board[0, :], board[1, :], board[2, :],  # wiersze
        board[:, 0], board[:, 1], board[:, 2],  # kolumny
        np.diag(board), np.diag(np.fliplr(board))  # przekątne
    ]
    for pattern in win_patterns:
        if np.all(pattern == "X"):
            return "X"
        elif np.all(pattern == "*"):
            return "*"
    return None

def is_draw(board):
    return np.all(board != " ")  # Remis, jeśli nie ma wolnych pól

def available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r, c] == " "]

def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 5)

def player_move(board):
    while True:
        try:
            move = input("Podaj swój ruch (rząd, kolumna) np. 0 1: ")
            r, c = map(int, move.split())
            if (r, c) in available_moves(board):
                return r, c
            else:
                print("Nieprawidłowy ruch, spróbuj ponownie.")
        except (ValueError, IndexError):
            print("Nieprawidłowy format, spróbuj ponownie.")

def play_game_with_player(menace):
    board = np.full((3, 3), " ")
    player_turn = "X"  # MENACE zawsze zaczyna jako "X"

    while True:
        if player_turn == "X":
            move = menace.make_move(board, available_moves(board))
            board[move] = "X"
            print("\nMENACE wykonuje ruch:")
        else:
            move = player_move(board)
            board[move] = "*"

        print_board(board)

        winner = check_winner(board)
        if winner:
            print(f"\nZwycięstwo: {winner}")
            return "win" if winner == "X" else "lose"

        if is_draw(board):
            print("\nRemis!")
            return "draw"

        player_turn = "X" if player_turn == "*" else "*"

def play_against_menace():
    menace = MENACE()
    menace.load_from_excel("menace_learning.xlsx")

    result = play_game_with_player(menace)
    menace.game_over(result)
    menace.save_to_excel("menace_learning.xlsx")

# Uruchomienie gry z graczem
play_against_menace()
