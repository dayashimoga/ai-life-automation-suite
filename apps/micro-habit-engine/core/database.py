import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "habit.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_habit(habit_name: str, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO habit_logs (habit_name, timestamp) VALUES (?, ?)", (habit_name, timestamp))
    conn.commit()
    conn.close()


def get_logs(habit_name: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if habit_name:
        c.execute("SELECT habit_name, timestamp FROM habit_logs WHERE habit_name = ? ORDER BY timestamp DESC", (habit_name,))
    else:
        c.execute("SELECT habit_name, timestamp FROM habit_logs ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [{"habit_name": r[0], "timestamp": r[1]} for r in rows]


def get_distinct_habits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT habit_name FROM habit_logs")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
