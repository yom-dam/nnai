import os
from dotenv import load_dotenv
load_dotenv()

from api.hf_client        import query_model
from api.parser           import parse_response, format_result_markdown
from report.pdf_generator import generate_report
from rag.vector_store     import build_index
from prompts.builder      import build_prompt
from ui.layout            import create_layout

# 앱 시작 시 RAG 인덱스 자동 초기화 (테스트 시 SKIP_RAG_INIT 환경변수로 건너뜀)
if not os.getenv("SKIP_RAG_INIT"):
    print("🔧 RAG 인덱스 초기화...")
    build_index(force=False)
    print("✅ RAG 준비 완료")


def nomad_advisor(nationality, income, lifestyle, timeline) -> tuple[str, str | None]:
    """핵심 파이프라인: RAG → 프롬프트 → Qwen3.5-27B → 파싱 → PDF"""
    user_profile = {
        "nationality": nationality,
        "income":      int(income),
        "lifestyle":   lifestyle if isinstance(lifestyle, list) else [lifestyle],
        "timeline":    timeline,
    }

    messages     = build_prompt(user_profile)
    raw_response = query_model(messages, max_tokens=2048)

    if raw_response.startswith("ERROR"):
        return f"⚠️ API 오류: {raw_response}", None

    parsed          = parse_response(raw_response)
    markdown_output = format_result_markdown(parsed)
    pdf_path        = generate_report(parsed, user_profile)

    return markdown_output, pdf_path


if __name__ == "__main__":
    demo = create_layout(nomad_advisor)
    demo.launch()
