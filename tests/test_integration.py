"""
통합 테스트 — 실제 API 호출 없이 전체 파이프라인 검증
"""
import os, json
from unittest.mock import patch

FAKE_JSON_RESPONSE = json.dumps({
    "top_cities": [
        {"city": "Chiang Mai", "country": "Thailand",
         "visa_type": "LTR", "monthly_cost": 1100, "score": 9,
         "why": "저렴하고 노마드 많음"}
    ],
    "visa_checklist": ["여권 확인"],
    "budget_breakdown": {"rent": 500, "food": 300, "cowork": 100, "misc": 200},
    "first_steps": ["여권 갱신"]
})

def test_nomad_advisor_pipeline(tmp_path, monkeypatch):
    """mock API + mock RAG → 마크다운 문자열 + PDF 경로 반환"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HF_TOKEN", "dummy")

    with patch("rag.vector_store.build_index"), \
         patch("prompts.builder.retrieve_as_context", return_value="RAG context"), \
         patch("api.hf_client.query_model", return_value=FAKE_JSON_RESPONSE):
        import importlib, app
        importlib.reload(app)
        md, pdf_path = app.nomad_advisor(
            nationality="Korean",
            income=3000,
            lifestyle=["해변", "저물가"],
            timeline="1년 단기 체험"
        )
        assert isinstance(md, str)
        assert "Chiang Mai" in md
        assert pdf_path is not None
        assert os.path.exists(pdf_path)

def test_nomad_advisor_api_error(tmp_path, monkeypatch):
    """API 오류 시 오류 메시지 반환, PDF는 None"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HF_TOKEN", "dummy")

    with patch("rag.vector_store.build_index"), \
         patch("prompts.builder.retrieve_as_context", return_value="RAG context"), \
         patch("api.hf_client.query_model", return_value="ERROR: timeout"):
        import importlib, app
        importlib.reload(app)
        md, pdf_path = app.nomad_advisor("Korean", 3000, ["해변"], "1년 단기 체험")
        assert "오류" in md or "ERROR" in md
        assert pdf_path is None
