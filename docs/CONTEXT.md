# NomadNavigator AI — 프로젝트 컨텍스트 문서

**최종 업데이트**: 2026-03-14
**현재 브랜치**: `main`
**테스트 상태**: 75/75 통과

---

## 프로젝트 개요

**NomadNavigator AI**는 한국인 디지털 노마드를 위한 AI 이민 설계 서비스입니다.
국적 · 소득 · 라이프스타일을 입력하면 RAG 기반으로 최적 거주 도시 TOP 3를 추천하고, 비자 체크리스트와 예산이 담긴 PDF 리포트를 생성합니다.

**배포 위치**
- `family-hackathon/nnai` HF Space: `https://huggingface.co/spaces/family-hackathon/nnai`
- `flexxiblethinking/nomad-navigator-ai` HF Space
- 로컬 경로: `/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai`

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| UI | Gradio 6.9 (`gr.Blocks`, `gr.Tabs`) |
| LLM | Gemini 2.5 Flash (OpenAI 호환 엔드포인트) |
| 임베딩 | Gemini `gemini-embedding-001` (REST API, 3072-dim) |
| 벡터 DB | FAISS (`IndexFlatIP`) |
| PDF | ReportLab + NanumGothic TTF |
| 환율 | 실시간 환율 API (`utils/currency.py`) |

---

## 환경 변수

**로컬 `.env`** (gitignore됨):
```
HUGGINGFACE_TOKEN=<로컬 .env 파일에서 확인>
GEMINI_API_KEY=<로컬 .env 파일에서 확인>
```

**HF Space Secrets** (양쪽 Space 모두 설정 완료):
- `GEMINI_API_KEY` — LLM(Gemini 2.5 Flash) + 임베딩(gemini-embedding-001) 공용

**테스트 실행 시**:
```bash
SKIP_RAG_INIT=1 python -m pytest tests/ -v
```

---

## 파일 구조

```
nnai/
├── app.py                      # 진입점. nomad_advisor(), show_city_detail()
├── api/
│   ├── hf_client.py            # LLM 클라이언트 (Gemini 2.5 Flash, OpenAI SDK)
│   └── parser.py               # JSON 파싱 + 마크다운 포맷 + 자동 검색 링크
├── prompts/
│   ├── builder.py              # Step1/Step2 프롬프트 빌더 (RAG + preferred_countries)
│   ├── system.py               # 시스템 프롬프트
│   └── few_shots.py            # Few-shot 예시
├── rag/
│   ├── embedder.py             # Gemini embedding-001 REST API
│   ├── vector_store.py         # FAISS 인덱스 빌드/로드
│   └── retriever.py            # 유사도 검색 → 컨텍스트 문자열
├── ui/
│   ├── layout.py               # Gradio Tabs UI (Tab1: 추천, Tab2: 상세가이드)
│   └── theme.py                # Gradio 테마
├── report/
│   └── pdf_generator.py        # ReportLab PDF (NanumGothic 한글 폰트)
├── data/
│   ├── visa_db.json            # 12개국 비자 데이터
│   └── city_scores.json        # 20개 도시 점수 데이터
├── assets/
│   └── fonts/NanumGothic.ttf   # 한글 PDF 폰트
├── tests/                      # 75개 테스트 (모두 통과)
└── requirements.txt
```

---

## 핵심 아키텍처: 2단계 파이프라인

### Step 1 — 도시 추천 (`nomad_advisor()`)
```
사용자 입력 → KRW→USD 환율 변환 → RAG 검색(top_k=6) →
프롬프트 빌드(preferred_countries 힌트 포함) →
Gemini 2.5 Flash → JSON 파싱 → 마크다운 포맷 → 추천 TOP 3
```

### Step 2 — 상세 가이드 (`show_city_detail()`)
```
선택 도시 → 상세 프롬프트 빌드 → Gemini 2.5 Flash →
JSON 파싱 → 마크다운 포맷 + PDF 생성(NanumGothic)
```

---

## 주요 컴포넌트 상세

### `api/hf_client.py`
- `MODEL_ID = "gemini-2.5-flash"`
- OpenAI SDK + Gemini base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- `query_model(messages, max_tokens)` → 문자열 (오류 시 `"ERROR: ..."`)
- `<think>...</think>` 블록 자동 제거

### `rag/embedder.py`
- `EMBED_MODEL = "models/gemini-embedding-001"` (3072-dim)
- REST API 직접 호출: `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent`
- `embed_texts(texts)` → `(N, 3072)` float32, L2 정규화
- `embed_query(query)` → `(3072,)` float32

> **중요**: 인덱스 파일(`rag/index.faiss`, `rag/documents.pkl`)은 `.gitignore`에 포함됨.
> HF Space 최초 기동 시 Gemini API로 자동 빌드 (44청크, ~30초).
> `SKIP_RAG_INIT=1` 환경변수로 빌드 건너뜀 (테스트용).

### `api/parser.py`
- `parse_response(raw)` → dict (JSON 추출, 실패 시 빈 dict)
- `format_step1_markdown(parsed)` — `source_url=None`이면 Google/YouTube 자동 링크 생성
- `format_step2_markdown(parsed)` — 이민 가이드 섹션 포맷

### `prompts/builder.py`
- `build_prompt(user_profile)` → messages list
  - `preferred_countries` 있으면 `"※ 우선 고려 국가: ..."` 힌트 삽입
  - 플래그 이모지 자동 제거: `"🇲🇾 말레이시아"` → `"말레이시아"`
- `build_detail_prompt(selected_city, user_profile)` → messages list

### `ui/layout.py`
- `COUNTRY_OPTIONS` — 12개국 (플래그 이모지 + 한국어명)
- `gr.Tabs()` 구조:
  - **Tab 0 "🔍 도시 추천"**: 입력 폼, preferred_countries 체크박스, 결과 패널, `btn_go_step2`(완료 후 노출)
  - **Tab 1 "📖 상세 가이드"**: 도시 선택, 가이드 출력, PDF 다운로드
- `run_step1()` — generator, yield 4개 값: `[step1_output, parsed_state, btn_go_step2, tabs]`
- `run_step2()` — generator, yield 2개 값: `[step2_output, output_pdf]`
- 탭 전환: `btn_go_step2.click(fn=lambda: gr.update(selected=1), outputs=[tabs])`

### `report/pdf_generator.py`
- `NanumGothic.ttf` 등록 (실패 시 Helvetica fallback)
- `parsed.get("selected_city", {})` 사용 (Step 2 단일 도시)
- 섹션: 선택 도시 상세, 비자 준비 체크리스트, 월 예산 브레이크다운, 첫 번째 실행 스텝

---

## RAG 데이터

**`data/visa_db.json`** — 12개국:
`MY, PT, TH, EE, ES, ID, DE, GE, CR, GR, PH, VN`

**`data/city_scores.json`** — 20개 도시:
쿠알라룸푸르, 코타키나발루, 리스본, 포르투, 치앙마이, 방콕, 탈린, 바르셀로나, 발리, 자카르타, 베를린, 함부르크, 트빌리시, 산호세, 아테네, 테살로니키, 세부, 다낭, 하노이, 호치민

**인덱스 구성** (총 44청크):
- `visa_{id}` × 12 — 비자 유형, 소득 기준, 체류 기간
- `docs_{id}` × 12 — 필수 서류 목록
- `city_{id}` × 20 — 도시 점수, 생활비, 기후

---

## LLM 응답 JSON 스키마

### Step 1 응답
```json
{
  "top_cities": [
    {
      "city": "Chiang Mai",
      "city_kr": "치앙마이",
      "country": "Thailand",
      "country_id": "TH",
      "visa_type": "LTR Visa",
      "visa_url": "https://...",
      "monthly_cost_usd": 1100,
      "score": 9,
      "reasons": [
        {"point": "...", "source_url": null}
      ],
      "realistic_warnings": ["..."]
    }
  ],
  "overall_warning": "..."
}
```

### Step 2 응답
```json
{
  "city": "Chiang Mai",
  "country_id": "TH",
  "immigration_guide": {
    "title": "...",
    "sections": [
      {"step": 1, "title": "...", "items": ["..."]}
    ]
  },
  "visa_checklist": ["..."],
  "budget_breakdown": {"rent": 0, "food": 0, "cowork": 0, "misc": 0},
  "first_steps": ["..."]
}
```

---

## Git 히스토리 (주요)

```
338f95c feat: replace HF embedding API with Gemini embedding-001 (fixes 402 error)
5f610ec fix: update Gemini model to gemini-2.5-flash
fbe8bdf feat: Korean PDF with NanumGothic font, selected_city section
a8fa85b feat: restructure UI into Tabs with loading indicators and country selector
02e9104 feat: add preferred_countries soft-hint to nomad_advisor and build_prompt
e2defa3 feat: auto-generate Google/YouTube search links when source_url is None
c432f4f fix: rename '한국어만 가능' to '한국어' in language options
29ac413 feat: v2 2단계 파이프라인 — 도시 추천 + 상세 이민 가이드
```

---

## 알려진 이슈 / 주의사항

1. **Gradio 6.0 경고**: `theme`, `css`를 `Blocks()` 생성자 대신 `launch()`에 전달해야 함 (현재 경고만 발생, 동작에 영향 없음)
2. **RAG 인덱스 빌드 시간**: HF Space 최초 기동 시 ~30초 소요 (44청크 × Gemini API)
3. **`SKIP_RAG_INIT=1`**: 테스트 시 반드시 설정 (RAG 빌드 스킵)
4. **인덱스 파일**: `rag/index.faiss`, `rag/documents.pkl`은 gitignore됨 — 로컬에는 빌드된 파일이 존재하나 커밋 불가 (HF Space가 바이너리 파일 거부)

---

## 로컬 실행

```bash
cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai"

# 의존성 설치
pip install -r requirements.txt

# 앱 실행 (RAG 인덱스 자동 빌드 포함)
python app.py

# 테스트
SKIP_RAG_INIT=1 python -m pytest tests/ -v
```

---

## Git 리모트

```
origin  https://huggingface.co/spaces/family-hackathon/nnai
hf      https://huggingface.co/spaces/flexxiblethinking/nomad-navigator-ai
```

푸시: `git push origin main && git push hf main`
