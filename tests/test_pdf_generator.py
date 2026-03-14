import os

SAMPLE_PARSED = {
    "top_cities": [
        {"city": "Chiang Mai", "country": "Thailand", "visa_type": "LTR",
         "monthly_cost": 1100, "score": 9, "why": "저렴하고 노마드 많음"}
    ],
    "visa_checklist": ["여권 18개월 확인", "소득 증빙 준비"],
    "budget_breakdown": {"rent": 500, "food": 300, "cowork": 100, "misc": 200},
    "first_steps": ["여권 갱신", "건강보험 가입"],
}
SAMPLE_PROFILE = {
    "nationality": "Korean",
    "income": 3000,
    "lifestyle": ["해변"],
    "timeline": "1년 단기 체험",
}

def test_generate_report_creates_pdf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from report.pdf_generator import generate_report
    path = generate_report(SAMPLE_PARSED, SAMPLE_PROFILE)
    assert path is not None
    assert os.path.exists(path)
    assert path.endswith(".pdf")

def test_generate_report_pdf_nonempty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from report.pdf_generator import generate_report
    path = generate_report(SAMPLE_PARSED, SAMPLE_PROFILE)
    assert os.path.getsize(path) > 1000


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
