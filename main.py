from src.parse_games import load_game, get_metadata
from src.analyze_games import analyze_game
from src.database import (
    create_tables,
    insert_game,
    insert_moves,
    game_exists,
)

FILE_PATH = "data/raw/test_game.pgn"


def main():
    create_tables()

    game = load_game(FILE_PATH)
    metadata = get_metadata(game)

    if game_exists(metadata["url"]):
        print("Game already analyzed.")
        return

    moves_data = analyze_game(FILE_PATH)

    game_id = insert_game(metadata)
    insert_moves(game_id, moves_data)

    print("Game saved successfully.")
    print("Game ID:", game_id)


if __name__ == "__main__":
    main()