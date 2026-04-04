# CHANGELOG

## [2026-04-04 21:30 KST] — 진입점 분리 + 로컬스토리지 전환 + Step2 롤백

### 변경 파일
- `app/[locale]/page.tsx` : 랜딩 페이지 전면 재작성 (진입점 2개 분리)
- `app/[locale]/onboarding/quiz/page.tsx` : sessionStorage → localStorage 전환
- `app/[locale]/onboarding/form/page.tsx` : sessionStorage → localStorage 전환 + "다시 하기" 링크 추가
- `app/[locale]/result/page.tsx` : Step 2 API 연결 시도 후 롤백 → alert 원복

### 작업 요약
- 무엇을: 랜딩 진입점 분리, 페르소나 저장 방식 전환, Step 2 API 롤백
- 왜: 퀴즈/직접진입 분기 UX 구현 + 재방문 시 페르소나 유지 + Step 2는 원래 기획(타로카드 UX)으로 재설계 필요 판단
- 영향 범위: 랜딩, 온보딩 퀴즈/폼, result 페이지

### 주요 결정사항
- 페르소나는 LLM 미연동 상태로 UX 경험 역할만 유지 (옵션 B 확정)
- LLM 재도입 시점 + 페르소나 백엔드 연동 방식은 별도 세션에서 논의
- 더 알아보기(Step 2)는 현재 구현 폐기. 타로카드 UX 기획으로 재설계 예정
- Google OAuth 연동은 로컬스토리지 브리지 완료 후 다음 우선순위

### 다음 세션 참고사항
- 더 알아보기 → 타로카드 UX 재설계 (별도 세션)
- LLM 재도입 시점 논의 (별도 세션)
- Google OAuth 프론트엔드 연동
- 페르소나 결과 공유 기능

---

## [2026-04-04 20:10 KST] — result 페이지 전면 재설계

### 변경 파일
- `backend/recommender.py` : city_scores.json + visa_db.json 필드 top_cities에 병합
- `backend/data/city_descriptions.json` : 50개 도시 한국어 소개 텍스트 생성
- `app/[locale]/result/page.tsx` : result 페이지 카드 구조 전면 재설계

### 작업 요약
- 무엇을: result 페이지 정보 레이어 + 서술 레이어 분리 재설계
- 왜: 팩트 나열에서 "노마드 선배의 조언" 구조로 전환, 신뢰+영감 동시 제공
- 영향 범위: result 페이지 전체, 백엔드 API 응답 구조

### 주요 변경사항
- 추천 점수(score) 제거
- 백엔드 city_scores/visa_db 필드 API 응답에 병합
  (internet_mbps, safety_score, english_score, stay_months, renewable 등)
- 50개 도시 소개 텍스트 city_descriptions.json으로 관리
- 카드 구조: 인사이트 → 정보 블록 → 서술 블록(도시소개+조언) → 링크
- 한화 환산 예산 표시 (약 {n}만원)
- 소득 대비 생활비 비율 조언 (소득의 약 n%)
- 인사이트/조언 중복 방지 로직
- 더 알아보기 → 버튼 추가 (Step 2 API 연결 미착수)
- 데이터 출처 표시 (Numbeo, NomadList)

### 다음 세션 참고사항
- 더 알아보기 → Step 2 API(/api/detail) 연결 미착수
- 페르소나 결과 공유 기능 미구현
- Google OAuth 프론트엔드 연동 미착수

---

## [2026-04-04 00:10 KST] — 폼 UX 전면 재설계

### 변경 파일
- `app/[locale]/onboarding/form/page.tsx` : 폼 6스텝 → 4스텝 재설계 전면 교체

### 작업 요약
- 무엇을: 폼 스텝 구조 재설계 + 불필요 필드 제거 + 소득 구간 버튼화
- 왜: 백엔드 API 스펙 분석 결과 실질 영향 없는 필드 정리, 월 소득 타이핑 제거
- 영향 범위: 온보딩 폼 전체 UX, API 전송 데이터 구조

### 주요 변경사항
- Step 1 "기본 정보" 제거 (nationality/languages/dual_nationality 고정값 처리)
- readiness_stage, income_type 제거
- 월 소득 숫자 입력 → 6개 구간 버튼 2×3 그리드로 교체
- 비공개 선택 시 추천 제한 안내 문구 노출
- 동행 조건 조건부 필드 추가 (children_ages, has_spouse_income, spouse_income_krw)
- 텍스트 전면 수정 (노마드 톤으로 통일)
- 퀴즈 버튼과 동일한 레이아웃/스타일 적용

### 다음 세션 참고사항
- 전체 플로우 end-to-end 테스트 필요 (폼 → API → result 페이지)
- result 페이지 UX 디테일 검토 필요
- 페르소나 결과 공유 기능 미구현
- Google OAuth 프론트엔드 연동 미착수

---

## [2026-04-03 23:00 KST] — 디자인 시스템 Amber Mono 2.0 전환 + 퀴즈/결과 페이지 디테일

### 변경 파일
- `app/globals.css` : Amber Mono 2.0 CSS 변수 전면 교체, accent hover primary hue 조정
- `app/layout.tsx` : Geist Mono(영문) + Noto Serif KR(한글) 폰트 조합 적용
- `components/onboarding/quiz-card.tsx` : hover/on-click 버튼 상태 정의
- `components/onboarding/persona-result-card.tsx` : 카드 border-l-4 accent line, 서브텍스트 수정

### 작업 요약
- 무엇을: MX-Brutalist → Amber Mono 2.0 컬러 시스템 전환 + 폰트 조합 확정
- 왜: 한글 폰트 호환성 + 아날로그 메모장 감성 + 브루탈리스트 무게감 조정
- 영향 범위: 프론트엔드 전체 스타일링

### 다음 세션 참고사항
- 다음 작업: /onboarding/form → 백엔드 API 연결
- 퀴즈 선택지 버튼 hover(accent)/on-click(primary) 상태 확정됨
- 결과 페이지 카드 border-l-4 primary accent line 적용됨

---

## [2026-04-03 KST] — UI 리디자인 + API 연결 완료

### 변경 파일
- `app/[locale]/layout.tsx` : 폰트 Noto Serif KR 단일 폰트로 교체
- `app/globals.css` : 세계之外 테마 토큰 전면 교체, dark 강제 해제
- `app/[locale]/onboarding/quiz/page.tsx` : 이전 버튼 추가, 레이아웃 수정, max-w-sm
- `app/[locale]/onboarding/result/page.tsx` : 결과 카드 위계 재설계, 카드 순서 변경 (도시→일→순간→가치)
- `components/onboarding/persona-result-card.tsx` : description/city/work/value/moment string→string[] 배열 구조로 변경
- `data/personas.ts` : 전체 필드 string[] 배열 구조로 변환
- `app/api/recommend/route.ts` : Next.js API Route 프록시 신규 생성
- `app/[locale]/onboarding/form/page.tsx` : API 호출 연결, 로딩/에러 처리
- `app/[locale]/result/page.tsx` : 도시 카드 3개 + 비교표 구현, 마크다운 제거

### 작업 요약
- 무엇을: 테마 라이트 모드 전환 + Noto Serif KR 폰트 확정 + 퀴즈/결과 UX 개선 + 백엔드 API 연결
- 왜: 다크 테마 감성 미달, 한글 폰트 미지원, API 연결 CORS 문제 해결
- 영향 범위: 프론트엔드 전체 + 백엔드 API 연결

### 다음 세션 참고사항
- 퀴즈 페이지 수직 정렬 마무리 필요
- 폼 페이지 UX 디테일 미완
- 페르소나 결과 공유 기능 미구현
- Google OAuth 프론트엔드 연동 미착수
- 테마 재선정 보류 (Noto Serif KR 확정, 컬러는 추후 판단)
- 로컬 테스트는 production 빌드 권장 (dev 서버 hydration 이슈)

---

## [2026-04-03 KST] — 디자인 시스템 전면 교체 + 퀴즈/결과 페이지 리디자인

### 변경 파일
- `app/layout.tsx` : 폰트 Instrument_Serif 단일 교체, dark 클래스 제거
- `app/globals.css` : CSS 변수 전면 교체 (oklch 색상, shadow, tracking)
- `app/[locale]/onboarding/quiz/page.tsx` : 레이아웃 리디자인 (max-w-sm, 수직 중앙, 이전 버튼)
- `app/[locale]/onboarding/quiz/result/page.tsx` : 처음부터 다시하기 버튼, i18n 제거, 스타일 통일
- `components/onboarding/quiz-card.tsx` : 선택지 스타일 통일 (text-foreground, font-medium)
- `components/onboarding/persona-result-card.tsx` : 결과 카드 sm:grid-cols-2, 디자인 변수 교체
- `components/onboarding/progress-bar.tsx` : 디자인 변수 교체
- `data/quiz-questions.ts` : 퀴즈 텍스트 수정 (줄바꿈, 문구 변경)

### 작업 요약
- 무엇을: shadcn 테마 기반 디자인 시스템 전면 교체 + 퀴즈/결과 페이지 레이아웃 리디자인
- 왜: v21 테마 적용 + 모바일 중심 UX 개선 + Instrument Serif 폰트 통일
- 영향 범위: 프론트엔드 전체 스타일링, 온보딩 퀴즈/결과 페이지

### 다음 세션 참고사항
- 다음 작업: /onboarding/form → 백엔드 API 연결
- 페르소나 결과 공유 기능 미구현 (자리만 잡혀 있음)
- 로컬 테스트는 production 빌드로 해야 함 (dev 서버는 네트워크 접속 시 hydration 실패)
- 기존 온보딩 CSS 변수(--onboarding-*) 완전 삭제됨, 참조하는 곳 없는지 확인 필요

---

## [2026-04-03 KST] — Framer Motion 인터랙션 추가 (퀴즈 전환 + 결과 등장)

### 변경 파일
- `app/[locale]/onboarding/quiz/page.tsx` : AnimatePresence + motion.div 퀴즈 카드 페이드 전환
- `components/onboarding/persona-result-card.tsx` : 타이틀 + 4개 축 카드 stagger 등장 애니메이션

### 작업 요약
- 무엇을: 퀴즈 문항 전환 페이드 (아웃 0.25s / 인 0.35s) + 결과 카드 순차 등장 (0.3s 간격 stagger, fadeUp)
- 왜: 온보딩 UX 인터랙션 완성
- 영향 범위: 퀴즈 페이지, 결과 페이지

### 다음 세션 참고사항
- 다음 작업: /onboarding/form → 백엔드 API 연결
- 페르소나 결과 공유 기능 미구현 (자리만 잡혀 있음)
- 로컬 테스트는 production 빌드로 해야 함 (dev 서버는 네트워크 접속 시 hydration 실패)

---

## [2026-04-03 KST] — 페르소나 결과 페이지 콘텐츠 + 퀴즈 데이터 업데이트

### 변경 파일
- `data/personas.ts` : 페르소나 5종 전체 콘텐츠 업데이트 (description, city, work, value, moment)
- `data/quiz-questions.ts` : 퀴즈 7문항 재설계 + 페르소나 매핑 순서 섞기 적용
- `components/onboarding/persona-result-card.tsx` : traits 3개 → 4개 축 구조로 변경

### 작업 요약
- 무엇을: 페르소나별 4개 축 콘텐츠 확정 및 결과 페이지 구조 변경
- 왜: UX 논의에서 확정된 "도시/일/가치/순간" 4축 구조 반영
- 영향 범위: 퀴즈 결과 페이지 전체 경험

### 다음 세션 참고사항
- 다음 작업: Framer Motion 인터랙션 (퀴즈 슬라이드, 결과 등장)
- 다음 작업: /onboarding/form → 백엔드 API 연결
- 페르소나 결과 공유 기능 미구현 (자리만 잡혀 있음)

---

## [2026-03-30 KST] — 온보딩 플로우 골격 + 스타일링 구현

### 변경 파일
- `frontend/src/app/layout.tsx` : Playfair Display, 다크 테마, 메타데이터
- `frontend/src/app/globals.css` : 온보딩 CSS 변수 12개 추가
- `frontend/src/data/personas.ts` : 페르소나 5종 상수
- `frontend/src/data/quiz-questions.ts` : 퀴즈 7문항 + calculatePersona()
- `frontend/src/data/form-options.ts` : 폼 선택지 10종
- `frontend/src/components/onboarding/*` : 5개 컴포넌트 생성
- `frontend/src/app/onboarding/**` : 퀴즈/결과/폼 페이지
- `frontend/src/app/result/**` : placeholder 페이지

### 작업 요약
- 무엇을: 투트랙 온보딩 플로우 전체 골격 및 스타일링 구현
- 왜: UX 논의에서 확정된 페르소나 진단 → 정밀 분석 구조 반영
- 영향 범위: 프론트엔드 전체 온보딩 경험

### 다음 세션 참고사항
- persona-result-card traits 텍스트 색상은 primary로 변경 완료
- 다음 작업: Framer Motion 인터랙션
- 다음 작업: /onboarding/form → 백엔드 API 연결

---

## [2026-03-30 KST] — 서비스 포지셔닝 확정

### 작업 요약
- 무엇을: 핵심 포지셔닝 및 UX 설계 필터 정의
- 왜: 온보딩 플로우 논의 중 MBTI/자아탐색 인사이트에서 도출
- 영향 범위: 전체 UX 설계 기준, 향후 기능 추가 판단 기준

### 다음 세션 참고사항
- 모든 기능 설계 시 "유저의 나 서사를 강화하는가?" 필터 적용
- 페르소나 결과 공유 기능은 자연 유입 경로로 우선 구현 대상

---

## [2026-03-30 KST] — 세션 문서 관리 체계 초기 설정

### 변경 파일
- `.claude/session/CONTEXT.md` : 프로젝트 현황 문서 최초 생성
- `.claude/session/CHANGELOG.md` : 작업 이력 로그 최초 생성
- `CLAUDE.md` : 세션 문서 관리 지시문 추가

### 작업 요약
- 무엇을: .claude/session/ 디렉토리에 CONTEXT.md, CHANGELOG.md 초기 생성 및 CLAUDE.md에 관리 규칙 추가
- 왜: 세션 간 컨텍스트 유지 및 작업 이력 추적을 위한 체계 수립
- 영향 범위: 모든 후속 세션의 작업 완료 프로세스

### 다음 세션 참고사항
- 작업 완료 시 반드시 Step 1~4 (CHANGELOG → CONTEXT → scp → git push) 순서 준수
- myserver SSH alias 정상 작동 확인 필요

---
