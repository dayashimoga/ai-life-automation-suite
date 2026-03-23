import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "journal.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            caption TEXT,
            tags TEXT,
            mock_location TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_entry(entry_dict: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO journal_entries (id, filename, caption, tags, mock_location, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (
            entry_dict["id"],
            entry_dict["filename"],
            entry_dict["caption"],
            json.dumps(entry_dict["tags"]),
            entry_dict.get("mock_location", ""),
            entry_dict["timestamp"],
        ),
    )
    conn.commit()
    conn.close()


def get_all_entries() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM journal_entries ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "filename": r["filename"],
            "caption": r["caption"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "mock_location": r["mock_location"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def search_entries(query: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM journal_entries WHERE caption LIKE ? OR tags LIKE ? ORDER BY timestamp DESC",
        (f"%{query}%", f"%{query}%"),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "filename": r["filename"],
            "caption": r["caption"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "mock_location": r["mock_location"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def get_entries_on_this_day() -> list:
    """Return entries from the same month-day in previous years."""
    from datetime import datetime

    today = datetime.utcnow()
    month_day = today.strftime("-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM journal_entries WHERE timestamp LIKE ? ORDER BY timestamp DESC",
        (f"%{month_day}%",),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "filename": r["filename"],
            "caption": r["caption"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "mock_location": r["mock_location"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]
