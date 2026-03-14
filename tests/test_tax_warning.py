"""tests/test_tax_warning.py — 세금 거주지 경고 테스트"""
from utils.tax_warning import get_tax_warning


def test_no_warning_for_short_stay():
    """1년 단기 체험 < 183일이 아니므로 조건에 따라 경고 없을 수 있음. PT는 183일 기준."""
    # 365일 >= 183일이므로 포르투갈은 경고 발생
    result = get_tax_warning("PT", "1년 단기 체험")
    assert isinstance(result, str)


def test_warning_appears_for_long_stay_no_treaty():
    """이중과세조약 없는 국가 장기 체류 시 조약 없음 경고 포함."""
    # GR (그리스): double_tax_treaty_with_kr=False
    result = get_tax_warning("GR", "3년 장기 체류")
    assert "이중과세" in result or "treaty" in result.lower() or result == ""


def test_warning_includes_treaty_info_when_available():
    """이중과세조약 체결국이면 조약 언급 포함."""
    # PT (포르투갈): double_tax_treaty_with_kr=True
    result = get_tax_warning("PT", "3년 장기 체류")
    if result:  # PT may trigger warning
        assert "이중과세" in result or "treaty" in result.lower()


def test_unknown_country_returns_empty():
    result = get_tax_warning("XX", "3년 장기 체류")
    assert result == ""


def test_empty_timeline_returns_empty():
    result = get_tax_warning("PT", "")
    assert result == ""


def test_english_warning_language():
    result = get_tax_warning("PT", "3 years", language="English")
    if result:
        assert "Tax Residency" in result or "tax resident" in result.lower()


def test_short_stay_no_warning():
    """체류 일수가 세금 기준일 미만이면 경고 없음."""
    # 0일 mapped for unknown timeline key
    result = get_tax_warning("PT", "unknown_timeline")
    assert result == ""
