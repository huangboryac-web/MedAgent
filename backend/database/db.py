import sqlite3
from typing import Literal

from constants import DB_NAME

def init_chat_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_chat_by_session_id(session_id: str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return rows

def insert_chat_by_session_id(session_id: str, chat: str, role: Literal['user', 'assistant'] = "assistant"):
    conn = sqlite3.connect(DB_NAME)
    
    conn.execute("INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)", 
                 (session_id, role, chat))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, MAX(timestamp) as last_active 
            FROM chat_history 
            GROUP BY session_id 
            ORDER BY last_active DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def delete_chat_by_session_id(session_id: str):
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()