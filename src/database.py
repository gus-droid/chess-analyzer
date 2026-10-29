import sqlite3


DB_PATH = "data/chess.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            white TEXT,
            black TEXT,
            result TEXT,
            date TEXT,
            white_elo INTEGER,
            black_elo INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            move_number INTEGER,
            color TEXT,
            move TEXT,
            before_cp INTEGER,
            after_cp INTEGER,
            cp_loss INTEGER,
            move_class TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    """)

    conn.commit()
    conn.close()


def insert_game(metadata):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO games (
            url,
            white,
            black,
            result,
            date,
            white_elo,
            black_elo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        metadata["url"],
        metadata["white"],
        metadata["black"],
        metadata["result"],
        metadata["date"],
        metadata["white_elo"],
        metadata["black_elo"],
    ))

    game_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return game_id


def insert_moves(game_id, moves_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for move in moves_data:
        cursor.execute("""
            INSERT INTO moves (
                game_id,
                move_number,
                color,
                move,
                before_cp,
                after_cp,
                cp_loss,
                move_class
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            move["move_number"],
            move["color"],
            move["move"],
            move["before"],
            move["after"],
            move["loss"],
            move["move_class"],
        ))

    conn.commit()
    conn.close()


def game_exists(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM games WHERE url = ?",
        (url,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None

if __name__ == "__main__":
    create_tables()