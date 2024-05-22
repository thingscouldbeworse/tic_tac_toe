import uuid
import random
from datetime import datetime


class Board:
    current_state = None
    board_history_by_turn = None

    def __init__(self):
        self.current_state = [
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
        ]
        self.board_history_by_turn = {}

    def pretty_print(self, board_state: list[list[str]] = None) -> dict[str, str]:
        """
        :param board_state: the board state to print; if not provided, use the current state
        :return a version of the game board that looks nicer in browser
        """
        if not board_state:
            board_state = self.current_state
        return {
            'row1': " | ".join(board_state[0]),
            'row2': " | ".join(board_state[1]),
            'row3': " | ".join(board_state[2])
        }

    def move(self, x: int, y: int, player: str = "X") -> bool:
        """
        Make a move on the board if possible, add that move to the history, update the `updated_at` timestamp
        :param x: the cartesian x, ie starting counting from left; 1 indexed
        :param y: the cartesian y, ie starting counting from bottom; 1 indexed
        :param player: the player making the move (X or O)
        :return True if the move was successful, False if the move was invalid
        """
        # translate from cartesian
        self.current_state[3 - y][x - 1] = player
        self.board_history_by_turn[len(self.board_history_by_turn) + 1] = (player, x, y)

        return True

    def make_computer_move(self) -> bool:
        """
        Make a move for the computer player (random spot right now)
        :return: True/False return value from `move()` method
        """
        for i in range(0, len(self.current_state) * len(self.current_state[0])):
            x = random.randint(1, 3)
            y = random.randint(1, 3)
            if self.current_state[3 - y][x - 1] == ".":
                return self.move(x, y, "O")


class Game:
    game_id: str = None
    open: bool = None
    winner: str = None
    board: Board = None
    created_at: datetime = None
    updated_at: datetime = None

    def __init__(self, game_id=None):
        if not game_id:
            self.game_id = uuid.uuid4().hex
        self.game_id = game_id
        self.board = Board()
        self.open = True
        self.winner = "None yet"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def is_valid_move(self, x: int, y: int) -> bool:
        """
        :param x: the cartesian x, ie starting counting from left; 1 indexed
        :param y: the cartesian y, ie starting counting from bottom; 1 indexed
        :return: True if the move is valid, False if the move is invalid
        """
        # translate from cartesian
        return self.open and self.board.current_state[3 - y][x - 1] == "."

    def check_for_win(self) -> str:
        """
        :return: the player who has won, or "." if no one has won yet
        """

        # check rows
        for row in self.board.current_state:
            if len(set(row)) == 1 and row[0] != ".":  # all elements are the same and non dot
                print(f"found win in row: {row}")
                self.open = False
                self.winner = row[0]
                return self.winner

        # check columns
        for i in range(3):
            if (
                self.board.current_state[0][i] != "." and
                self.board.current_state[0][i] == self.board.current_state[1][i] == self.board.current_state[2][i]
            ):
                print(f"Found win in column: {self.board.current_state[0][i]}")
                self.open = False
                self.winner = self.board.current_state[0][i]
                return self.winner

        # check diagonals
        if (
            self.board.current_state[0][0] != '.' and
            self.board.current_state[0][0] == self.board.current_state[1][1] == self.board.current_state[2][2]
        ):
            print(f"Found win in decline diagonal: {self.board.current_state[0][0]}")
            self.open = False
            self.winner = self.board.current_state[0][0]
            return self.winner
        if (
            self.board.current_state[0][2] != '.' and
            self.board.current_state[0][2] == self.board.current_state[1][1] == self.board.current_state[2][0]
        ):
            print(f"Found win in incline diagonal: {self.board.current_state[0][2]}")
            self.open = False
            self.winner = self.board.current_state[0][2]
            return self.winner

        # check for tie
        if all([cell != "." for row in self.board.current_state for cell in row]):
            self.open = False
            self.winner = "Tie"
            return self.winner

        return "."

    def player_move(self, x: int, y: int):
        """
        Make a move on the board and update the timestamp
        :param x:
        :param y:
        :return:
        """
        result = self.board.move(x, y)
        self.updated_at = datetime.now()
        return result

