# Design Variation Agent — 아키텍처 설계서

> 마지막 업데이트: 2026-04-24
> 상태: 구조 보강 완료, 매체 프리셋 데이터 입력 중

---

## 목차

```
Part 1. 개요
  1.1  프로젝트 목표
  1.2  설계 원칙
  1.3  전체 흐름 (한눈에 보기)
  1.4  폴더 구조

Part 2. 입력 & 설정
  2.1  매체 프리셋 구조 (사이즈 & 규정)
  2.2  디자이너 부연설명 시스템
  2.3  플랫폼 세이프 존

Part 3. 파이프라인 (데이터가 흘러가는 길)
  3.1  전체 데이터 흐름도
  3.2  각 모듈이 주고받는 데이터
  3.3  모듈 간 의존성 규칙

Part 4. 분석 & 변환 규칙
  4.1  이미지 배치 전략 — 포커스 영역
  4.2  Figma 컴포넌트/그룹 처리
  4.3  변환 엔진 핵심 로직
  4.4  레이아웃 연동 속성
  4.5  텍스트 오버플로우 처리
  4.6  소스 버전 추적

Part 5. 품질 관리
  5.1  검증 파이프라인 (Validation Pipeline)
  5.2  미리보기 대시보드 (검수 시스템)
  5.3  에러 처리 흐름
  5.4  핵심 데이터 구조 요약

Part 6. 학습 & 확장
  6.1  피드백 & 학습 시스템
  6.2  규칙 충돌 감지 및 해결
  6.3  확장 계획
  6.4  기존 프로젝트와의 관계
```

---
---

# Part 1. 개요

---

## 1.1 프로젝트 목표

기준 디자인 1개를 Figma에서 읽어와서,
각 매체에 맞는 다양한 사이즈로 레이아웃을 재조정하고,
Figma에 편집 가능한 프레임으로 자동 생성하는 에이전트.

---

## 1.2 설계 원칙

**유연성** — 새 매체/사이즈가 추가되어도 엔진 코드는 수정하지 않는다.
**분리** — 매체 규정(설정)과 변환 로직(엔진)은 분리한다.
**편집 가능** — 출력물은 이미지가 아니라, Figma에서 수정 가능한 레이어 구조다.
**검수 우선** — AI 결과물은 반드시 디자이너 검수를 거친 후 최종 생성한다.

---

## 1.3 전체 흐름 (한눈에 보기)

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
[4] 검증 (Validation Pipeline)
    7개 이상의 체크 항목을 자동 실행
    → 통과하면 다음 단계, 실패하면 중단 또는 자동 보정
         │
         ▼
[5] 미리보기 대시보드 (검수 단계) ⭐ 핵심
    사이즈별 미리보기를 한 화면에 보여줌
    → 디자이너가 각 사이즈별로 검수
    → 개별 승인 / 수정 요청 / 재생성 선택
         │
         ▼
[6] 최종 생성 (Figma Writer)
    디자이너가 지정한 Figma 파일에 "AI Variation" 전용 페이지 생성
    → 승인된 사이즈만 해당 페이지에 프레임 생성
    → 모든 요소가 편집 가능한 레이어로 유지
```

---

## 1.4 폴더 구조

```
design_variation_agent/
├── ARCHITECTURE.md          ← 이 파일 (설계서)
│
├── media_presets/           ← 매체 카테고리별 사이즈 & 규정
│   ├── __init__.py          ← REGISTRY (카테고리/사이즈 자동 인식)
│   ├── base.py              ← 사이즈 규정 데이터 구조 문서
│   ├── internal.py          ← 내부배너 (자사 사이트/앱)
│   ├── external.py          ← 외부배너 (네이버, 카카오, GDN 등)
│   └── etc.py               ← 기타 (이메일, 인쇄 등)
│
├── engine/                  ← 변환 엔진 (매체 이름 하드코딩 없음)
│   ├── __init__.py
│   ├── figma_reader.py      ← Figma 프레임 읽기 (MCP 활용)
│   ├── analyzer.py          ← 레이아웃 분석 (요소 분류, 공간 관계)
│   ├── layout_engine.py     ← 레이아웃 재계산 (핵심 변환 로직)
│   ├── validator.py         ← 검증 실행기 (체크 레지스트리 관리)
│   ├── preview_renderer.py  ← 미리보기 이미지 생성 (검수용)
│   ├── figma_writer.py      ← Figma에 프레임 생성 (MCP 활용)
│   ├── schema.py            ← 데이터 구조 정의
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
│   ├── app.py               ← 대시보드 서버
│   └── templates/
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
│   └── errors.jsonl
│
├── output/                  ← 미리보기 이미지
│   └── .gitkeep
│
└── main.py                  ← 실행 진입점
```

---
---

# Part 2. 입력 & 설정

---

## 2.1 매체 프리셋 구조 (사이즈 & 규정)

### 핵심 개념: 카테고리 → 사이즈 → 규정

매체를 카테고리로 분류하고, 각 카테고리 안에 사이즈를 나열한다.
새 사이즈는 설정 파일에 항목 하나 추가로 끝. 엔진은 건드리지 않는다.

### 카테고리 구분

```
media_presets/
├── internal.py      ← 내부배너 (자사 사이트/앱에 노출)
│   ├── PC 배너
│   └── Mobile 배너
│
├── external.py      ← 외부배너 (외부 매체에 노출)
│   ├── 네이버
│   ├── 카카오
│   ├── GDN
│   └── ...
│
└── etc.py           ← 기타
    ├── 이메일 배너
    └── 인쇄물 (필요 시)
```

### 사이즈별 규정 데이터 구조

각 사이즈마다 이 정보를 담는다:

```python
{
    "name": "main_curtain",
    "display_name": "메인 커튼 배너",
    "category": "internal_pc",
    "width": 2160,
    "height": 160,
    "display_size": "1080x80",          # 화면 내 실제 노출 크기
    "file_size_limit": "30KB",
    "file_types": ["jpg", "jpeg", "gif", "png"],
    "rules": {
        "min_font_size": 12,
        "max_text_ratio": null,
        "padding": {
            "top": 40, "bottom": 40,
            "left": 20, "right": 20
        },
        "source_label": {               # 출처 표기
            "position": "top-right",
            "margin": 8
        },
        "safe_zone": {                   # 세이프 존 (있으면)
            "avoid_areas": []
        },
        "notes": "붉은계열 배경 컬러 지양, BG 블랙 컬러 사용 불가"
    }
}
```

### 새 매체/사이즈 추가 방법

1. 기존 카테고리에 사이즈 추가 → 해당 카테고리 파일에 항목 하나 추가
2. 새 카테고리 추가 → 새 파일 하나 만들고 레지스트리에 등록
3. 엔진 코드 수정: 0줄

### 현재 등록된 내부배너 사이즈 (배너가이드 기준)

```
내부배너 — PC
┌──────────────────┬──────────┬──────────┬────────┬──────────────────────────┐
│ 이름             │ 사이즈    │ 노출위치  │ 용량   │ 특이사항                  │
├──────────────────┼──────────┼──────────┼────────┼──────────────────────────┤
│ 메인 커튼 배너    │ 2160×160 │ 메인 최상단│ 30KB  │ 붉은계열·블랙 BG 불가     │
│ 메인 탑 배너     │ 1556×232 │ 메인 좌측  │ 50KB  │ BI 인접 붉은계열 지양     │
│ 공고 스카이 배너  │ 560×700  │ 채용공고   │ 30KB  │ 흰 배경 BG컬러 사용      │
│ 채용 하단 배너   │ 495×110  │ 서브 하단  │ 30KB  │ 라운딩 불가              │
│ 채용 하단 텍스트  │ 텍스트   │ 서브 하단  │ 30KB  │ 최대 2줄, 줄당 15자      │
│ 로그인 우측 배너  │ 325×310  │ 로그인 우측│ 30KB  │ 라운딩 불가              │
│ 검색 우측 배너   │ 320×155  │ 검색 우측  │ 30KB  │ #DFE6EE BG, 라운딩 불가  │
│ 기업 좌측 배너   │ 200×275  │ 기업 좌측  │ 30KB  │ 라운딩 불가              │
└──────────────────┴──────────┴──────────┴────────┴──────────────────────────┘

내부배너 — Mobile
┌──────────────────┬──────────┬──────────┬────────┬──────────────────────────┐
│ 이름             │ 사이즈    │ 노출위치  │ 용량   │ 특이사항                  │
├──────────────────┼──────────┼──────────┼────────┼──────────────────────────┤
│ 앱 스플래시 배너  │ 1440×976 │ 앱 스플래시│ 300KB │ 투명 png, 로고 고정      │
│ M 서브 배너      │ 1029×258 │ 서브 하단  │ 100KB │ 라운딩 불가, 단색 BG     │
└──────────────────┴──────────┴──────────┴────────┴──────────────────────────┘

내부배너 — E-mail
┌──────────────────┬──────────────┬────────┬──────────────────────────┐
│ 이름             │ 사이즈        │ 유형   │ 특이사항                  │
├──────────────────┼──────────────┼────────┼──────────────────────────┤
│ 타겟메일         │ 700×1500이내  │ HTML  │ 통이미지, (광고)표기 필수   │
└──────────────────┴──────────────┴────────┴──────────────────────────┘
```

### 공통 제작 가이드 (배너가이드 기준)

```
파일명 규정   : 제작일_가로사이즈_세로사이즈_컬러값
                 예) 20230116_752_110_3399ff
확장자        : jpg, jpeg, gif, png
이미지 용량   : 30KB 미만 (배너별 상이)
출처 표기     : 배너 우측 상단에 출처·로고 표기 (여백 8px)
서체          : 고딕 계열 사용
폰트 최소사이즈: PC 12px / Mobile 22px
폰트행간      : 한줄 100% / 두줄 이상 120%
텍스트 컬러   : 최대 2개까지 가능
이미지        : 외곽이 깔끔한 고해상도 이미지·일러스트
배경 컬러     : 단색 권장, 광고 영역과 구분되는 컬러
               패턴/이미지/보색/화이트/명도 높은 색/레드계열/형광색 지양
명도차        : 가독성을 저해하지 않는 명도차
모바일 배너   : 좌우 10px은 단색만 가능 (가변영역)
```

---

## 2.2 디자이너 부연설명 시스템

Figma에서 읽어온 디자인만으로는 AI가 알 수 없는 것들이 있다.
디자이너가 추가 지시를 내릴 수 있는 구조.

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

### 우선순위

```
디자이너 부연설명 > 매체 규정 > AI 자동 판단
```

부연설명은 변환 엔진에 "우선 규칙"으로 전달된다.
AI가 레이아웃을 재구성할 때 이 규칙을 최우선으로 따른다.

---

## 2.3 플랫폼 세이프 존 (Safe Zone)

> ⚠️ 초기 설계안입니다. 실제 매체별 세이프 존 데이터는 나중에 추가합니다.

### 문제

각 매체/플랫폼마다 UI가 콘텐츠 위에 겹치는 영역이 있다.
예: 인스타 스토리 상단(계정 이름), 유튜브 썸네일 우하단(재생시간)

### 해결: 매체 프리셋에 safe_zone 추가

```python
"safe_zone": {
    "avoid_areas": [
        {
            "name": "상단 계정 UI",
            "position": "top",
            "height": 120        # 상단에서 120px까지 금지
        },
        {
            "name": "하단 답장 UI",
            "position": "bottom",
            "height": 160        # 하단에서 160px까지 금지
        }
    ]
}
```

### 엔진에서의 처리

1. padding으로 기본 여백 확보
2. safe_zone의 avoid_areas에 중요 요소(텍스트, CTA, 로고)가 겹치지 않도록 추가 조정
3. 장식 요소는 safe_zone에 들어가도 허용 (가려져도 괜찮으므로)

---
---

# Part 3. 파이프라인 (데이터가 흘러가는 길)

---

## 3.1 전체 데이터 흐름도

각 모듈이 데이터를 받아서 처리하고 다음 모듈에 넘기는 구조.
모듈 사이에 주고받는 데이터의 형태가 명확하게 정의되어 있어야
하나를 수정해도 다른 것이 깨지지 않는다.

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

---

## 3.2 각 모듈이 주고받는 데이터

### 1단계: figma_reader → SourceFrame

Figma에서 프레임을 읽어서 내부 표현으로 변환한다.
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
      role        : null                     ← analyzer가 채울 영역
      bounds      : { x, y, width, height }
      style       : {
        fills       : [...]
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
      auto_layout : {
        direction   : "VERTICAL" | "HORIZONTAL"
        spacing     : 10
        padding     : { top, right, bottom, left }
        alignment   : "MIN" | "CENTER" | "MAX"
      } | null
      constraints : {
        horizontal  : "FIXED" | "SCALE" | "MIN" | ...
        vertical    : "FIXED" | "SCALE" | "MIN" | ...
      }
    },
    ...
  ]

  snapshot        : SourceSnapshot           ← 소스 버전 추적 데이터
```

### 2단계: analyzer → AnalyzedDesign

각 레이어에 역할을 부여하고, 디자인의 공간 구조를 파악한다.

```
AnalyzedDesign:
  source          : SourceFrame              ← 원본 데이터 그대로 포함

  layer_roles     : [
    {
      layer_id    : "1:3"
      role        : "background_image" | "title" | "subtitle" | "cta" |
                    "logo" | "character" | "decoration" | "gradient_overlay" |
                    "info_bar" | "unknown"
      priority    : 1~4                      ← 1:필수, 2:중요, 3:권장, 4:선택
      is_text     : true | false
      is_image    : true | false
      focus_area  : FocusArea | null
    },
    ...
  ]

  spatial_info    : {
    layout_direction : "vertical" | "horizontal" | "centered" | "free"
    text_region      : { x, y, width, height }
    image_region     : { x, y, width, height }
    text_image_ratio : 0.4                   ← 텍스트 영역 비율 (0~1)
    alignment_pattern: "center-center" | "left-top" | ...
  }

  designer_notes  : [
    {
      original    : "제목 텍스트는 줄여도 됨"
      parsed_rule : { type: "text_modify", target: "title", action: "allow_shorten" }
    },
    ...
  ]
```

### 3단계: layout_engine → LayoutPlan

새 사이즈에 맞는 구체적인 레이아웃 계획을 생성한다.

```
LayoutPlan:
  source_size     : { width: 560, height: 700 }
  target_size     : { width: 1200, height: 600 }
  target_preset   : "web_banner"
  target_category : "external"

  layout_type     : "horizontal" | "vertical" | "square"

  element_plans   : [
    {
      layer_id    : "1:3"
      role        : "background_image"
      action      : "resize" | "move" | "scale" | "hide" | "keep"
      original    : { x, y, width, height }
      planned     : { x, y, width, height }
      style_changes: {
        text_align  : "LEFT"
        font_size   : 77.08
        scale_factor: 1.15
      }
      applied_rules: ["rule_001", "layout_linked_alignment"]
    },
    ...
  ]

  warnings        : [
    {
      type        : "text_overflow" | "safe_zone_near" | "element_hidden" | ...
      message     : "부제목이 영역을 초과하여 폰트 크기를 줄였습니다"
      layer_id    : "1:5"
      severity    : "info" | "warning" | "error"
    },
    ...
  ]

  metadata        : {
    generation_time : "2026-04-23T15:00:00"
    rules_applied   : ["rule_001", "rule_003"]
    engine_version  : "0.1.0"
  }
```

### 4단계: validator → ValidationResult

```
ValidationResult:
  passed          : true | false
  layout_plan     : LayoutPlan

  checks          : [
    {
      check_id    : "output_location"
      check_name  : "출력 위치 확인"
      passed      : true
      severity    : "block" | "warn"
      message     : ""
    },
    ...
  ]

  blocked         : false
  warnings_count  : 1
  errors_count    : 0
```

### 5단계: figma_writer → FigmaOutput

```
FigmaOutput:
  success         : true | false
  file_key        : "S0i1zFhCEF04F1rqBmMUZZ"
  page_name       : "AI Variation"
  created_frames  : [
    {
      preset_name : "web_banner"
      frame_id    : "23:3"
      frame_name  : "AI_web_banner_1200x600"
      url         : "https://figma.com/..."
    },
    ...
  ]
  errors          : [
    {
      frame       : "web_banner"
      error       : "폰트 로드 실패: Paperlogy 8 ExtraBold"
      fallback    : "rescale 방식으로 대체 적용"
    },
    ...
  ]
```

---

## 3.3 모듈 간 의존성 규칙

```
1. 단방향 흐름만 허용한다
   figma_reader → analyzer → layout_engine → validator → figma_writer
   역방향 호출 금지.

2. 모듈은 인접 모듈의 출력만 사용한다
   layout_engine은 AnalyzedDesign만 받는다.
   SourceFrame을 직접 참조하려면 AnalyzedDesign.source를 통해서만.

3. 외부 의존(Figma API)은 양 끝에서만
   figma_reader와 figma_writer만 Figma를 직접 호출한다.
   중간 모듈은 Figma를 모른다.

4. 설정 데이터는 수평으로 주입한다
   MediaPreset, LearnedRules는 layout_engine에 직접 주입된다.
   다른 모듈의 출력을 거치지 않는다.
```

---
---

# Part 4. 분석 & 변환 규칙

---

## 4.1 이미지 배치 전략 — 포커스 영역 (Focus Area)

> ⚠️ 초기 설계안입니다. 실제 구현 과정에서 변경될 수 있습니다.

### 문제

사이즈 변환 시 프레임 비율이 달라지면, 이미지가 프레임 안에서 어떤 위치·스케일로 보여야 하는지 기준이 필요하다.
(피그마에서는 이미지를 자르지 않고, 프레임이 마스크 역할을 하므로 이미지 원본은 유지됨)

### 해결: 포커스 영역

이미지에서 "반드시 보여야 하는 핵심 영역"을 한 번만 지정하면,
어떤 사이즈로 변환하든 그 영역이 항상 보이도록 위치와 스케일을 자동 계산한다.

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

**미지정 시** — 기본값은 이미지 중앙 (center-center)

### 배치와의 관계

디자이너가 원하는 배치가 다르면 부연설명으로 덮어쓸 수 있다.
예: 세로형인데 "위에 이미지, 아래에 텍스트로 배치해줘"
→ 부연설명이 우선 적용됨

### 데이터 구조

```
FocusArea:
  target_layer    : "background_image"
  mode            : "auto" | "manual"
  description     : "인물 중심"
  area            : { x, y, width, height }  ← 시각적 도구로 지정 시
  fallback        : "center-center"
```

---

## 4.2 Figma 컴포넌트/그룹 처리 전략

> ⚠️ 초기 설계안입니다. 추가 피그마 파일 학습 후 보완이 필요합니다.
> 📌 TODO: 카드뉴스, 포스터, SNS 등 다른 콘텐츠 유형도 분석 필요

### 현재까지 학습한 패턴 (외부배너 16개 프레임 기준)

**패턴 1: 기능별 그룹핑**

```
루트 FRAME (CLIP 적용, 배경색 채움)
├── 텍스트 블록 (FRAME, AL:VERTICAL) — 21~24 nodes
├── 일러스트/장식 (GROUP, 오토레이아웃 없음) — 379~502 nodes
└── 하단 바 (FRAME, AL:HORIZONTAL) — 119 nodes (있거나 없음)
```

**패턴 2: 오토레이아웃 사용 규칙**

- 텍스트 영역 → FRAME + VERTICAL 오토레이아웃
- 하단 바/로고 영역 → FRAME + HORIZONTAL 오토레이아웃
- 일러스트/장식 그래픽 → GROUP, 오토레이아웃 없음 (자유 배치)

**패턴 3: 사이즈별 레이어 재배치**

```
가로형 (1200x628)  → 텍스트 좌 + 그래픽 우, 하단 바 생략
정방형 (1200x1200) → 그래픽 상 + 텍스트 하, 하단 바 포함
세로형 (1200x1500) → 텍스트 상 + 그래픽 하, 하단 바 생략
```

### 변환 엔진에서의 처리 방식

1. 원본 프레임의 최상위 자식들을 역할별로 분류 (텍스트/그래픽/바)
2. 타겟 사이즈의 비율에 따라 배치 전략 결정
3. 각 그룹을 통째로 이동/리사이즈 (내부 구조는 유지)
4. 오토레이아웃이 있는 그룹은 설정 유지
5. 자유 배치 그룹(일러스트)은 포커스 영역 기준으로 위치/스케일 조정

### 아직 확인 필요한 것들

- [ ] 카드뉴스, 포스터 등 다른 콘텐츠 유형도 같은 패턴인지
- [ ] 컴포넌트/인스턴스를 사용하는 디자인 처리 방법
- [ ] 더 복잡한 중첩 구조(3단계 이상)의 처리
- [ ] 네이밍 규칙을 활용한 자동 역할 분류 가능 여부

---

## 4.3 변환 엔진 핵심 로직

### AI가 판단하는 것들

1. **위치 재계산** — 비율 기반으로 요소 위치를 새 사이즈에 맞게 조정
2. **폰트 크기 조정** — 매체 규정의 최소 폰트 크기를 지키면서 비례 조정
3. **요소 순서 변경** — 가로형 → 세로형 전환 시 배치 순서 변경
4. **요소 숨기기** — 공간 부족 시 덜 중요한 요소 제거
5. **텍스트 축약** — 긴 제목을 짧은 버전으로 조정
6. **여백 조정** — 매체별 안전 영역(safe zone) 적용

### 요소 우선순위 (공간 부족 시 낮은 것부터 숨김)

```
1순위 🔴 필수 — 로고, 메인 제목
2순위 🟠 중요 — CTA 버튼, 핵심 이미지
3순위 🟡 권장 — 부제목, 설명 텍스트
4순위 🟢 선택 — 장식 요소, 배경 패턴, 부가 텍스트
```

디자이너 부연설명으로 이 우선순위를 덮어쓸 수 있다.

---

## 4.4 레이아웃 연동 속성

> 이 섹션은 지속적으로 추가됩니다. 실제 작업에서 발견되는 규칙을 계속 추가해 주세요.

### 왜 필요한가

사이즈가 바뀌면 위치/크기뿐 아니라, 텍스트 정렬·줄간격·자간 등
함께 바뀌어야 하는 속성들이 있다.

### 현재 등록된 연동 속성

**1. 텍스트 정렬 (text alignment)**

```
가로형 (텍스트 좌측 배치) → 좌측 정렬 (LEFT)
정사각형 (텍스트 중앙 배치) → 가운데 정렬 (CENTER)
세로형 (텍스트 상단 배치) → 가운데 정렬 (CENTER)
```

디자이너 부연설명으로 덮어쓸 수 있음.

**2. 폰트 크기 비례 조정** — 텍스트 영역 비율에 맞게, min_font_size 이하로는 줄이지 않음

**3. 줄간격 (line height)** — 원본의 폰트 대비 줄간격 비율을 유지

**4. 자간 (letter spacing)** — 원본의 자간 설정을 유지, 폰트 크기가 바뀌어도 비율은 동일

### 속성 추가 방법

실제 작업 중 "이것도 같이 바뀌어야 했는데" 하는 항목이 발견되면
이 섹션에 추가하고, 검증 단계에도 체크 항목을 함께 추가한다.

---

## 4.5 텍스트 오버플로우 처리

### 2단계 대응 + 알림

텍스트가 넘칠 때 아래 순서로 대응한다.
2단계까지 해서 안 되면 자동 처리하지 않고 디자이너에게 알린다.

```
[1단계] 줄바꿈 조정
    - 단어가 잘리지 않도록 단어 단위로 줄바꿈
    - 맥락에 맞게 의미 단위로 끊기
    - 예: "2026년 상반기 신규 채용 대규모 공개 모집"
      → "2026년 상반기
         신규 채용
         대규모 공개 모집"
         │
         ▼
[2단계] 폰트 크기 줄이기
    - 매체 프리셋의 min_font_size까지만 줄임
         │
         ▼
[알림] 디자이너에게 조치 필요 알림
    - 대시보드에 "⚠️ 텍스트 오버플로우: 수동 조치 필요" 표시
```

### 왜 자동 축약을 안 하는가

텍스트를 AI가 임의로 줄이면 의도와 다른 결과물이 나올 수 있다.
판단이 필요한 상황은 디자이너에게 넘긴다 (검수 우선 원칙).

---

## 4.6 소스 버전 추적

### 문제

원본 디자인이 피그마에서 수정될 수 있다.
이전에 만든 베리에이션이 옛날 버전 기준이라 안 맞게 될 수 있다.

### 해결: 원본 스냅샷 기록

```
SourceSnapshot:
  figma_file_id   : "OsIOTyo6kx..."
  frame_id        : "74:5547"
  frame_name      : "jk_googleac_1200x1200_a"
  captured_at     : "2026-04-23T14:30:00"
  last_modified   : "2026-04-22T10:00:00"
  layer_summary   : {
    total_children: 3,
    child_names: ["illustration", "bottom_bar", "text_block"],
    text_contents: ["신규 채용 오픈", "지금 바로 지원하세요"]
  }
```

### 동작 방식

```
[1] 첫 베리에이션 생성 시 → 스냅샷 저장
[2] 같은 프레임으로 다시 요청 시 → 현재 vs 저장된 스냅샷 비교
    ├─ 변경 없음 → 정상 진행
    └─ 변경 있음 → "원본이 수정되었습니다" 알림 + 새 스냅샷 업데이트
```

---
---

# Part 5. 품질 관리

---

## 5.1 검증 파이프라인 (Validation Pipeline)

### 왜 필요한가

설계서에 합의한 규칙이 실행 과정에서 빠지거나 누락되면,
나중에 문제가 눈덩이처럼 커진다.
검증 단계를 코드에 강제해서, 규칙을 하나라도 건너뛰면 생성 자체가 안 되도록 막는다.

### 설계 원칙: 플러그인 방식

각 검증 항목은 독립적인 "체크 모듈"이다.
`checks/` 폴더에 파일 하나 추가하면 자동으로 등록된다.
코드에 하드코딩하지 않는다.

### 체크 모듈 구조

```
CheckModule:
  id              : "output_location"        ← 고유 ID
  name            : "출력 위치 확인"
  severity        : "block" | "warn"         ← 실패 시 중단 or 경고만
  phase           : "pre_layout" | "post_layout" | "pre_generation"
  order           : 100                      ← 같은 phase 안에서의 실행 순서
  enabled         : true                     ← 비활성화 가능

  check(layout_plan, context) → CheckResult
```

### 실행 시점 3단계

```
[Phase 1] pre_layout — 변환 전 (입력이 유효한가?)
[Phase 2] post_layout — 변환 후 (결과가 규칙에 맞는가?)
[Phase 3] pre_generation — 생성 직전 (최종 확인)
```

### 현재 등록된 체크 목록

```
Phase 1: pre_layout
  output_location  [block]  AI Variation 전용 페이지 지정 확인
  source_version   [warn]   원본 스냅샷 기록 확인

Phase 2: post_layout
  focus_area       [warn]   이미지 포커스 영역 적용 확인
  safe_zone        [block]  중요 요소의 세이프 존 침범 확인
  text_overflow    [warn]   텍스트 오버플로우 감지
  layout_linked    [warn]   텍스트 정렬·줄간격 연동 확인
  bounds_check     [warn]   모든 요소가 프레임 안에 있는지 확인

Phase 3: pre_generation
  layer_structure  [block]  편집 가능한 레이어 구조 유지 확인
  approval_status  [block]  디자이너 승인 상태 확인
```

### 자동 보정 (Auto-fix)

일부 체크는 실패 시 스스로 보정한다:

```
focus_area     : 미지정 → 기본값(center-center) 자동 적용
source_version : 스냅샷 없음 → 현재 상태로 자동 생성
layout_linked  : 텍스트 정렬 미변경 → 배치에 맞게 자동 변경
bounds_check   : 프레임 밖 요소 → 프레임 안으로 자동 이동
```

---

## 5.2 미리보기 대시보드 (검수 시스템)

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
│  │  [원본]   │  크기: 1080 x 1080                            │
│  └──────────┘                                               │
│                                                             │
│  ─── 내부배너 PC ───────────────────────────────────────     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │메인커튼   │  │공고스카이 │  │로그인우측 │                  │
│  │2160x160  │  │560x700   │  │325x310   │                  │
│  │ ✅ 승인  │  │ ⚠️ 수정  │  │ ✅ 승인  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                             │
│  승인: 2개  │  수정 필요: 1개                                │
│                                                             │
│  [ 수정 사항 적용하고 재미리보기 ]  [ 승인된 것만 Figma 생성 ]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 검수 옵션

```
✅ 승인    → 이 사이즈는 그대로 Figma에 생성해도 됨
⚠️ 수정    → 수정 지시를 남기면 해당 사이즈만 재생성
❌ 재생성  → AI가 다른 레이아웃 방식으로 재시도
```

### 검수 루프

```
미리보기 생성 → 디자이너 검수
  ├─ ✅ 승인 → 대기
  ├─ ⚠️ 수정 → 수정 반영 → 재미리보기
  └─ ❌ 재생성 → 새로 생성 → 재미리보기

모두 승인 완료 → [ Figma에 최종 생성 ]
```

### 구현 단계

```
1단계: 텍스트 기반으로 검수 (빠르게 시작)
2단계: 웹 대시보드 (HTML) — 시각적으로 미리보기 비교
3단계: 독립 웹 서비스 — URL로 접속, 팀 공유 가능
```

---

## 5.3 에러 처리 흐름

### 에러 3단계

```
[FATAL]       — 더 이상 진행 불가. 즉시 중단, 디자이너에게 알림.
[RECOVERABLE] — 대안(fallback)이 있어서 계속 진행 가능. 경고 표시.
[WARNING]     — 결과에 영향 적음. 로그 기록.
```

### 모듈별 주요 에러

```
figma_reader
  FATAL        : 파일 접근 불가, 프레임 ID 없음, 빈 프레임
  RECOVERABLE  : API 타임아웃 → 3회 재시도

analyzer
  WARNING      : 레이어 역할 판단 불가 → "unknown"으로 설정
  WARNING      : 부연설명 파싱 실패 → 무시하고 진행

layout_engine
  FATAL        : 매체 프리셋 못 찾음
  RECOVERABLE  : 텍스트 오버플로우 → min_font_size로 설정
  RECOVERABLE  : 규칙 충돌 → 충돌 해결 로직 실행
  RECOVERABLE  : 요소 프레임 밖 → 자동 보정

validator
  FATAL        : block 레벨 검증 실패
  WARNING      : warn 레벨 검증 실패

figma_writer
  FATAL        : 출력 파일 접근 불가
  RECOVERABLE  : 폰트 로드 실패 → rescale() 방식으로 대체
  RECOVERABLE  : 개별 프레임 실패 → 해당 사이즈만 건너뜀
```

### 에러 전파 규칙

```
1. FATAL은 즉시 전체 파이프라인을 중단한다.
2. RECOVERABLE은 대안을 실행하고, warnings에 기록한다.
3. WARNING은 로그에만 기록한다.
4. 같은 RECOVERABLE 에러가 3회 이상 → FATAL로 승격한다.
5. 정의되지 않은 에러는 FATAL로 처리한다.
   → 테스트를 통해 발견될 때마다 적절한 레벨과 대응을 정의하여 추가한다.
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

## 5.4 핵심 데이터 구조 요약

### VariationRequest (입력 양식)

```
VariationRequest:
  figma_url       : "https://figma.com/..."    ← 원본 프레임 링크 (필수)
  output_figma_url: "https://figma.com/..."    ← 결과물 생성할 파일 링크 (필수)
  designer_notes  : ["제목 줄여도 됨", ...]     ← 부연설명 (선택)
  target_sizes    : ["all"] 또는 ["main_curtain", "sky_banner"]
  target_category : "internal_pc" 또는 "" (전체)
```

### VariationResult (결과)

```
VariationResult:
  source_frame    : { 원본 프레임 정보 }
  variations      : [
    {
      size: "main_curtain",
      preview_path: "output/preview_main_curtain.png",
      layout_data: { ... },
      review_status: "approved" | "revision" | "rejected" | "pending",
      revision_note: "",
      figma_frame_id: "",
    },
    ...
  ]
```

### ReviewStatus (검수 상태)

```
pending   → 아직 검수 전
approved  → ✅ 승인됨
revision  → ⚠️ 수정 요청
rejected  → ❌ 재생성
```

---
---

# Part 6. 학습 & 확장

---

## 6.1 피드백 & 학습 시스템

### 목표

AI가 같은 실수를 반복하지 않고, 사용할수록 결과물 품질이 올라가는 구조.
디자이너의 검수 결과와 수정 이력이 곧 학습 데이터가 된다.

### 피드백 데이터 수집

대시보드에서 검수할 때 자동으로 기록되는 것들:

```
FeedbackRecord:
  timestamp       : "2026-04-23T14:30:00"
  source_design   : { 원본 프레임 정보 }
  target_size     : "main_curtain"
  target_category : "internal_pc"
  ai_layout       : { ... AI가 계산한 레이아웃 ... }
  review_status   : "revision"
  revision_note   : "캐릭터 40% 줄이고 텍스트 왼쪽 정렬"
  final_layout    : { ... 최종 승인된 레이아웃 ... }
  issue_tags      : ["element_too_large", "alignment_wrong"]
```

### 학습 흐름

```
[1] 피드백 수집 — 검수할 때마다 자동 기록
         │
[2] 패턴 분석 — 반복되는 문제 추출
         │
[3] 규칙 반영 — 매체 규정 또는 AI 프롬프트에 반영
         │
[4] 품질 향상 — 다음 변환부터 같은 실수 없이
```

### 학습 3단계

```
1단계 (규칙 기반) — 피드백에서 뽑은 패턴을 매체 규정에 명시적으로 추가
2단계 (사례 기반) — 과거 수정 사례를 AI에게 알려줌
3단계 (자동 학습) — 승인율이 높은 레이아웃 패턴을 자동으로 우선 적용
```

### 즉시 학습 입력 시스템

디자이너가 피드백을 주면 바로 규칙으로 반영할 수 있는 구조.
`learned_rules.json`만 수정하면 다음 변환부터 적용된다.

```json
{
  "version": "1.0",
  "rules": [
    {
      "id": "rule_001",
      "category": "text_size",
      "condition": "프레임 면적이 원본보다 커지면",
      "action": "텍스트를 비례 확대한다",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

#### 규칙 카테고리

```
text_size / text_alignment / text_position / image_placement
image_scale / gradient / spacing / safe_zone / layer_structure / general
```

#### 학습 입력 방식

```
[방법 1] 직접 피드백 — "텍스트가 너무 작아" → 규칙 추가
[방법 2] 비교 학습 — 원본 vs 결과물 비교하며 교정
[방법 3] 레퍼런스 학습 — "이 디자인처럼 해줘" → 패턴 추출
```

#### 규칙 우선순위

```
1순위: learned_rules.json의 priority: "high"
2순위: ARCHITECTURE.md에 명시된 기본 규칙
3순위: learned_rules.json의 priority: "normal"
4순위: 엔진 기본값
```

#### 규칙 상태

```
pending  : 추가됨, 아직 검증 안 됨
active   : 검증 완료, 적용 중
disabled : 비활성화 (문제 발견)
archived : 더 나은 규칙으로 대체됨
```

### 측정 지표

```
1차 승인율      : 수정 없이 바로 승인된 비율 (높을수록 좋음)
수정 빈도       : 평균 몇 번 수정해야 승인되는지 (낮을수록 좋음)
카테고리별 승인율 : 어떤 매체 유형에서 잘하고, 어디서 약한지
시간 추이       : 사용할수록 승인율이 올라가는지
```

---

## 6.2 규칙 충돌 감지 및 해결

### 왜 필요한가

학습 규칙이 쌓이면서 서로 모순되는 규칙이 생길 수 있다.
예: "프레임 커지면 텍스트 확대" vs "가로 배너에서는 텍스트 작게"

### 충돌 유형

```
[유형 1] 직접 충돌 — 같은 속성에 대해 반대 지시
  rule_A: text_size → "확대"
  rule_B: text_size → "축소"

[유형 2] 조건 중첩 — 조건이 겹쳐서 동시에 적용됨
  rule_A: "프레임이 원본보다 크면" → 텍스트 확대
  rule_B: "가로형 배너일 때" → 텍스트 축소
  → 1200x600은 둘 다 해당

[유형 3] 간접 충돌 — 다른 속성이지만 결과적으로 모순
  rule_A: spacing → "여백 넓히기"
  rule_B: text_size → "텍스트 확대"
  → 여백 넓히면 텍스트 공간 줄어듦
  ⚠️ 간접 충돌은 사전 감지가 어렵다.
     레이아웃 계산 후 검증 파이프라인이 결과적으로 잡아낸다.
```

### 충돌 해결 우선순위

```
1순위: 디자이너 부연설명에서 온 규칙
2순위: 더 구체적인 조건의 규칙 (특정 매체 > 일반 조건)
3순위: 더 최근에 만들어진 규칙
4순위: priority가 높은 규칙
5순위: 해당 매체에서 승인율이 높은 규칙
```

### 디자이너에게 표시

```
⚠️ 규칙 충돌 감지
  - rule_001: "프레임이 커지면 텍스트 확대" 
  - rule_015: "가로형 배너에서는 텍스트 작게"
  → rule_015 적용됨 (이유: 더 구체적인 조건)
  
  이 결정이 맞지 않으면 검수에서 수정해주세요.
```

### 충돌 학습

디자이너가 충돌 해결 결과를 수정하면, 다음 같은 충돌에 그 판단이 반영된다.

---

## 6.3 확장 계획

### 당장은 안 하지만, 나중에 추가할 수 있는 것들

- [ ] 브랜드 스타일 시스템 연동 (기존 프로젝트에서 가져오기)
- [ ] 배치 처리 (여러 기준 디자인을 한 번에)
- [ ] SVG 출력 옵션 (Figma 없이도 사용)
- [ ] 팀 공유 대시보드 (여러 디자이너가 함께 검수)

---

## 6.4 기존 프로젝트와의 관계

| 항목 | 기존 (card_news_generator) | 신규 (design_variation_agent) |
|------|---------------------------|-------------------------------|
| 목표 | 자연어 → 디자인 자동 생성 | 기준 디자인 → 사이즈별 변환 |
| 입력 | 텍스트 (주제/분위기) | Figma 프레임 + 부연설명 |
| 출력 | SVG/PNG 파일 | Figma 프레임 직접 생성 |
| 핵심 | 카피 생성 + 템플릿 매핑 | 레이아웃 분석 + 재구성 |
| 상태 | 1차 프로토타입 완성 | 설계 완료 + 구조 보강 완료 |

두 프로젝트는 독립적이지만, 나중에 브랜드 스타일 데이터 등은 공유할 수 있다.
