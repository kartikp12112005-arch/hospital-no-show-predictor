"""
Lightweight application logging module.

Writes INFO / WARNING / ERROR events to the application_logs table so
admins can audit activity without needing an external logging service.
"""

import sqlite3
from datetime import datetime, timezone


def log_event(db_path: str, level: str, message: str) -> None:
    """
    Insert a log entry. Failures here are swallowed intentionally —
    logging should never crash the main request.

    Args:
        db_path: Absolute path to the .db file.
        level: 'INFO', 'WARNING', or 'ERROR'.
        message: Human-readable log message.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO application_logs (level, message, created_at) VALUES (?, ?, ?)",
            (level, message, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
