import chess.pgn
MY_USERNAME = "ChessGoon23"

def load_game(file_path):
    with open(file_path, "r") as pgn_file:
        game = chess.pgn.read_game(pgn_file)

    return game

def get_metadata(game):
    return {
        "white": game.headers.get("White"),
        "black": game.headers.get("Black"),
        "result": game.headers.get("Result"),
        "date": game.headers.get("Date"),
        "white_elo": game.headers.get("WhiteElo"),
        "black_elo": game.headers.get("BlackElo"),
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
    game = load_game("data/raw/soumyodeepdutta_vs_ChessGoon23_2026.10.22.pgn")
    print(game)
    metadata = get_metadata(game)
    print(metadata)
    print(get_moves(game))
    print(get_my_color(game))
    print("Color:", get_my_color(game))
    print("Result:", get_my_result(game))