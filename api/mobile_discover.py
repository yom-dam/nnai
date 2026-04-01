"""모바일 앱 전용 Discover 라우터."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.db import get_conn
from utils.mobile_auth import require_mobile_auth

router = APIRouter(prefix="/api/mobile", tags=["mobile-discover"])


class PinCreate(BaseModel):
    city: str
    display: str
    note: str
    lat: float
    lng: float
    user_lat: float | None = None
    user_lng: float | None = None


@router.get("/cities")
def get_cities(user_id: str = Depends(require_mobile_auth)):
    del user_id  # 인증 목적만 사용
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT city_id, city, city_kr, country, country_id,
                   monthly_cost_usd, internet_mbps, safety_score, english_score, nomad_score
            FROM verified_cities
            WHERE is_verified = TRUE
            ORDER BY nomad_score DESC NULLS LAST
            LIMIT 50
            """
        )
        rows = cur.fetchall()

    return [
        {
            "city_id": r[0],
            "city": r[1],
            "city_kr": r[2],
            "country": r[3],
            "country_id": r[4],
            "monthly_cost_usd": r[5],
            "internet_mbps": r[6],
            "safety_score": r[7],
            "english_score": r[8],
            "nomad_score": r[9],
        }
        for r in rows
    ]


@router.get("/cities/{city_id}")
def get_city(city_id: str, user_id: str = Depends(require_mobile_auth)):
    del user_id  # 인증 목적만 사용
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT city_id, city, city_kr, country, country_id,
                   monthly_cost_usd, internet_mbps, safety_score,
                   english_score, nomad_score, tax_residency_days, data_verified_date
            FROM verified_cities
            WHERE city_id = %s
            """,
            (city_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="City not found")

    return {
        "city_id": row[0],
        "city": row[1],
        "city_kr": row[2],
        "country": row[3],
        "country_id": row[4],
        "monthly_cost_usd": row[5],
        "internet_mbps": row[6],
        "safety_score": row[7],
        "english_score": row[8],
        "nomad_score": row[9],
        "tax_residency_days": row[10],
        "data_verified_date": row[11],
    }


@router.get("/circles")
def get_circles(user_id: str = Depends(require_mobile_auth)):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.description, c.member_count,
                   EXISTS(
                       SELECT 1 FROM circle_members
                       WHERE circle_id = c.id AND user_id = %s
                   ) AS joined
            FROM circles c
            ORDER BY c.member_count DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "member_count": r[3],
            "joined": r[4],
        }
        for r in rows
    ]


@router.post("/circles/{circle_id}/join")
def toggle_circle(circle_id: int, user_id: str = Depends(require_mobile_auth)):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM circles WHERE id = %s", (circle_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Circle not found")

        cur.execute(
            "SELECT 1 FROM circle_members WHERE circle_id = %s AND user_id = %s",
            (circle_id, user_id),
        )
        is_member = cur.fetchone() is not None

        if is_member:
            cur.execute(
                "DELETE FROM circle_members WHERE circle_id = %s AND user_id = %s",
                (circle_id, user_id),
            )
            cur.execute(
                "UPDATE circles SET member_count = GREATEST(0, member_count - 1) WHERE id = %s",
                (circle_id,),
            )
        else:
            cur.execute(
                "INSERT INTO circle_members (circle_id, user_id) VALUES (%s, %s)",
                (circle_id, user_id),
            )
            cur.execute(
                "UPDATE circles SET member_count = member_count + 1 WHERE id = %s",
                (circle_id,),
            )
    conn.commit()

    return {"joined": not is_member}


@router.get("/pins")
def get_pins(user_id: str = Depends(require_mobile_auth)):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, city, display, note, lat, lng, created_at
            FROM pins
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "city": r[1],
            "display": r[2],
            "note": r[3],
            "lat": r[4],
            "lng": r[5],
            "created_at": str(r[6]),
        }
        for r in rows
    ]


@router.post("/pins", status_code=201)
def create_pin(body: PinCreate, user_id: str = Depends(require_mobile_auth)):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO pins (user_id, city, display, note, lat, lng, user_lat, user_lng, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW()::text)
            RETURNING id, city, created_at
            """,
            (user_id, body.city, body.display, body.note, body.lat, body.lng, body.user_lat, body.user_lng),
        )
        row = cur.fetchone()
    conn.commit()

    return {"id": row[0], "city": row[1], "created_at": str(row[2])}
