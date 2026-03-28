"""SQLite data/users.db → PostgreSQL 1회성 마이그레이션 스크립트.

사용법:
    DATABASE_URL=<pg_url> python scripts/migrate_sqlite_to_pg.py
"""
import os
import sqlite3
import psycopg2

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")
PG_URL = os.environ.get("DATABASE_URL")

if not PG_URL:
    raise RuntimeError("DATABASE_URL 환경변수를 설정하세요.")

sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_conn.row_factory = sqlite3.Row

pg_conn = psycopg2.connect(PG_URL)

# users
users = sqlite_conn.execute("SELECT id, email, name, picture, created_at FROM users").fetchall()
print(f"users {len(users)}건 마이그레이션 중...")
with pg_conn.cursor() as cur:
    for u in users:
        cur.execute(
            "INSERT INTO users(id,email,name,picture,created_at) VALUES(%s,%s,%s,%s,%s) "
            "ON CONFLICT(id) DO NOTHING",
            (u["id"], u["email"], u["name"], u["picture"], u["created_at"])
        )

# pins
pins = sqlite_conn.execute(
    "SELECT user_id,city,display,note,lat,lng,user_lat,user_lng,created_at FROM pins"
).fetchall()
print(f"pins {len(pins)}건 마이그레이션 중...")
with pg_conn.cursor() as cur:
    for p in pins:
        cur.execute(
            "INSERT INTO pins(user_id,city,display,note,lat,lng,user_lat,user_lng,created_at) "
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (p["user_id"], p["city"], p["display"], p["note"],
             p["lat"], p["lng"], p["user_lat"], p["user_lng"], p["created_at"])
        )

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()
print("마이그레이션 완료!")
