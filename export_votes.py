import sqlite3
import pandas as pd

conn = sqlite3.connect("election.db")

df = pd.read_sql_query(
    """
    SELECT 
        voter_name,
        head_boy,
        head_girl
    FROM votes
    """,
    conn
)

df.to_excel(
    "Election_Voting_Record.xlsx",
    index=False
)

conn.close()

print("Excel file generated successfully!")