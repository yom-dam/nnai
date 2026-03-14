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
