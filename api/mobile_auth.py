"""모바일 앱 전용 인증 라우터."""
from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.db import get_conn
from utils.mobile_auth import create_jwt, require_mobile_auth

router = APIRouter(prefix="/auth/mobile", tags=["mobile-auth"])

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")


class TokenRequest(BaseModel):
    code: str
    redirect_uri: str


def _get_user(user_id: str) -> dict | None:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, picture FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "picture": row[2]}


@router.post("/token")
async def mobile_token(body: TokenRequest):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    async with httpx.AsyncClient(timeout=15) as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": body.code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": body.redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Google OAuth failed")

        access_token = token_res.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Google OAuth failed")

        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    info = userinfo_res.json()
    user_id = info.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (id, email, name, picture, created_at)
            VALUES (%s, %s, %s, %s, NOW()::text)
            ON CONFLICT (id) DO UPDATE
                SET email = EXCLUDED.email,
                    name = EXCLUDED.name,
                    picture = EXCLUDED.picture
            """,
            (user_id, info.get("email"), info.get("name"), info.get("picture")),
        )
    conn.commit()

    return {
        "token": create_jwt(user_id),
        "user": {
            "uid": user_id,
            "name": info.get("name"),
            "picture": info.get("picture"),
        },
    }


@router.get("/me")
def mobile_me(user_id: str = Depends(require_mobile_auth)):
    user = _get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"uid": user["id"], "name": user["name"], "picture": user["picture"]}
