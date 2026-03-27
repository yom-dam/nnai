"""SQLite 연결 + 스키마 초기화."""
import sqlite3
import os
import threading

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")


def init_db(path: str | None = None) -> sqlite3.Connection:
    """DB 연결 + 테이블 생성. path=':memory:' 이면 인메모리."""
    db_path = path or os.environ.get("NNAI_DB_PATH") or _DEFAULT_PATH
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         TEXT PRIMARY KEY,
            email      TEXT,
            name       TEXT,
            picture    TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS pins (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    TEXT NOT NULL REFERENCES users(id),
            city       TEXT NOT NULL,
            display    TEXT,
            note       TEXT,
            lat        REAL NOT NULL,
            lng        REAL NOT NULL,
            user_lat   REAL,
            user_lng   REAL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


_conn: sqlite3.Connection | None = None
_lock = threading.Lock()


def get_conn() -> sqlite3.Connection:
    """앱 전역 싱글턴 연결 반환."""
    global _conn
    if _conn is None:
        with _lock:
            if _conn is None:
                _conn = init_db()
    return _conn
