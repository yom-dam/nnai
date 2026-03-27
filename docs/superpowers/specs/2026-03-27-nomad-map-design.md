# 노마드 방명록 지도 — 설계 문서

**Date:** 2026-03-27
**Status:** Approved

---

## 1. 개요

헤더의 지구본 아이콘을 클릭하면 세계지도 모달이 열리고, 사용자가 방문한 도시를 검색·핀으로 기록해 자신만의 디지털 노마드 여정 지도를 완성하는 기능.

---

## 2. 사용자 플로우

```
지구본 클릭 → 세계지도 모달 오픈
  → (비로그인) 상단 CTA 배너: "로그인하고 나만의 디지털 노마드 지도를 완성해보세요!"
  → Google 로그인 → OAuth 콜백 → 세션 저장
  → 도시 검색 (검색창)
      → 로컬 퍼지서치 (즉각 결과) + Nominatim API (전 세계 보완)
      → 자동완성 드롭다운 → 도시 선택
  → 지도 fly-to 애니메이션
  → 핀 추가 팝업
      - 도시명 (자동입력, 읽기전용)
      - 한줄평 (최대 60자)
      - 위치 권한 상태 표시 (현재 위치 ↔ 도시 거리)
  → 저장 → SQLite DB 기록
  → 지도에 주황 핀 드롭 + 리플 애니메이션
  → 이전 핀들과 선으로 연결 (시간순)
```

---

## 3. 아키텍처

### 3.1 Frontend (Gradio HTML 삽입)

`ui/layout.py`의 헤더에 지구본 버튼 + 세계지도 모달 HTML을 `gr.HTML`로 주입.

- **지도 라이브러리:** Leaflet.js (CDN, 실제 지도 타일)
- **지도 타일:** OpenStreetMap (다크 필터 CSS 적용)
- **도시 검색:**
  - 1순위: 로컬 CITIES 배열 퍼지서치 (즉각 응답)
  - 2순위: Nominatim API (`nominatim.openstreetmap.org/search`) 디바운스 400ms
  - 두 결과 병합 (중복 제거)
- **위치 권한:** `navigator.geolocation.getCurrentPosition()`
  - 허용 시: 선택 도시까지 거리(km) 계산 → 팝업에 표시
  - 거부 시: 경고 표시, 저장은 허용 (위치 검증은 soft-check)
- **핀 시각화:**
  - 파란 점: 커뮤니티 전체 핀 (집계, 클릭 시 "N명 방문" 팝업)
  - 주황 점: 내 핀 (맥박 애니메이션)
  - 주황 선: 내 핀들을 추가 시간순으로 연결

### 3.2 Backend (Python / Gradio + FastAPI)

Gradio의 `gr.mount_gradio_app()`으로 FastAPI와 병합.

```
app (FastAPI)
├── /auth/google          → Google OAuth redirect
├── /auth/google/callback → 토큰 교환 → 세션 쿠키 발급
├── /api/pins             → GET (내 핀 목록), POST (핀 저장)
├── /api/pins/community   → GET (커뮤니티 핀 집계)
└── /                     → Gradio 앱 마운트
```

### 3.3 DB 스키마 (SQLite — `data/users.db`)

```sql
CREATE TABLE users (
  id          TEXT PRIMARY KEY,   -- Google sub (고유 ID)
  email       TEXT,
  name        TEXT,
  picture     TEXT,
  created_at  TEXT
);

CREATE TABLE pins (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     TEXT NOT NULL REFERENCES users(id),
  city        TEXT NOT NULL,       -- "쿠알라룸푸르"
  display     TEXT,                -- "Kuala Lumpur, Malaysia"
  note        TEXT,                -- 한줄평
  lat         REAL NOT NULL,
  lng         REAL NOT NULL,
  user_lat    REAL,                -- 저장 시점 사용자 위치 (optional)
  user_lng    REAL,
  created_at  TEXT NOT NULL        -- ISO 8601
);
```

---

## 4. Google OAuth 설정

- **라이브러리:** `authlib` (Python) + `httpx`
- **환경변수:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SECRET_KEY`
- **세션:** `itsdangerous` signed cookie (24h TTL)
- **Callback URL:** `http://localhost:7860/auth/google/callback` (개발) / HF Spaces URL (배포)

---

## 5. 새 파일 목록

| 파일 | 역할 |
|------|------|
| `ui/globe_map.py` | 지도 모달 HTML/JS 생성 함수 |
| `api/auth.py` | Google OAuth FastAPI 라우터 |
| `api/pins.py` | 핀 CRUD FastAPI 라우터 |
| `utils/db.py` | SQLite 연결 + 마이그레이션 |
| `server.py` | FastAPI 앱 생성 + Gradio 마운트 |

---

## 6. 수정 파일

| 파일 | 변경 내용 |
|------|---------|
| `ui/layout.py` | 헤더에 지구본 버튼 + 모달 HTML 삽입, `/api/pins` 호출 JS 추가 |
| `app.py` | `server.py`의 FastAPI 앱 사용으로 진입점 변경 |
| `requirements.txt` | `authlib`, `httpx`, `itsdangerous` 추가 |

---

## 7. 핵심 동작 세부 사항

### 도시 검색
- 로컬 퍼지서치: 쿼리 문자가 도시명에 순서대로 포함되면 매칭
- Nominatim: 400ms 디바운스 후 호출, `accept-language: ko,en`
- 결과 최대 7개, 좌표 0.1도 반경 중복 제거

### 핀 저장 시 JS → Backend 흐름
```js
POST /api/pins
Body: { city, display, note, lat, lng, user_lat, user_lng }
→ 200 { id, created_at }
→ 지도에 핀 렌더링 + 여정선 갱신
```

### 페이지 로드 시 내 핀 복원
```js
GET /api/pins  →  [{ city, note, lat, lng, created_at }, ...]
→ 시간순 정렬 → 주황 핀 + 선 렌더링
```

### 커뮤니티 핀
```js
GET /api/pins/community  →  [{ lat, lng, city, count }, ...]
→ 파란 점으로 렌더링 (클릭 시 "N명 방문" 팝업)
```

---

## 8. 범위 외 (이번 구현에서 제외)

- 핀 삭제/수정
- 다른 유저의 여정 보기
- 위치 검증 강제 (soft-check만)
- 사진 첨부
