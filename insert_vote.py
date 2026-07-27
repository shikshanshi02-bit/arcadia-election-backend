import sqlite3
conn = sqlite3.connect('election.db')
cur = conn.cursor()
cur.execute("INSERT OR IGNORE INTO votes(voter_name, head_boy, head_girl, created_at) VALUES(?,?,?, datetime('now'))", ('Local Test Voter','hb-1','hg-1'))
conn.commit()
conn.close()
print('Inserted')
