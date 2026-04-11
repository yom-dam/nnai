"""타로 세션 — 5장 추천 결과의 서버사이드 저장 및 reveal 게이팅."""
from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# In-memory session store (추후 DB/Redis로 교체 가능)
_sessions: dict[str, dict[str, Any]] = {}


def create_session(cities: list[dict]) -> str:
    """5장 도시 데이터를 저장하고 session_id를 반환한다."""
    session_id = uuid.uuid4().hex[:16]
    _sessions[session_id] = {
        "cities": cities,
        "revealed_indices": None,
    }
    logger.info(
        "[tarot_session] created session=%s, cities=%d",
        session_id, len(cities),
    )
    return session_id


def get_session(session_id: str) -> dict[str, Any] | None:
    """세션 데이터를 반환한다. 없으면 None."""
    return _sessions.get(session_id)


def reveal_cards(session_id: str, indices: list[int]) -> list[dict]:
    """선택된 3장의 인덱스를 받아 해당 도시 데이터를 반환한다."""
    session = _sessions.get(session_id)
    if session is None:
        raise ValueError("Session not found")
    if session["revealed_indices"] is not None:
        raise ValueError("Cards already revealed")
    if len(indices) != 3:
        raise ValueError("Must select exactly 3 cards")
    if any(i < 0 or i >= len(session["cities"]) for i in indices):
        raise ValueError("Invalid card index")

    session["revealed_indices"] = sorted(indices)
    return [session["cities"][i] for i in indices]
