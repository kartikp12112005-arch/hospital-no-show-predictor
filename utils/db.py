"""
Database utility module.

Handles SQLite connection management and one-time schema initialization,
including seeding a default admin account on first run.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# Default admin credentials used ONLY on first run when no admin exists yet.
# Change these immediately after first login in a real deployment.
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@123"

# schema.sql always lives alongside this file's project, regardless of
# where the actual .db file is being created (e.g. a temp dir in tests).
_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "schema.sql")
_SCHEMA_PATH = os.path.normpath(_SCHEMA_PATH)


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Open a new SQLite connection with row access by column name.

    Args:
        db_path: Absolute path to the .db file.

    Returns:
        sqlite3.Connection configured with Row factory and foreign keys on.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL mode lets readers (dashboard/history pages) run concurrently
    # with writers (new predictions being saved) without locking errors.
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: str) -> None:
    """
    Create database tables (if they don't already exist) from schema.sql
    and seed a default admin account if the admin table is empty.

    Args:
        db_path: Absolute path to the .db file.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = get_db_connection(db_path)

    try:
        with open(_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())

        existing_admin = conn.execute(
            "SELECT id FROM admin WHERE username = ?", (DEFAULT_ADMIN_USERNAME,)
        ).fetchone()

        if existing_admin is None:
            password_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
            conn.execute(
                "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                (DEFAULT_ADMIN_USERNAME, password_hash),
            )
            conn.commit()
    finally:
        conn.close()
