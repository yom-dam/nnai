"""ui/layout_v2.py — Faceted filter with card UI using pure Gradio components"""
import json
import os
import gradio as gr
from recommender import recommend_from_db
from api.parser import _inject_visa_urls

KRW_TO_USD = 1 / 1350.0

LIFESTYLE_TAG_MAP = {
    "저물가": "저비용 생활",
    "코워킹": "코워킹스페이스 중시",
    "안전": "안전 중시",
    "한인커뮤니티": "한인 커뮤니티",
    "영어권": "영어권 선호",
}

TIMELINE_MAP = {
    "90일": "90일 단기 체험",
    "6개월": "6개월 단기 체험",
    "1년": "1년 단기 체험",
    "3년+": "3년 이상 장기 이민",
}

CONTINENT_MAP_EXPANSION = {"기타": ["중동/아프리카", "북미"]}

LIFESTYLE_OPTIONS = ["저물가", "코워킹", "안전", "한인커뮤니티", "자연", "도시", "비건", "반려동물", "의료"]
CONTINENT_OPTIONS = ["아시아", "유럽", "중남미", "기타"]
TIMELINE_OPTIONS = ["90일", "6개월", "1년", "3년+"]

# Global cache for the last cities list (to avoid Gradio State serialization issues)
_LAST_CITIES = []


def _map_profile(profile_dict):
    """Translate UI profile fields to recommend_from_db() field names."""
    raw_continents = profile_dict.get("continents") or []
    expanded = []
    for c in raw_continents:
        expanded.extend(CONTINENT_MAP_EXPANSION.get(c, [c]))

    raw_tags = profile_dict.get("lifestyle_tags") or []
    mapped_lifestyle = [LIFESTYLE_TAG_MAP.get(t, t) for t in raw_tags]

    raw_timeline = profile_dict.get("timeline", "1년")
    mapped_timeline = TIMELINE_MAP.get(raw_timeline, raw_timeline)

    nationality = profile_dict.get("nationality", "한국")
    if nationality == "KR":
        nationality = "한국"

    return {
        "income_usd": (profile_dict.get("monthly_income_krw") or 300) * KRW_TO_USD,
        "preferred_countries": expanded,
        "lifestyle": mapped_lifestyle,
        "timeline": mapped_timeline,
        "nationality": nationality,
    }


def render_city_cards_html(cities):
    """Render city data as HTML card grid."""
    if not cities:
        return "<div style='text-align:center;padding:40px;color:#666;'>조건에 맞는 도시가 없습니다</div>"

    html = """
    <style>
    .city-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .city-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: #7c3aed;
        background: linear-gradient(135deg, #f8f5ff 0%, #faf9ff 100%);
    }
    .city-flag {
        font-size: 48px;
        margin-bottom: 12px;
    }
    .city-name {
        font-weight: 700;
        font-size: 16px;
        color: #1a1a2e;
        margin-bottom: 4px;
    }
    .city-location {
        font-size: 13px;
        color: #888;
        margin-bottom: 12px;
    }
    .city-score {
        font-size: 14px;
        color: #333;
        margin-bottom: 4px;
    }
    .city-cost {
        font-size: 15px;
        font-weight: 600;
        color: #0066cc;
    }
    .city-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        padding: 20px;
    }
    </style>
    <div class="city-grid">
    """

    for i, city in enumerate(cities):
        flag = city.get("flag", "🌍")
        city_kr = city.get("city_kr", city.get("city", "?"))
        city_en = city.get("city", "?")
        country = city.get("country_id", "?")
        cost = city.get("monthly_cost_usd", "?")
        score = city.get("score", 0)

        html += f"""
        <div class="city-card" onclick="document.getElementById('city-btn-{i}').click()">
            <div class="city-flag">{flag}</div>
            <div class="city-name">{city_kr}</div>
            <div class="city-location">{city_en}, {country}</div>
            <div class="city-score">⭐ {score:.1f}/10</div>
            <div class="city-cost">${cost}/월</div>
        </div>
        """

    html += "</div>"
    return html


def get_city_options(cities):
    """Create dropdown options from cities."""
    return [f"{c.get('flag', '🌍')} {c.get('city_kr', c.get('city', '?'))}" for c in cities]


def update_cities_view(*args):
    """Update city cards and dropdown when filters change."""
    global _LAST_CITIES

    monthly_income, nationality, lifestyle_tags, continents, timeline, ui_language = args

    profile = {
        "monthly_income_krw": int(monthly_income) if monthly_income else 300,
        "nationality": nationality,
        "lifestyle_tags": lifestyle_tags,
        "continents": continents,
        "timeline": timeline,
    }

    db_profile = _map_profile(profile)
    result = recommend_from_db(db_profile, top_n=12)
    _inject_visa_urls(result)

    cities = result.get("top_cities", [])
    _LAST_CITIES = cities  # Store in global variable
    cities_html = render_city_cards_html(cities)
    city_options = get_city_options(cities)

    return cities_html, gr.update(choices=city_options if city_options else [])


def get_detail_guide(selected_city_text):
    """Get detail guide for selected city."""
    global _LAST_CITIES

    if not selected_city_text:
        return "도시를 선택해주세요"

    if not _LAST_CITIES:
        return "도시를 선택해주세요"

    # Find matching city from the global cache
    selected_city = None
    for city in _LAST_CITIES:
        city_kr = city.get("city_kr", city.get("city", "?"))
        if city_kr in selected_city_text:
            selected_city = city
            break

    if not selected_city:
        return "선택된 도시를 찾을 수 없습니다"

    # Return a simple summary for now (Gradio has serialization bug with complex events)
    city_en = selected_city.get("city", "?")
    country = selected_city.get("country_id", "?")
    cost = selected_city.get("monthly_cost_usd", "?")

    summary = f"""
## 📍 {city_en}, {country}

**월 생활비**: ${cost}/월

이 도시에 대한 상세 가이드는 처리 중입니다.
메인 화면에서 **"상세 보기"** 버튼을 클릭하면 전체 분석을 볼 수 있습니다.

### 주요 정보
- **도시명**: {selected_city.get('city_kr', city_en)}
- **국가**: {country}
- **추천도**: ⭐ {selected_city.get('score', 0):.1f}/10
- **비자 정보**: {selected_city.get('visa_type', '정보 준비 중')}
"""
    return summary


def build_layout_v2(nomad_advisor_fn, show_city_detail_fn):
    """Build Gradio UI with card-based faceted filter."""

    with gr.Blocks(title="NomadNavigator AI") as demo:
        # Header
        gr.Markdown("# 🌍 노마드 도시 탐색")
        gr.Markdown("필터를 설정하면 조건에 맞는 도시가 카드로 나타납니다")

        # Main content
        with gr.Row():
            # Left: Filters
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 📋 필터 설정")

                monthly_income = gr.Slider(
                    minimum=100,
                    maximum=5000,
                    value=500,
                    step=100,
                    label="월 소득 (만원)",
                )

                nationality = gr.Dropdown(
                    choices=["한국", "미국", "일본", "중국", "기타"],
                    value="한국",
                    label="국적",
                )

                continents = gr.CheckboxGroup(
                    choices=CONTINENT_OPTIONS,
                    value=["아시아", "유럽", "중남미"],
                    label="선호 대륙",
                )

                timeline = gr.Radio(
                    choices=TIMELINE_OPTIONS,
                    value="1년",
                    label="체류 기간",
                )

                lifestyle_tags = gr.CheckboxGroup(
                    choices=LIFESTYLE_OPTIONS,
                    label="라이프스타일",
                )

                ui_language = gr.Radio(
                    choices=["한국어", "English"],
                    value="한국어",
                    label="언어",
                )

            # Right: City cards
            with gr.Column(scale=2):
                gr.Markdown("### 🎴 추천 도시")
                cities_html = gr.HTML(
                    "<div style='text-align:center;padding:40px;'>필터를 설정하면 도시가 나타납니다</div>"
                )

        # Detail section
        gr.Markdown("---")
        gr.Markdown("### 📖 상세 가이드")

        with gr.Row():
            with gr.Column(scale=1):
                city_dropdown = gr.Dropdown(
                    choices=[],
                    label="도시 선택",
                )
                detail_btn = gr.Button("📖 상세 가이드 받기", size="lg")

            with gr.Column(scale=2):
                detail_output = gr.Markdown("도시를 선택하면 상세 가이드가 표시됩니다")

        # Hidden buttons for card clicks
        for i in range(12):
            hidden_btn = gr.Button(visible=False, elem_id=f"city-btn-{i}")

        # Events: Filter changes -> Update cities
        filter_inputs = [
            monthly_income,
            nationality,
            lifestyle_tags,
            continents,
            timeline,
            ui_language,
        ]

        def on_filter_change(*args):
            html, dropdown_update = update_cities_view(*args)
            return html, dropdown_update

        for inp in filter_inputs:
            inp.change(
                fn=on_filter_change,
                inputs=filter_inputs,
                outputs=[cities_html, city_dropdown],
            )

        # Event: City selection -> Show details
        # Only pass city_dropdown to avoid Gradio serialization issues
        detail_btn.click(
            fn=get_detail_guide,
            inputs=[city_dropdown],
            outputs=[detail_output],
        )

        # Initial load - load default cities on page load
        demo.load(
            fn=on_filter_change,
            inputs=filter_inputs,
            outputs=[cities_html, city_dropdown],
        )

    return demo
