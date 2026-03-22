import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analyses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  counts TEXT,
                  events TEXT)''')
    conn.commit()
    conn.close()

def save_analysis(counts: Dict[str, int], events: List[Dict[str, Any]]):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO analyses (timestamp, counts, events) VALUES (?, ?, ?)",
                  (datetime.utcnow().isoformat(), json.dumps(counts), json.dumps(events)))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, counts, events FROM analyses ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "timestamp": r[0], 
            "counts": json.loads(r[1]), 
            "events": json.loads(r[2])
        } 
        for r in rows
    ]
