from src.fetch_games import get_archives, get_games
from src.parse_games import load_game_from_pgn, get_metadata
from src.analyze_games import analyze_game
from src.database import (
    create_tables,
    insert_game,
    insert_moves,
    game_exists,
)

USERNAME = "ChessGoon23"

"""
Fetch Chess.com games from the last 6 months -> keep bullet, blitz, and rapid ->
parse each PGN -> merge metadata -> skip duplicates -> analyze with Stockfish ->
save game-level and move-level data to the database
"""


def main():
    create_tables()

    archives = get_archives(USERNAME)

    # Only analyze the last 6 months
    recent_archives = archives[-6:]

    for archive in recent_archives:
        print("\nProcessing archive:", archive)

        api_games = get_games(archive)

        print("Games found:", len(api_games))

        for api_game in api_games:

            # Only analyze bullet, blitz, and rapid games
            if api_game["time_class"] not in ["bullet", "blitz", "rapid"]:
                continue

            # Parse the PGN string into a chess.pgn.Game object
            game = load_game_from_pgn(
                api_game["pgn"]
            )

            metadata = get_metadata(game)

            # Add metadata that comes from Chess.com API
            metadata["time_class"] = api_game["time_class"]
            metadata["time_control"] = api_game["time_control"]

            # Skip games that have already been analyzed
            if game_exists(metadata["url"]):
                print(
                    "Skipping already analyzed game:",
                    metadata["url"]
                )
                continue

            # Analyze all moves with Stockfish
            moves_data = analyze_game(game)

            # Save game-level metadata
            game_id = insert_game(metadata)

            # Save move-level Stockfish analysis
            insert_moves(game_id, moves_data)

            print("Saved game:", game_id, metadata["time_class"], metadata["url"])


if __name__ == "__main__":
    main()