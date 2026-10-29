import chess.pgn
import chess.engine


ENGINE_PATH = "engines/stockfish-windows-x86-64-universal.exe"


def analyze_game(file_path):
    moves_data = []
    with open(file_path, "r") as pgn_file:
        game = chess.pgn.read_game(pgn_file)

    board = game.board()
    move_number = 0

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    for move in game.mainline_moves():
        move_number = board.fullmove_number

        if board.turn == chess.WHITE:
            color = "White"
        else:
            color = "Black"

        move_san = board.san(move)

        # Evaluation before the move
        before_info = engine.analyse(board, chess.engine.Limit(depth=12))

        before_score = before_info["score"].pov(board.turn)
        before_centipawn = before_score.score(mate_score=100000)

        board.push(move)

        # Evaluation after the move
        after_info = engine.analyse(board, chess.engine.Limit(depth=12))

        # Eval from perspective of player who just moved
        after_score = after_info["score"].pov(not board.turn)
        after_centipawn = after_score.score(mate_score=100000)

        centipawn_loss = max(0, before_centipawn - after_centipawn)
        move_classification = classify_move(centipawn_loss)

        moves_data.append({
            "move_number": move_number,
            "color": color,
            "move": move_san,
            "before": before_centipawn,
            "after": after_centipawn,
            "loss": centipawn_loss,
            "move_class": move_classification,
        })

    engine.quit()
    return moves_data

def classify_move(centipawn_loss):
    if centipawn_loss < 50:
        return "good"
    elif centipawn_loss < 100:
        return "inaccuracy"
    elif centipawn_loss < 200:
        return "mistake"
    else:
        return "blunder"

if __name__ == "__main__":
    moves = analyze_game("data/raw/test_game.pgn")
    for move in moves:
        print(move)
