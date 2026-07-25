import sqlite3

DB_NAME = "election.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_name TEXT UNIQUE,
    head_boy TEXT,
    head_girl TEXT
)
""")

conn.commit()
conn.close()

print("Database table created successfully!")