"""
JEEVAN Core Protocol - Database & Persistent Memory Manager
"""
import sqlite3
import datetime
import json
from pathlib import Path
from backend.config import settings

DB_PATH = settings.database_path

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Conversations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            intent TEXT
        )
    """)
    
    # User Preferences Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'preference'
        )
    """)

    # Task Execution Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_executions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'RUNNING',
            execution_mode TEXT DEFAULT 'Background',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_conversation(sender: str, message: str, intent: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (timestamp, sender, message, intent) VALUES (?, ?, ?, ?)",
        (datetime.datetime.utcnow().isoformat(), sender, message, intent)
    )
    conn.commit()
    conn.close()

def get_recent_conversations(limit: int = 20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def set_preference(key: str, value: str, category: str = "preference"):
    # Security Policy: Credentials must never be committed to memory
    low_key = key.lower()
    if any(k in low_key for k in ["password", "secret", "token", "key", "credential"]):
        raise ValueError("Security Policy Refusal: Private credentials cannot be stored in memory.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_preferences (key, value, category) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value, category)
    )
    conn.commit()
    conn.close()

def get_all_preferences():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_preferences")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

init_db()
