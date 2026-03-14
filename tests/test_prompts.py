import json
from prompts.system    import SYSTEM_PROMPT
from prompts.few_shots import FEW_SHOT_EXAMPLES

def test_system_prompt_is_string():
    assert isinstance(SYSTEM_PROMPT, str)
    assert "JSON" in SYSTEM_PROMPT

def test_few_shots_format():
    assert isinstance(FEW_SHOT_EXAMPLES, list)
    assert len(FEW_SHOT_EXAMPLES) >= 4  # user+assistant 2쌍 = 4 메시지
    for msg in FEW_SHOT_EXAMPLES:
        assert "role" in msg
        assert "content" in msg
        assert msg["role"] in ("user", "assistant")

def test_few_shots_assistant_is_valid_json():
    for msg in FEW_SHOT_EXAMPLES:
        if msg["role"] == "assistant":
            parsed = json.loads(msg["content"])
            assert "top_cities" in parsed
            assert "overall_warning" in parsed

def test_few_shots_pairs():
    """user → assistant 쌍 순서 확인"""
    roles = [m["role"] for m in FEW_SHOT_EXAMPLES]
    for i in range(0, len(roles) - 1, 2):
        assert roles[i] == "user"
        assert roles[i+1] == "assistant"
