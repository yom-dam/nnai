"""핀 CRUD FastAPI 라우터."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from utils.db import get_conn

router = APIRouter()
SESSION_KEY = "user_id"


class PinIn(BaseModel):
    city: str
    display: str
    note: str
    lat: float
    lng: float
    user_lat: float | None = None
    user_lng: float | None = None


def _user_id(request: Request) -> str | None:
    return getattr(request.state, SESSION_KEY, None)


@router.get("/pins")
def list_pins(request: Request):
    uid = _user_id(request)
    if not uid:
        return []
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT city, display, note, lat, lng, created_at FROM pins "
            "WHERE user_id=%s ORDER BY created_at ASC", (uid,)
        )
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]


@router.post("/pins")
def add_pin(request: Request, pin: PinIn):
    uid = _user_id(request)
    if not uid:
        raise HTTPException(401, "로그인이 필요합니다")
    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pins(user_id,city,display,note,lat,lng,user_lat,user_lng,created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (uid, pin.city, pin.display, pin.note,
             pin.lat, pin.lng, pin.user_lat, pin.user_lng, now)
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return {"id": new_id, "city": pin.city, "created_at": now}


class PinUpdate(BaseModel):
    note: str


@router.put("/pins/{pin_id}")
def update_pin(pin_id: int, request: Request, body: PinUpdate):
    uid = _user_id(request)
    if not uid:
        raise HTTPException(401, "로그인이 필요합니다")
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pins SET note=%s WHERE id=%s AND user_id=%s RETURNING id",
            (body.note, pin_id, uid)
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "핀을 찾을 수 없습니다")
    conn.commit()
    return {"id": row[0], "note": body.note}


@router.delete("/pins/{pin_id}")
def delete_pin(pin_id: int, request: Request):
    uid = _user_id(request)
    if not uid:
        raise HTTPException(401, "로그인이 필요합니다")
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM pins WHERE id=%s AND user_id=%s RETURNING id",
            (pin_id, uid)
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "핀을 찾을 수 없습니다")
    conn.commit()
    return {"ok": True}


@router.get("/pins/community")
def community_pins():
    """전체 사용자 핀을 도시별로 집계."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT city, MIN(display) display, ROUND(AVG(lat)::numeric,4) lat, "
            "ROUND(AVG(lng)::numeric,4) lng, COUNT(*) cnt "
            "FROM pins GROUP BY city ORDER BY cnt DESC LIMIT 100"
        )
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]
