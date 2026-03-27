import os, tempfile, pytest
os.environ.setdefault("NNAI_DB_PATH", ":memory:")

from utils.db import init_db, get_conn

def test_init_creates_users_table():
    conn = init_db(":memory:")
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "users" in tables
    assert "pins" in tables
    conn.close()

def test_insert_and_fetch_pin():
    conn = init_db(":memory:")
    conn.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        ("uid1","test@example.com","Test","http://img",
         "2026-01-01T00:00:00")
    )
    conn.execute(
        "INSERT INTO pins(user_id,city,display,note,lat,lng,user_lat,user_lng,created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        ("uid1","방콕","Bangkok, Thailand","최고!",13.75,100.5,
         13.0,100.0,"2026-01-01T00:00:00")
    )
    conn.commit()
    rows = conn.execute("SELECT city, note FROM pins WHERE user_id=?",("uid1",)).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "방콕"
    assert rows[0][1] == "최고!"
    conn.close()
