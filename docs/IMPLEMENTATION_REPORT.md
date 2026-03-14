# NomadNavigator AI — 구현 보고서

> 작성일: 2026-03-14
> 배포 URL: https://huggingface.co/spaces/flexxiblethinking/nomad-navigator-ai

---

## 1. 프로젝트 개요

디지털 노마드를 위한 AI 기반 이민 설계 서비스.
국적·월 수입·라이프스타일·목표 기간을 입력하면 **RAG + Qwen3.5-27B**가 최적의 거주 도시 TOP 3, 비자 체크리스트, 예산 시뮬레이션을 JSON으로 생성하고 PDF 리포트를 즉시 다운로드할 수 있다.

---

## 2. 기술 스택

| 영역 | 기술 |
|------|------|
| LLM | Qwen/Qwen3.5-27B (HuggingFace Inference Providers) |
| LLM API | `openai.OpenAI` → `router.huggingface.co/v1` |
| 임베딩 | BAAI/bge-m3 (1024차원, 다국어, L2 정규화) |
| 벡터 DB | FAISS IndexFlatIP (코사인 유사도) |
| 프레임워크 | Gradio 6.x |
| PDF | ReportLab 4.x |
| 테스트 | pytest 9.x + pytest-mock |
| 환경 | Python 3.13, HuggingFace Spaces (CPU) |

---

## 3. 프로젝트 구조

```
nomad-navigator-ai/
├── app.py                    ← 진입점: RAG 초기화 + nomad_advisor 파이프라인
├── requirements.txt
├── pytest.ini
├── .env.example
│
├── api/
│   ├── hf_client.py          ← HF Router 연결 + Qwen3.5-27B 호출
│   └── parser.py             ← JSON 파싱 + 마크다운 포맷터
│
├── rag/
│   ├── embedder.py           ← BGE-M3 임베딩 (HF InferenceClient)
│   ├── vector_store.py       ← FAISS 인덱스 빌드·저장·로드
│   ├── retriever.py          ← 쿼리 → top-k 청크 검색
│   └── build_index.py        ← CLI 빌드 스크립트
│
├── prompts/
│   ├── system.py             ← JSON 출력 강제 시스템 프롬프트
│   ├── few_shots.py          ← 2쌍의 OpenAI messages 형식 예시
│   └── builder.py            ← RAG 컨텍스트 주입 + messages 조합
│
├── report/
│   └── pdf_generator.py      ← ReportLab A4 PDF 생성
│
├── ui/
│   ├── theme.py              ← Gradio Soft 커스텀 테마
│   └── layout.py             ← Blocks 레이아웃 (입력 패널 + 결과 패널)
│
├── data/
│   ├── visa_db.json          ← 12개국 비자 정보
│   └── city_scores.json      ← 20개 도시 점수
│
└── tests/
    ├── conftest.py
    ├── test_data_schema.py
    ├── test_hf_client.py
    ├── test_parser.py
    ├── test_embedder.py
    ├── test_vector_store.py
    ├── test_retriever.py
    ├── test_prompts.py
    ├── test_builder.py
    ├── test_pdf_generator.py
    ├── test_ui.py
    └── test_integration.py
```

---

## 4. 핵심 파이프라인

```
유저 입력 (국적, 소득, 라이프스타일, 기간)
        ↓
[prompts/builder.py] RAG 쿼리 생성
        ↓
[rag/retriever.py] BGE-M3 쿼리 임베딩 → FAISS 검색 → top-6 청크
        ↓
[prompts/builder.py] System + Few-shots + RAG 컨텍스트 + 유저 프로필 → messages 리스트
        ↓
[api/hf_client.py] Qwen3.5-27B 호출 (HF Router via OpenAI SDK)
        ↓
[api/parser.py] JSON 파싱 → 마크다운 포맷
        ↓
[report/pdf_generator.py] ReportLab PDF 생성
        ↓
결과 (마크다운 표시 + PDF 다운로드)
```

---

## 5. 데이터 레이어

### 5-1. visa_db.json — 12개국

| ID | 국가 | 비자 종류 | 최소 월 소득 |
|----|------|-----------|-------------|
| MY | 말레이시아 | DE Nomad Visa | $2,400 |
| PT | 포르투갈 | D8 Digital Nomad Visa | $3,280 |
| TH | 태국 | LTR Visa | $80,000/년 |
| EE | 에스토니아 | Digital Nomad Visa | $4,500 |
| ES | 스페인 | Startup Law Nomad Visa | $2,763 |
| ID | 인도네시아 | E33G Social Visit Visa | $2,000 |
| DE | 독일 | Freiberufler Visa | $3,500 |
| GE | 조지아 | Remotely from Georgia | $2,000 |
| CR | 코스타리카 | Rentista / Nomad Visa | $3,000 |
| GR | 그리스 | Digital Nomad Visa | $3,500 |
| PH | 필리핀 | Tourist Visa 연장 | $2,000 |
| VN | 베트남 | E-Visa (90일) | $1,500 |

각 국가 항목: `id`, `name`, `name_kr`, `visa_type`, `min_income_usd`, `stay_months`, `renewable`, `key_docs` (≥2개), `visa_fee_usd`, `tax_note`, `cost_tier`, `notes`, `source`

### 5-2. city_scores.json — 20개 도시

쿠알라룸푸르, 페낭, 리스본, 포르투, 치앙마이, 방콕, 탈린, 바르셀로나, 마드리드, 발리(짱구), 베를린, 트빌리시, 산호세, 타마린도, 아테네, 헤라클리온, 마닐라, 세부, 하노이, 호치민

각 도시 항목: `id`, `city`, `city_kr`, `country`, `country_id`, `monthly_cost_usd`, `internet_mbps`, `safety_score`, `english_score`, `nomad_score`, `climate`, `cowork_usd_month`

### RAG 청크 구성

| 소스 | 청크 방식 | 청크 수 |
|------|-----------|---------|
| visa_db.json | 국가별 비자 기본정보 + 서류목록 (2개/국가) | 24개 |
| city_scores.json | 도시별 1개 | 20개 |
| **합계** | | **44개** |

---

## 6. 모듈별 구현 상세

### api/hf_client.py

- `query_model(messages, max_tokens=2048) -> str`
  - `openai.OpenAI(base_url="https://router.huggingface.co/v1")` 사용
  - `temperature=0.3`, `thinking=False` → 안정적 JSON 출력
  - `<think>...</think>` 블록 자동 제거 (정규식)
  - 예외 시 `"ERROR: ..."` 반환 (앱 크래시 없음)
- `query_model_with_thinking(messages, max_tokens=4096) -> tuple[str, str]`
  - thinking 모드 활성화 버전 (고급 추론용)

### api/parser.py

- `parse_response(raw_text) -> dict`
  - ①  ` ```json ... ``` ` 코드 블록 추출 시도
  - ② `{ ... }` 패턴 추출 (길이 내림차순)
  - ③ 두 방법 모두 실패 시 fallback dict 반환 (앱 중단 없음)
- `format_result_markdown(data) -> str`
  - TOP 3 도시, 비자 체크리스트, 예산 테이블, 실행 스텝 마크다운 렌더링

### rag/embedder.py

- `embed_texts(texts) -> np.ndarray` — shape: `(N, 1024)`, dtype: `float32`
- `embed_query(query) -> np.ndarray` — shape: `(1024,)`
- HF InferenceClient `feature_extraction` 사용 (토큰 512 절단)
- L2 정규화 → 코사인 유사도 검색 준비

### rag/vector_store.py

- `build_index(force=False)` — 청크 생성 → 임베딩 → `IndexFlatIP` → `.faiss` + `.pkl` 저장
- `load_index()` — 저장된 인덱스 + 문서 리스트 로드
- 인덱스 파일 존재 시 스킵 (Space 재시작 비용 절감)

### rag/retriever.py

- `retrieve(query, top_k=6) -> list[dict]` — 쿼리 임베딩 → FAISS 검색 → score 포함 결과
- `retrieve_as_context(query, top_k=6) -> str` — 프롬프트 주입용 포맷 문자열

### prompts/system.py + few_shots.py

- SYSTEM_PROMPT: 순수 JSON 출력 강제, 스키마 명시, RAG 데이터 최우선 지시
- FEW_SHOT_EXAMPLES: OpenAI messages 형식 2쌍 (저소득 동남아 / 고소득 유럽)

### prompts/builder.py

- `build_prompt(user_profile) -> list[dict]`
  - RAG 쿼리: `"{nationality} 디지털 노마드 월 소득 ${income} 라이프스타일 ... 비자 도시 추천"`
  - 반환 형식: `[system, user(few-shot), assistant, user(few-shot), assistant, user(실제)]`

### report/pdf_generator.py

- `generate_report(parsed, user_profile) -> str` — `reports/nomad_report_YYYYMMDD_HHMMSS.pdf`
- ReportLab A4, 커스텀 색상(#0C447C), 테이블 스타일 포함

### ui/theme.py + layout.py

- `create_theme()` — Gradio Soft 테마, blue/indigo 배색, Inter 폰트
- `create_layout(advisor_fn)` — 좌측 입력 패널 (Dropdown, Slider, CheckboxGroup, Radio, Button) + 우측 결과 패널 (Markdown, File)

---

## 7. 테스트 결과

**실행일**: 2026-03-14
**환경**: Python 3.13.4, pytest 9.0.2

```
============================= test session starts ==============================
platform darwin -- Python 3.13.4, pytest-9.0.2
rootdir: nomad-navigator-ai
configfile: pytest.ini

collected 41 items

tests/test_builder.py::test_build_prompt_returns_list              PASSED
tests/test_builder.py::test_build_prompt_starts_with_system        PASSED
tests/test_builder.py::test_build_prompt_ends_with_user            PASSED
tests/test_builder.py::test_build_prompt_includes_rag_context      PASSED
tests/test_builder.py::test_build_prompt_includes_user_profile     PASSED
tests/test_builder.py::test_build_prompt_rag_query_uses_profile    PASSED
tests/test_data_schema.py::test_visa_db_has_12_countries           PASSED
tests/test_data_schema.py::test_visa_db_schema                     PASSED
tests/test_data_schema.py::test_visa_db_income_positive            PASSED
tests/test_data_schema.py::test_visa_db_key_docs_nonempty          PASSED
tests/test_data_schema.py::test_city_scores_has_at_least_10        PASSED
tests/test_data_schema.py::test_city_scores_schema                 PASSED
tests/test_data_schema.py::test_city_scores_range                  PASSED
tests/test_data_schema.py::test_city_country_id_exists_in_visa_db  PASSED
tests/test_embedder.py::test_embed_texts_returns_correct_shape     PASSED
tests/test_embedder.py::test_embed_texts_is_l2_normalized          PASSED
tests/test_embedder.py::test_embed_query_returns_1d                PASSED
tests/test_hf_client.py::test_query_model_returns_string           PASSED
tests/test_hf_client.py::test_query_model_strips_think_blocks      PASSED
tests/test_hf_client.py::test_query_model_returns_error_on_exception PASSED
tests/test_hf_client.py::test_query_model_with_thinking_returns_tuple PASSED
tests/test_integration.py::test_nomad_advisor_pipeline             PASSED
tests/test_integration.py::test_nomad_advisor_api_error            PASSED
tests/test_parser.py::test_parse_pure_json                         PASSED
tests/test_parser.py::test_parse_code_block_json                   PASSED
tests/test_parser.py::test_parse_failure_returns_fallback          PASSED
tests/test_parser.py::test_format_result_markdown_contains_sections PASSED
tests/test_parser.py::test_format_result_markdown_budget_sum       PASSED
tests/test_pdf_generator.py::test_generate_report_creates_pdf      PASSED
tests/test_pdf_generator.py::test_generate_report_pdf_nonempty     PASSED
tests/test_prompts.py::test_system_prompt_is_string                PASSED
tests/test_prompts.py::test_few_shots_format                       PASSED
tests/test_prompts.py::test_few_shots_assistant_is_valid_json      PASSED
tests/test_prompts.py::test_few_shots_pairs                        PASSED
tests/test_retriever.py::test_retrieve_returns_list_of_dicts       PASSED
tests/test_retriever.py::test_retrieve_as_context_returns_string   PASSED
tests/test_ui.py::test_create_theme_returns_gradio_theme           PASSED
tests/test_ui.py::test_create_layout_returns_blocks                PASSED
tests/test_ui.py::test_create_layout_has_correct_inputs            PASSED
tests/test_vector_store.py::test_build_and_load_index              PASSED
tests/test_vector_store.py::test_build_index_skip_if_exists        PASSED

======================== 41 passed, 5 warnings in 1.71s ========================
```

### 테스트 파일별 커버리지

| 테스트 파일 | 검증 대상 | 테스트 수 | 결과 |
|-------------|-----------|----------|------|
| test_data_schema.py | visa_db/city_scores JSON 스키마 | 8 | ✅ 전체 통과 |
| test_hf_client.py | HF Router 호출, think 블록 제거, 에러 처리 | 4 | ✅ 전체 통과 |
| test_parser.py | JSON 파싱 3가지 케이스, 마크다운 포맷 | 5 | ✅ 전체 통과 |
| test_embedder.py | 임베딩 shape, L2 정규화, 1D 반환 | 3 | ✅ 전체 통과 |
| test_vector_store.py | 인덱스 빌드/로드, 스킵 조건 | 2 | ✅ 전체 통과 |
| test_retriever.py | top-k 검색, 컨텍스트 문자열 반환 | 2 | ✅ 전체 통과 |
| test_prompts.py | 시스템 프롬프트, few-shot 형식/JSON 유효성 | 4 | ✅ 전체 통과 |
| test_builder.py | messages 형식, RAG 주입, 프로필 포함 | 6 | ✅ 전체 통과 |
| test_pdf_generator.py | PDF 생성 여부, 파일 크기 | 2 | ✅ 전체 통과 |
| test_ui.py | 테마 타입, Blocks 반환, 필수 컴포넌트 | 3 | ✅ 전체 통과 |
| test_integration.py | end-to-end 파이프라인, API 에러 핸들링 | 2 | ✅ 전체 통과 |
| **합계** | | **41** | **✅ 41/41** |

### 테스트 설계 원칙

- **모든 외부 의존성 Mock 처리**: HF API, FAISS 인덱스, RAG 검색 모두 `unittest.mock`으로 격리
- **TDD 방식**: 각 모듈 구현 전 테스트 작성 → FAIL 확인 → 구현 → PASS 확인
- **conftest.py**: `autouse` fixture로 모든 테스트에 `HF_TOKEN=hf_test_dummy_token` 자동 주입

---

## 8. 커밋 히스토리

| 커밋 | 메시지 |
|------|--------|
| `fbcc3ee` | fix: use valid HF Space color (indigo) |
| `1c1136e` | docs: update README for HF Space deployment |
| `510cfb9` | feat: integrate all modules in app.py with end-to-end pipeline |
| `6f3312b` | feat: add Gradio theme and layout UI |
| `c638b6d` | feat: add PDF report generator using ReportLab |
| `eff0465` | feat: add prompt engineering (system prompt, few-shots, RAG builder) |
| `6651dd3` | feat: add RAG pipeline (BGE-M3 embeddings + FAISS IndexFlatIP) |
| `43f127f` | feat: add HF client (Qwen3.5-27B via HF Router) and JSON parser |
| `143e262` | feat: add visa_db (12 countries) and city_scores (20 cities) with schema tests |
| `e9cb973` | chore: project bootstrap — deps, gitignore, test scaffold |

---

## 9. 배포

| 항목 | 내용 |
|------|------|
| 플랫폼 | HuggingFace Spaces |
| Space URL | https://huggingface.co/spaces/flexxiblethinking/nomad-navigator-ai |
| SDK | Gradio 6.9.0 |
| 환경변수 | `HF_TOKEN` (Repository Secret 등록 완료) |
| RAG 인덱스 | 앱 최초 실행 시 `build_index()` 자동 호출 |

### 배포 시 동작 순서

1. HF Space 빌드 → `requirements.txt` 패키지 설치
2. `app.py` 실행 → `build_index(force=False)` 호출
3. BGE-M3로 44개 청크 임베딩 → `rag/index.faiss` + `rag/documents.pkl` 생성
4. `✅ RAG 준비 완료` 로그 출력
5. Gradio 앱 서빙 시작

---

## 10. 알려진 이슈 / 향후 개선 사항

| 구분 | 내용 |
|------|------|
| Warning | Gradio 6.0에서 `theme`, `css` 파라미터를 `Blocks()` 대신 `launch()`로 이동 권고 |
| 데이터 | 태국 LTR Visa `min_income_usd: 80000` — 실제 연 소득 기준이나 월 소득 필드에 저장됨 (주석 필요) |
| 성능 | BGE-M3 임베딩이 첫 실행 시 순차 처리 (배치 처리로 개선 가능) |
| 확장 | 국가·도시 데이터 추가 시 `build_index(force=True)` 재실행 필요 |
