import gradio as gr
from ui.theme import create_theme

NATIONALITIES = [
    "Korean", "Japanese", "Chinese", "American",
    "British", "German", "French", "Australian", "Other"
]
LIFESTYLE_OPTIONS = [
    "🏖️ 해변", "🏙️ 도심", "💰 저물가", "🔒 안전 우선",
    "🌐 영어권", "☀️ 따뜻한 기후", "❄️ 선선한 기후",
    "🤝 노마드 커뮤니티", "🍜 한국 음식",
]


def create_layout(advisor_fn):
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

        with gr.Column(elem_classes="main-header"):
            gr.HTML("""
                <h1>🌏 NomadNavigator AI</h1>
                <p>국적 · 소득 · 라이프스타일을 입력하면 AI가 최적의 이민 설계를 제안합니다</p>
            """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📋 내 프로필 입력")

                nationality = gr.Dropdown(
                    choices=NATIONALITIES, value="Korean",
                    label="국적", info="여권 발급 국가 기준"
                )
                income = gr.Slider(
                    minimum=1000, maximum=12000, value=3000, step=500,
                    label="월 수입 (USD)", info="세전 월 소득 기준"
                )
                lifestyle = gr.CheckboxGroup(
                    choices=LIFESTYLE_OPTIONS,
                    label="라이프스타일 선호",
                    info="해당 항목 모두 선택"
                )
                timeline = gr.Radio(
                    choices=["1년 단기 체험", "3년 장기 이민"],
                    value="1년 단기 체험",
                    label="목표 기간"
                )
                btn = gr.Button("🚀 이민 설계 시작", variant="primary", size="lg")
                gr.Markdown("_⚠️ 본 서비스는 참고용이며 법적 이민 조언이 아닙니다._")

            with gr.Column(scale=1):
                gr.Markdown("### 📊 맞춤 이민 설계 결과")
                output_md  = gr.Markdown("← 왼쪽에서 프로필을 입력하고 분석을 시작하세요.")
                output_pdf = gr.File(label="📄 리포트 PDF 다운로드")

        btn.click(
            fn=advisor_fn,
            inputs=[nationality, income, lifestyle, timeline],
            outputs=[output_md, output_pdf],
            show_progress=True,
        )

    return demo
