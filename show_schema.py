import sqlite3
conn = sqlite3.connect('election.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info('votes')")
cols = cur.fetchall()
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='votes'")
tbl = cur.fetchone()
cur.execute("SELECT COUNT(*) FROM votes")
count = cur.fetchone()[0]
conn.close()
print('COLUMNS:')
for c in cols:
    print(c)
print('\nCREATE SQL:')
print(tbl[0] if tbl else None)
print('\nROW COUNT:')
print(count)
