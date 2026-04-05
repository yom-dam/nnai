from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.mobile_uploads import router as uploads_router
from utils.mobile_auth import require_mobile_auth


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(uploads_router)
    app.dependency_overrides[require_mobile_auth] = lambda: "test-user"
    return app


def test_mobile_upload_image_is_fetchable_by_returned_url():
    client = TestClient(_make_app())

    uploaded = client.post(
        "/api/mobile/uploads/image",
        files={"file": ("photo.png", b"png-bytes", "image/png")},
        headers={"Authorization": "Bearer test-token"},
    )
    assert uploaded.status_code == 200
    payload = uploaded.json()
    uploaded_url = payload.get("url") or payload.get("image_url")
    assert isinstance(uploaded_url, str)
    assert uploaded_url.startswith("/api/mobile/uploads/")

    fetched = client.get(uploaded_url, headers={"Authorization": "Bearer test-token"})
    assert fetched.status_code == 200
    assert fetched.content == b"png-bytes"
