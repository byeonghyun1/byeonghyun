# AI 콘텐츠 디자인 자동화

디자인 작업을 AI로 자동화하는 프로젝트입니다. 세 개의 독립 프로젝트로 구성되어 있습니다.

---

## 프로젝트 구성

### 1. Banner Maker (진행 중) ⭐

키비주얼 이미지 + 텍스트만 넣으면 다양한 사이즈의 배너를 자동으로 만들어주는 에이전트. 비디자이너(기획자, 마케터)도 웹 대시보드에서 쉽게 사용 가능.

**핵심 흐름:** 이미지 업로드 → 텍스트 입력 → 사이즈 선택 → 자동 레이아웃 → PNG + Figma 출력

**현재 상태:** 아키텍처 설계 완료, 구현 준비 중

```
banner_maker/
├── ARCHITECTURE.md      ← 전체 설계서 (8파트)
├── engine/              ← 핵심 엔진 (이미지 분석, 레이아웃, 렌더링)
├── templates/           ← 레이아웃 템플릿
├── presets/             ← 매체별 사이즈 & 규정
├── dashboard/           ← 웹 대시보드 UI
├── checks/              ← 검증 체크 모듈 (플러그인 방식)
├── feedback/            ← 피드백 & 학습 데이터
├── logs/                ← 에러 로그
└── output/              ← 생성된 결과물
```

### 2. Design Variation Agent (보관)

기준 디자인 1개를 Figma에서 읽어서, 각 매체에 맞는 다양한 사이즈로 레이아웃을 자동 재조정하는 에이전트.

**현재 상태:** 아키텍처 설계 완료, 프로토타입 테스트 1회 완료. Banner Maker로 방향 전환.

```
design_variation_agent/
├── ARCHITECTURE.md       ← 전체 설계서 (6파트)
├── media_presets/        ← 매체별 사이즈 & 규정
├── engine/               ← 변환 엔진
│   └── checks/           ← 검증 체크 모듈
├── dashboard/            ← 검수 대시보드
├── feedback/             ← 피드백 & 학습 데이터
├── logs/                 ← 에러 로그
└── output/               ← 결과물
```

### 3. Card News Generator (보관)

자연어 입력으로 카드뉴스/배너/포스터를 자동 생성하는 프로토타입. 3축 아키텍처(콘텐츠 유형 x 브랜드 x 사이즈)로 설계.

**현재 상태:** 프로토타입 완성, 별도 보관 중

```
card_news_generator/
├── engine/               ← 핵심 엔진
├── content_types/        ← 카드뉴스, 배너, 포스터
├── brands/               ← 알바몬, 잡코리아, 워스피어
├── templates/            ← HTML 템플릿
└── output/               ← 생성된 결과물
```

---

## 설계 문서

| 문서 | 위치 | 내용 |
|---|---|---|
| Banner Maker 설계서 | `banner_maker/ARCHITECTURE.md` | 현재 진행 프로젝트 전체 설계 |
| Design Variation 설계서 | `design_variation_agent/ARCHITECTURE.md` | 이전 프로젝트 설계 (보관) |
| Card News 설계서 | `ARCHITECTURE.md` | 최초 프로젝트 기술 설계 (보관) |

---

## 기술 스택

- **Python** — 핵심 엔진
- **React + Tailwind** — 웹 대시보드
- **Python FastAPI** — 백엔드 API
- **Figma MCP** — Figma 읽기/쓰기
- **Claude Vision API** — 이미지 분석, 레이아웃 판단
- **Pillow** — 이미지 렌더링

---

마지막 업데이트: 2026-04-24
