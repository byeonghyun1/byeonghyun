# AI 콘텐츠 디자인 자동화

디자인 작업을 AI로 자동화하는 프로젝트입니다. 두 개의 독립 프로젝트로 구성되어 있습니다.

---

## 프로젝트 구성

### 1. Design Variation Agent (진행 중)

기준 디자인 1개를 Figma에서 읽어서, 각 매체에 맞는 다양한 사이즈로 레이아웃을 자동 재조정하고, Figma에 편집 가능한 프레임으로 생성하는 에이전트.

**핵심 흐름:** Figma 원본 읽기 → 레이아웃 분석 → 사이즈별 변환 → 대시보드 검수 → Figma 생성

**현재 상태:** 아키텍처 설계 및 구조 보강 완료, 프로토타입 테스트 1회 완료

**설계서 구성 (21개 섹션):** 전체 흐름, 매체 프리셋, 대시보드 검수, 모듈 간 인터페이스, 검증 파이프라인(플러그인 방식), 에러 처리, 피드백 학습, 규칙 충돌 해결

```
design_variation_agent/
├── ARCHITECTURE.md       ← 전체 설계서 (21개 섹션)
├── media_presets/        ← 매체별 사이즈 & 규정
├── engine/               ← 변환 엔진
│   └── checks/           ← 검증 체크 모듈 (플러그인 방식)
├── dashboard/            ← 검수 대시보드
├── feedback/             ← 피드백 & 학습 데이터
│   └── learned_rules.json ← 학습 규칙
├── logs/                 ← 에러 로그
└── output/               ← 결과물
```

### 2. Card News Generator (1차 완성)

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
| Design Variation 설계서 | `design_variation_agent/ARCHITECTURE.md` | 신규 프로젝트 전체 설계 |
| Card News 설계서 | `ARCHITECTURE.md` | 이전 프로젝트 기술 설계 |
| 대화 기록 | `conversation_history_full.md` | 이전 프로젝트 전체 진행 과정 |

---

## 기술 스택

- **Python** — 핵심 엔진
- **Figma MCP** — 디자인 읽기/쓰기
- **Anthropic Claude API** — AI 카피 생성, 레이아웃 판단
- **SVG/PNG** — 미리보기 렌더링

---

마지막 업데이트: 2026-04-23
