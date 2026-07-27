import sqlite3
import sys
DB='election.db'

try:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM votes")
    before = cur.fetchone()[0]

    cur.execute("DELETE FROM votes")
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM votes")
    after = cur.fetchone()[0]

    # VACUUM to reclaim space and reset AUTOINCREMENT in sqlite
    cur.execute("VACUUM")
    conn.close()

    print(f"OK: deleted votes: {before} -> {after}")
    sys.exit(0)
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)
