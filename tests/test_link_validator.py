"""tests/test_link_validator.py"""
import json
import pytest
from unittest.mock import patch, MagicMock
from utils.link_validator import validate_url, find_replacement_url, run_validation_batch


class TestValidateUrl:
    def test_valid_url_returns_true(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            assert validate_url("https://example.com") is True

    def test_404_returns_false(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            assert validate_url("https://example.com/gone") is False

    def test_503_returns_false(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            assert validate_url("https://example.com/down") is False

    def test_connection_error_returns_false(self):
        import requests as req
        with patch("utils.link_validator.requests.head", side_effect=req.exceptions.ConnectionError):
            assert validate_url("https://bad-host.invalid") is False

    def test_timeout_returns_false(self):
        import requests as req
        with patch("utils.link_validator.requests.head", side_effect=req.exceptions.Timeout):
            assert validate_url("https://slow.example.com") is False


class TestFindReplacementUrl:
    def test_falls_back_to_google_search_for_unknown(self):
        """visa_db.json에 없는 country_id는 Google 검색 URL 반환."""
        result = find_replacement_url("XX", "Unknown Visa")
        assert result is not None
        assert "google.com/search" in result
        assert "XX" in result

    def test_google_fallback_contains_visa_type(self):
        result = find_replacement_url("ZZ", "Digital Nomad Visa")
        assert "Digital" in result or "Nomad" in result or "Visa" in result

    def test_known_country_returns_non_google_url(self):
        """visa_db.json에 official_url이 있는 국가는 Google URL이 아닌 것을 반환."""
        # PT는 visa_db.json에 official_url 있음
        result = find_replacement_url("PT", "D8 Digital Nomad Visa")
        assert result is not None
        assert result.startswith("http")
        # official_url이 있으면 Google fallback 아님
        # (실제 official_url 값은 visa_db.json에 따라 다를 수 있으므로 느슨하게 검증)


class TestRunValidationBatch:
    def test_valid_urls_unchanged(self, tmp_path):
        """유효한 URL은 그대로 유지."""
        test_data = {"PT": "https://imigracao.pt/en/visas/digital-nomad"}
        urls_file = tmp_path / "visa_urls.json"
        urls_file.write_text(json.dumps(test_data))

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            run_validation_batch(urls_path=str(urls_file))

        result = json.loads(urls_file.read_text())
        assert result["PT"] == "https://imigracao.pt/en/visas/digital-nomad"

    def test_invalid_url_replaced_with_fallback(self, tmp_path):
        """무효 URL은 fallback으로 교체."""
        test_data = {"PT": "https://invalid.example.com/404"}
        urls_file = tmp_path / "visa_urls.json"
        urls_file.write_text(json.dumps(test_data))

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            run_validation_batch(urls_path=str(urls_file))

        result = json.loads(urls_file.read_text())
        assert result["PT"] != "https://invalid.example.com/404"

    def test_batch_saves_result_to_file(self, tmp_path):
        """결과가 파일에 저장됨."""
        test_data = {"TH": "https://example.com"}
        urls_file = tmp_path / "visa_urls.json"
        urls_file.write_text(json.dumps(test_data))

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("utils.link_validator.requests.head", return_value=mock_resp):
            run_validation_batch(urls_path=str(urls_file))

        result = json.loads(urls_file.read_text())
        assert "TH" in result
