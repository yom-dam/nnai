# NomadNavigator AI — UI/UX 개선 설계 문서

**작성일**: 2026-03-14
**범위**: 6가지 UI/UX 개선 항목
**관련 파일**: `ui/layout.py`, `api/parser.py`, `prompts/builder.py`, `report/pdf_generator.py`, `app.py`, `tests/`

---

## 1. Step 2 별도 탭 분리

### 현재 상태
- 단일 페이지에 Step 1 (도시 추천)과 Step 2 (상세 가이드)가 세로로 배치
- Step 1 미완료 상태에서도 Step 2 UI가 노출됨

### 변경 내용
Gradio `gr.Tabs`로 두 스텝을 분리:

**Tab 1: 🔍 도시 추천**
- 기존 Step 1 입력 폼 + 결과 패널 유지
- Step 1 완료 시 하단에 `"📖 상세 가이드 받기 →"` 버튼 등장 (`visible=False` → `True`)
- 버튼 클릭 시 Tab 2로 자동 전환 → `gr.update(selected=1)`을 `tabs` 컴포넌트에 출력

**Tab 2: 📖 상세 가이드**
- 도시 선택 Radio (1~3순위)
- `"상세 가이드 + PDF 받기"` 버튼
- 결과 Markdown + PDF 다운로드 컴포넌트
- `gr.State`로 Step 1 결과(parsed_dict) 공유

### 구현 포인트
```python
with gr.Tabs() as tabs:
    with gr.Tab("🔍 도시 추천", id=0):
        ...
        btn_go_step2 = gr.Button("📖 상세 가이드 받기 →", visible=False)
    with gr.Tab("📖 상세 가이드", id=1):
        ...

# Tab 전환: gr.update(selected=1)을 tabs의 출력으로 사용
btn_go_step2.click(
    fn=lambda: gr.update(selected=1),
    inputs=[],
    outputs=[tabs],
)
```

`gr.Tabs.select()`는 이벤트 리스너(사용자 클릭 감지용)이므로 프로그래밍 방식 전환에 사용 불가.
반드시 `gr.update(selected=id)` → `outputs=[tabs]` 패턴을 사용한다.

---

## 2. 로딩 인디케이터 — yield 스트리밍

### 현재 상태
- `show_progress=True`만 설정되어 있어 Gradio 기본 스피너만 표시
- 결과 패널에 시각적 변화 없음

### 변경 내용
`run_step1()`, `run_step2()` 함수를 **generator 함수**로 변환하여 단계별 메시지 yield.

`btn_step1.click`의 `outputs`는 다음 4개:
```python
outputs=[step1_output, parsed_state, btn_go_step2, tabs]
```

**모든 yield는 정확히 4개의 값을 반환해야 한다:**

```python
def run_step1(nat, inc, purpose, life, langs, tl, preferred_countries):
    yield "🔍 프로필을 분석하는 중이에요...",    gr.update(), gr.update(visible=False), gr.update()
    yield "🌍 전 세계 비자 데이터를 검색하는 중이에요...", gr.update(), gr.update(visible=False), gr.update()
    yield "🤖 AI가 최적의 도시를 선별하는 중이에요...", gr.update(), gr.update(visible=False), gr.update()
    yield "✨ 거의 다 됐어요!",                gr.update(), gr.update(visible=False), gr.update()
    markdown, cities, parsed = advisor_fn(nat, inc, purpose, life, langs, tl, preferred_countries)
    yield markdown, parsed, gr.update(visible=True), gr.update()
```

**Step 2 메시지 시퀀스** (`outputs=[step2_output, output_pdf]` — 2개):
```python
def run_step2(parsed, choice):
    yield "🏙️ 선택한 도시 정보를 불러오는 중이에요...", gr.update()
    yield "📋 맞춤 이민 가이드를 작성하는 중이에요...", gr.update()
    yield "📄 PDF 리포트를 생성하는 중이에요...",       gr.update()
    markdown, pdf_path = detail_fn(parsed, city_index=idx)
    yield markdown, pdf_path
```

---

## 3. 관심 국가 선택 (소프트 힌트)

### 현재 상태
- 국가/도시 관련 입력 없음. AI가 전체 RAG 데이터에서 자유롭게 추천

### 변경 내용
Step 1 입력 폼에 `gr.CheckboxGroup` 추가 (timeline 아래, 버튼 위):

```
관심 국가 선택 (선택 안 하면 전체 고려)
info: "선택한 국가를 우선 고려하지만, AI가 더 적합한 곳을 제안할 수 있어요"

🇲🇾 말레이시아  🇵🇹 포르투갈    🇹🇭 태국
🇪🇪 에스토니아  🇪🇸 스페인      🇮🇩 인도네시아
🇩🇪 독일        🇬🇪 조지아      🇨🇷 코스타리카
🇬🇷 그리스      🇵🇭 필리핀      🇻🇳 베트남
```

RAG 데이터의 12개 국가 전체 제공 (각 flag emoji + 한국어명).

### app.py 시그니처 변경
`nomad_advisor()`에 `preferred_countries: list` 파라미터 추가 (7번째):
```python
def nomad_advisor(
    nationality, income_krw, immigration_purpose,
    lifestyle, languages, timeline,
    preferred_countries: list = [],  # 신규
) -> tuple[str, list, dict]:
```
`user_profile` dict에 포함:
```python
user_profile = {
    ...
    "preferred_countries": preferred_countries,
}
```

### 프롬프트 연동 (`prompts/builder.py`)
flag emoji 제거 변환 적용 후 프롬프트에 삽입:
```python
# flag emoji + 공백 제거: "🇲🇾 말레이시아" → "말레이시아"
country_names = [c.split(" ", 1)[-1] for c in preferred_countries]
```

**preferred_countries가 비어있지 않은 경우:**
```
※ 우선 고려 국가: 말레이시아, 태국 (단, 프로필에 더 적합한 다른 도시가 있다면 포함 가능)
```

**preferred_countries가 빈 리스트 `[]`인 경우:**
해당 줄 전체 생략 (프롬프트에 아무것도 추가하지 않음).

### 테스트
`tests/test_integration.py`의 `nomad_advisor()` 호출에 `preferred_countries=[]` 기본값 추가.

---

## 4. 언어 옵션 텍스트 수정

### 변경 내용
`ui/layout.py`:
```python
# Before
"🇰🇷 한국어만 가능"

# After
"🇰🇷 한국어"
```

연관 파일 동일 수정:
- `tests/test_ui.py` — 해당 문자열 참조 시 수정
- `tests/test_integration.py` — mock 데이터에서 참조 시 수정

---

## 5. PDF 한글 폰트 수정

### 현재 상태
- ReportLab 기본 Helvetica 폰트 사용
- 한글 문자 출력 불가 (빈 박스 또는 깨짐)
- `generate_report()`가 `parsed.get("top_cities", [])` 사용 — Step 2 pdf_data에는 `top_cities` 키가 없어 해당 섹션이 항상 비어있음

### 변경 내용

**폰트 번들링:**
- `assets/fonts/NanumGothic.ttf` 파일 추가
- 취득처: `https://fonts.google.com/specimen/Nanum+Gothic` (Google Fonts, OFL 라이선스)
- HF Space(Linux) 환경에서도 동작하도록 폰트 파일 직접 번들

**ReportLab 등록 (폰트 없을 경우 fallback 포함):**
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
FONT_PATH = os.path.join(FONT_DIR, "NanumGothic.ttf")

try:
    pdfmetrics.registerFont(TTFont("NanumGothic", FONT_PATH))
    BODY_FONT = "NanumGothic"
except Exception:
    BODY_FONT = "Helvetica"  # fallback: 한글 깨지지만 크래시 방지
```

**모든 ParagraphStyle에 `fontName=BODY_FONT` 적용.**

**PDF 구조 수정 — selected_city 사용:**
기존 `parsed.get("top_cities", [])` → `pdf_data["selected_city"]`(단일 도시 dict)로 교체.
출력 섹션: "선택 도시 상세" (단일 도시 정보: 도시명, 비자, 월 비용, 점수).

**PDF 내용 한국어화:**
- 제목: "NomadNavigator AI — 이민 설계 리포트"
- 섹션: "선택 도시 상세", "비자 준비 체크리스트", "월 예산 브레이크다운", "첫 번째 실행 스텝"
- 예산 항목: 임대료, 식비, 코워킹, 기타

**Table `FONTNAME` 지정:**
```python
TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), BODY_FONT),
    ...
])
```

---

## 6. 추천 근거 링크 자동 생성

### 현재 상태
- `source_url`이 있으면 `([출처](url))` 표시
- `source_url`이 null이면 링크 없음

### 변경 내용
`api/parser.py`의 `format_step1_markdown()` 수정:

**source_url 있는 경우:** 기존 `([출처](url))` 유지

**source_url 없는 경우:** Google 검색 + YouTube 검색 링크 자동 생성
```python
from urllib.parse import quote

def _make_search_links(city: str, point: str) -> str:
    query = quote(f"{city} {point[:20]} 이민")
    google  = f"https://www.google.com/search?q={query}"
    youtube = f"https://www.youtube.com/results?search_query={query}"
    return f" ([🔍 검색]({google})) ([▶ 유튜브]({youtube}))"
```

**출력 예시:**
```markdown
- 치앙마이는 디지털 노마드 커뮤니티 규모 기준 전 세계 상위 5개 도시입니다. ([🔍 검색](...)) ([▶ 유튜브](...))
- 코워킹 스페이스 월 이용료가 $60~100 수준입니다. ([출처](https://nomads.com))
```

---

## 변경 파일 목록

| 파일 | 변경 유형 | 내용 |
|------|---------|------|
| `ui/layout.py` | 수정 | Tabs 구조, 로딩 yield, 국가 선택 추가, 언어 텍스트 |
| `app.py` | 수정 | `nomad_advisor()` 7번째 파라미터 `preferred_countries` 추가 |
| `prompts/builder.py` | 수정 | preferred_countries 힌트 삽입 (빈 리스트 시 생략) |
| `api/parser.py` | 수정 | 자동 검색 링크 생성 |
| `report/pdf_generator.py` | 수정 | NanumGothic 폰트 등록, 한국어화, selected_city 사용 |
| `assets/fonts/NanumGothic.ttf` | 신규 | 한글 폰트 파일 (Google Fonts, OFL) |
| `tests/test_ui.py` | 수정 | 언어 텍스트, 탭 구조 반영 |
| `tests/test_integration.py` | 수정 | 언어 텍스트, preferred_countries 파라미터 |
| `tests/test_parser.py` | 수정 | 자동 링크 생성 테스트 추가 |

---

## 비변경 파일

- `rag/` — RAG 데이터 변경 없음
- `api/hf_client.py` — 변경 없음
- `prompts/few_shots.py` — 변경 없음
- `prompts/system.py` — 변경 없음

---

## 테스트 전략

- `test_ui.py`: 탭 구조, 국가 선택 컴포넌트 존재, 언어 옵션 확인
- `test_parser.py`: `source_url=None` 시 Google/YouTube 링크 포함 여부
- `test_integration.py`: `preferred_countries` 파라미터 전달 정상 동작 (빈 리스트 + 값 있는 경우)
- `tests/test_pdf_generator.py`: PDF 생성 시 한글 깨짐 없음 (파일 사이즈 > 0 확인), selected_city 섹션 존재
