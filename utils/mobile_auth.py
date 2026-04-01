"""모바일 앱용 JWT 인증 유틸리티."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request

JWT_SECRET = os.environ.get("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"


class MobileAuthError(Exception):
    """모바일 JWT 처리 예외."""


def create_jwt(user_id: str, expires_in_seconds: int = 86400) -> str:
    if not JWT_SECRET:
        raise MobileAuthError("JWT_SECRET is not configured")
    now = datetime.now(tz=timezone.utc)
    payload = {
        "uid": user_id,
        "exp": now + timedelta(seconds=expires_in_seconds),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    if not JWT_SECRET:
        raise MobileAuthError("JWT_SECRET is not configured")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise MobileAuthError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise MobileAuthError("Invalid token") from exc


def require_mobile_auth(request: Request) -> str:
    """FastAPI dependency: Bearer JWT에서 user_id(uid)를 반환한다."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token required")

    try:
        payload = decode_jwt(token)
    except MobileAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    uid = payload.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    return uid
