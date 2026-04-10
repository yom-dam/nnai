"""타로 세션 저장/조회/reveal 테스트"""
import pytest
from api.tarot_session import create_session, get_session, reveal_cards


def test_create_session_returns_session_id():
    cities = [{"city": f"City{i}", "country_id": f"C{i}"} for i in range(5)]
    sid = create_session(cities)
    assert isinstance(sid, str)
    assert len(sid) > 8


def test_get_session_returns_stored_data():
    cities = [{"city": f"City{i}", "country_id": f"C{i}"} for i in range(5)]
    sid = create_session(cities)
    session = get_session(sid)
    assert session is not None
    assert len(session["cities"]) == 5
    assert session["revealed_indices"] is None


def test_reveal_cards_returns_selected_cities():
    cities = [{"city": f"City{i}", "score": i} for i in range(5)]
    sid = create_session(cities)
    revealed = reveal_cards(sid, [0, 2, 4])
    assert len(revealed) == 3
    assert revealed[0]["city"] == "City0"
    assert revealed[1]["city"] == "City2"
    assert revealed[2]["city"] == "City4"


def test_reveal_cards_stores_indices():
    cities = [{"city": f"City{i}"} for i in range(5)]
    sid = create_session(cities)
    reveal_cards(sid, [1, 3, 4])
    session = get_session(sid)
    assert session["revealed_indices"] == [1, 3, 4]


def test_reveal_cards_rejects_invalid_indices():
    cities = [{"city": f"City{i}"} for i in range(5)]
    sid = create_session(cities)
    with pytest.raises(ValueError):
        reveal_cards(sid, [0, 1, 5])


def test_reveal_cards_rejects_wrong_count():
    cities = [{"city": f"City{i}"} for i in range(5)]
    sid = create_session(cities)
    with pytest.raises(ValueError):
        reveal_cards(sid, [0, 1])


def test_reveal_cards_rejects_double_reveal():
    cities = [{"city": f"City{i}"} for i in range(5)]
    sid = create_session(cities)
    reveal_cards(sid, [0, 1, 2])
    with pytest.raises(ValueError):
        reveal_cards(sid, [0, 1, 2])


def test_get_session_returns_none_for_unknown():
    assert get_session("nonexistent") is None


def test_reveal_endpoint_integration():
    """reveal API가 3장의 도시 데이터를 반환하는지 검증."""
    cities = [
        {"city": "Lisbon", "country_id": "PT", "monthly_cost_usd": 1800},
        {"city": "Bangkok", "country_id": "TH", "monthly_cost_usd": 1100},
        {"city": "Medellin", "country_id": "CO", "monthly_cost_usd": 1200},
        {"city": "Tbilisi", "country_id": "GE", "monthly_cost_usd": 900},
        {"city": "Budapest", "country_id": "HU", "monthly_cost_usd": 1500},
    ]
    sid = create_session(cities)
    revealed = reveal_cards(sid, [0, 2, 3])
    assert len(revealed) == 3
    assert revealed[0]["city"] == "Lisbon"
    assert revealed[1]["city"] == "Medellin"
    assert revealed[2]["city"] == "Tbilisi"
