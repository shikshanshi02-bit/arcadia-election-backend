#!/usr/bin/env python3
"""
Reset the election database votes table by deleting all rows while keeping the table structure.

This script:
- Makes a timestamped backup copy of the SQLite file (unless --no-backup)
- Shows the number of rows before deletion
- Deletes all rows from the 'votes' table
- VACUUMs the database to reclaim space
- Shows the number of rows after deletion

Usage:
  python reset_election_db.py [--db PATH] [--backup-dir DIR] [--yes] [--no-backup]

Examples:
  # Interactive (prompts for confirmation)
  python reset_election_db.py

  # Non-interactive, makes a backup in ./backups
  python reset_election_db.py --yes --backup-dir backups

  # Non-interactive, skip backup
  python reset_election_db.py --yes --no-backup

Be careful: this permanently removes vote records. The backup file is created by default.
"""

import argparse
import datetime
import os
import shutil
import sqlite3
import sys


def backup_db(db_path: str, backup_dir: str) -> str:
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.basename(db_path)
    backup_name = f"{base}.{ts}.bak"
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    return backup_path


def get_row_count(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM votes")
    return cur.fetchone()[0]


def reset_votes(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        before = get_row_count(conn)
        print(f"Rows before: {before}")

        cur = conn.cursor()
        cur.execute("DELETE FROM votes")
        conn.commit()

        # VACUUM requires closing connection for some sqlite setups; use it safely
        conn.close()
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.commit()

        after = get_row_count(conn)
        print(f"Rows after: {after}")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Reset election database votes table (delete rows, keep schema)")
    parser.add_argument("--db", default="election.db", help="Path to SQLite DB file (default: election.db)")
    parser.add_argument("--backup-dir", default="backups", help="Directory to place DB backup (default: backups)")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt and proceed")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a backup before resetting")

    args = parser.parse_args()

    db_path = args.db

    if not os.path.isfile(db_path):
        print(f"ERROR: Database file not found: {db_path}")
        sys.exit(2)

    if not args.yes:
        print("WARNING: This will permanently delete all rows from the 'votes' table while keeping the table structure.")
        resp = input("Type 'DELETE' to proceed: ")
        if resp.strip() != "DELETE":
            print("Aborted by user.")
            sys.exit(0)

    backup_path = None
    if not args.no_backup:
        try:
            backup_path = backup_db(db_path, args.backup_dir)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"ERROR: Failed to create backup: {e}")
            print("Aborting to avoid data loss.")
            sys.exit(1)

    try:
        reset_votes(db_path)
        print("Reset completed successfully.")
        if backup_path:
            print(f"Backup retained at: {backup_path}")
    except Exception as e:
        print(f"ERROR during reset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
