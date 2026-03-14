from unittest.mock import patch

FAKE_RAG_CONTEXT = "=== RAG 검색 결과 ===\n[1] 말레이시아 비자 정보..."
SAMPLE_PROFILE = {
    "nationality": "Korean",
    "income": 3000,
    "lifestyle": ["해변", "저물가"],
    "timeline": "1년 단기 체험",
}

def test_build_prompt_returns_list():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(SAMPLE_PROFILE)
        assert isinstance(result, list)

def test_build_prompt_starts_with_system():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(SAMPLE_PROFILE)
        assert result[0]["role"] == "system"

def test_build_prompt_ends_with_user():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(SAMPLE_PROFILE)
        assert result[-1]["role"] == "user"

def test_build_prompt_includes_rag_context():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(SAMPLE_PROFILE)
        last_user = result[-1]["content"]
        assert "RAG 검색 결과" in last_user

def test_build_prompt_includes_user_profile():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(SAMPLE_PROFILE)
        last_user = result[-1]["content"]
        assert "Korean" in last_user
        assert "3,000" in last_user
        assert "해변" in last_user

def test_build_prompt_rag_query_uses_profile():
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT) as mock_rag:
        from prompts.builder import build_prompt
        build_prompt(SAMPLE_PROFILE)
        call_args = mock_rag.call_args[0][0]
        assert "Korean" in call_args or "3000" in call_args
