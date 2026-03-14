FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": (
            "국적: Korean | 월 수입: $2,500 | "
            "라이프스타일: 저물가, 따뜻한 기후, 해변 | 기간: 1년 단기 체험\n"
            "위 프로필에 맞는 JSON 추천을 출력하세요."
        )
    },
    {
        "role": "assistant",
        "content": """{
  "top_cities": [
    {
      "city": "Chiang Mai",
      "country": "Thailand",
      "visa_type": "LTR Visa 또는 Thailand Elite",
      "monthly_cost": 1100,
      "score": 9,
      "why": "월 $1,100으로 생활 가능하며 세계 최대 규모의 디지털 노마드 커뮤니티가 있습니다. 한국 음식점도 다수 있어 적응이 빠르고 연평균 26도의 쾌적한 날씨를 자랑합니다."
    },
    {
      "city": "Kuala Lumpur",
      "country": "Malaysia",
      "visa_type": "DE Nomad Visa",
      "monthly_cost": 1500,
      "score": 8,
      "why": "DE Nomad 비자는 월 $2,400 소득 기준으로 취득 가능하며 현 수입으로 충분합니다. 영어가 통용되고 한인 커뮤니티가 활발해 첫 노마드 기지로 최적입니다."
    },
    {
      "city": "Bali (Canggu)",
      "country": "Indonesia",
      "visa_type": "E33G Social Visit Visa",
      "monthly_cost": 1400,
      "score": 7,
      "why": "짱구 지역은 코워킹 인프라가 뛰어나고 전 세계 노마드가 모이는 허브입니다. 단기 체류는 E33G 비자 반복 갱신이 현실적인 방법입니다."
    }
  ],
  "visa_checklist": [
    "여권 잔여 유효기간 18개월 이상 확인",
    "고용계약서 또는 프리랜서 계약서 영문 공증",
    "최근 3개월 급여명세서 영문 번역본 준비",
    "해외 체류 건강보험 가입 (SafetyWing 권장)",
    "말레이시아 DE Nomad Visa 온라인 사전 신청"
  ],
  "budget_breakdown": {
    "rent": 550,
    "food": 300,
    "cowork": 100,
    "misc": 150
  },
  "first_steps": [
    "여권 유효기간 확인 후 필요 시 갱신 신청",
    "SafetyWing Nomad Insurance 가입 ($56/월)",
    "말레이시아 DE Nomad Visa 공식 사이트에서 자격 요건 셀프 체크",
    "치앙마이 Airbnb 첫 한 달 예약 후 현지에서 월세 전환"
  ]
}"""
    },
    {
        "role": "user",
        "content": (
            "국적: Korean | 월 수입: $6,000 | "
            "라이프스타일: 도심, 영어권, 안전, 고속 인터넷 | 기간: 3년 장기 이민\n"
            "위 프로필에 맞는 JSON 추천을 출력하세요."
        )
    },
    {
        "role": "assistant",
        "content": """{
  "top_cities": [
    {
      "city": "Lisbon",
      "country": "Portugal",
      "visa_type": "D8 Digital Nomad Visa + NHR 세제",
      "monthly_cost": 2600,
      "score": 9,
      "why": "D8 비자 소득 기준을 크게 초과하며 NHR 혜택으로 외국 소득에 20% 단일세율이 10년간 적용됩니다. EU 영주권 경로가 열리고 영어 환경도 양호합니다."
    },
    {
      "city": "Tallinn",
      "country": "Estonia",
      "visa_type": "Digital Nomad Visa + e-Residency",
      "monthly_cost": 2200,
      "score": 8,
      "why": "디지털 노마드 비자와 e-Residency를 병행하면 EU 기반 법인 설립이 가능합니다. 인터넷 인프라가 EU 최상급이며 영어 소통이 원활합니다."
    },
    {
      "city": "Barcelona",
      "country": "Spain",
      "visa_type": "Startup Law Digital Nomad Visa",
      "monthly_cost": 2900,
      "score": 8,
      "why": "베케리아 법으로 외국 소득에 4년간 24% 단일세율이 적용됩니다. 유럽 최고의 노마드 씬과 지중해 라이프스타일을 동시에 누릴 수 있습니다."
    }
  ],
  "visa_checklist": [
    "여권 유효기간 36개월 이상 확인",
    "D8 비자: 고용계약서 + 3개월 급여명세서 영문 준비",
    "NHR 세제: 포르투갈 도착 90일 이내 세무청 신청",
    "범죄경력증명서 발급 + 아포스티유 인증",
    "포르투갈어 기초 학습 앱 시작 (Duolingo 30일)"
  ],
  "budget_breakdown": {
    "rent": 1400,
    "food": 600,
    "cowork": 250,
    "misc": 350
  },
  "first_steps": [
    "포르투갈 대사관 D8 비자 신청 서류 공식 확인",
    "NHR 전문 세무사 무료 상담 예약",
    "리스본 단기 1개월 테스트 체류 후 장기 계약 전환",
    "e-Residency 병행 신청으로 EU 법인 설립 준비"
  ]
}"""
    },
]
