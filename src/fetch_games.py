import requests

HEADERS = {
    "User-Agent": "chess-analyzer/1.0 (username: ChessGoon23)"
}


def get_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    return data["archives"]


def get_games(archive_url):
    response = requests.get(archive_url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    return data["games"]

def save_games_to_pgn(games, file_path):
    with open(file_path, "w", encoding="utf-8") as pgn_file:
        for game in games:
            pgn_file.write(game["pgn"])
            pgn_file.write("\n\n")

if __name__ == "__main__":
    archives = get_archives("ChessGoon23")
    latest_archive = archives[-1]
    games = get_games(latest_archive)

    save_games_to_pgn(games, "data/raw/latest_month.pgn")

    print("Saved", len(games), "games.")