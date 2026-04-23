# Design Variation Agent — 아키텍처 설계서

## 1. 프로젝트 목표

기준 디자인 1개를 Figma에서 읽어와서,
각 매체에 맞는 다양한 사이즈로 레이아웃을 재조정하고,
Figma에 편집 가능한 프레임으로 자동 생성하는 에이전트.

---

## 2. 설계 원칙

**유연성**: 새 매체/사이즈가 추가되어도 엔진 코드는 수정하지 않는다.
**분리**: 매체 규정(설정)과 변환 로직(엔진)은 분리한다.
**편집 가능**: 출력물은 이미지가 아니라, Figma에서 수정 가능한 레이어 구조다.
**검수 우선**: AI 결과물은 반드시 디자이너 검수를 거친 후 최종 생성한다.

---

## 3. 전체 흐름

```
[1] 입력
    Figma 원본 프레임 URL/ID + 디자이너 부연설명
    + 타겟 사이즈 선택 (전체 / 카테고리 / 개별)
    + 생성할 Figma 파일 URL (결과물을 넣을 위치)
         │
         ▼
[2] 분석 (Analyzer)
    Figma에서 프레임 읽기 (모든 레이어)
    → 요소 분류: 제목/본문/CTA/로고/이미지/장식/배경
    → 공간 관계 파악: 정렬, 간격, 비율
    → 디자이너 노트 반영
         │
         ▼
[3] 변환 (Variation Engine)
    타겟 매체 프리셋 로드 (카테고리 → 사이즈 → 규정)
    → 레이아웃 재계산: 위치, 크기, 폰트, 순서
    → 매체 규정 적용: 최소 폰트, 여백, 텍스트 비율
    → AI 판단: 요소 순서 변경, 숨기기, 텍스트 축약
         │
         ▼
[4] 미리보기 대시보드 (검수 단계) ⭐ 핵심
    사이즈별 미리보기를 한 화면에 보여줌
    → 디자이너가 각 사이즈별로 검수
    → 개별 승인 / 수정 요청 / 재생성 선택
    → 부분 수정 후 재미리보기 가능
         │
         ▼
[5] 최종 생성 (Figma Writer)
    디자이너가 지정한 Figma 파일에 "AI Variation" 전용 페이지 생성
    → 승인된 사이즈만 해당 페이지에 프레임 생성
    → 기존 페이지는 건드리지 않음
    → 모든 요소가 편집 가능한 레이어로 유지
    → 디자이너가 바로 수정·확인·내보내기 가능
```

---

## 4. 매체 프리셋 구조

### 핵심: 카테고리 → 사이즈 → 규정

매체를 카테고리로 분류하고, 각 카테고리 안에 사이즈를 나열합니다.
새 사이즈는 설정 파일에 항목 하나 추가로 끝. 엔진은 건드리지 않습니다.

```
media_presets/
├── sns.py                ← SNS 카테고리
│   ├── instagram_feed      1080x1080
│   ├── instagram_story     1080x1920
│   ├── instagram_reels     1080x1920
│   ├── facebook_cover      820x312
│   ├── youtube_thumbnail   1280x720
│   └── kakao_channel       720x720
│
├── ads.py                ← 광고/배너 카테고리
│   ├── web_banner          1200x628
│   ├── gdn_square          300x250
│   ├── gdn_leaderboard     728x90
│   ├── naver_da            300x250
│   └── kakao_bizboard      1029x258
│
├── print.py              ← 인쇄/포스터 카테고리
│   ├── A4_vertical         595x842
│   ├── A4_horizontal       842x595
│   └── A3_vertical         842x1191
│
└── etc.py                ← 기타 (필요시 추가)
    ├── detail_page         860xN (가변)
    └── email_header        600x200
```

### 사이즈별 규정 데이터 구조

각 사이즈마다 다음 정보를 담습니다:

```python
{
    "name": "instagram_feed",
    "display_name": "인스타그램 피드",
    "category": "sns",
    "width": 1080,
    "height": 1080,
    "rules": {
        "min_font_size": 24,        # 최소 폰트 크기 (px)
        "max_text_ratio": 0.20,     # 전체 면적 대비 텍스트 비율
        "padding": {                 # 안전 여백
            "top": 40, "bottom": 40,
            "left": 40, "right": 40
        },
        "cta_position": "bottom",   # CTA 기본 위치
        "logo_position": "top-right", # 로고 기본 위치
        "notes": "정사각형. 텍스트 20% 이내 권장."
    }
}
```

### 새 매체/사이즈 추가 방법

1. 기존 카테고리에 사이즈 추가 → 해당 카테고리 파일에 항목 하나 추가
2. 새 카테고리 추가 → 새 파일 하나 만들고 레지스트리에 등록
3. 엔진 코드 수정: 0줄

---

## 5. 디자이너 부연설명 시스템

Figma에서 읽어온 디자인만으로는 AI가 알 수 없는 것들이 있습니다.
디자이너가 추가 지시를 내릴 수 있는 구조입니다.

### 입력 예시

```
기준 디자인: [Figma 프레임 링크]

부연설명:
- 제목 텍스트는 줄여도 됨
- 로고는 항상 우상단에 고정
- 하단 CTA 버튼은 모든 사이즈에 유지
- 배경 이미지는 잘라도 괜찮음
- GDN 300x250에서는 본문 텍스트 숨겨도 됨
```

### 내부 처리

부연설명은 변환 엔진에 "우선 규칙"으로 전달됩니다.
AI가 레이아웃을 재구성할 때 이 규칙을 최우선으로 따릅니다.

우선순위: 디자이너 부연설명 > 매체 규정 > AI 자동 판단

---

## 6. 미리보기 대시보드 (검수 시스템)

### 왜 필요한가

AI가 만든 결과물을 무검수로 Figma에 바로 생성하면 안 된다.
디자이너가 확인하고 승인한 것만 최종 생성해야 한다.

### 대시보드 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│  Design Variation Agent — 미리보기 대시보드                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📌 원본 디자인                                              │
│  ┌──────────┐                                               │
│  │          │  파일: 잡코리아_네이버페이_이벤트                  │
│  │  [원본]   │  크기: 1080 x 1080                            │
│  │          │  요소: 배경이미지, 캐릭터, 제목, 부제목            │
│  └──────────┘                                               │
│                                                             │
│  ─── SNS ───────────────────────────────────────────────    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │인스타피드 │  │인스타스토리│  │페이스북커버│  │유튜브썸네일│    │
│  │1080x1080 │  │1080x1920 │  │820x312   │  │1280x720  │    │
│  │          │  │          │  │          │  │          │    │
│  │[미리보기] │  │[미리보기] │  │[미리보기] │  │[미리보기] │    │
│  │          │  │          │  │          │  │          │    │
│  │ ✅ 승인  │  │ ⚠️ 수정  │  │ ✅ 승인  │  │ ❌ 재생성 │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                             │
│  ─── 광고/배너 ─────────────────────────────────────────    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ 웹배너   │  │ GDN사각  │  │카카오비즈 │                  │
│  │1200x628  │  │300x250   │  │1029x258  │                  │
│  │          │  │          │  │          │                  │
│  │[미리보기] │  │[미리보기] │  │[미리보기] │                  │
│  │          │  │          │  │          │                  │
│  │ ✅ 승인  │  │ ✅ 승인  │  │ ⚠️ 수정  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  승인: 5개  │  수정 필요: 2개  │  재생성: 1개                 │
│                                                             │
│  [ 수정 사항 적용하고 재미리보기 ]  [ 승인된 것만 Figma 생성 ]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 검수 단계별 동작

**✅ 승인** — 이 사이즈는 그대로 Figma에 생성해도 됨

**⚠️ 수정 요청** — 디자이너가 수정 지시를 남김 (예: "캐릭터 좀 더 크게", "텍스트 왼쪽 정렬로")
  → 수정 지시를 반영해서 해당 사이즈만 재생성
  → 다시 미리보기에서 확인

**❌ 재생성** — 결과가 마음에 안 들어서 처음부터 다시 생성
  → AI가 다른 레이아웃 방식으로 재시도

**최종 생성 버튼** — 승인된 사이즈만 골라서 Figma에 프레임 생성.
  수정/재생성 상태인 것은 포함하지 않음

### 검수 루프

```
미리보기 생성
     │
     ▼
디자이너 검수 ←──────────────────┐
     │                           │
     ├─ ✅ 승인 → 대기            │
     ├─ ⚠️ 수정 → 수정 반영 → 재미리보기 ─┘
     └─ ❌ 재생성 → 새로 생성 → 재미리보기 ─┘
     
모두 승인 완료
     │
     ▼
[ Figma에 최종 생성 ]
```

### 미리보기 생성 방식

대시보드의 미리보기는 실제 Figma 생성 전에 보여주는 것이므로,
가볍게 렌더링한 이미지(SVG 또는 PNG 썸네일)로 보여줍니다.
Figma에 실제 프레임을 만드는 것은 최종 승인 후에만 실행합니다.

### 대시보드 구현 방식 (추후 결정)

1단계: 이 에이전트 안에서 텍스트 기반으로 검수 (빠르게 시작)
2단계: 웹 대시보드 (HTML) — 시각적으로 미리보기 비교 가능
3단계: 독립 웹 서비스 — URL로 접속, 팀 공유 가능

---

## 7. 폴더 구조

```
design_variation_agent/
├── ARCHITECTURE.md          ← 이 파일 (설계서)
│
├── media_presets/           ← 매체 카테고리별 사이즈 & 규정
│   ├── __init__.py          ← REGISTRY (카테고리/사이즈 자동 인식)
│   ├── base.py              ← 사이즈 규정 데이터 구조 문서
│   ├── sns.py               ← SNS (인스타, 페이스북, 유튜브, 카카오)
│   ├── ads.py               ← 광고/배너 (웹배너, GDN, 네이버, 카카오)
│   └── print.py             ← 인쇄 (A4, A3, 포스터)
│
├── engine/                  ← 변환 엔진 (매체 이름 하드코딩 없음)
│   ├── __init__.py
│   ├── figma_reader.py      ← Figma 프레임 읽기 (MCP 활용)
│   ├── analyzer.py          ← 레이아웃 분석 (요소 분류, 공간 관계)
│   ├── layout_engine.py     ← 레이아웃 재계산 (핵심 변환 로직)
│   ├── validator.py         ← 검증 실행기 (체크 레지스트리 관리)
│   ├── preview_renderer.py  ← 미리보기 이미지 생성 (검수용)
│   ├── figma_writer.py      ← Figma에 프레임 생성 (MCP 활용)
│   ├── schema.py            ← 데이터 구조 (SourceFrame, AnalyzedDesign, LayoutPlan 등)
│   └── checks/              ← 검증 체크 모듈 (플러그인 방식)
│       ├── __init__.py      ← 레지스트리 (폴더 내 모듈 자동 등록)
│       ├── output_location.py
│       ├── focus_area.py
│       ├── safe_zone.py
│       ├── text_overflow.py
│       ├── layer_structure.py
│       ├── source_version.py
│       ├── layout_linked.py
│       └── bounds_check.py
│
├── dashboard/               ← 미리보기 대시보드 (검수 UI)
│   ├── app.py               ← 대시보드 서버 (1단계: 간단한 웹 페이지)
│   └── templates/           ← 대시보드 HTML 템플릿
│       └── review.html      ← 검수 화면
│
├── feedback/                ← 피드백 & 학습 데이터
│   ├── history.jsonl        ← 모든 검수 기록 (시간순)
│   ├── patterns.json        ← 추출된 패턴 요약
│   ├── learned_rules.json   ← 학습으로 추가된 규칙들
│   ├── conflicts.jsonl      ← 규칙 충돌 기록
│   └── snapshots.json       ← 원본 스냅샷 기록
│
├── logs/                    ← 에러 로그
│   └── errors.jsonl         ← 에러 기록 (모듈별, 시간순)
│
├── output/                  ← 미리보기 이미지
│   └── .gitkeep
│
└── main.py                  ← 실행 진입점
```

---

## 8. 핵심 데이터 구조

### VariationRequest (입력 양식)

```
VariationRequest:
  figma_url       : "https://figma.com/..."   ← 원본 프레임 링크 (필수)
  output_figma_url: "https://figma.com/..."   ← 결과물 생성할 Figma 파일 링크 (필수)
  designer_notes  : ["제목 줄여도 됨", ...]    ← 부연설명 (선택)
  target_sizes    : ["all"] 또는 ["instagram_feed", "web_banner"]
                                               ← 타겟 사이즈 (필수)
  target_category : "sns" 또는 "" (전체)        ← 카테고리 필터 (선택)
```

### VariationResult (결과)

```
VariationResult:
  source_frame    : { 원본 프레임 정보 }
  variations      : [
    {
      size: "instagram_feed",
      preview_path: "output/preview_instagram_feed.png",
      layout_data: { ... 레이아웃 계산 결과 ... },
      review_status: "approved" | "revision" | "rejected" | "pending",
      revision_note: "",            ← 수정 요청 시 디자이너 코멘트
      figma_frame_id: "",           ← 최종 생성 후에만 채워짐
    },
    ...
  ]
  designer_notes_applied : ["제목 줄여도 됨" → 적용됨, ...]
```

### ReviewStatus (검수 상태)

```
pending   → 아직 검수 전 (미리보기 생성 직후)
approved  → ✅ 승인됨 (Figma 생성 대기)
revision  → ⚠️ 수정 요청 (디자이너 코멘트 반영 후 재생성 필요)
rejected  → ❌ 재생성 (처음부터 다시)
```

---

## 9. 이미지 배치 전략 — 포커스 영역 (Focus Area)

> ⚠️ 초기 설계안입니다. 실제 구현 과정에서 변경될 수 있습니다.

### 문제

사이즈 변환 시 프레임 비율이 달라지면, 이미지가 프레임 안에서 어떤 위치·스케일로 보여야 하는지 기준이 필요하다.
(피그마에서는 이미지를 자르지 않고, 프레임이 마스크 역할을 하므로 이미지 원본은 유지됨)

### 해결: 포커스 영역

이미지에서 "반드시 보여야 하는 핵심 영역"을 한 번만 지정하면,
어떤 사이즈로 변환하든 그 영역이 이미지 배치 영역 안에 항상 들어오도록
위치와 스케일을 자동 계산한다.

### 동작 방식

```
원본 디자인 (1080x1080)
  └─ 배경 이미지에 포커스 영역 지정: "인물 중심"
       │
       ├─ 가로 배너 (1200x628) 변환 시
       │    왼쪽: 텍스트 / 오른쪽: 이미지
       │    → 포커스 영역(인물)이 오른쪽 이미지 영역 안에서 중심 잡힘
       │
       ├─ 세로 스토리 (1080x1920) 변환 시
       │    위: 텍스트 / 아래: 이미지
       │    → 포커스 영역(인물)이 아래쪽 이미지 영역 안에서 중심 잡힘
       │
       └─ 정사각 SNS (1080x1080) 변환 시
            배경 전체에 이미지
            → 포커스 영역(인물)이 화면 중심에 위치
```

### 포커스 영역 지정 방법

**1단계 (텍스트 기반)** — 디자이너가 부연설명에 텍스트로 작성
  예: "배경 이미지는 인물 위주로", "상품이 중심"
  → 에이전트가 이미지를 분석해서 해당 요소 위치를 포커스 영역으로 설정

**2단계 (시각적 도구)** — 대시보드에서 이미지 위에 드래그로 포커스 영역 지정
  → 대시보드 구현 시 같이 추가

**미지정 시** — 기본값은 이미지 중앙 (center-center)

### 레이아웃 배치와의 관계

엔진이 사이즈 비율에 따라 텍스트/이미지 배치를 자동으로 결정하지만,
디자이너가 원하는 배치가 다르면 부연설명으로 덮어쓸 수 있다.

예: 세로형인데 "위에 이미지, 아래에 텍스트로 배치해줘"
→ 부연설명이 우선 적용됨 (디자이너 부연설명 > 매체 규정 > AI 자동 판단)

### 데이터 구조

```
FocusArea:
  target_layer    : "background_image"     ← 어떤 이미지 레이어에 적용할지
  mode            : "auto" | "manual"      ← 자동 감지 / 수동 지정
  description     : "인물 중심"             ← 텍스트 기반 지정 시
  area            : { x, y, width, height } ← 시각적 도구로 지정 시 (2단계)
  fallback        : "center-center"         ← 감지 실패 시 기본값
```

---

## 10. Figma 컴포넌트/그룹 처리 전략

> ⚠️ 초기 설계안입니다. 추가 피그마 파일 학습 후 보완이 필요합니다.
> 📌 TODO: 카드뉴스, 포스터, SNS 등 다른 콘텐츠 유형의 피그마 파일도 분석해서 패턴을 추가해야 합니다.

### 문제

피그마 디자인을 읽어서 변환할 때, GROUP/FRAME/VECTOR/INSTANCE 등
다양한 노드 타입을 어떻게 해석하고 재배치할지 기준이 필요하다.

### 현재까지 학습한 패턴 (외부배너 16개 프레임 기준)

**패턴 1: 기능별 그룹핑**

루트 FRAME 아래 자식이 2~3개로, 역할별로 분리되어 있음:

```
루트 FRAME (CLIP 적용, 배경색 채움)
├── 텍스트 블록 (FRAME, AL:VERTICAL) — 21~24 nodes
├── 일러스트/장식 (GROUP, 오토레이아웃 없음) — 379~502 nodes
└── 하단 바 (FRAME, AL:HORIZONTAL) — 119 nodes (있거나 없음)
```

- 컴포넌트/인스턴스 사용 없이 플랫한 구조
- 최상위 깊이를 최소화하고, 세부 요소는 그룹 안에 포함

**패턴 2: 오토레이아웃 사용 규칙**

- 텍스트 영역 → FRAME + VERTICAL 오토레이아웃 (위→아래 쌓기)
- 하단 바/로고 영역 → FRAME + HORIZONTAL 오토레이아웃 (좌→우 나열)
- 일러스트/장식 그래픽 → GROUP, 오토레이아웃 없음 (자유 배치)
- 사이즈: 전부 FIXED
- 제약: MIN 또는 SCALE constraints

**패턴 3: 사이즈별 레이어 재배치**

```
가로형 (1200x628)  → 텍스트 좌 + 그래픽 우, 하단 바 생략, 자식 2개
정방형 (1200x1200) → 그래픽 상 + 텍스트 하, 하단 바 포함, 자식 3개
세로형 (1200x1500) → 텍스트 상 + 그래픽 하, 하단 바 생략, 자식 2개
스토리 (1080x1920) → 텍스트 상 + 그래픽 하, 하단 바 포함, 자식 3개
SNS   (1080x1080) → 그래픽 상 + 텍스트 하, 하단 바 포함, 자식 3개
```

핵심 규칙: 구성 요소(텍스트, 일러스트, 하단 바)는 동일하고, 사이즈 비율에 따라 배치만 달라짐

### 변환 엔진에서의 처리 방식

1. 원본 프레임의 최상위 자식들을 역할별로 분류 (텍스트/그래픽/바)
2. 타겟 사이즈의 비율에 따라 배치 전략 결정
3. 각 그룹을 통째로 이동/리사이즈 (내부 구조는 유지)
4. 오토레이아웃이 있는 그룹은 오토레이아웃 설정 유지
5. 자유 배치 그룹(일러스트)은 포커스 영역 기준으로 위치/스케일 조정

### 아직 확인이 필요한 것들

- [ ] 카드뉴스, 포스터 등 다른 콘텐츠 유형도 같은 패턴인지
- [ ] 컴포넌트/인스턴스를 사용하는 디자인은 어떻게 처리할지
- [ ] 더 복잡한 중첩 구조(3단계 이상)가 있는 경우의 처리
- [ ] 네이밍 규칙을 활용한 자동 역할 분류 가능 여부

---

## 11. 소스 버전 추적

> ⚠️ 초기 설계안입니다. 실제 구현 과정에서 변경될 수 있습니다.

### 문제

원본 디자인이 피그마에서 수정될 수 있다.
이전에 만든 베리에이션이 옛날 버전 기준이라 안 맞게 되는데,
어떤 베리에이션을 다시 돌려야 하는지 알 수 없다.

### 해결: 원본 스냅샷 기록

베리에이션을 생성할 때마다 원본 프레임의 스냅샷 정보를 기록해둔다.
다음에 같은 프레임으로 다시 베리에이션을 돌릴 때, 원본이 바뀌었는지 비교해서 알려준다.

### 기록하는 정보

```
SourceSnapshot:
  figma_file_id   : "OsIOTyo6kx..."       ← 피그마 파일 ID
  frame_id        : "74:5547"              ← 프레임 노드 ID
  frame_name      : "jk_googleac_1200x1200_a"  ← 프레임 이름
  captured_at     : "2026-04-23T14:30:00"  ← 스냅샷 시점
  last_modified   : "2026-04-22T10:00:00"  ← 피그마에서의 마지막 수정 시간
  layer_summary   : {                      ← 레이어 구성 요약
    total_children: 3,
    child_names: ["illustration", "bottom_bar", "text_block"],
    text_contents: ["신규 채용 오픈", "지금 바로 지원하세요"]
  }
```

### 동작 방식

```
[1] 첫 베리에이션 생성 시
    원본 프레임의 스냅샷을 기록하고 저장

[2] 같은 프레임으로 다시 베리에이션 요청 시
    현재 프레임 상태 vs 저장된 스냅샷 비교
    
    ├─ 변경 없음 → "원본 동일합니다" 안내, 정상 진행
    └─ 변경 있음 → "원본이 수정되었습니다" 알림
         ├─ 어떤 부분이 바뀌었는지 요약 (텍스트? 레이어? 구조?)
         ├─ 이전 베리에이션 결과 갱신 필요 여부 안내
         └─ 새 스냅샷으로 업데이트
```

### 저장 위치

```
design_variation_agent/
├── feedback/
│   ├── history.jsonl        ← 기존 검수 기록
│   ├── snapshots.json       ← 원본 스냅샷 기록 (추가)
│   └── ...
```

---

## 12. 플랫폼 세이프 존 (Safe Zone)

> ⚠️ 초기 설계안입니다. 실제 매체별 세이프 존 데이터는 나중에 추가합니다.

### 문제

각 매체/플랫폼마다 UI가 콘텐츠 위에 겹치는 영역이 있다.
단순 여백(padding)과 달리, 특정 위치에 중요한 요소를 배치하면 가려지는 문제.

예시:
- 인스타그램 스토리: 상단(계정 이름), 하단(답장 UI)
- 유튜브 썸네일: 우하단(재생시간 표시)
- 카카오 비즈보드: 하단(더보기 버튼)

### 해결: 매체 프리셋에 safe_zone 추가

기존 `rules`에 `safe_zone`을 추가해서, "이 영역에는 중요한 요소를 배치하지 마라"는 금지 구역을 정의한다.

### 데이터 구조

```python
{
    "name": "instagram_story",
    "width": 1080,
    "height": 1920,
    "rules": {
        "min_font_size": 28,
        "padding": { "top": 40, "bottom": 40, "left": 40, "right": 40 },
        "safe_zone": {                    # 추가
            "avoid_areas": [
                {
                    "name": "상단 계정 UI",
                    "position": "top",
                    "height": 120,        # 상단에서 120px까지 금지
                },
                {
                    "name": "하단 답장 UI",
                    "position": "bottom",
                    "height": 160,        # 하단에서 160px까지 금지
                }
            ]
        }
    }
}
```

### 엔진에서의 처리

변환 엔진이 레이아웃을 계산할 때:
1. padding으로 기본 여백 확보
2. safe_zone의 avoid_areas에 중요 요소(텍스트, CTA, 로고)가 겹치지 않도록 추가 조정
3. 장식 요소는 safe_zone에 들어가도 허용 (가려져도 괜찮으므로)

---

## 13. 텍스트 오버플로우 처리

> ⚠️ 초기 설계안입니다. 실제 구현 과정에서 변경될 수 있습니다.

### 문제

사이즈가 작아지면 원본의 텍스트가 영역 안에 들어가지 않을 수 있다.
무작정 폰트를 줄이거나 텍스트를 자르면 품질이 떨어진다.

### 해결: 2단계 대응 + 알림

텍스트가 넘칠 때 아래 순서로 대응한다. 2단계까지 해서 안 되면 자동으로 처리하지 않고 디자이너에게 알린다.

```
[1단계] 줄바꿈 조정
    - 단어가 잘리지 않도록 단어 단위로 줄바꿈
    - 맥락에 맞게 의미 단위로 끊기
    - 예: "2026년 상반기 신규 채용 대규모 공개 모집"
      → "2026년 상반기
         신규 채용
         대규모 공개 모집"
      (❌ "2026년 상반기 신규 채용 대규모 공개 모"  ← 이런 식으로 잘리면 안 됨)
         │
         ▼
[2단계] 폰트 크기 줄이기
    - 매체 프리셋의 min_font_size까지만 줄임
    - 그 이하로는 줄이지 않음 (가독성 보장)
         │
         ▼
[알림] 디자이너에게 조치 필요 알림
    - 2단계까지 해서도 안 들어가면 자동으로 더 이상 처리하지 않음
    - 대시보드에 "⚠️ 텍스트 오버플로우: 수동 조치 필요" 표시
    - 디자이너가 직접 판단: 텍스트 축약 / 요소 숨기기 / 레이아웃 변경
```

### 왜 자동 축약/숨기기를 안 하는가

텍스트를 AI가 임의로 줄이거나 숨기면, 의도와 다른 결과물이 나올 수 있다.
"대규모 공개 모집" → "공개 모집" 이렇게 줄여도 되는지는 디자이너가 판단해야 한다.
검수 우선 원칙에 따라, 판단이 필요한 상황은 디자이너에게 넘긴다.

---

## 14. 생성 전 검증 단계 (Validation Pipeline)

### 왜 필요한가

설계서에 합의한 규칙이 실행 과정에서 빠지거나 누락되면,
나중에 문제가 눈덩이처럼 커진다.
검증 단계를 코드에 강제해서, 규칙을 하나라도 건너뛰면 생성 자체가 안 되도록 막는다.

### 설계 원칙: 플러그인 방식

검증 항목을 코드에 하드코딩하지 않는다.
각 검증 항목은 독립적인 "체크 모듈"이고, 레지스트리에 등록하면 자동으로 실행된다.
새 규칙이 추가되면 체크 모듈 하나만 만들어서 등록하면 끝.

### 체크 모듈 구조

모든 검증 항목은 동일한 형태를 따른다:

```
CheckModule:
  id              : "output_location"        ← 고유 ID
  name            : "출력 위치 확인"           ← 사람이 읽는 이름
  description     : "AI Variation 전용 페이지가 지정되어 있는가"
  severity        : "block" | "warn"         ← 실패 시 중단할지 경고만 할지
  phase           : "pre_generation"         ← 실행 시점 (아래 참조)
  order           : 100                      ← 같은 phase 안에서의 실행 순서
  enabled         : true                     ← 활성화 여부 (비활성화 가능)
  
  check(layout_plan, context) → CheckResult  ← 실행 함수
```

```
CheckResult:
  check_id        : "output_location"
  passed          : true | false
  message         : ""                       ← 실패 시 사유
  auto_fix_applied: false                    ← 자동 보정 적용 여부
  auto_fix_detail : ""                       ← 자동 보정 내용
```

### 실행 시점 (phase)

검증은 세 시점에 나눠서 실행된다:

```
[Phase 1] pre_layout — 변환 전 (입력 검증)
  layout_engine이 작업하기 전에, 입력 자체가 유효한지 확인.
  예: 출력 위치가 지정되었는가, 소스 버전이 기록되었는가

[Phase 2] post_layout — 변환 후 (결과 검증)
  layout_engine이 LayoutPlan을 만든 후, 결과가 규칙에 맞는지 확인.
  예: 세이프 존 침범, 텍스트 오버플로우, 레이아웃 연동 속성

[Phase 3] pre_generation — 생성 직전 (최종 확인)
  figma_writer가 실행되기 직전, 모든 조건이 갖춰졌는지 최종 확인.
  예: 레이어 구조, 승인 상태
```

### 체크 레지스트리

```
design_variation_agent/
├── engine/
│   ├── validator.py              ← 검증 실행기 (레지스트리 로드 → 순서대로 실행)
│   └── checks/                   ← 체크 모듈 폴더
│       ├── __init__.py           ← 레지스트리 (이 폴더의 모듈을 자동 등록)
│       ├── output_location.py    ← 출력 위치 확인
│       ├── focus_area.py         ← 포커스 영역 확인
│       ├── safe_zone.py          ← 세이프 존 확인
│       ├── text_overflow.py      ← 텍스트 오버플로우 확인
│       ├── layer_structure.py    ← 레이어 구조 확인
│       ├── source_version.py     ← 소스 버전 확인
│       └── layout_linked.py      ← 레이아웃 연동 속성 확인
```

새 검증 추가: `checks/` 폴더에 파일 하나 추가하면 자동으로 등록됨.
검증 비활성화: `enabled: false`로 설정하면 건너뜀.
순서 변경: `order` 값만 변경.

### 현재 등록된 체크 목록

```
Phase 1: pre_layout
┌────────────────────┬───────────┬───────┬──────────────────────────────────────┐
│ ID                 │ severity  │ order │ 설명                                 │
├────────────────────┼───────────┼───────┼──────────────────────────────────────┤
│ output_location    │ block     │ 100   │ AI Variation 전용 페이지 지정 확인    │
│ source_version     │ warn      │ 200   │ 원본 스냅샷 기록 확인, 없으면 자동 생성│
└────────────────────┴───────────┴───────┴──────────────────────────────────────┘

Phase 2: post_layout
┌────────────────────┬───────────┬───────┬──────────────────────────────────────┐
│ ID                 │ severity  │ order │ 설명                                 │
├────────────────────┼───────────┼───────┼──────────────────────────────────────┤
│ focus_area         │ warn      │ 100   │ 이미지에 포커스 영역 적용 확인         │
│ safe_zone          │ block     │ 200   │ 중요 요소의 세이프 존 침범 확인        │
│ text_overflow      │ warn      │ 300   │ 텍스트 오버플로우 감지 및 2단계 대응   │
│ layout_linked      │ warn      │ 400   │ 텍스트 정렬·줄간격·자간 연동 확인     │
│ bounds_check       │ warn      │ 500   │ 모든 요소가 프레임 안에 있는지 확인    │
└────────────────────┴───────────┴───────┴──────────────────────────────────────┘

Phase 3: pre_generation
┌────────────────────┬───────────┬───────┬──────────────────────────────────────┐
│ ID                 │ severity  │ order │ 설명                                 │
├────────────────────┼───────────┼───────┼──────────────────────────────────────┤
│ layer_structure    │ block     │ 100   │ 편집 가능한 레이어 구조 유지 확인      │
│ approval_status    │ block     │ 200   │ 디자이너 승인 상태 확인               │
└────────────────────┴───────────┴───────┴──────────────────────────────────────┘
```

### 검증 실행 흐름

```
LayoutPlan 생성됨
       │
       ▼
[validator.py] 레지스트리에서 체크 모듈 로드
       │
       ├─ Phase 1 체크들 실행 (order 순)
       │    ├─ block 실패 → 즉시 중단, ValidationResult 반환
       │    └─ warn 실패 → 기록하고 계속
       │
       ├─ Phase 2 체크들 실행 (order 순)
       │    ├─ auto_fix 가능하면 자동 보정 후 기록
       │    ├─ block 실패 → 즉시 중단
       │    └─ warn 실패 → 기록하고 계속
       │
       └─ Phase 3 체크들은 Figma 생성 직전에 별도 실행
            └─ 이 시점의 block 실패 → 해당 프레임만 생성 건너뜀

모든 결과를 ValidationResult에 담아서 반환
```

### 자동 보정 (Auto-fix)

일부 체크는 실패 시 스스로 보정할 수 있다:

```
focus_area     : 미지정 → 기본값(center-center) 자동 적용
source_version : 스냅샷 없음 → 현재 상태로 자동 생성
layout_linked  : 텍스트 정렬 미변경 → 배치에 맞게 자동 변경
bounds_check   : 프레임 밖 요소 → 프레임 안으로 자동 이동
```

자동 보정이 적용되면 CheckResult.auto_fix_applied = true로 표시하고,
대시보드에서 "자동 보정됨" 표시를 통해 디자이너가 확인할 수 있다.

---

## 15. 레이아웃 연동 속성

> 이 섹션은 지속적으로 추가됩니다. 실제 작업에서 발견되는 규칙을 계속 추가해 주세요.

### 왜 필요한가

사이즈가 바뀌면 위치/크기뿐 아니라, 텍스트 정렬·줄간격·자간 등
함께 바뀌어야 하는 속성들이 있다. 이걸 빠뜨리면 부자연스러운 결과가 나온다.

### 현재 등록된 연동 속성

**1. 텍스트 정렬 (text alignment)**

배치가 바뀌면 텍스트 정렬도 자동으로 따라간다.

```
가로형 (텍스트 좌측 배치) → 좌측 정렬 (LEFT)
정사각형 (텍스트 중앙 배치) → 가운데 정렬 (CENTER)
세로형 (텍스트 상단 배치) → 가운데 정렬 (CENTER)
```

디자이너 부연설명으로 덮어쓸 수 있음.
예: "가로형이지만 가운데 정렬 유지해줘"

**2. 폰트 크기 비례 조정**

사이즈 변환 시 텍스트 영역의 비율에 맞게 폰트 크기를 조정한다.
단, 매체 프리셋의 min_font_size 이하로는 줄이지 않는다.

**3. 줄간격 (line height)**

폰트 크기가 변하면 줄간격도 비례해서 조정한다.
원본의 폰트 대비 줄간격 비율을 유지한다.

**4. 자간 (letter spacing)**

원본의 자간 설정을 유지한다. 폰트 크기가 바뀌어도 비율은 동일하게.

### 속성 추가 방법

실제 작업 중 "이것도 같이 바뀌어야 했는데" 하는 항목이 발견되면
이 섹션에 추가하고, 검증 단계(섹션 14)에도 체크 항목을 함께 추가한다.

---

## 16. 모듈 간 인터페이스 (데이터 계약)

### 왜 필요한가

각 모듈이 주고받는 데이터의 형태가 정확하게 정의되어 있어야,
모듈을 독립적으로 개발하고 교체할 수 있다.
인터페이스가 없으면 모듈끼리 암묵적 의존이 생기고, 하나를 고치면 다른 것이 깨진다.

### 전체 데이터 흐름

```
VariationRequest (입력)
       │
       ▼
[figma_reader] ──→ SourceFrame ──→ [analyzer] ──→ AnalyzedDesign
                                                       │
                                                       ▼
MediaPreset (설정) ──→ [layout_engine] ←── LearnedRules (학습 규칙)
                            │
                            ▼
                      LayoutPlan ──→ [validator] ──→ ValidationResult
                                                         │
                                                         ▼
                                                   (통과 시)
                                                         │
                      LayoutPlan ──→ [preview_renderer] ──→ PreviewImage
                                                              │
                                                              ▼
                                                   (디자이너 승인 후)
                                                              │
                      LayoutPlan ──→ [figma_writer] ──→ FigmaOutput
```

### 1단계: figma_reader → SourceFrame

figma_reader가 Figma에서 프레임을 읽어서 내부 표현으로 변환한다.
이후 모든 모듈은 Figma API를 직접 호출하지 않고, 이 데이터만 사용한다.

```
SourceFrame:
  file_key        : "S0i1zFhCEF04F1rqBmMUZZ"
  frame_id        : "1:2"
  frame_name      : "공고스카이_560x700"
  width           : 560
  height          : 700

  layers          : [                        ← 최상위 자식들 (순서 유지)
    {
      id          : "1:3"
      name        : "background"
      type        : "RECTANGLE" | "FRAME" | "GROUP" | "TEXT" | "VECTOR" | ...
      role        : null                     ← analyzer가 채울 영역 (이 시점에선 비어있음)
      bounds      : { x, y, width, height }  ← 프레임 내 위치/크기
      style       : {                        ← 시각적 속성
        fills       : [...]                  ← 배경색, 이미지, 그라데이션
        opacity     : 1.0
        blendMode   : "NORMAL"
        cornerRadius: 0
      }
      text_data   : {                        ← type이 TEXT일 때만
        content     : "네이버페이\n받아 가세요!"
        font_family : "Paperlogy"
        font_style  : "8 ExtraBold"
        font_size   : 90.68
        line_height : 100
        letter_spacing: 0
        text_align  : "CENTER"
        color       : { r, g, b, a }
      } | null
      children    : [...]                    ← 하위 레이어 (재귀 구조)
      auto_layout : {                        ← 오토레이아웃 설정 (있으면)
        direction   : "VERTICAL" | "HORIZONTAL"
        spacing     : 10
        padding     : { top, right, bottom, left }
        alignment   : "MIN" | "CENTER" | "MAX"
      } | null
      constraints : {                        ← 크기 제약
        horizontal  : "FIXED" | "SCALE" | "MIN" | ...
        vertical    : "FIXED" | "SCALE" | "MIN" | ...
      }
    },
    ...
  ]

  snapshot        : SourceSnapshot           ← 소스 버전 추적 데이터 (섹션 11)
```

### 2단계: analyzer → AnalyzedDesign

analyzer가 SourceFrame의 각 레이어에 역할을 부여하고,
디자인의 공간 구조를 파악한다.

```
AnalyzedDesign:
  source          : SourceFrame              ← 원본 데이터 그대로 포함

  layer_roles     : [                        ← 각 레이어의 역할 분류
    {
      layer_id    : "1:3"
      role        : "background_image" | "title" | "subtitle" | "cta" |
                    "logo" | "character" | "decoration" | "gradient_overlay" |
                    "info_bar" | "unknown"
      priority    : 1~4                      ← 1:필수, 2:중요, 3:권장, 4:선택
      is_text     : true | false
      is_image    : true | false
      focus_area  : FocusArea | null         ← 이미지일 때 포커스 영역
    },
    ...
  ]

  spatial_info    : {                        ← 공간 구조 분석 결과
    layout_direction : "vertical" | "horizontal" | "centered" | "free"
    text_region      : { x, y, width, height }   ← 텍스트가 차지하는 영역
    image_region     : { x, y, width, height }   ← 이미지가 차지하는 영역
    text_image_ratio : 0.4                       ← 텍스트 영역 비율 (0~1)
    alignment_pattern: "center-center" | "left-top" | ...
  }

  designer_notes  : [                        ← 부연설명 파싱 결과
    {
      original    : "제목 텍스트는 줄여도 됨"
      parsed_rule : { type: "text_modify", target: "title", action: "allow_shorten" }
    },
    ...
  ]
```

### 3단계: layout_engine → LayoutPlan

layout_engine이 AnalyzedDesign과 MediaPreset을 받아서,
새 사이즈에 맞는 구체적인 레이아웃 계획을 생성한다.

```
LayoutPlan:
  source_size     : { width: 560, height: 700 }
  target_size     : { width: 1200, height: 600 }
  target_preset   : "web_banner"
  target_category : "ads"

  layout_type     : "horizontal" | "vertical" | "square"  ← 결정된 배치 유형

  element_plans   : [                        ← 각 요소의 새 위치/크기/속성
    {
      layer_id    : "1:3"
      role        : "background_image"
      action      : "resize" | "move" | "scale" | "hide" | "keep"

      original    : { x, y, width, height }  ← 원래 값
      planned     : { x, y, width, height }  ← 새 값

      style_changes: {                       ← 변경할 스타일 속성
        text_align  : "LEFT"                 ← 변경할 것만 포함
        font_size   : 77.08                  ← null이면 변경 안 함
        scale_factor: 1.15                   ← rescale 적용 비율
      }

      applied_rules: ["rule_001", "layout_linked_alignment"]
                                             ← 이 요소에 적용된 규칙 ID들 (추적용)
    },
    ...
  ]

  warnings        : [                        ← 주의 사항 (디자이너에게 표시)
    {
      type        : "text_overflow" | "safe_zone_near" | "element_hidden" | ...
      message     : "부제목이 영역을 초과하여 폰트 크기를 줄였습니다 (24px → 20px)"
      layer_id    : "1:5"
      severity    : "info" | "warning" | "error"
    },
    ...
  ]

  metadata        : {
    generation_time : "2026-04-23T15:00:00"
    rules_applied   : ["rule_001", "rule_003"]   ← 적용된 학습 규칙 목록
    engine_version  : "0.1.0"
  }
```

### 4단계: validator → ValidationResult

validator가 LayoutPlan을 검증한다. (섹션 14의 검증 파이프라인)

```
ValidationResult:
  passed          : true | false             ← 전체 통과 여부
  layout_plan     : LayoutPlan               ← 검증 대상

  checks          : [                        ← 각 검증 항목의 결과
    {
      check_id    : "output_location"
      check_name  : "출력 위치 확인"
      passed      : true
      severity    : "block" | "warn"         ← 실패 시 중단할지 경고만 할지
      message     : ""                       ← 실패 시 사유
    },
    ...
  ]

  blocked         : false                    ← block 레벨 검증 실패가 있으면 true
  warnings_count  : 1
  errors_count    : 0
```

### 5단계: figma_writer → FigmaOutput

figma_writer가 LayoutPlan을 받아서 Figma에 실제 프레임을 생성한다.

```
FigmaOutput:
  success         : true | false
  file_key        : "S0i1zFhCEF04F1rqBmMUZZ"
  page_name       : "AI Variation"
  created_frames  : [
    {
      preset_name : "web_banner"
      frame_id    : "23:3"                   ← 생성된 프레임의 Figma ID
      frame_name  : "AI_web_banner_1200x600"
      url         : "https://figma.com/..."  ← 직접 링크
    },
    ...
  ]
  errors          : [                        ← 생성 중 발생한 문제
    {
      frame       : "web_banner"
      error       : "폰트 로드 실패: Paperlogy 8 ExtraBold"
      fallback    : "rescale 방식으로 대체 적용"
    },
    ...
  ]
```

### 모듈 간 의존성 규칙

```
1. 단방향 흐름만 허용한다
   figma_reader → analyzer → layout_engine → validator → figma_writer
   역방향 호출 금지. validator가 figma_reader를 부르면 안 된다.

2. 모듈은 인접 모듈의 출력만 사용한다
   layout_engine은 AnalyzedDesign만 받는다.
   SourceFrame을 직접 참조하려면 AnalyzedDesign.source를 통해서만.

3. 외부 의존(Figma API)은 양 끝에서만
   figma_reader와 figma_writer만 Figma를 직접 호출한다.
   중간 모듈(analyzer, layout_engine, validator)은 Figma를 모른다.

4. 설정 데이터는 수평으로 주입한다
   MediaPreset, LearnedRules는 layout_engine에 직접 주입된다.
   다른 모듈의 출력을 거치지 않는다.
```

---

## 17. 변환 엔진 핵심 로직 (layout_engine.py)

### AI가 판단하는 것들

1. **위치 재계산** — 기준 디자인의 비율 기반으로 요소 위치를 새 사이즈에 맞게 조정
2. **폰트 크기 조정** — 매체 규정의 최소 폰트 크기를 지키면서 비례 축소/확대
3. **요소 순서 변경** — 가로형 → 세로형 전환 시 요소 배치 순서 변경
4. **요소 숨기기** — 공간이 부족한 소형 매체에서 덜 중요한 요소 제거
5. **텍스트 축약** — 긴 제목을 짧은 버전으로 조정
6. **여백 조정** — 매체별 안전 영역(safe zone) 적용

### 요소 우선순위 (기본)

변환할 때 공간이 부족하면, 우선순위가 낮은 것부터 숨김:

1. 🔴 필수 — 로고, 메인 제목
2. 🟠 중요 — CTA 버튼, 핵심 이미지
3. 🟡 권장 — 부제목, 설명 텍스트
4. 🟢 선택 — 장식 요소, 배경 패턴, 부가 텍스트

디자이너 부연설명으로 이 우선순위를 덮어쓸 수 있습니다.

---

## 18. 피드백 & 학습 시스템

### 목표

AI가 같은 실수를 반복하지 않고, 사용할수록 결과물 품질이 올라가는 구조.
디자이너의 검수 결과와 수정 이력이 곧 학습 데이터가 된다.

### 피드백 데이터 수집

대시보드에서 검수할 때 자동으로 기록되는 것들:

```
FeedbackRecord:
  timestamp       : "2026-04-23T14:30:00"
  source_design   : { 원본 프레임 정보 }
  target_size     : "gdn_square"           ← 어떤 사이즈였는지
  target_category : "ads"                  ← 어떤 카테고리였는지

  # AI가 한 판단
  ai_layout       : { ... AI가 계산한 레이아웃 ... }

  # 디자이너 평가
  review_status   : "revision"             ← 승인? 수정? 재생성?
  revision_note   : "캐릭터 40% 줄이고 텍스트 왼쪽 정렬"  ← 수정 이유
  
  # 수정 후 결과
  final_layout    : { ... 최종 승인된 레이아웃 ... }
  
  # 패턴 태그 (자동 분류)
  issue_tags      : ["element_too_large", "alignment_wrong"]
```

### 학습 흐름

```
[1] 피드백 수집
    검수할 때마다 자동으로 기록됨
         │
         ▼
[2] 패턴 분석
    쌓인 피드백에서 반복되는 문제를 추출
    예: "300x250 이하에서 캐릭터가 항상 너무 큼"
    예: "가로형 배너에서 텍스트 정렬이 자주 수정됨"
         │
         ▼
[3] 규칙 반영
    발견된 패턴을 매체 규정 또는 변환 로직에 반영
    → 매체 프리셋에 규칙 추가 (설정 레벨)
    → 또는 AI 프롬프트에 사례로 포함 (학습 레벨)
         │
         ▼
[4] 품질 향상
    다음 변환부터 같은 실수 없이 더 나은 결과
```

### 학습 데이터 활용 방식

**1단계 (규칙 기반)** — 피드백에서 뽑은 패턴을 매체 규정에 명시적으로 추가
  예: `gdn_square`의 `rules`에 `"max_character_ratio": 0.3` 추가

**2단계 (사례 기반)** — 과거 수정 사례를 AI에게 "이전에 이렇게 했더니 수정당했고, 이렇게 고치니 승인받았다"고 알려줌
  예: AI 프롬프트에 "GDN 300x250에서는 캐릭터를 전체 면적의 30% 이하로" 추가

**3단계 (자동 학습)** — 충분한 데이터가 쌓이면, 승인율이 높은 레이아웃 패턴을 자동으로 우선 적용

### 피드백 저장 위치

```
design_variation_agent/
├── feedback/                ← 피드백 & 학습 데이터
│   ├── history.jsonl        ← 모든 검수 기록 (시간순, 한 줄씩 추가)
│   ├── patterns.json        ← 추출된 패턴 요약
│   └── learned_rules.json   ← 학습으로 추가된 규칙들
```

### 즉시 학습 입력 시스템

디자이너가 피드백을 주면 바로 규칙으로 반영할 수 있는 구조.
별도 개발 없이 데이터 파일만 수정하면 다음 변환부터 적용된다.

#### learned_rules.json 구조

```json
{
  "version": "1.0",
  "last_updated": "2026-04-23",
  "rules": [
    {
      "id": "rule_001",
      "category": "text_size",
      "condition": "프레임 면적이 원본보다 커지면",
      "action": "텍스트를 비례 확대 (면적 비율의 제곱근 기준)",
      "source": "프로토타입 테스트 피드백",
      "created": "2026-04-23",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

#### 규칙 카테고리

```
text_size        : 텍스트 크기 관련 (확대/축소/최소크기)
text_alignment   : 텍스트 정렬 관련 (레이아웃별 정렬 방향)
text_position    : 텍스트 위치 관련 (여백, 배치)
image_placement  : 이미지 배치 관련 (포커스 영역, 비율)
image_scale      : 이미지 크기 관련 (커버, 비율 유지)
gradient         : 그라데이션 관련 (방향, 가독성)
spacing          : 요소 간 간격 관련
safe_zone        : 플랫폼 안전 영역 관련
layer_structure  : 레이어 구조 관련
general          : 기타
```

#### 학습 입력 방식

```
[방법 1] 디자이너가 직접 피드백
    "텍스트가 너무 작아" → text_size 카테고리에 규칙 추가
    "캐릭터가 안 보여"  → image_placement 카테고리에 규칙 추가
    "여백이 부족해"     → spacing 카테고리에 규칙 추가

[방법 2] 비교 학습
    원본 vs 결과물을 보면서 "이건 이래야 해" 식으로 교정
    → 해당 케이스를 규칙으로 변환하여 저장

[방법 3] 레퍼런스 학습
    "이 디자인처럼 해줘" → 레퍼런스의 레이아웃 패턴을 분석하여 규칙 추출
```

#### 규칙 적용 우선순위

```
1순위: learned_rules.json의 priority: "high" 규칙
2순위: ARCHITECTURE.md에 명시된 기본 규칙 (레이아웃 연동 속성 등)
3순위: learned_rules.json의 priority: "normal" 규칙
4순위: 엔진 기본값
```

#### 규칙 상태 관리

```
pending   : 추가됨, 아직 검증 안 됨
active    : 검증 완료, 적용 중
disabled  : 비활성화 (문제가 발견되어 일시 중단)
archived  : 더 나은 규칙으로 대체됨
```

> ⚠️ 초기 설계안입니다. 학습 데이터가 쌓이면서 카테고리와 구조가 확장될 수 있습니다.

### 측정 지표

시스템이 얼마나 발전하고 있는지 확인할 수 있는 지표:

- **1차 승인율**: 수정 없이 바로 승인된 비율 (높을수록 좋음)
- **수정 빈도**: 평균 몇 번 수정해야 승인되는지 (낮을수록 좋음)
- **카테고리별 승인율**: 어떤 매체 유형에서 잘하고, 어디서 약한지
- **시간 추이**: 사용할수록 승인율이 올라가는지

### 규칙 충돌 감지 및 해결

#### 왜 필요한가

학습 규칙이 쌓이면서 서로 모순되는 규칙이 생길 수 있다.
예: rule_001 "프레임이 커지면 텍스트 확대" vs rule_015 "가로 배너에서는 텍스트를 작게"
→ 1200x600 가로 배너로 변환할 때 텍스트를 키워야 하나 줄여야 하나?

충돌을 감지하지 않으면 실행할 때마다 결과가 달라지거나, 마지막에 적용된 규칙이 이기는
예측 불가능한 시스템이 된다.

#### 충돌의 종류

```
[유형 1] 직접 충돌 — 같은 속성에 대해 반대 지시
  rule_A: text_size → "확대"
  rule_B: text_size → "축소"
  → 같은 카테고리, 같은 속성을 건드리는 규칙끼리 action이 반대

[유형 2] 조건 중첩 — 조건이 겹쳐서 동시에 적용됨
  rule_A: condition "프레임이 원본보다 크면" → 텍스트 확대
  rule_B: condition "가로형 배너일 때" → 텍스트 축소
  → 1200x600은 원본(560x700)보다 크면서 가로형이기도 함

[유형 3] 간접 충돌 — 다른 속성을 건드리지만 결과적으로 모순
  rule_A: spacing → "여백 넓히기"
  rule_B: text_size → "텍스트 확대"
  → 여백을 넓히면 텍스트 공간이 줄어서 확대된 텍스트가 안 들어감
  ⚠️ 간접 충돌은 사전 감지가 현실적으로 어렵다.
     실제 레이아웃 계산 후 검증 파이프라인(text_overflow, bounds_check 등)이
     결과적으로 발생한 문제를 잡아내는 방식으로 처리한다.
```

#### 충돌 감지 방법

규칙이 추가되거나 변환이 실행될 때, 아래 검사를 자동으로 수행한다:

```
[검사 1] 카테고리 + 속성 중복 검사
  같은 category의 규칙들 중 action이 반대 방향인 쌍을 찾는다.
  "확대" vs "축소", "LEFT" vs "CENTER", "보이기" vs "숨기기"

[검사 2] 조건 겹침 검사
  두 규칙의 condition이 동시에 참이 될 수 있는지 확인한다.
  동시에 참이면서 action이 다르면 충돌로 판정.

[검사 3] 실행 시점 충돌 검사
  변환 실행 중 하나의 요소에 2개 이상의 규칙이 적용되려 할 때,
  결과 값이 서로 다르면 충돌로 판정.
```

#### 충돌 해결 우선순위

충돌이 감지되면 아래 순서로 어떤 규칙을 적용할지 결정한다:

```
1순위: 디자이너 부연설명에서 온 규칙
  → 디자이너가 이번 작업에서 직접 지시한 것은 항상 최우선

2순위: 더 구체적인 조건의 규칙
  "가로형 배너에서 텍스트 축소" > "프레임이 크면 텍스트 확대"
  구체적 조건(특정 매체, 특정 사이즈)이 일반 조건보다 우선

3순위: 더 최근에 만들어진 규칙
  나중에 추가된 규칙이 이전 규칙보다 우선 (더 많은 경험이 반영됨)

4순위: priority가 높은 규칙
  "high" > "normal" > "low"

5순위: 해당 매체에서 승인율이 높은 규칙
  과거 피드백 데이터에서 해당 규칙 적용 시 승인율이 더 높았던 쪽
```

#### 충돌 기록 구조

```
ConflictRecord:
  detected_at     : "2026-04-23T15:00:00"
  rule_a          : "rule_001"
  rule_b          : "rule_015"
  conflict_type   : "direct" | "condition_overlap" | "indirect"
  target_element  : "title_text"
  resolution      : "rule_b_applied"         ← 어떤 규칙이 적용되었는지
  resolution_reason: "더 구체적인 조건 (가로형 배너 한정)"
  context         : {
    target_preset : "web_banner"
    source_size   : { width: 560, height: 700 }
    target_size   : { width: 1200, height: 600 }
  }
```

#### 디자이너에게 표시

충돌이 발생하면 대시보드에 표시한다:

```
⚠️ 규칙 충돌 감지
  - rule_001: "프레임이 커지면 텍스트 확대" 
  - rule_015: "가로형 배너에서는 텍스트 작게"
  → rule_015 적용됨 (이유: 더 구체적인 조건)
  
  이 결정이 맞지 않으면 검수에서 수정해주세요.
  수정 결과는 향후 충돌 해결에 반영됩니다.
```

#### 충돌 학습

디자이너가 충돌 해결 결과를 수정하면, 그 판단이 다음 충돌에 반영된다:

```
[1] 충돌 발생 → 자동 해결 → 디자이너 검수
[2] 디자이너가 다른 규칙을 선택 → 해당 충돌 패턴에 "디자이너 선호" 기록
[3] 같은 충돌 다시 발생 → 디자이너 선호를 1순위로 적용
```

---

## 19. 에러 처리 흐름

### 왜 필요한가

프로토타입 테스트에서 이미 Figma 권한 문제, 폰트 로드 실패 등을 겪었다.
에러가 나면 시스템이 멈추는 게 아니라, 어떤 에러인지 알려주고
가능하면 대안을 실행해야 한다.

### 에러 분류

```
[Level 1] FATAL — 더 이상 진행 불가. 즉시 중단하고 디자이너에게 알림.
[Level 2] RECOVERABLE — 대안(fallback)이 있어서 계속 진행 가능. 경고 표시.
[Level 3] WARNING — 결과에 영향은 적지만 알아두면 좋은 정보. 로그 기록.
```

### 모듈별 에러 목록과 대응

#### figma_reader 에러

```
에러: Figma 파일 접근 불가 (권한 없음 / 파일 삭제됨)
레벨: FATAL
대응: 중단. "Figma 파일에 접근할 수 없습니다. 공유 권한을 확인해주세요."
     → 파일 URL과 필요한 권한(편집자)을 안내

에러: 프레임 ID를 찾을 수 없음
레벨: FATAL
대응: 중단. "지정한 프레임이 존재하지 않습니다. URL을 확인해주세요."
     → 파일 내 최상위 프레임 목록을 보여주며 선택 유도

에러: Figma API 응답 타임아웃
레벨: RECOVERABLE
대응: 3회까지 재시도 (5초 간격). 3회 실패 시 FATAL로 승격.
     "Figma 서버 응답이 느립니다. 재시도 중... (n/3)"

에러: 빈 프레임 (자식 레이어 없음)
레벨: FATAL
대응: 중단. "프레임 안에 레이어가 없습니다. 디자인이 있는 프레임을 선택해주세요."
```

#### analyzer 에러

```
에러: 레이어 역할 분류 실패 (어떤 역할인지 판단 불가)
레벨: WARNING
대응: role을 "unknown"으로 설정, priority를 4(선택)로 지정.
     경고: "일부 레이어의 역할을 자동 판단하지 못했습니다. 검수 시 확인해주세요."

에러: 이미지 레이어가 없는 디자인
레벨: WARNING
대응: 포커스 영역 관련 처리를 건너뜀. 정상 진행.
     "이미지 없는 텍스트 전용 디자인으로 처리합니다."

에러: 디자이너 부연설명 파싱 실패
레벨: WARNING
대응: 해당 부연설명을 무시하고 진행. 검수 대시보드에 원본 텍스트를 표시.
     "부연설명을 해석하지 못했습니다: [원본 텍스트]. 검수 시 직접 확인해주세요."
```

#### layout_engine 에러

```
에러: 매체 프리셋을 찾을 수 없음
레벨: FATAL
대응: 중단. "등록되지 않은 매체입니다: [이름]. 사용 가능한 매체 목록: [...]"

에러: 텍스트 오버플로우 (2단계까지 해결 불가)
레벨: RECOVERABLE
대응: min_font_size로 설정하고 진행. LayoutPlan.warnings에 기록.
     대시보드에서 "⚠️ 텍스트 오버플로우" 표시.

에러: 학습 규칙 간 충돌 감지
레벨: RECOVERABLE
대응: 충돌 해결 로직 실행 (섹션 18 규칙 충돌 참조). 어떤 규칙이 적용되었는지 기록.

에러: 요소가 프레임 밖으로 벗어남
레벨: RECOVERABLE
대응: 프레임 경계 안으로 자동 보정. warnings에 기록.
     "요소 [이름]이 프레임 밖으로 벗어나 자동 보정되었습니다."
```

#### validator 에러

```
에러: block 레벨 검증 실패
레벨: FATAL
대응: 생성 중단. 실패한 검증 항목과 사유를 디자이너에게 표시.

에러: warn 레벨 검증 실패
레벨: WARNING
대응: 경고 표시 후 진행. 대시보드에서 해당 항목을 하이라이트.
```

#### figma_writer 에러

```
에러: 출력 Figma 파일 접근 불가
레벨: FATAL
대응: 중단. "결과물을 생성할 Figma 파일에 접근할 수 없습니다."

에러: 폰트 로드 실패
레벨: RECOVERABLE
대응: node.rescale() 방식으로 시각적 크기만 변경. 폰트 속성은 원본 유지.
     warnings에 기록: "폰트 [이름]을 로드할 수 없어 rescale 방식으로 대체했습니다."

에러: AI Variation 페이지 생성 실패
레벨: RECOVERABLE
대응: 기존 페이지에서 "AI Variation" 이름의 페이지를 검색.
     있으면 해당 페이지 사용. 없으면 FATAL로 승격.

에러: 개별 프레임 생성 실패
레벨: RECOVERABLE
대응: 해당 사이즈만 건너뛰고 나머지 계속 생성.
     "web_banner (1200x600) 생성 실패. 나머지 사이즈는 정상 생성되었습니다."
```

### 에러 전파 규칙

```
1. FATAL은 즉시 전체 파이프라인을 중단한다.
   중단 시점까지의 진행 상황과 에러 내용을 디자이너에게 보여준다.

2. RECOVERABLE은 대안을 실행하고, 결과의 warnings에 기록한다.
   디자이너가 검수할 때 어떤 대안이 적용되었는지 확인할 수 있다.

3. WARNING은 로그에만 기록한다.
   대시보드에서 "상세 로그 보기"로 확인 가능.

4. 에러가 누적되면 승격한다.
   같은 RECOVERABLE 에러가 3회 이상 반복되면 FATAL로 승격.
   예: 폰트 로드 실패가 3개 이상이면 "폰트 환경 점검 필요" FATAL.

5. 정의되지 않은 에러는 FATAL로 처리한다.
   위 목록에 없는 예상 못 한 에러가 발생하면 무조건 중단한다.
   에러 내용 전체를 로그에 기록하고 디자이너에게 보여준다.
   → 테스트를 통해 에러가 발견될 때마다 적절한 레벨과 대응을 정의하여 목록에 추가한다.
   → 정의가 완료되면 FATAL에서 RECOVERABLE 또는 WARNING으로 내려갈 수 있다.
```

### 에러 로그 구조

```
ErrorLog:
  timestamp       : "2026-04-23T15:00:00"
  module          : "figma_writer"
  level           : "RECOVERABLE"
  error_code      : "FONT_LOAD_FAILED"
  message         : "폰트 로드 실패: Paperlogy 8 ExtraBold"
  fallback_used   : "rescale(0.85) 적용"
  context         : {
    file_key      : "S0i1zFhCEF04F1rqBmMUZZ"
    frame_id      : "23:3"
    target_preset : "web_banner"
  }
```

---

## 20. 확장 계획

### 당장은 안 하지만, 나중에 추가할 수 있는 것들

- [ ] 브랜드 스타일 시스템 연동 (기존 프로젝트에서 가져오기)
- [ ] 배치 처리 (여러 기준 디자인을 한 번에)
- [ ] SVG 출력 옵션 (Figma 없이도 사용)
- [ ] 팀 공유 대시보드 (여러 디자이너가 함께 검수)

---

## 21. 기존 프로젝트와의 관계

| 항목 | 기존 (card_news_generator) | 신규 (design_variation_agent) |
|------|---------------------------|-------------------------------|
| 목표 | 자연어 → 디자인 자동 생성 | 기준 디자인 → 사이즈별 변환 |
| 입력 | 텍스트 (주제/분위기) | Figma 프레임 + 부연설명 |
| 출력 | SVG/PNG 파일 | Figma 프레임 직접 생성 |
| 핵심 | 카피 생성 + 템플릿 매핑 | 레이아웃 분석 + 재구성 |
| 상태 | 1차 프로토타입 완성 | 설계 시작 |

두 프로젝트는 독립적이지만, 나중에 브랜드 스타일 데이터 등은 공유할 수 있습니다.

---

생성일: 2026-04-23
상태: 초기 설계
