# CONTEXT.md — NomadNavigator AI

> **최종 업데이트**: 2026-03-18
> **기준 브랜치**: main
> **총 테스트**: 256 passed, 4 skipped
> **작성 방식**: 코드를 직접 읽고 사실만 기재 (추측 없음)

---

## 1. 프로젝트 개요

**NomadNavigator AI (NNAI)**
한국인 + 글로벌 디지털 노마드를 위한 AI 이민 설계 서비스.
소득·국적·라이프스타일·이민 동기를 입력하면 Gemini 2.5 Flash 기반으로
최적 거주 도시 TOP 3를 추천하고, 비자 체크리스트·예산·숙소·세금 경고를
마크다운으로 제공한다.

**로컬 경로**
```
/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai
```

**HF Space 배포 URL**
- `https://huggingface.co/spaces/family-hackathon/nnai` (origin)
- `https://huggingface.co/spaces/flexxiblethinking/nomad-navigator-ai` (hf)

**푸시 명령**
```bash
git push origin main
git push "https://flexxiblethinking:{HUGGINGFACE_TOKEN}@huggingface.co/spaces/flexxiblethinking/nomad-navigator-ai" main
```

---

## 2. 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| UI | Gradio ≥4.0 (`gr.Blocks`, `gr.Tabs`) | layout.py에서 구현 |
| LLM | Gemini 2.5 Flash | OpenAI 호환 엔드포인트 |
| LLM 캐싱 | Gemini 서버사이드 Context Caching | SYSTEM_PROMPT+DATA_CONTEXT+FEW_SHOTS (~7,500 tokens), TTL 1시간 |
| 컨텍스트 | 정적 텍스트 컨텍스트 (`prompts/data_context.py`) | visa_db.json + city_scores.json을 압축 텍스트로 변환해 LLM에 직접 전달. RAG(임베딩) 호출 없음 |
| 벡터 DB | FAISS (`rag/`) | 현재 미사용 (data_context.py로 대체), 코드는 유지 |
| 환율 | 실시간 API (`utils/currency.py`) | 실패 시 1 USD ≈ 1,400 KRW 폴백 |
| PDF | ❌ 제거됨 | test_pdf_generator.py 전체 skip 처리 |

---

## 3. 환경 변수

```bash
GEMINI_API_KEY        # LLM + Gemini Context Caching 공용
HUGGINGFACE_TOKEN     # hf remote 푸시 전용 (로컬 .env, gitignore)
SKIP_RAG_INIT=1       # 테스트 시 반드시 설정 (RAG 초기화 생략)
```

---

## 4. 파일 구조 (현재)

```
nnai/
├── CLAUDE.md                   # Claude Code 세션 지침 (핵심)
├── CONTEXT.md                  # ← 이 파일 (UI/UX 세션 진입점)
├── PLAN.md                     # PM 실행 계획
├── README.md
├── app.py                      # 진입점: nomad_advisor(), show_city_detail()
├── start.sh
├── pytest.ini
├── requirements.txt
│
├── api/
│   ├── hf_client.py            # Gemini 2.5 Flash 클라이언트 (OpenAI compat)
│   ├── parser.py               # JSON 파싱 + 마크다운 포맷 + 도시 비교 테이블
│   ├── schengen_calculator.py  # 쉥겐 90/180 롤링 윈도우 계산기
│   └── cache_manager.py        # Gemini 서버사이드 Context Caching 관리
│
├── prompts/
│   ├── builder.py              # build_prompt(), build_detail_prompt(), validate_user_profile()
│   ├── system.py               # 한국어 시스템 프롬프트 (Step 1 JSON 스키마 포함)
│   ├── system_en.py            # 영어 시스템 프롬프트
│   ├── few_shots.py            # Few-shot 예시
│   └── data_context.py         # visa_db.json + city_scores.json → 압축 텍스트 (모듈 로드 시 1회 빌드)
│
├── utils/
│   ├── currency.py             # get_exchange_rates() — 실시간 환율 조회
│   ├── persona.py              # diagnose_persona(), get_persona_hint() — 페르소나 진단
│   ├── tax_warning.py          # get_tax_warning() — 세금 거주지 경고 자동 생성
│   ├── planb.py                # get_planb_suggestions() — 쉥겐 소진 후 비쉥겐 버퍼 추천
│   ├── accommodation.py        # get_accommodation_links() — 중기 숙소 딥링크
│   └── link_validator.py       # 배포 전 URL 검증 CLI (런타임 미사용)
│
├── ui/
│   ├── layout.py               # create_layout(), check_income_warning(), check_companion_warning()
│   └── theme.py                # Gradio 테마
│
├── rag/                        # 현재 미사용 (data_context.py로 대체)
│   ├── embedder.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── build_index.py
│
├── data/
│   ├── visa_db.json            # 29개국 비자 데이터
│   ├── city_scores.json        # 50개 도시 점수 데이터
│   └── visa_urls.json          # 국가별 공식 비자 URL (parser.py에서 자동 주입)
│
├── docs/
│   ├── archive/                # 완료된 작업 문서 보관
│   └── superpowers/plans/      # 구현 계획서
│
├── reports/                    # 생성된 PDF 보관 (PDF 기능 제거됨, 기존 파일만 존재)
│
└── tests/
    ├── conftest.py
    ├── test_accommodation.py
    ├── test_builder.py
    ├── test_city_scores.py
    ├── test_currency.py
    ├── test_data_schema.py
    ├── test_embedder.py
    ├── test_hf_client.py
    ├── test_integration.py
    ├── test_link_validator.py
    ├── test_parser.py
    ├── test_pdf_generator.py   # 전체 skip (PDF 제거됨)
    ├── test_persona.py
    ├── test_planb.py
    ├── test_prompts.py
    ├── test_retriever.py
    ├── test_schengen_calculator.py
    ├── test_tax_warning.py
    ├── test_ui.py
    ├── test_vector_store.py
    └── test_visa_db.py
```

---

## 5. 핵심 아키텍처: 2단계 파이프라인

### Step 1 — 도시 추천 (`nomad_advisor()` in `app.py`)

```
사용자 입력 (UI)
→ 페르소나 진단 (utils/persona.py:diagnose_persona)
→ KRW → USD 환율 변환 (utils/currency.py)
→ 사전 검증 (prompts/builder.py:validate_user_profile)
    └─ hard_block 시: LLM 호출 없이 즉시 안내 메시지 반환
→ Gemini Context Cache 조회 (api/cache_manager.py)
    ├─ 캐시 히트: build_step1_user_message() → query_model_cached()
    └─ 캐시 미스: build_prompt() → query_model()
→ parse_response() — 3단계 파싱 (코드블록 → 정규식 → suffix 복구 → 폴백)
→ visa_url 자동 주입 (data/visa_urls.json)
→ user_profile 주입 (_user_profile 키)
→ format_step1_markdown()
    ├─ TOP 3 도시 카드 (USD + KRW 이중 통화)
    ├─ 세금 거주지 경고 (utils/tax_warning.py:get_tax_warning)
    ├─ 참고 자료 링크
    └─ 도시 비교 테이블 (api/parser.py:generate_comparison_table, city_scores.json)
→ 반환: (markdown_str, cities_list, parsed_dict)
```

### Step 2 — 상세 가이드 (`show_city_detail()` in `app.py`)

```
선택 도시 + user_profile (_user_profile 키)
→ build_detail_prompt() — 개인화 블록 조립
    ├─ 소득 증빙 유형별 힌트 (_INCOME_TYPE_GUIDE_HINTS)
    ├─ 체류 기간별 힌트 (_STAY_DURATION_GUIDE_HINTS)
    ├─ 동반 구성별 힌트 (_TRAVEL_TYPE_GUIDE_HINTS)
    └─ 출국 임박 단계: 건강보험 기한 경고 + 초보 여행 정보 제외
→ query_model() (max_tokens=6144)
→ parse_response()
→ format_step2_markdown()
    ├─ 단계별 정착 가이드
    ├─ 비자 체크리스트 (type defense: str/list[str]/list[dict])
    ├─ 예산 테이블 (rent/food/cowork/insurance/misc + Numbeo 출처 링크)
    ├─ 첫 번째 실행 스텝 (기한 있는 항목 최우선)
    ├─ 중기 숙소 딥링크 (utils/accommodation.py)
    └─ 플랜B 비쉥겐 버퍼 (쉥겐 국가 선택 시만, utils/planb.py)
→ 반환: markdown_str
```

### Step 0 — 쉥겐 계산기 (독립 모듈, UI Tab 2)

```
입출국 날짜 리스트 → api/schengen_calculator.py → 잔여일 + 리셋 날짜 + 경고
```
- 29개국 기준 (불가리아·루마니아·크로아티아 포함)
- 롤링 윈도우 방식 (과거 180일 중 체류 합산)

### 사전 경고 시스템 (입력 변경 시 즉시 반응)

```
소득/대륙/동반/기간 입력 변경
→ check_income_warning() (ui/layout.py)
    ├─ 유럽 + $2,849 미만: 소프트 경고
    ├─ 유럽 + $1,500 미만: 하드 경고 텍스트
    ├─ 유럽 + $1,000 미만 + 3년/5년: submit_warning + btn_step1 비활성화
    ├─ 중남미 + $1,000 미만: 소프트 경고
    ├─ 가족 전체 동반 + $3,000 미만: 소프트 경고
    └─ 90일 이하 선택: 정보 메시지
→ check_companion_warning() (ui/layout.py)
    └─ 배우자/가족 동반 + 소득 미입력: 합산 소득 기준 안내
```

---

## 6. 주요 컴포넌트 상세

### `app.py`
- `nomad_advisor(nationality, income_krw, immigration_purpose, lifestyle, languages, timeline, preferred_countries, preferred_language, persona_type, income_type, travel_type, children_ages, dual_nationality, readiness_stage, has_spouse_income, spouse_income_krw)` → `tuple[str, list, dict]`
- `show_city_detail(parsed_data, city_index)` → `str`

### `api/hf_client.py`
- `query_model(messages, max_tokens=2048)` → `str` — Gemini 2.5 Flash 호출, `<think>` 블록 자동 제거
- `query_model_cached(user_message, cache, max_tokens=8192)` → `str` — 서버사이드 캐시 활용

### `api/parser.py`
- `parse_response(raw_text)` → `dict` — 4단계 파싱 (코드블록→정규식→suffix 복구→폴백)
- `format_step1_markdown(data)` → `str`
- `format_step2_markdown(data, visa_data=None)` → `str`
- `generate_comparison_table(top_cities)` → `str` — 5점 척도 비교 테이블 (city_scores.json 참조)
- `format_result_markdown(data)` → `str` — 레거시 (현재 미사용)

### `api/schengen_calculator.py`
- `SCHENGEN_COUNTRIES: frozenset[str]` — 29개국 ISO-2 코드
- `calculate_remaining_days(trips)` — 롤링 윈도우 방식 잔여일 계산

### `api/cache_manager.py`
- `get_or_create_cache(system_prompt, data_context, few_shot_messages, cache_key)` — TTL 1시간, 만료 5분 전 갱신
- `invalidate(cache_key)` — 캐시 무효화

### `prompts/builder.py`
- `build_prompt(user_profile)` → `list[dict]` — Step 1 전체 메시지 조립 (사전 검증 포함)
- `build_step1_user_message(user_profile)` → `str` — 캐시 모드용 (동적 부분만)
- `build_detail_prompt(selected_city, user_profile)` → `list[dict]` — Step 2 메시지 조립
- `validate_user_profile(user_profile)` → `dict` — 규칙 기반 사전 검증 (`{"valid", "warnings", "hard_block"}`)

### `utils/persona.py`
- 5가지 페르소나: `schengen_loop`, `slow_nomad`, `fire_optimizer`, `burnout_escape`, `expat_freedom`
- `diagnose_persona(motivation, europe_plan, stay_duration, lifestyle, concerns)` → `str`
- `get_persona_hint(persona_type)` → `str`

### `utils/tax_warning.py`
- `get_tax_warning(country_id, timeline, language)` → `str` — visa_db.json의 `tax_residency_days` 기준, 이중과세조약 여부 포함

### `utils/planb.py`
- `get_planb_suggestions(current_country_id, language, max_suggestions=3)` → `list[dict]`
- 10개 비쉥겐 버퍼 국가 (GE·AL·RS·MK·CY·TH·VN·PH·MA·ID)
- GE: 2026-03-01 조지아 노동이민법 경고 포함

### `utils/accommodation.py`
- `get_accommodation_links(city_name)` → `dict` — city_scores.json에서 `flatio_search_url`, `anyplace_search_url`, `nomad_meetup_url` 조회

### `utils/currency.py`
- `get_exchange_rates()` → `dict` — 1 KRW 기준 환율. 실패 시 fallback (USD: 0.000714 = 약 1,400원)

### `ui/layout.py`
- `create_layout(advisor_fn, detail_fn)` — Gradio Blocks UI 생성
- `check_income_warning(income_krw, preferred_countries, travel_type, timeline, exchange_rate_usd)` → `tuple[gr.update, gr.update, gr.update]`
- `check_companion_warning(travel_type, has_spouse_income)` → `dict`

---

## 7. UI 구조 (`ui/layout.py`)

### Tab 1: 🔍 도시 추천

**입력 컴포넌트 (좌측 패널)**
- `ui_language`: Radio (한국어 / English)
- `nationality`: Dropdown (9개 국적)
- `dual_nationality`: Checkbox
- `travel_type`: Radio (혼자/배우자/자녀/가족 전체)
- `children_ages`: CheckboxGroup (자녀 동반 시 노출)
- `has_spouse_income`: Radio + `spouse_income_krw`: Number (배우자 동반 시 노출)
- `income_krw`: Number (만원 단위)
- `income_type`: Dropdown (5가지 계약 형태)
- `immigration_purpose`: Dropdown (5가지 목적)
- `readiness_stage`: Radio (3단계: 막연/준비/임박)
- `timeline`: Radio (90일/1년/3년/5년+)
- `lifestyle`: CheckboxGroup (9가지 선호)
- `languages`: CheckboxGroup
- `preferred_countries`: CheckboxGroup (아시아/유럽/중남미)
- 아코디언: `q_motivation` / `q_europe` / `q_concern`
- **경고 컴포넌트**: `income_warning`, `companion_warning`, `submit_warning` (gr.Markdown, 조건부 가시)
- `btn_step1`: 제출 버튼 (hard_block 시 비활성화)

**결과 컴포넌트 (우측 패널)**
- `step1_output`: gr.Markdown
- `btn_go_step2`: 상세 가이드 이동 버튼 (Step 1 완료 후 노출)

**실시간 이벤트 연결**
- `income_krw`, `preferred_countries`, `travel_type`, `timeline` 변경 → `check_income_warning()` → `[income_warning, submit_warning, btn_step1]`
- `travel_type`, `has_spouse_income` 변경 → `check_companion_warning()` → `[companion_warning]`

### Tab 2: 🗓️ 쉥겐 계산기 (별도 독립 탭)

- 입출국 날짜 입력 → `api/schengen_calculator.py` 호출
- Step 1/2 파이프라인과 독립적으로 동작

### Tab 3 (내부 id=1): 📖 상세 가이드

- `city_choice`: Radio (1~3순위 도시 선택, Step 1 완료 후 동적 레이블)
- `btn_step2` → `show_city_detail()` 호출
- `step2_output`: gr.Markdown

---

## 8. 데이터 현황

### `data/visa_db.json` — 29개국

**국가 ID 목록**: DE, PT, TH, MY, EE, ES, ID, GE, CR, GR, PH, VN, HR, CZ, HU, SI, MT, CY, AL, RS, MK, MX, CO, AR, BR, AE, MA, CA, JP

**주요 필드**:
```
id, name, name_kr, visa_type, min_income_usd, stay_months, renewable,
key_docs, visa_fee_usd, tax_note, cost_tier, notes, source, schengen,
buffer_zone, tax_residency_days, double_tax_treaty_with_kr,
mid_term_rental_available, income_period, ees_applicable,
income_tiers, data_verified_date
```

### `data/city_scores.json` — 50개 도시

**주요 필드**:
```
id, city, city_kr, country, country_id, monthly_cost_usd, internet_mbps,
safety_score, english_score, nomad_score, climate, cowork_usd_month,
coworking_score, community_size, mid_term_rent_usd, tax_residency_days,
flatio_search_url, anyplace_search_url, nomad_meetup_url,
korean_community_size, entry_tips
```

### `data/visa_urls.json`

국가별 공식 비자 URL. `parse_response()` 호출 시 `_inject_visa_urls()`가 LLM 생성 URL을 자동 교체.

---

## 9. LLM 응답 JSON 스키마

### Step 1 (`prompts/system.py` 기준)

```json
{
  "top_cities": [
    {
      "city": "도시명 (영어)",
      "city_kr": "도시명 (한국어)",
      "country": "국가명 (영어)",
      "country_id": "ISO-2 코드",
      "visa_type": "비자 유형명",
      "visa_url": "비자 공식 URL (시스템이 visa_urls.json으로 자동 교체)",
      "monthly_cost_usd": 숫자,
      "score": 숫자(1-10),
      "reasons": [{"point": "한국어 추천 근거", "source_url": null}],
      "realistic_warnings": ["경고 문자열"],
      "tax_warning": "세금 거주지 경고 또는 null",
      "plan_b_trigger": false,
      "references": [{"title": "출처 제목", "url": "https://..."}]
    }
  ],
  "overall_warning": "전체 공통 경고 (한국어)"
}
```

**시스템 프롬프트 주요 규칙 (13개)**:
- 쉥겐 국가 → EES 경고 필수 (2025년 10월 발효, 현재 시행 중)
- GE(조지아) → 노동이민법 경고 필수 (2026-03-01 시행)
- EE(에스토니아) → e-Residency 비체류 경고 + DNV 중단 이력 경고
- 한국 국적 → 건강보험 임의계속가입 + 국민연금 납부예외 overall_warning 필수

### Step 2 (`prompts/builder.py:_STEP2_SYSTEM_PROMPT` 기준)

```json
{
  "city": "도시명",
  "country_id": "ISO-2 코드",
  "immigration_guide": {
    "title": "가이드 제목",
    "sections": [{"step": 1, "title": "섹션 제목", "items": ["항목 1", "항목 2"]}]
  },
  "visa_checklist": ["여권 사본", "소득 증빙 서류", "..."],
  "budget_breakdown": {
    "rent": 600,
    "food": 300,
    "cowork": 100,
    "insurance": 60,
    "misc": 150
  },
  "budget_source": "https://www.numbeo.com/cost-of-living/in/Chiang-Mai",
  "first_steps": ["건강보험 임의계속가입 신청 (퇴직 후 2개월 이내)", "..."]
}
```

**Step 2 주요 규칙**:
- `insurance` 필드 필수 (SafetyWing Nomad Insurance 기준 $45~80)
- `first_steps` 순서: 기한 있는 항목 최우선 (건강보험, 국민연금, 비자 서류)
- 출국 임박 단계: 초보 여행 정보(SIM카드, 대중교통 등) 제외
- 원격근무 발설 금지 경고: 모든 국가 (쉥겐 포함)

---

## 10. 테스트 구성

**실행 명령**:
```bash
SKIP_RAG_INIT=1 .venv/bin/pytest tests/ -v
```

**현재 결과**: 256 passed, 4 skipped (test_pdf_generator.py 전체 skip)

**테스트 파일별 역할**:

| 파일 | 주요 테스트 내용 |
|------|----------------|
| test_builder.py | build_prompt(), build_detail_prompt(), validate_user_profile() |
| test_parser.py | parse_response() 4단계, format_step1/step2_markdown(), generate_comparison_table() |
| test_schengen_calculator.py | 90/180 롤링 윈도우, 경계값 |
| test_visa_db.py | 29개국 필수 필드 존재 여부 |
| test_city_scores.py | 50개 도시 필수 필드 |
| test_data_schema.py | visa_db + city_scores 스키마 검증 |
| test_ui.py | check_income_warning(), check_companion_warning(), 컴포넌트 구조 |
| test_tax_warning.py | get_tax_warning() 국가별 경고 |
| test_planb.py | get_planb_suggestions(), GE 노동이민법 경고 포함 여부 |
| test_persona.py | diagnose_persona() 5가지 분류 |
| test_accommodation.py | get_accommodation_links() |
| test_prompts.py | 시스템 프롬프트 필수 문구 (EES, GE, 건강보험 등) |
| test_integration.py | 전체 파이프라인 연동 |
| test_currency.py | 환율 폴백 동작 |
| test_hf_client.py | query_model() 에러 처리 |
| test_pdf_generator.py | 전체 skip (PDF 기능 제거됨) |

---

## 11. 최근 주요 커밋 (git log --oneline -10)

```
a48e40d feat: add income/companion warning UI components and event wiring
8c4412b feat: add validate_user_profile() with hard_block for Europe+low_income+long_stay
11110d2 merge: feature/domain-followup-issues → main
9279d9b fix: 도메인검증 후속이슈 7건 처리 (PLAN_도메인검증후속이슈_20260317)
2e6f637 merge: feature/parsing-fix-domain-hotfix → main
97514d0 fix: 파싱버그 수정 + 도메인 이슈 핫픽스 (4건)
b15bf91 feat: Step 2 출처·기준일 블록 자동 삽입 (PLAN_PDF출처기준일_20260315)
cc7882b feat: 비자 데이터 P1 현행화 — EE/ID/GR/MY (PLAN_비자데이터수정_P1_20260315)
4cedfa7 feat: Step 2 상세가이드 개인화 분기 추가 (PLAN_상세가이드개인화_20260315)
5c992e9 feat: 비자 체크리스트 한국인 실전화 (PLAN_비자체크리스트실전화_20260315)
```

---

## 12. 로컬 실행

```bash
cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai"

# 의존성 설치 (최초 1회)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 환경 변수 설정
export GEMINI_API_KEY="..."

# 앱 실행
.venv/bin/python app.py

# 테스트 실행
SKIP_RAG_INIT=1 .venv/bin/pytest tests/ -v
```

---

## 13. 알려진 이슈 (현재 미해결)

1. **Gradio 경고**: `theme`, `css` 파라미터를 `Blocks()` 대신 `launch()`에 전달하면 경고 발생. 현재는 경고만 발생하며 동작에 영향 없음.

2. **RAG 코드 잔존**: `rag/` 디렉토리 및 `SKIP_RAG_INIT` 환경변수 처리 코드가 잔존. 현재 `prompts/data_context.py`가 RAG 역할을 대체하므로 실제 RAG 초기화는 일어나지 않으나, 테스트 시 `SKIP_RAG_INIT=1` 설정 필요.

3. **`format_result_markdown()` 레거시**: `api/parser.py`에 잔존하나 현재 `format_step1_markdown()`으로 대체됨. 미사용.

4. **Gemini Context Cache 조건부 동작**: `GEMINI_API_KEY` 없는 환경에서는 캐싱 없이 OpenAI-compat 경로로 자동 폴백. HF Space 환경에서는 정상 캐싱.

5. **Schengen Calculator UI**: Tab 구조상 존재하지만 layout.py에서의 정확한 UI 구현 상태는 별도 확인 필요 (Tab 2가 schengen_calculator인지 layout.py 직접 확인).
