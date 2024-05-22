from fastapi import FastAPI, Request
import uuid

from game_board import Game, Board

app = FastAPI()

client_to_games = {}


def valid_game_id(client_host: str, game_id: str) -> tuple[bool, str]:
    """
    :param client_host:
    :param game_id: the game id to check for
    :return: tuple of (valid, message) where
        - valid is a boolean indicating if the game id exists in storage and
        - message is a string to report back to user
    """
    valid = game_id in client_to_games[client_host]
    message = "valid game id"
    if not valid:
        message = f"Can't find a game with id {game_id}"

    return valid, message


@app.get("/")
async def root():
    return {"message": "welcome to knots and crosses! Visit the /game/init endpoint to start a new game"}


@app.get("/game/init")
async def init_game(request: Request):
    client_host = request.client.host
    print(f"client host: {client_host}")
    game_id = uuid.uuid4().hex
    if client_host not in client_to_games:
        client_to_games[str(client_host)] = {game_id: Game(game_id=game_id)}
    else:
        client_to_games[str(client_host)][game_id] = Game(game_id=game_id)
    this_game = client_to_games[client_host][game_id]
    print(client_to_games)

    return {
        "game_id": this_game.game_id,
        "message":
            "welcome to knots and crosses! Here's your empty game board, " +
            "feel free to go first! Keep your unique `game_id` safe " +
            "so that no on else can make unauthorized moves in your game. " +
            "Make a move by POSTing to the `/{game_id}/move` endpoint with `x` and `y` " +
            "parameters set to the square coordinates you want an X in.",
        "board": this_game.board.pretty_print()
    }


@app.get("/game/{game_id}/move")
async def make_move(request: Request, game_id: str, x: int, y: int):
    client_host = request.client.host
    valid, message = valid_game_id(client_host, game_id)
    if not valid:
        return {"message": message}
    else:
        this_game = client_to_games[client_host][game_id]

    if this_game.is_valid_move(x, y):
        # game move, update timestamp
        this_game.player_move(x, y)
        message = "Move successful"
        print(f"{game_id} move successful: {x}, {y}")
        winner = this_game.check_for_win()
        print(f"{game_id} winner: {winner}")
        if winner != ".":
            return {
                "message": f"{winner} has won the game! Congratulations!",
                "board": this_game.board.pretty_print(),
                "history": build_history(this_game)
            }
    else:
        message = "Invalid move"
        print(f"{game_id} invalid move: {x}, {y}")

    if message == "Move successful":
        print(f"{game_id} making computer move")
        # make the move directly, don't update timestamp on non-human initiated moves
        this_game.board.make_computer_move()
        winner = this_game.check_for_win()
        print(f"{game_id} winner: {winner}")
        if winner != ".":
            return {
                    "message": f"{winner} has won the game! Try again next time!",
                    "board": this_game.board.pretty_print(),
                    "history": build_history(this_game)
                }

    return {
        "message": message,
        "board": this_game.board.pretty_print()
    }


def build_history(this_game: Game) -> list[dict[str, str]]:
    """
    :param this_game:
    :return: list of board states and turns
    """
    phantom_board = Board()
    history = [{
        "turn": 0,
        "board": phantom_board.pretty_print()
    }]
    for turn, move in this_game.board.board_history_by_turn.items():
        phantom_board.move(x=move[1], y=move[2], player=move[0])
        history.append({
            "turn": turn,
            "board": phantom_board.pretty_print()
        })

    return history


@app.get("/game/{game_id}/state")
async def get_board_state(request: Request, game_id: str):
    client_host = request.client.host
    valid, message = valid_game_id(client_host, game_id)
    if not valid:
        return {"message": message}
    else:
        this_game = client_to_games[client_host][game_id]

    return {
        "message": "Here's the current state and history of the board",
        "board": this_game.board.pretty_print(),
        "winner": this_game.winner,
        "open": this_game.open,
        "history": build_history(this_game)
    }


@app.get("/game/list")
async def get_list_of_games_by_client_host(request: Request):
    client_host = request.client.host
    this_clients_games = client_to_games.get(client_host, {})
    if this_clients_games:
        return sorted(this_clients_games.values(), key=lambda x: x.updated_at, reverse=True)
    else:
        return {}


@app.get("/game/test")
async def run_test_game(request: Request):
    start = await init_game(request)
    game_id = start["game_id"]
    move1 = await make_move(request, game_id, 1, 3)
    move2 = await make_move(request, game_id, 2, 3)
    move2 = await make_move(request, game_id, 2, 2)
    move3 = await make_move(request, game_id, 3, 3)
    state = await get_board_state(request, game_id)
    return state


@app.get("/game/test/computer_win")
async def run_test_computer_win(request: Request):
    start = await init_game(request)
    game_id = start["game_id"]
    game = client_to_games[request.client.host][game_id]
    game.player_move(1, 3)
    game.board.move(2, 2, "O")
    game.player_move(1, 2)
    game.board.move(1, 1, "O")
    game.player_move(3, 1)
    game.board.move(3, 3, "O")
    game.check_for_win()
    state = await get_board_state(request, game_id)
    assert state["winner"] == "O"
    return state
