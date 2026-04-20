"""SQLite connection helper for the api app.

The database file path is controlled by the ``POC_SDD_DB_PATH`` env var and
defaults to ``./data/poc-sdd.db`` relative to the current working directory
(which, for the api app, is ``apps/api``). The parent directory is created
if it does not yet exist.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = "./data/poc-sdd.db"


def get_db_path() -> Path:
    """Return the resolved DB path, honoring ``POC_SDD_DB_PATH``."""
    return Path(os.environ.get("POC_SDD_DB_PATH", DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection to the configured DB path.

    Ensures the parent directory exists. Returns rows as ``sqlite3.Row`` so
    callers can access columns by name.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT    NOT NULL,
  done       INTEGER NOT NULL DEFAULT 0,
  created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
"""


def init_schema() -> None:
    """Create tables/indexes if they don't already exist. Idempotent.

    Also migrates pre-existing databases by adding the ``done`` column if
    it is not yet present.
    """
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        if "done" not in columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN done INTEGER NOT NULL DEFAULT 0"
            )
