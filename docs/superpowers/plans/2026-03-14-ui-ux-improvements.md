# UI/UX Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 6가지 UX 개선 — Tabs 분리, 로딩 인디케이터, 관심 국가 선택, 언어 텍스트, PDF 한글 폰트, 추천 근거 자동 링크

**Architecture:** 기존 Gradio 단일 페이지를 Tabs로 분리하고, 각 기능을 독립적으로 수정한다. 의존성이 없는 항목(언어 텍스트, 링크 생성, preferred_countries)을 먼저 처리하고, UI 구조 변경(Tabs/로딩)과 PDF 수정을 이후에 적용한다.

**Tech Stack:** Gradio 6.9, ReportLab, NanumGothic TTF, Python urllib.parse

**Spec:** `docs/superpowers/specs/2026-03-14-ui-ux-improvements-design.md`

---

## Chunk 1: 언어 텍스트 + 추천 근거 자동 링크 + preferred_countries

### Task 1: "한국어만 가능" → "한국어" 텍스트 변경

**Files:**
- Modify: `ui/layout.py:32`
- Modify: `tests/test_ui.py`
- Modify: `tests/test_builder.py:68`
- Modify: `tests/test_integration.py` (languages mock 문자열)

- [ ] **Step 1: 테스트에서 새 문자열 확인 (현재 실패 확인용)**

`tests/test_ui.py`에 아래 테스트 추가:
```python
def test_language_options_has_korean():
    from ui.layout import LANGUAGE_OPTIONS
    assert "🇰🇷 한국어" in LANGUAGE_OPTIONS
    assert "🇰🇷 한국어만 가능" not in LANGUAGE_OPTIONS
```

Run: `cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai" && SKIP_RAG_INIT=1 python -m pytest tests/test_ui.py::test_language_options_has_korean -v`
Expected: **FAIL** — `assert '🇰🇷 한국어' in [...]` 실패

- [ ] **Step 2: ui/layout.py 텍스트 변경**

`ui/layout.py` line 32:
```python
# Before
"🇰🇷 한국어만 가능",

# After
"🇰🇷 한국어",
```

- [ ] **Step 3: 연관 테스트 파일 문자열 동기화**

`tests/test_builder.py` line 68: `"한국어만 가능"` → `"한국어"`

`tests/test_integration.py` 전체에서 `"🇰🇷 한국어만 가능"` → `"🇰🇷 한국어"` 치환 (3곳: line 114, 158, 191 모두 교체).

- [ ] **Step 4: 테스트 통과 확인**

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_ui.py tests/test_builder.py tests/test_integration.py -v -q`
Expected: **전체 통과**

- [ ] **Step 5: 커밋**

```bash
git add ui/layout.py tests/test_ui.py tests/test_builder.py tests/test_integration.py
git commit -m "fix: rename '한국어만 가능' to '한국어' in language options"
```

---

### Task 2: 추천 근거 자동 검색 링크 (source_url=None 시 Google/YouTube)

**Files:**
- Modify: `api/parser.py`
- Modify: `tests/test_parser.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_parser.py`에 아래 테스트 2개 추가 (파일 끝에):
```python
def test_format_step1_no_source_url_generates_search_links():
    """source_url=None 이면 Google/YouTube 자동 링크가 포함되어야 함"""
    data = {
        "top_cities": [{
            "city": "Chiang Mai",
            "city_kr": "치앙마이",
            "country": "Thailand",
            "country_id": "TH",
            "visa_type": "Tourist Visa",
            "monthly_cost_usd": 1100,
            "score": 9,
            "reasons": [
                {"point": "노마드 커뮤니티가 활발합니다.", "source_url": None},
            ],
            "realistic_warnings": [],
        }],
    }
    result = format_step1_markdown(data)
    assert "google.com/search" in result
    assert "youtube.com/results" in result


def test_format_step1_with_source_url_no_auto_links():
    """source_url이 있으면 자동 링크 없이 출처 링크만 있어야 함"""
    data = {
        "top_cities": [{
            "city": "Chiang Mai",
            "city_kr": "치앙마이",
            "country": "Thailand",
            "country_id": "TH",
            "visa_type": "Tourist Visa",
            "monthly_cost_usd": 1100,
            "score": 9,
            "reasons": [
                {"point": "노마드 커뮤니티가 활발합니다.", "source_url": "https://nomads.com"},
            ],
            "realistic_warnings": [],
        }],
    }
    result = format_step1_markdown(data)
    assert "[출처]" in result
    assert "google.com/search" not in result
```

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_parser.py::test_format_step1_no_source_url_generates_search_links tests/test_parser.py::test_format_step1_with_source_url_no_auto_links -v`
Expected: **FAIL**

- [ ] **Step 2: api/parser.py에 _make_search_links 헬퍼 추가 및 format_step1_markdown 수정**

`api/parser.py` 상단 stdlib import 블록(line 1–2의 `import json`, `import re` 바로 다음)에 추가:
```python
from urllib.parse import quote
```

`_usd_to_krw` 함수 바로 위에 헬퍼 함수 추가:
```python
def _make_search_links(city: str, point: str) -> str:
    """source_url이 없을 때 Google/YouTube 자동 검색 링크를 생성합니다."""
    query = quote(f"{city} {point[:20]} 이민")
    google  = f"https://www.google.com/search?q={query}"
    youtube = f"https://www.youtube.com/results?search_query={query}"
    return f" ([🔍 검색]({google})) ([▶ 유튜브]({youtube}))"
```

`format_step1_markdown` 내 추천 근거 루프 수정 (현재 line 99-105):
```python
# Before
for reason in city.get("reasons", []):
    point = reason.get("point", "")
    source = reason.get("source_url")
    if source:
        lines.append(f"- {point} ([출처]({source}))")
    else:
        lines.append(f"- {point}")

# After
for reason in city.get("reasons", []):
    point  = reason.get("point", "")
    source = reason.get("source_url")
    if source:
        lines.append(f"- {point} ([출처]({source}))")
    else:
        lines.append(f"- {point}{_make_search_links(city_en, point)}")
```

- [ ] **Step 3: 테스트 통과 확인**

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_parser.py -v -q`
Expected: **전체 통과** (기존 19개 + 신규 2개 = 21개)

- [ ] **Step 4: 커밋**

```bash
git add api/parser.py tests/test_parser.py
git commit -m "feat: auto-generate Google/YouTube search links when source_url is None"
```

---

### Task 3: preferred_countries — app.py 시그니처 + builder.py 프롬프트 힌트

**Files:**
- Modify: `app.py`
- Modify: `prompts/builder.py`
- Modify: `tests/test_builder.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: builder.py 테스트 추가**

`tests/test_builder.py` 끝에 추가:
```python
def test_build_prompt_includes_preferred_countries_hint():
    """preferred_countries가 있으면 프롬프트에 우선 고려 국가 힌트가 포함되어야 함"""
    profile = {
        **SAMPLE_PROFILE,
        "preferred_countries": ["🇲🇾 말레이시아", "🇹🇭 태국"],
    }
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(profile)
    last_user = result[-1]["content"]
    assert "말레이시아" in last_user
    assert "태국" in last_user
    assert "우선 고려" in last_user


def test_build_prompt_no_hint_when_empty_preferred_countries():
    """preferred_countries가 빈 리스트이면 프롬프트에 힌트 줄이 없어야 함"""
    profile = {
        **SAMPLE_PROFILE,
        "preferred_countries": [],
    }
    with patch("prompts.builder.retrieve_as_context", return_value=FAKE_RAG_CONTEXT):
        from prompts.builder import build_prompt
        result = build_prompt(profile)
    last_user = result[-1]["content"]
    assert "우선 고려 국가" not in last_user
```

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_builder.py::test_build_prompt_includes_preferred_countries_hint tests/test_builder.py::test_build_prompt_no_hint_when_empty_preferred_countries -v`
Expected: **FAIL**

- [ ] **Step 2: prompts/builder.py 수정 — preferred_countries 힌트 삽입**

`build_prompt` 함수 내 `user_message` 구성 직전에 추가:
```python
preferred_countries = user_profile.get("preferred_countries", [])
# flag emoji 제거: "🇲🇾 말레이시아" → "말레이시아"
country_names = [c.split(" ", 1)[-1] for c in preferred_countries if c.strip()]
```

`user_message` 문자열 끝 "위 프로필 기반으로..." 앞에 조건부 힌트 삽입:
```python
preferred_hint = ""
if country_names:
    preferred_hint = (
        f"※ 우선 고려 국가: {', '.join(country_names)} "
        f"(단, 프로필에 더 적합한 다른 도시가 있다면 포함 가능)\n\n"
    )

user_message = (
    f"국적: {nationality} | 월 수입: {income_krw * 100:,.0f}만원 "
    f"(약 ${income_usd:,.0f} USD) | "
    f"이민 목적: {purpose} | "
    f"사용 가능 언어: {', '.join(languages) if languages else '미응답'} | "
    f"목표 체류 기간: {timeline}\n"
    f"라이프스타일 선호: {', '.join(lifestyle) if lifestyle else '특별한 선호 없음'}\n\n"
    f"{rag_context}\n\n"
    f"{preferred_hint}"
    "위 프로필 기반으로 최적 거주 도시 TOP 3를 추천하세요. "
    "현실적 어려움과 위험 요소를 반드시 포함하세요. "
    "반드시 순수 JSON만 출력하세요."
)
```

- [ ] **Step 3: app.py 시그니처 수정**

`nomad_advisor()` 함수 시그니처에 7번째 파라미터 추가 (mutable default 방지를 위해 `None` + 내부 guard 사용):
```python
def nomad_advisor(
    nationality: str,
    income_krw: int,
    immigration_purpose: str,
    lifestyle: list,
    languages: list,
    timeline: str,
    preferred_countries=None,   # 신규 — None을 기본값으로, 내부에서 [] 처리
) -> tuple[str, list, dict]:
```

`user_profile` dict에 포함 (함수 body 첫 줄에 None guard 추가):
```python
if preferred_countries is None:
    preferred_countries = []

...

user_profile = {
    "nationality":          nationality,
    "income_usd":           income_usd,
    "income_krw":           income_krw,
    "purpose":              immigration_purpose,
    "lifestyle":            lifestyle if isinstance(lifestyle, list) else [lifestyle],
    "languages":            languages if isinstance(languages, list) else [languages],
    "timeline":             timeline,
    "preferred_countries":  preferred_countries,
}
```

- [ ] **Step 4: test_integration.py — nomad_advisor 호출에 preferred_countries=[] 추가**

`tests/test_integration.py` 내 `nomad_advisor(...)` 호출 3곳 모두에 `preferred_countries=[]` 추가:
```python
markdown, cities, parsed = app_mod.nomad_advisor(
    nationality="Korean",
    income_krw=500,
    immigration_purpose="💻 디지털 노마드 / 원격 근무",
    lifestyle=["저물가"],
    languages=["🇰🇷 한국어"],
    timeline="1년 단기 체험",
    preferred_countries=[],   # 신규
)
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_builder.py tests/test_integration.py -v -q`
Expected: **전체 통과**

- [ ] **Step 6: 커밋**

```bash
git add app.py prompts/builder.py tests/test_builder.py tests/test_integration.py
git commit -m "feat: add preferred_countries soft-hint to nomad_advisor and build_prompt"
```

---

## Chunk 2: UI — Tabs 분리 + yield 로딩 인디케이터

### Task 4: Tabs 구조로 UI 재편 + Step 2 별도 탭

**Files:**
- Modify: `ui/layout.py` (전체 재작성)
- Modify: `tests/test_ui.py`

- [ ] **Step 1: 테스트 업데이트 (Tabs 구조 확인)**

`tests/test_ui.py`의 기존 3개 테스트 아래에 추가:
```python
def test_layout_has_tabs():
    """레이아웃에 Tabs 컴포넌트가 있어야 함"""
    import gradio as gr
    from ui.layout import create_layout
    demo = create_layout(lambda *a: ("", [], {}), lambda *a: ("", None))
    component_types = {type(c).__name__ for c in demo.blocks.values()}
    assert "Tabs" in component_types


def test_layout_has_preferred_countries_checkbox():
    """관심 국가 선택 CheckboxGroup이 있어야 함"""
    import gradio as gr
    from ui.layout import create_layout, COUNTRY_OPTIONS
    demo = create_layout(lambda *a: ("", [], {}), lambda *a: ("", None))
    # COUNTRY_OPTIONS 리스트가 존재하고 12개 국가를 포함해야 함
    assert len(COUNTRY_OPTIONS) == 12
    assert "🇲🇾 말레이시아" in COUNTRY_OPTIONS
    assert "🇻🇳 베트남" in COUNTRY_OPTIONS
```

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_ui.py::test_layout_has_tabs tests/test_ui.py::test_layout_has_preferred_countries_checkbox -v`
Expected: **FAIL**

- [ ] **Step 2: ui/layout.py 전면 재작성**

`ui/layout.py`를 아래로 교체:

```python
# ui/layout.py
import gradio as gr
from ui.theme import create_theme

NATIONALITIES = [
    "Korean", "Japanese", "Chinese", "American",
    "British", "German", "French", "Australian", "Other",
]

IMMIGRATION_PURPOSES = [
    "💻 디지털 노마드 / 원격 근무",
    "👨‍👩‍👧 자녀 교육 이민",
    "🏖️ 은퇴 이민",
    "💼 취업 / 창업 이민",
    "🎓 유학 후 이민",
    "🌿 라이프스타일 이민 (삶의 질)",
]

LIFESTYLE_OPTIONS = [
    "🏖️ 해변",
    "🏙️ 도심",
    "💰 저물가",
    "🔒 안전 우선",
    "🌐 영어권",
    "☀️ 따뜻한 기후",
    "❄️ 선선한 기후",
    "🤝 노마드 커뮤니티",
    "🍜 한국 음식",
]

LANGUAGE_OPTIONS = [
    "🇰🇷 한국어",
    "🇺🇸 영어 (기본 소통)",
    "🇺🇸 영어 (업무 가능 수준)",
    "🇯🇵 일본어",
    "🇨🇳 중국어",
    "🇪🇸 스페인어",
    "🇵🇹 포르투갈어",
]

COUNTRY_OPTIONS = [
    "🇲🇾 말레이시아",
    "🇵🇹 포르투갈",
    "🇹🇭 태국",
    "🇪🇪 에스토니아",
    "🇪🇸 스페인",
    "🇮🇩 인도네시아",
    "🇩🇪 독일",
    "🇬🇪 조지아",
    "🇨🇷 코스타리카",
    "🇬🇷 그리스",
    "🇵🇭 필리핀",
    "🇻🇳 베트남",
]

# Step 1 로딩 메시지 시퀀스
_STEP1_LOADING = [
    "🔍 프로필을 분석하는 중이에요...",
    "🌍 전 세계 비자 데이터를 검색하는 중이에요...",
    "🤖 AI가 최적의 도시를 선별하는 중이에요...",
    "✨ 거의 다 됐어요!",
]

# Step 2 로딩 메시지 시퀀스
_STEP2_LOADING = [
    "🏙️ 선택한 도시 정보를 불러오는 중이에요...",
    "📋 맞춤 이민 가이드를 작성하는 중이에요...",
    "📄 PDF 리포트를 생성하는 중이에요...",
]


def create_layout(advisor_fn, detail_fn):
    theme = create_theme()

    with gr.Blocks(
        theme=theme,
        title="NomadNavigator AI",
        css="""
        .main-header{text-align:center;padding:20px 0 10px}
        .main-header h1{font-size:2rem;color:#0C447C}
        .main-header p{color:#888780;font-size:.95rem}
        footer{display:none!important}
        """,
    ) as demo:

        # ── 헤더 ──────────────────────────────────────────────────────
        with gr.Column(elem_classes="main-header"):
            gr.HTML("""
                <h1>🌏 NomadNavigator AI</h1>
                <p>국적 · 소득 · 이민 목적을 입력하면 AI가 최적의 이민 설계를 제안합니다</p>
            """)

        # ── State ──────────────────────────────────────────────────────
        parsed_state = gr.State({})

        # ── Tabs ───────────────────────────────────────────────────────
        with gr.Tabs() as tabs:

            # ── Tab 1: 도시 추천 ───────────────────────────────────────
            with gr.Tab("🔍 도시 추천", id=0):
                with gr.Row():
                    # 입력 패널
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 내 프로필 입력")

                        nationality = gr.Dropdown(
                            choices=NATIONALITIES, value="Korean",
                            label="국적", info="여권 발급 국가 기준",
                        )
                        income_krw = gr.Slider(
                            minimum=100, maximum=2000, value=500, step=50,
                            label="월 수입 (만원)",
                            info="세전 월 소득 (만원 단위, 예: 500 = 500만원)",
                        )
                        immigration_purpose = gr.Dropdown(
                            choices=IMMIGRATION_PURPOSES,
                            value=IMMIGRATION_PURPOSES[0],
                            label="이민 목적",
                        )
                        lifestyle = gr.CheckboxGroup(
                            choices=LIFESTYLE_OPTIONS,
                            label="라이프스타일 선호",
                            info="해당 항목 모두 선택",
                        )
                        languages = gr.CheckboxGroup(
                            choices=LANGUAGE_OPTIONS,
                            label="사용 가능 언어",
                            info="가능한 언어 모두 선택",
                        )
                        timeline = gr.Radio(
                            choices=["1년 단기 체험", "3년 장기 이민", "영구 이민 (영주권 목표)"],
                            value="1년 단기 체험",
                            label="목표 체류 기간",
                        )
                        preferred_countries = gr.CheckboxGroup(
                            choices=COUNTRY_OPTIONS,
                            label="관심 국가 선택",
                            info="선택한 국가를 우선 고려하지만, AI가 더 적합한 곳을 제안할 수 있어요. 선택 안 하면 전체 고려",
                        )
                        btn_step1 = gr.Button(
                            "🚀 도시 추천 받기", variant="primary", size="lg",
                        )
                        gr.Markdown("_⚠️ 본 서비스는 참고용이며 법적 이민 조언이 아닙니다._")

                    # 결과 패널
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 추천 도시 TOP 3")
                        step1_output = gr.Markdown(
                            "← 왼쪽에서 프로필을 입력하고 분석을 시작하세요."
                        )

                # Step 1 완료 후 등장하는 Tab 2 진입 버튼
                btn_go_step2 = gr.Button(
                    "📖 상세 가이드 받기 →",
                    variant="secondary",
                    size="lg",
                    visible=False,
                )

            # ── Tab 2: 상세 가이드 ─────────────────────────────────────
            with gr.Tab("📖 상세 가이드", id=1):
                with gr.Row():
                    with gr.Column(scale=1):
                        city_choice = gr.Radio(
                            choices=["1순위 도시", "2순위 도시", "3순위 도시"],
                            value="1순위 도시",
                            label="상세 가이드를 받을 도시 선택",
                        )
                        btn_step2 = gr.Button(
                            "📖 상세 가이드 + PDF 받기",
                            variant="primary",
                            size="lg",
                        )

                    with gr.Column(scale=2):
                        step2_output = gr.Markdown(
                            "← Step 1을 먼저 완료한 후 도시를 선택하세요."
                        )
                        output_pdf = gr.File(label="📄 리포트 PDF 다운로드")

        # ── Step 1 이벤트 ──────────────────────────────────────────────
        def run_step1(nat, inc, purpose, life, langs, tl, pref_countries):
            try:
                for msg in _STEP1_LOADING:
                    yield msg, gr.update(), gr.update(visible=False), gr.update()
                markdown, cities, parsed = advisor_fn(
                    nat, inc, purpose, life, langs, tl, pref_countries
                )
                yield markdown, parsed, gr.update(visible=True), gr.update()
            except Exception as e:
                yield f"⚠️ 오류가 발생했습니다: {str(e)}", {}, gr.update(visible=False), gr.update()

        btn_step1.click(
            fn=run_step1,
            inputs=[
                nationality, income_krw, immigration_purpose,
                lifestyle, languages, timeline, preferred_countries,
            ],
            outputs=[step1_output, parsed_state, btn_go_step2, tabs],
        )

        # Step 2 탭으로 이동
        btn_go_step2.click(
            fn=lambda: gr.update(selected=1),
            inputs=[],
            outputs=[tabs],
        )

        # ── Step 2 이벤트 ──────────────────────────────────────────────
        def run_step2(parsed, choice):
            try:
                idx = {"1순위 도시": 0, "2순위 도시": 1, "3순위 도시": 2}.get(choice, 0)
                for msg in _STEP2_LOADING:
                    yield msg, gr.update()
                markdown, pdf_path = detail_fn(parsed, city_index=idx)
                yield markdown, pdf_path
            except Exception as e:
                yield f"⚠️ 오류가 발생했습니다: {str(e)}", None

        btn_step2.click(
            fn=run_step2,
            inputs=[parsed_state, city_choice],
            outputs=[step2_output, output_pdf],
        )

    return demo
```

- [ ] **Step 3: 테스트 통과 확인**

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_ui.py -v`
Expected: **5개 모두 통과**

- [ ] **Step 4: 커밋**

```bash
git add ui/layout.py tests/test_ui.py
git commit -m "feat: restructure UI into Tabs with loading indicators and country selector"
```

---

## Chunk 3: PDF 한글 폰트 + 한국어화

### Task 5: NanumGothic 폰트 번들링

**Files:**
- Create: `assets/fonts/NanumGothic.ttf`

- [ ] **Step 1: assets/fonts 디렉터리 생성 및 폰트 다운로드**

```bash
mkdir -p "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai/assets/fonts"
```

폰트 취득 — curl로 Naver 공식 GitHub에서 다운로드:
```bash
curl -L "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothicOTF/NanumGothic.ttf" \
     -o "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai/assets/fonts/NanumGothic.ttf"
```

- [ ] **Step 2: 폰트 파일 존재 확인**

```bash
ls -lh "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai/assets/fonts/NanumGothic.ttf"
```
Expected: 파일 크기 > 0 (통상 2~5MB)

- [ ] **Step 3: 커밋**

```bash
cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai"
git add assets/fonts/NanumGothic.ttf
git commit -m "chore: bundle NanumGothic.ttf for Korean PDF support"
```

---

### Task 6: report/pdf_generator.py — 한글 폰트 등록 + 한국어화 + selected_city 사용

**Files:**
- Modify: `report/pdf_generator.py` (전면 재작성)
- Modify: `tests/test_pdf_generator.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_pdf_generator.py`에 아래 테스트 2개 추가:
```python
SAMPLE_STEP2_PARSED = {
    "city": "Kuala Lumpur",
    "country_id": "MY",
    "immigration_guide": {
        "title": "대한민국 국민의 쿠알라룸푸르 이민 가이드",
        "sections": [
            {"step": 1, "title": "출국 전 준비", "items": ["여권 유효기간 확인"]},
        ],
    },
    "visa_checklist": ["여권 사본", "소득 증빙"],
    "budget_breakdown": {"rent": 700, "food": 400, "cowork": 150, "misc": 250},
    "first_steps": ["여권 유효기간 확인"],
}

SAMPLE_STEP2_PROFILE = {
    "nationality": "Korean",
    "income_usd": 3570,
    "income_krw": 500,
}

SAMPLE_SELECTED_CITY = {
    "city": "Kuala Lumpur",
    "city_kr": "쿠알라룸푸르",
    "country": "Malaysia",
    "visa_type": "DE Nomad Visa",
    "monthly_cost_usd": 1500,
    "score": 8,
}


def test_generate_report_with_selected_city(tmp_path, monkeypatch):
    """selected_city 키를 포함한 pdf_data로 PDF가 생성되어야 함"""
    monkeypatch.chdir(tmp_path)
    from report.pdf_generator import generate_report
    pdf_data = {
        **SAMPLE_STEP2_PARSED,
        "_user_profile": SAMPLE_STEP2_PROFILE,
        "selected_city": SAMPLE_SELECTED_CITY,
    }
    path = generate_report(pdf_data, SAMPLE_STEP2_PROFILE)
    assert path is not None
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000


def test_generate_report_korean_content_no_crash(tmp_path, monkeypatch):
    """한글 내용(쿠알라룸푸르, 여권 사본 등)이 포함된 PDF가 생성되어야 함"""
    monkeypatch.chdir(tmp_path)
    from report.pdf_generator import generate_report
    pdf_data = {
        **SAMPLE_STEP2_PARSED,
        "selected_city": SAMPLE_SELECTED_CITY,
    }
    # 크래시 없이 생성되어야 함
    path = generate_report(pdf_data, SAMPLE_STEP2_PROFILE)
    assert os.path.getsize(path) > 1000
```

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_pdf_generator.py::test_generate_report_with_selected_city tests/test_pdf_generator.py::test_generate_report_korean_content_no_crash -v`
Expected: **FAIL** (generate_report signature 또는 내용 불일치)

- [ ] **Step 2: report/pdf_generator.py 전면 재작성**

```python
# report/pdf_generator.py
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

# ── 한글 폰트 등록 ──────────────────────────────────────────────────
_FONT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "assets", "fonts", "NanumGothic.ttf"
)
try:
    pdfmetrics.registerFont(TTFont("NanumGothic", _FONT_PATH))
    _BODY_FONT = "NanumGothic"
except Exception:
    _BODY_FONT = "Helvetica"  # fallback: 한글 깨질 수 있으나 크래시 방지


def generate_report(parsed: dict, user_profile: dict) -> str:
    os.makedirs("reports", exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"reports/nomad_report_{ts}.pdf"

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm,   bottomMargin=2 * cm,
    )

    styles  = getSampleStyleSheet()
    title_s = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=20, textColor=colors.HexColor("#0C447C"),
        spaceAfter=12, fontName=_BODY_FONT,
    )
    heading_s = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#185FA5"),
        spaceBefore=12, spaceAfter=6, fontName=_BODY_FONT,
    )
    body_s = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=10, leading=14, fontName=_BODY_FONT,
    )
    disclaimer_s = ParagraphStyle(
        "Disclaimer", parent=body_s,
        fontSize=8, textColor=colors.gray,
    )

    story = []

    # ── 제목 + 메타 ──────────────────────────────────────────────────
    story.append(Paragraph("NomadNavigator AI — 이민 설계 리포트", title_s))
    story.append(Paragraph(
        f"작성일: {datetime.now().strftime('%Y-%m-%d')} | "
        f"국적: {user_profile.get('nationality', '-')} | "
        f"월 소득: ${user_profile.get('income_usd', user_profile.get('income', 0)):,} USD",
        body_s,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0C447C")))
    story.append(Spacer(1, 12))

    # ── 선택 도시 상세 ────────────────────────────────────────────────
    selected = parsed.get("selected_city", {})
    if selected:
        story.append(Paragraph("선택 도시 상세", heading_s))
        city_name = f"{selected.get('city_kr', selected.get('city', ''))} ({selected.get('city', '')})"
        story.append(Paragraph(
            f"{city_name}, {selected.get('country', '')} — "
            f"{selected.get('visa_type', '-')} | "
            f"${selected.get('monthly_cost_usd', 0):,}/월 | "
            f"추천 점수: {selected.get('score', '-')}/10",
            body_s,
        ))
        story.append(Spacer(1, 6))

    # ── 비자 준비 체크리스트 ───────────────────────────────────────────
    checklist = parsed.get("visa_checklist", [])
    if checklist:
        story.append(Paragraph("비자 준비 체크리스트", heading_s))
        for item in checklist:
            story.append(Paragraph(f"☐  {item}", body_s))
        story.append(Spacer(1, 6))

    # ── 월 예산 브레이크다운 ───────────────────────────────────────────
    bd = parsed.get("budget_breakdown", {})
    if bd:
        story.append(Paragraph("월 예산 브레이크다운", heading_s))
        label_map = [("rent", "임대료"), ("food", "식비"), ("cowork", "코워킹"), ("misc", "기타")]
        table_data = [["항목", "금액 (USD)"]]
        for k, label in label_map:
            table_data.append([label, f"${bd.get(k, 0):,}"])
        table_data.append(["합계", f"${sum(bd.values()):,}"])
        t = Table(table_data, colWidths=[8 * cm, 6 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0),  (-1, 0),  colors.HexColor("#0C447C")),
            ("TEXTCOLOR",     (0, 0),  (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0),  (-1, -1), _BODY_FONT),
            ("FONTSIZE",      (0, 0),  (-1, -1), 10),
            ("ROWBACKGROUNDS",(0, 1),  (-1, -2), [colors.white, colors.HexColor("#EEF4FB")]),
            ("FONTNAME",      (0, -1), (-1, -1), _BODY_FONT),
            ("GRID",          (0, 0),  (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # ── 첫 번째 실행 스텝 ──────────────────────────────────────────────
    first_steps = parsed.get("first_steps", [])
    if first_steps:
        story.append(Paragraph("첫 번째 실행 스텝", heading_s))
        for j, step in enumerate(first_steps, 1):
            story.append(Paragraph(f"{j}. {step}", body_s))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "본 리포트는 참고용이며 법적 이민 조언이 아닙니다. "
        "비자 정책은 수시로 변경될 수 있으므로 반드시 공식 기관에서 확인하세요.",
        disclaimer_s,
    ))

    doc.build(story)
    return path
```

- [ ] **Step 3: 테스트 통과 확인**

Run: `SKIP_RAG_INIT=1 python -m pytest tests/test_pdf_generator.py -v`
Expected: **4개 모두 통과** (기존 2개 + 신규 2개)

> 기존 2개 테스트(`test_generate_report_creates_pdf`, `test_generate_report_pdf_nonempty`)는 `SAMPLE_PARSED`(구 스키마)를 사용하므로 `selected_city` 섹션이 빈 채로 통과하면 정상.

- [ ] **Step 4: 커밋**

```bash
git add report/pdf_generator.py tests/test_pdf_generator.py
git commit -m "feat: Korean PDF with NanumGothic font, selected_city section"
```

---

### Task 7: 전체 테스트 통과 확인 + 최종 커밋

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai"
SKIP_RAG_INIT=1 python -m pytest tests/ -v -q
```
Expected: **70개 이상 통과**, 0 failed

- [ ] **Step 2: 로컬 앱 실행 확인 (선택)**

```bash
cd "/Users/flexx/Library/Mobile Documents/com~apple~CloudDocs/dev/nnai"
SKIP_RAG_INIT=1 python app.py
```
브라우저에서 Tabs 구조, 로딩 메시지, 관심 국가 체크박스 확인.

- [ ] **Step 3: 최종 커밋**

```bash
git add -u
git commit -m "feat: complete UI/UX improvements — tabs, loading, country select, PDF Korean font, search links"
```
