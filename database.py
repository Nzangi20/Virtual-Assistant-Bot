"""
database.py - SQLite Database Module
======================================
Stores user information and chat messages for analytics.
Uses SQLite for zero-configuration, file-based storage.
"""

import sqlite3
import logging
from datetime import datetime, timezone
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db() -> None:
    """
    Initialize the database tables.
    Called once when the bot starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table: users — stores everyone who interacted with the bot
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            last_name   TEXT,
            first_seen  TEXT NOT NULL,
            last_seen   TEXT NOT NULL
        )
    """)

    # Table: messages — logs every incoming message
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER NOT NULL,
            message     TEXT,
            timestamp   TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES users(chat_id)
        )
    """)

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized successfully.")


def save_user(chat_id: int, username: str | None,
              first_name: str | None, last_name: str | None) -> None:
    """
    Save or update a user record.
    If the user already exists, update their last_seen timestamp.
    """
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (chat_id, username, first_name, last_name, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                username   = excluded.username,
                first_name = excluded.first_name,
                last_name  = excluded.last_name,
                last_seen  = excluded.last_seen
        """, (chat_id, username, first_name, last_name, now, now))
        conn.commit()
        logger.debug(f"User saved: {chat_id} ({first_name})")
    except sqlite3.Error as e:
        logger.error(f"Error saving user {chat_id}: {e}")
    finally:
        conn.close()


def save_message(chat_id: int, message_text: str) -> None:
    """Log an incoming message to the database."""
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO messages (chat_id, message, timestamp)
            VALUES (?, ?, ?)
        """, (chat_id, message_text, now))
        conn.commit()
        logger.debug(f"Message saved from {chat_id}")
    except sqlite3.Error as e:
        logger.error(f"Error saving message from {chat_id}: {e}")
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    """Return a list of all registered users (for admin/analytics)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY last_seen DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def get_user_messages(chat_id: int, limit: int = 50) -> list[dict]:
    """Return recent messages from a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
        (chat_id, limit),
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages
