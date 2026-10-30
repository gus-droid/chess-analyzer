import sqlite3
import pandas as pd


DB_PATH = "data/chess.db"
ECO_PATH = "data/eco_names.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():
    conn = sqlite3.connect(DB_PATH)

    games = pd.read_sql_query(
        "SELECT * FROM games",
        conn
    )

    moves = pd.read_sql_query(
        "SELECT * FROM moves",
        conn
    )

    conn.close()

    return games, moves


def load_eco_names():
    eco_names = pd.read_csv(ECO_PATH)

    return dict(
        zip(
            eco_names["eco"],
            eco_names["name"]
        )
    )


# --------------------------------------------------
# PREPARE GAME DATA
# --------------------------------------------------

def get_my_result(row):
    if row["result"] == "1/2-1/2":
        return "draw"

    if row["my_color"] == "White":
        if row["result"] == "1-0":
            return "win"
        else:
            return "loss"

    if row["my_color"] == "Black":
        if row["result"] == "0-1":
            return "win"
        else:
            return "loss"

    return None


def get_my_moves(games, moves):
    merged = moves.merge(
        games[["id", "my_color"]],
        left_on="game_id",
        right_on="id",
        suffixes=("", "_game")
    )

    my_moves = merged[
        merged["color"] == merged["my_color"]
    ].copy()

    return my_moves


def add_game_phase(my_moves):
    def classify_phase(move_number):
        if move_number <= 10:
            return "opening"
        elif move_number <= 30:
            return "middlegame"
        else:
            return "endgame"

    my_moves = my_moves.copy()

    my_moves["phase"] = (
        my_moves["move_number"]
        .apply(classify_phase)
    )

    return my_moves


def prepare_data(games, moves):
    games = games.copy()

    games["my_result"] = games.apply(
        get_my_result,
        axis=1
    )

    games["rating_diff"] = (
        games["my_rating"]
        - games["opponent_rating"]
    )

    eco_names = load_eco_names()

    games["opening_name"] = (
        games["eco"]
        .map(eco_names)
        .fillna(games["eco"])
    )

    my_moves = get_my_moves(
        games,
        moves
    )

    my_moves = add_game_phase(
        my_moves
    )

    return games, my_moves


# --------------------------------------------------
# BASIC GAME STATS
# --------------------------------------------------

def basic_game_stats(games):
    total_games = len(games)

    wins = int(
        (games["my_result"] == "win").sum()
    )

    losses = int(
        (games["my_result"] == "loss").sum()
    )

    draws = int(
        (games["my_result"] == "draw").sum()
    )

    if total_games == 0:
        win_rate = 0
    else:
        win_rate = wins / total_games * 100

    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": round(win_rate, 2),
    }


# --------------------------------------------------
# MOVE QUALITY STATS
# --------------------------------------------------

def average_cp_loss(my_moves):
    if len(my_moves) == 0:
        return 0

    return my_moves["cp_loss"].mean()


def mistake_stats(my_moves, total_games):
    inaccuracies = int(
        (my_moves["move_class"] == "inaccuracy").sum()
    )

    mistakes = int(
        (my_moves["move_class"] == "mistake").sum()
    )

    blunders = int(
        (my_moves["move_class"] == "blunder").sum()
    )

    if total_games == 0:
        return {
            "inaccuracies": 0,
            "mistakes": 0,
            "blunders": 0,
            "inaccuracies_per_game": 0,
            "mistakes_per_game": 0,
            "blunders_per_game": 0,
        }

    return {
        "inaccuracies": inaccuracies,
        "mistakes": mistakes,
        "blunders": blunders,
        "inaccuracies_per_game": round(
            inaccuracies / total_games,
            2
        ),
        "mistakes_per_game": round(
            mistakes / total_games,
            2
        ),
        "blunders_per_game": round(
            blunders / total_games,
            2
        ),
    }


# --------------------------------------------------
# COLOR STATS
# --------------------------------------------------

def win_rate_by_color(games):
    return (
        games.groupby("my_color")["my_result"]
        .apply(
            lambda results:
            round(
                (results == "win").mean() * 100,
                2
            )
        )
    )


# --------------------------------------------------
# GAME PHASE STATS
# --------------------------------------------------

def cp_loss_by_phase(my_moves):
    return (
        my_moves.groupby("phase")["cp_loss"]
        .mean()
        .round(2)
    )


def blunders_by_phase(my_moves):
    blunders = my_moves[
        my_moves["move_class"] == "blunder"
    ]

    return (
        blunders["phase"]
        .value_counts()
    )


# --------------------------------------------------
# PER-GAME STATS
# --------------------------------------------------

def game_move_stats(games, my_moves):
    move_stats = (
        my_moves.groupby("game_id")
        .agg(
            avg_cp_loss=(
                "cp_loss",
                "mean"
            ),

            inaccuracies=(
                "move_class",
                lambda x:
                (x == "inaccuracy").sum()
            ),

            mistakes=(
                "move_class",
                lambda x:
                (x == "mistake").sum()
            ),

            blunders=(
                "move_class",
                lambda x:
                (x == "blunder").sum()
            ),
        )
        .reset_index()
    )

    result = games.merge(
        move_stats,
        left_on="id",
        right_on="game_id",
        how="left"
    )

    return result


# --------------------------------------------------
# PERFORMANCE OVER TIME
# --------------------------------------------------

def performance_over_time(game_stats):
    data = game_stats.copy()

    data["date"] = pd.to_datetime(
        data["date"],
        format="%Y.%m.%d"
    )

    return (
        data[
            [
                "date",
                "my_rating",
                "my_result",
                "avg_cp_loss",
                "blunders",
            ]
        ]
        .sort_values("date")
    )


# --------------------------------------------------
# TIME CONTROL STATS
# --------------------------------------------------

def stats_by_time_control(games):
    return (
        games.groupby("time_control")
        .agg(
            games=("id", "count"),

            avg_rating=(
                "my_rating",
                "mean"
            ),

            win_rate=(
                "my_result",
                lambda x:
                (x == "win").mean() * 100
            ),
        )
        .round(2)
    )


def stats_by_time_class(games):
    if "time_class" not in games.columns:
        return None

    return (
        games.groupby("time_class")
        .agg(
            games=("id", "count"),

            avg_rating=(
                "my_rating",
                "mean"
            ),

            win_rate=(
                "my_result",
                lambda x:
                (x == "win").mean() * 100
            ),
        )
        .round(2)
    )


# --------------------------------------------------
# BEST / WORST GAMES
# --------------------------------------------------

def best_worst_games(game_stats):
    if len(game_stats) == 0:
        return None, None

    best_game = game_stats.loc[
        game_stats["avg_cp_loss"].idxmin()
    ]

    worst_game = game_stats.loc[
        game_stats["avg_cp_loss"].idxmax()
    ]

    return best_game, worst_game


# --------------------------------------------------
# OPENING ANALYSIS
# --------------------------------------------------

def opening_stats(game_stats):
    return (
        game_stats
        .dropna(subset=["opening_name"])
        .groupby("opening_name")
        .agg(
            games=("id", "count"),

            wins=(
                "my_result",
                lambda x:
                (x == "win").sum()
            ),

            losses=(
                "my_result",
                lambda x:
                (x == "loss").sum()
            ),

            draws=(
                "my_result",
                lambda x:
                (x == "draw").sum()
            ),

            win_rate=(
                "my_result",
                lambda x:
                (x == "win").mean() * 100
            ),

            avg_cp_loss=(
                "avg_cp_loss",
                "mean"
            ),

            avg_blunders=(
                "blunders",
                "mean"
            ),
        )
        .sort_values(
            "games",
            ascending=False
        )
        .round(2)
    )


def best_worst_openings(game_stats, minimum_games=10):
    stats = opening_stats(game_stats)

    eligible = stats[
        stats["games"] >= minimum_games
    ]

    if len(eligible) == 0:
        return None, None, None, None

    best_name = eligible["win_rate"].idxmax()
    worst_name = eligible["win_rate"].idxmin()

    best_opening = eligible.loc[
        best_name
    ]

    worst_opening = eligible.loc[
        worst_name
    ]

    return (
        best_name,
        best_opening,
        worst_name,
        worst_opening
    )


def cp_loss_by_opening(game_stats):
    return (
        game_stats
        .dropna(subset=["opening_name"])
        .groupby("opening_name")["avg_cp_loss"]
        .mean()
        .sort_values(ascending=False)
        .round(2)
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    games, moves = load_data()

    games, my_moves = prepare_data(
        games,
        moves
    )

    game_stats = game_move_stats(
        games,
        my_moves
    )

    print("\nBASIC STATS")
    print(
        basic_game_stats(games)
    )

    print("\nAVERAGE CENTIPAWN LOSS")
    print(
        round(
            average_cp_loss(my_moves),
            2
        )
    )

    print("\nMISTAKE STATS")
    print(
        mistake_stats(
            my_moves,
            len(games)
        )
    )

    print("\nWIN RATE BY COLOR")
    print(
        win_rate_by_color(games)
    )

    print("\nAVERAGE CP LOSS BY PHASE")
    print(
        cp_loss_by_phase(my_moves)
    )

    print("\nBLUNDERS BY PHASE")
    print(
        blunders_by_phase(my_moves)
    )

    print("\nSTATS BY TIME CONTROL")
    print(
        stats_by_time_control(games)
    )

    print("\nSTATS BY TIME CLASS")
    time_class_stats = stats_by_time_class(
        games
    )

    if time_class_stats is not None:
        print(time_class_stats)

    print("\nPERFORMANCE OVER TIME")
    print(
        performance_over_time(
            game_stats
        )
    )

    best_game, worst_game = (
        best_worst_games(game_stats)
    )

    if best_game is not None:
        print("\nBEST GAME")
        print(
            best_game[
                [
                    "url",
                    "date",
                    "my_result",
                    "avg_cp_loss",
                    "blunders",
                ]
            ]
        )

        print("\nWORST GAME")
        print(
            worst_game[
                [
                    "url",
                    "date",
                    "my_result",
                    "avg_cp_loss",
                    "blunders",
                ]
            ]
        )

    print("\nOPENING STATS")
    openings = opening_stats(
        game_stats
    )

    print(openings)

    print("\nCP LOSS BY OPENING")
    print(
        cp_loss_by_opening(
            game_stats
        )
    )

    (
        best_name,
        best_opening,
        worst_name,
        worst_opening
    ) = best_worst_openings(
        game_stats
    )

    if best_name is not None:
        print("\nBEST OPENING")
        print("Opening:", best_name)
        print(best_opening)

        print("\nWORST OPENING")
        print("Opening:", worst_name)
        print(worst_opening)