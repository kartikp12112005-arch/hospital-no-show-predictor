"""
Standalone database reset utility.

Deletes the existing hospital.db (if any) and recreates it from
schema.sql, re-seeding the default admin account. Useful during
development or before a fresh demo.

Run from the project root:
    python database/reset_db.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.db import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, init_db  # noqa: E402

DB_PATH = os.path.join(BASE_DIR, "database", "hospital.db")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")

    # Also remove WAL/SHM sidecar files if present
    for suffix in ("-wal", "-shm"):
        sidecar = DB_PATH + suffix
        if os.path.exists(sidecar):
            os.remove(sidecar)

    init_db(DB_PATH)
    print(f"Fresh database created at {DB_PATH}")
    print(f"Seeded admin login -> username: {DEFAULT_ADMIN_USERNAME} | password: {DEFAULT_ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
