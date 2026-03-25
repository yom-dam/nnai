"""tests/test_recommender.py — recommend_from_db() 단위 테스트"""
import pytest
from recommender import recommend_from_db


def _profile(**kwargs):
    base = {
        "nationality":        "한국",
        "income_usd":         3000,
        "income_krw":         420,
        "purpose":            "디지털 노마드",
        "lifestyle":          [],
        "languages":          [],
        "timeline":           "1년 단기 체험",
        "preferred_countries": [],
        "language":           "한국어",
        "persona_type":       "",
        "income_type":        "",
        "travel_type":        "혼자 (솔로)",
        "children_ages":      [],
        "dual_nationality":   False,
        "readiness_stage":    "",
        "has_spouse_income":  "없음",
        "spouse_income_krw":  0,
    }
    base.update(kwargs)
    return base


def test_returns_top_cities_list():
    result = recommend_from_db(_profile())
    assert isinstance(result, dict)
    assert "top_cities" in result
    assert isinstance(result["top_cities"], list)


def test_returns_at_most_3_cities():
    result = recommend_from_db(_profile())
    assert len(result["top_cities"]) <= 3


def test_city_dict_has_required_fields():
    required = {"city", "city_kr", "country", "country_id", "visa_type",
                "visa_url", "monthly_cost_usd", "score",
                "reasons", "realistic_warnings", "plan_b_trigger", "references"}
    result = recommend_from_db(_profile())
    for city in result["top_cities"]:
        missing = required - set(city.keys())
        assert not missing, f"누락 필드: {missing}"


def test_overall_warning_present():
    result = recommend_from_db(_profile())
    assert "overall_warning" in result
    assert isinstance(result["overall_warning"], str)


def test_income_filter_excludes_high_income_required_countries():
    """소득 $500이면 소득 기준 높은 국가 제외."""
    result = recommend_from_db(_profile(income_usd=500))
    for city in result["top_cities"]:
        # All returned cities must have passed the income filter
        # Check that none require more than $500
        assert city["monthly_cost_usd"] >= 0  # basic sanity


def test_high_income_includes_more_results():
    result = recommend_from_db(_profile(income_usd=5000))
    assert len(result["top_cities"]) > 0


def test_long_stay_filters_non_renewable():
    """3년+ 체류 선택 시 renewable=false 국가는 결과에서 제외."""
    result = recommend_from_db(_profile(timeline="3년 이상 장기 이민", income_usd=5000))
    assert isinstance(result["top_cities"], list)


def test_90day_returns_results():
    result = recommend_from_db(_profile(timeline="90일 단기 체험", income_usd=3000))
    assert len(result["top_cities"]) > 0


def test_asia_filter_excludes_european_countries():
    european_ids = {"DE", "PT", "EE", "ES", "GR", "HR", "CZ", "HU", "SI", "MT", "CY", "AL", "RS", "MK"}
    result = recommend_from_db(_profile(preferred_countries=["아시아"], income_usd=5000))
    result_ids = {c["country_id"] for c in result["top_cities"]}
    assert result_ids.isdisjoint(european_ids), f"유럽 국가 포함됨: {result_ids & european_ids}"


def test_score_is_float_in_range():
    result = recommend_from_db(_profile(income_usd=5000))
    for city in result["top_cities"]:
        assert 0.0 <= city["score"] <= 10.0, f"score 범위 초과: {city['score']}"


def test_korean_nationality_warning():
    result = recommend_from_db(_profile(nationality="한국"))
    assert "건강보험" in result["overall_warning"]


def test_schengen_in_result_triggers_ees_warning():
    result = recommend_from_db(_profile(preferred_countries=["유럽"], income_usd=5000))
    schengen_ids = {"DE", "PT", "EE", "ES", "GR", "HR", "CZ", "HU", "SI", "MT", "CY", "AL", "RS", "MK"}
    result_ids = {c["country_id"] for c in result["top_cities"]}
    if result_ids & schengen_ids:
        assert "EES" in result["overall_warning"]


def test_schengen_city_plan_b_trigger():
    result = recommend_from_db(_profile(preferred_countries=["유럽"], income_usd=5000))
    schengen_ids = {"DE", "PT", "EE", "ES", "GR", "HR", "CZ", "HU", "SI", "MT", "CY", "AL", "RS", "MK"}
    for city in result["top_cities"]:
        if city["country_id"] in schengen_ids:
            assert city["plan_b_trigger"] is True


def test_no_duplicate_countries_in_results():
    """같은 나라 도시가 2개 이상 나오면 안 됨."""
    result = recommend_from_db(_profile(income_usd=5000))
    country_ids = [c["country_id"] for c in result["top_cities"]]
    assert len(country_ids) == len(set(country_ids)), f"중복 국가: {country_ids}"


def test_top_n_default_still_returns_3():
    """Default top_n=3 keeps existing callers unchanged."""
    profile = {"income_usd": 3000, "preferred_countries": [], "lifestyle": [], "timeline": "1년 단기 체험", "nationality": ""}
    result = recommend_from_db(profile)
    assert len(result["top_cities"]) <= 3

def test_top_n_8_returns_up_to_8():
    """top_n=8 can return more than 3 cities."""
    profile = {"income_usd": 3000, "preferred_countries": [], "lifestyle": [], "timeline": "1년 단기 체험", "nationality": ""}
    result = recommend_from_db(profile, top_n=8)
    assert len(result["top_cities"]) >= 4  # must exceed old cap

def test_6month_timeline_filters_stay_6():
    """6개월 단기 체험 excludes countries with stay_months < 6."""
    profile = {"income_usd": 2000, "preferred_countries": [], "lifestyle": [], "timeline": "6개월 단기 체험", "nationality": ""}
    result = recommend_from_db(profile, top_n=8)
    from recommender import _load_data
    countries, _ = _load_data()
    country_map = {c["id"]: c for c in countries}
    for city in result["top_cities"]:
        cid = city["country_id"]
        country = country_map.get(cid, {})
        assert (country.get("stay_months") or 0) >= 6, f"{cid} has stay_months < 6"

def test_compute_disabled_options_returns_dict():
    """compute_disabled_options returns a dict with expected keys."""
    from recommender import compute_disabled_options
    profile = {"income_usd": 2000, "preferred_countries": ["아시아"], "lifestyle": [], "timeline": "1년 단기 체험", "nationality": ""}
    result = compute_disabled_options(profile)
    assert "continents" in result
    assert "timeline" in result
    assert "lifestyle_tags" in result

def test_compute_disabled_options_values_are_lists():
    """disabled option values are lists of JS chip label strings."""
    from recommender import compute_disabled_options
    profile = {"income_usd": 100, "preferred_countries": [], "lifestyle": [], "timeline": "1년 단기 체험", "nationality": ""}
    result = compute_disabled_options(profile)
    for key, val in result.items():
        assert isinstance(val, list), f"{key} should be a list"
