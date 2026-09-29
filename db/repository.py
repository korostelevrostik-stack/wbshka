import os
import sqlite3
from datetime import datetime
from config import config


class Repo:
    def __init__(self, path: str | None = None):
        self.path = path or config.db_path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS posted_products (
                    nm_id      INTEGER PRIMARY KEY,
                    name       TEXT,
                    price      REAL,
                    posted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tracked_users (
                    user_id    INTEGER PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def is_posted(self, nm_id: int) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM posted_products WHERE nm_id = ?", (nm_id,)
            ).fetchone()
        return row is not None

    def mark_posted(self, nm_id: int, name: str, price: float) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO posted_products (nm_id, name, price) "
                "VALUES (?, ?, ?)",
                (nm_id, name, price),
            )

    def add_user(self, user_id: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tracked_users (user_id) VALUES (?)",
                (user_id,),
            )

    def stats(self) -> dict:
        with self._conn() as conn:
            posted = conn.execute(
                "SELECT COUNT(*) AS c FROM posted_products"
            ).fetchone()["c"]
            users = conn.execute(
                "SELECT COUNT(*) AS c FROM tracked_users"
            ).fetchone()["c"]
        return {"posted": posted, "users": users}


repo = Repo()
