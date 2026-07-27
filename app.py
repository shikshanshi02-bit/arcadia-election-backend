from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd

app = Flask(__name__)

CORS(app)

DB_NAME = "election.db"

# Ensure votes table has a created_at column for timestamps. This will add the column
# when the app starts if it's not already present (safe to run multiple times).
def ensure_created_at_column():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE votes ADD COLUMN created_at TEXT DEFAULT (datetime('now'))")
        conn.commit()
    except sqlite3.OperationalError:
        # Column probably already exists; ignore
        pass
    finally:
        conn.close()

ensure_created_at_column()


@app.route("/")
def home():
    return "Arcadia School Election Backend Running"


@app.route("/vote", methods=["POST"])
def vote():

    data = request.json

    voter_name = data["voter_name"]
    head_boy = data["head_boy"]
    head_girl = data["head_girl"]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM votes WHERE voter_name=?",
        (voter_name,)
    )

    if cursor.fetchone():
        conn.close()

        return jsonify({
            "success": False,
            "message": "This student has already voted."
        })


    cursor.execute(
        "INSERT INTO votes(voter_name, head_boy, head_girl, created_at) VALUES(?,?,?, datetime('now'))",
        (voter_name, head_boy, head_girl)
    )

    conn.commit()
    conn.close()


    return jsonify({
        "success": True,
        "message": "Vote Saved Successfully"
    })


@app.route("/results")
def results():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    cursor.execute("""
        SELECT head_boy, COUNT(*)
        FROM votes
        GROUP BY head_boy
    """)

    head_boy_results = cursor.fetchall()


    cursor.execute("""
        SELECT head_girl, COUNT(*)
        FROM votes
        GROUP BY head_girl
    """)

    head_girl_results = cursor.fetchall()


    conn.close()


    return jsonify({
        "head_boy": head_boy_results,
        "head_girl": head_girl_results
    })


@app.route("/voters")
def voters():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT voter_name, head_boy, head_girl, created_at FROM votes"
    )

    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            "voter_name": r[0],
            "head_boy": r[1],
            "head_girl": r[2],
            "created_at": r[3],
        }
        for r in rows
    ]

    return jsonify(data)


# LIVE EXCEL EXPORT FROM RENDER DATABASE

from flask import send_file

@app.route("/export")
def export():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM votes",
        conn
    )

    file_name = "Election_Voting_Record.xlsx"

    df.to_excel(
        file_name,
        index=False
    )

    conn.close()

    return send_file(
        file_name,
        as_attachment=True
    )


@app.route("/admin-login", methods=["POST"])
def admin_login():

    data = request.json

    username = data["username"]
    password = data["password"]


    if username == "admin" and password == "admin123":

        return jsonify({
            "success": True,
            "message": "Login successful"
        })


    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )