import os
import pytest

TEST_DB_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DB_URL,
    reason="TEST_DATABASE_URL 환경변수가 없으면 스킵"
)

from fastapi.testclient import TestClient
from fastapi import FastAPI
from utils.db import init_db


def _make_app(user_id: str | None):
    from api.pins import router, SESSION_KEY
    from starlette.middleware.base import BaseHTTPMiddleware

    app = FastAPI()

    class FakeAuth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.user_id = user_id
            return await call_next(request)

    app.add_middleware(FakeAuth)
    app.include_router(router, prefix="/api")

    from utils import db as db_mod
    db_mod._conn = init_db(TEST_DB_URL)
    # 테스트용 테이블 초기화
    with db_mod._conn.cursor() as cur:
        cur.execute("DELETE FROM pins")
        cur.execute("DELETE FROM users")
        cur.execute(
            "INSERT INTO users VALUES (%s,%s,%s,%s,%s)",
            ("uid1", "t@t.com", "T", "", "2026-01-01T00:00:00")
        )
    db_mod._conn.commit()
    return app


def test_get_pins_empty_returns_list():
    client = TestClient(_make_app("uid1"))
    r = client.get("/api/pins")
    assert r.status_code == 200
    assert r.json() == []


def test_post_pin_saves_and_returns():
    client = TestClient(_make_app("uid1"))
    payload = {
        "city": "방콕", "display": "Bangkok, Thailand",
        "note": "좋아요", "lat": 13.75, "lng": 100.5,
        "user_lat": 13.0, "user_lng": 100.0
    }
    r = client.post("/api/pins", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["city"] == "방콕"
    assert "id" in data


def test_post_pin_requires_auth():
    client = TestClient(_make_app(None))
    r = client.post("/api/pins", json={
        "city": "x", "display": "x", "note": "x", "lat": 0, "lng": 0
    })
    assert r.status_code == 401


def test_get_pins_returns_saved_pins():
    client = TestClient(_make_app("uid1"))
    client.post("/api/pins", json={
        "city": "서울", "display": "Seoul, Korea", "note": "홈",
        "lat": 37.56, "lng": 126.97, "user_lat": 37.5, "user_lng": 126.9
    })
    r = client.get("/api/pins")
    assert r.status_code == 200
    pins = r.json()
    assert len(pins) == 1
    assert pins[0]["city"] == "서울"


def test_get_community_pins():
    client = TestClient(_make_app("uid1"))
    client.post("/api/pins", json={
        "city": "발리", "display": "Bali, Indonesia", "note": "x",
        "lat": -8.34, "lng": 115.09, "user_lat": None, "user_lng": None
    })
    r = client.get("/api/pins/community")
    assert r.status_code == 200
    data = r.json()
    assert any(p["city"] == "발리" for p in data)


# ── PUT /api/pins/{pin_id} ────────────────────────────────────

def test_put_pin_updates_note():
    """저장한 핀의 note를 수정하면 200과 변경된 note를 반환한다."""
    client = TestClient(_make_app("uid1"))
    r = client.post("/api/pins", json={
        "city": "도쿄", "display": "Tokyo, Japan", "note": "원래 메모",
        "lat": 35.68, "lng": 139.69
    })
    pin_id = r.json()["id"]

    r2 = client.put(f"/api/pins/{pin_id}", json={"note": "변경된 메모"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["id"] == pin_id
    assert body["note"] == "변경된 메모"


def test_put_pin_requires_auth():
    """미로그인 상태에서 PUT 시 401을 반환한다."""
    # uid1으로 핀 생성 후, 비로그인 클라이언트로 수정 시도
    uid1_client = TestClient(_make_app("uid1"))
    r = uid1_client.post("/api/pins", json={
        "city": "파리", "display": "Paris, France", "note": "x",
        "lat": 48.85, "lng": 2.35
    })
    pin_id = r.json()["id"]

    anon_client = TestClient(_make_app(None))
    r2 = anon_client.put(f"/api/pins/{pin_id}", json={"note": "해킹"})
    assert r2.status_code == 401


def test_put_pin_other_user_returns_404():
    """다른 유저의 핀을 수정하려 하면 404를 반환한다."""
    uid1_client = TestClient(_make_app("uid1"))
    r = uid1_client.post("/api/pins", json={
        "city": "베를린", "display": "Berlin, Germany", "note": "x",
        "lat": 52.52, "lng": 13.4
    })
    pin_id = r.json()["id"]

    # uid2는 DB에 없지만 auth 미들웨어만 테스트 — uid2로 시도
    uid2_client = TestClient(_make_app("uid2"))
    r2 = uid2_client.put(f"/api/pins/{pin_id}", json={"note": "타인 수정"})
    assert r2.status_code == 404


def test_put_pin_nonexistent_id_returns_404():
    """존재하지 않는 pin_id로 PUT 시 404를 반환한다."""
    client = TestClient(_make_app("uid1"))
    r = client.put("/api/pins/999999", json={"note": "없는 핀"})
    assert r.status_code == 404


# ── DELETE /api/pins/{pin_id} ─────────────────────────────────

def test_delete_pin_returns_ok():
    """자신의 핀을 삭제하면 200 {"ok": true}를 반환한다."""
    client = TestClient(_make_app("uid1"))
    r = client.post("/api/pins", json={
        "city": "싱가포르", "display": "Singapore", "note": "삭제 예정",
        "lat": 1.35, "lng": 103.82
    })
    pin_id = r.json()["id"]

    r2 = client.delete(f"/api/pins/{pin_id}")
    assert r2.status_code == 200
    assert r2.json() == {"ok": True}


def test_delete_pin_actually_removes_from_list():
    """삭제 후 GET /api/pins에서 해당 핀이 조회되지 않는다."""
    client = TestClient(_make_app("uid1"))
    r = client.post("/api/pins", json={
        "city": "암스테르담", "display": "Amsterdam, Netherlands", "note": "y",
        "lat": 52.37, "lng": 4.89
    })
    pin_id = r.json()["id"]
    client.delete(f"/api/pins/{pin_id}")

    pins = client.get("/api/pins").json()
    assert not any(p.get("city") == "암스테르담" for p in pins)


def test_delete_pin_requires_auth():
    """미로그인 상태에서 DELETE 시 401을 반환한다."""
    uid1_client = TestClient(_make_app("uid1"))
    r = uid1_client.post("/api/pins", json={
        "city": "프라하", "display": "Prague, Czech", "note": "z",
        "lat": 50.07, "lng": 14.43
    })
    pin_id = r.json()["id"]

    anon_client = TestClient(_make_app(None))
    r2 = anon_client.delete(f"/api/pins/{pin_id}")
    assert r2.status_code == 401


def test_delete_pin_other_user_returns_404():
    """다른 유저의 핀을 삭제하려 하면 404를 반환한다."""
    uid1_client = TestClient(_make_app("uid1"))
    r = uid1_client.post("/api/pins", json={
        "city": "마드리드", "display": "Madrid, Spain", "note": "w",
        "lat": 40.41, "lng": -3.7
    })
    pin_id = r.json()["id"]

    uid2_client = TestClient(_make_app("uid2"))
    r2 = uid2_client.delete(f"/api/pins/{pin_id}")
    assert r2.status_code == 404


def test_delete_pin_nonexistent_id_returns_404():
    """존재하지 않는 pin_id로 DELETE 시 404를 반환한다."""
    client = TestClient(_make_app("uid1"))
    r = client.delete("/api/pins/999999")
    assert r.status_code == 404


# ── 엣지케이스 ────────────────────────────────────────────────

def test_post_pin_missing_required_field_returns_422():
    """필수 필드(city) 없이 POST 시 422를 반환한다."""
    client = TestClient(_make_app("uid1"))
    r = client.post("/api/pins", json={
        "display": "Unknown", "note": "x", "lat": 0, "lng": 0
    })
    assert r.status_code == 422


def test_get_pins_unauthenticated_returns_empty_list():
    """미로그인 상태에서 GET /api/pins는 빈 배열을 반환한다 (401 아님)."""
    client = TestClient(_make_app(None))
    r = client.get("/api/pins")
    assert r.status_code == 200
    assert r.json() == []


def test_community_pins_has_cnt_field():
    """community 핀 응답에 cnt 집계 필드가 포함된다."""
    client = TestClient(_make_app("uid1"))
    client.post("/api/pins", json={
        "city": "교토", "display": "Kyoto, Japan", "note": "k",
        "lat": 35.01, "lng": 135.76
    })
    r = client.get("/api/pins/community")
    assert r.status_code == 200
    data = r.json()
    kyoto = next((p for p in data if p["city"] == "교토"), None)
    assert kyoto is not None
    assert "cnt" in kyoto
    assert int(kyoto["cnt"]) >= 1
