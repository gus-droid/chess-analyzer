import chess.pgn
import io
import chess.pgn
MY_USERNAME = "ChessGoon23"

def load_game_from_pgn(pgn_text):
    pgn_file = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_file)

    return game

def load_game(file_path):
    with open(file_path, "r") as pgn_file:
        game = chess.pgn.read_game(pgn_file)

    return game

def load_games(file_path):
    games = []

    with open(file_path, "r", encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)

            if game is None:
                break

            games.append(game)

    return games

MY_USERNAME = "ChessGoon23"


def get_metadata(game):
    white = game.headers.get("White")
    black = game.headers.get("Black")

    white_elo = game.headers.get("WhiteElo")
    black_elo = game.headers.get("BlackElo")

    if white and white.lower() == MY_USERNAME.lower():
        my_color = "White"
        my_rating = white_elo
        opponent_rating = black_elo

    elif black and black.lower() == MY_USERNAME.lower():
        my_color = "Black"
        my_rating = black_elo
        opponent_rating = white_elo

    else:
        my_color = None
        my_rating = None
        opponent_rating = None

    return {
        "url": game.headers.get("Link"),
        "white": white,
        "black": black,
        "result": game.headers.get("Result"),
        "date": game.headers.get("Date"),
        "white_elo": white_elo,
        "black_elo": black_elo,
        "my_color": my_color,
        "my_rating": my_rating,
        "opponent_rating": opponent_rating,
        "eco": game.headers.get("ECO"),
        "opening": game.headers.get("Opening"),
    }


def get_moves(game):
    board = game.board()
    moves = []
    for move in game.mainline_moves():
        san_move = board.san(move)
        moves.append(san_move)
        board.push(move)
    return moves

def get_my_color(game):
    white = game.headers.get("White")
    black = game.headers.get("Black")

    if white.lower() == MY_USERNAME.lower():
        return "white"
    elif black.lower() == MY_USERNAME.lower():
        return "black"
    return None

def get_my_result(game):
    color = get_my_color(game)
    result = game.headers.get("Result")

    if result == "1/2-1/2":
        return "draw"

    if color == "white":
        if result == "1-0":
            return "win"
        else:
            return "loss"

    if color == "black":
        if result == "0-1":
            return "win"
        else:
            return "loss"

    return None

if __name__ == "__main__":
    games = load_games("data/raw/latest_month.pgn")

    print("Games loaded:", len(games))