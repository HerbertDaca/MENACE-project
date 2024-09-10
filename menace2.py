import random
import numpy as np
import pandas as pd

class MENACE:
    def __init__(self):
        self.boxes = {}  # Pudełka z koralikami dla każdego stanu gry
        self.moves_history = []  # Historia ruchów MENACE w danej grze

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
        move = random.choices(moves, weights=weights)[0]
        return move

    def game_over(self, result):
        # Wynik gry (MENACE wygrało/przegrało/zremisowało)
        reward = 3 if result == "win" else (-1 if result == "lose" else 1)

        # Aktualizacja koralików dla każdej planszy, na której MENACE wykonał ruch
        for board_str, move in self.moves_history:
            self.boxes[board_str][move] = max(1, self.boxes[board_str][move] + reward)

        # Reset historii ruchów po zakończeniu gry
        self.moves_history = []

    def save_to_excel(self, file_name="menace_learning.xlsx"):
        # Tworzymy listy do przechowywania danych
        data = []
        for board_str, moves in self.boxes.items():
            for move, beads in moves.items():
                data.append([board_str, str(move), beads])

        # Tworzymy DataFrame i zapisujemy do pliku Excel
        df = pd.DataFrame(data, columns=["Board", "Move", "Beads"])
        df.to_excel(file_name, index=False)

    def board_to_string(self, board):
        """Konwertuje planszę numpy.ndarray na czytelny ciąg znaków."""
        return str(board)

    def string_to_board(self, board_str):
        """Konwertuje ciąg znaków z powrotem na numpy.ndarray."""
        board_list = eval(board_str)  # Convert the string back to a list (dangerous in real-world code)
        return np.array(board_list)

# Funkcje pomocnicze do symulacji gry

def check_winner(board):
    """Sprawdza, czy na planszy jest zwycięzca."""
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
    """Sprawdza, czy na planszy jest remis."""
    return np.all(board != " ")  # Remis, jeśli nie ma wolnych pól


def available_moves(board):
    """Zwraca dostępne ruchy na planszy."""
    return [(r, c) for r in range(3) for c in range(3) if board[r, c] == " "]


def play_game(menace, opponent, print_game=False):
    """Symuluje jedną grę MENACE vs przeciwnik."""
    board = np.full((3, 3), " ")
    player_turn = "X"

    while True:
        if player_turn == "X":
            move = menace.make_move(board, available_moves(board))
            board[move] = "X"
        else:
            move = random.choice(available_moves(board))  # Ruch przeciwnika
            board[move] = "*"

        winner = check_winner(board)
        if winner:
            if print_game:
                print(board)
            return "win" if winner == "X" else "lose"

        if is_draw(board):
            if print_game:
                print(board)
            return "draw"

        player_turn = "X" if player_turn == "*" else "*"


def simulate_games(num_games=1000, print_game_every=None):
    """Symuluje wiele gier MENACE vs losowy przeciwnik."""
    menace = MENACE()
    for i in range(num_games):
        result = play_game(menace, random, print_game=(print_game_every and i % print_game_every == 0))
        menace.game_over(result)

    # Zapis wyników do Excela po zakończeniu symulacji
    menace.save_to_excel("menace_learning.xlsx")


# Uruchomienie symulacji 1000 gier
simulate_games(100000)
