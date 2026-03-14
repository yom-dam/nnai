from prompts.system    import SYSTEM_PROMPT
from prompts.few_shots import FEW_SHOT_EXAMPLES
from rag.retriever     import retrieve_as_context


def build_prompt(user_profile: dict) -> list[dict]:
    nationality = user_profile.get("nationality", "Korean")
    income      = user_profile.get("income", 3000)
    lifestyle   = user_profile.get("lifestyle", [])
    timeline    = user_profile.get("timeline", "1년 단기 체험")

    rag_query = (
        f"{nationality} 디지털 노마드 월 소득 ${income} "
        f"라이프스타일 {' '.join(lifestyle)} {timeline} 비자 도시 추천"
    )
    rag_context = retrieve_as_context(rag_query, top_k=6)

    user_message = f"""국적: {nationality}
월 수입: ${income:,} USD
라이프스타일: {', '.join(lifestyle) if lifestyle else '특별한 선호 없음'}
목표 기간: {timeline}

{rag_context}

위 프로필과 RAG 데이터를 기반으로 최적의 디지털 노마드 거주 도시 3곳을 추천하세요.
반드시 순수 JSON만 출력하세요. 코드 블록이나 설명 문장 없이 JSON만."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(FEW_SHOT_EXAMPLES)
    messages.append({"role": "user", "content": user_message})

    return messages
