import sqlite3

conn = sqlite3.connect("data/chess.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM games")
print(cursor.fetchall())

cursor.execute("SELECT * FROM moves LIMIT 10")
print(cursor.fetchall())

conn.close()