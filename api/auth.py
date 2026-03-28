# api/auth.py
"""Google OAuth 2.0 FastAPI 라우터."""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from itsdangerous import URLSafeTimedSerializer, BadSignature
from utils.db import get_conn

router = APIRouter()

_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
_REDIRECT_URI  = os.environ.get(
    "OAUTH_REDIRECT_URI",
    "http://localhost:7860/auth/google/callback"
)
_SECRET_KEY    = os.environ.get("SECRET_KEY", "dev-secret-change-me")
_SIGNER        = URLSafeTimedSerializer(_SECRET_KEY)
_COOKIE_NAME   = "nnai_session"
_SCOPES        = "openid email profile"

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/auth/google")
async def google_login():
    async with AsyncOAuth2Client(
        client_id=_CLIENT_ID,
        redirect_uri=_REDIRECT_URI,
        scope=_SCOPES,
    ) as client:
        uri, _ = client.create_authorization_url(GOOGLE_AUTH_URL)
    return RedirectResponse(uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request, code: str = "", error: str = ""):
    if error or not code:
        return RedirectResponse("/?auth_error=1")
    async with AsyncOAuth2Client(
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET,
        redirect_uri=_REDIRECT_URI,
    ) as client:
        token = await client.fetch_token(GOOGLE_TOKEN_URL, code=code)
        resp  = await client.get(GOOGLE_USER_URL, headers={'Authorization': f'Bearer {token["access_token"]}'})
    info = resp.json()
    uid  = info.get("sub")
    if not uid:
        return RedirectResponse("/?auth_error=1")

    # upsert user
    conn = get_conn()
    conn.execute(
        "INSERT INTO users(id,email,name,picture,created_at) VALUES(?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET email=excluded.email, name=excluded.name, picture=excluded.picture",
        (uid, info.get("email"), info.get("name"),
         info.get("picture"), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()

    # 서명 쿠키 발급
    token_str = _SIGNER.dumps({"uid": uid, "name": info.get("name"), "picture": info.get("picture")})
    resp = RedirectResponse("/")
    resp.set_cookie(_COOKIE_NAME, token_str, httponly=True, samesite="lax", max_age=86400)
    return resp


@router.get("/auth/me")
def me(request: Request):
    raw = request.cookies.get(_COOKIE_NAME)
    if not raw:
        return JSONResponse({"logged_in": False})
    try:
        data = _SIGNER.loads(raw, max_age=86400)
        return JSONResponse({"logged_in": True, "name": data["name"], "picture": data.get("picture"), "uid": data["uid"]})
    except BadSignature:
        return JSONResponse({"logged_in": False})


@router.get("/auth/logout")
def logout():
    resp = RedirectResponse("/")
    resp.delete_cookie(_COOKIE_NAME)
    return resp


def extract_user_id(request: Request) -> str | None:
    """미들웨어용 — 쿠키에서 user_id 추출."""
    raw = request.cookies.get(_COOKIE_NAME)
    if not raw:
        return None
    try:
        return _SIGNER.loads(raw, max_age=86400)["uid"]
    except BadSignature:
        return None
