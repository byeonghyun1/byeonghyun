# AI 콘텐츠 디자인 에이전트 시스템 — 아키텍처 설계서

## 1. 설계 원칙

**유연성**: 입력 통로, 콘텐츠 유형, 브랜드가 추가되어도 엔진 코어는 수정하지 않는다.
**확장성**: 새로운 기능은 기존 코드를 고치는 게 아니라, 새 모듈을 "꽂는" 방식으로 추가한다.
**분리**: 입력(Input) · 엔진(Engine) · 출력(Output) 세 계층은 서로 직접 의존하지 않는다.

---

## 2. 전체 구조 (3계층)

```
┌─────────────────────────────────────────────────────┐
│                    입력 계층 (Input Layer)             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Google   │ │  Slack   │ │  Web     │ │  CLI    │ │
│  │ Sheets   │ │  Bot     │ │  API     │ │         │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘ │
│       │            │            │            │      │
│       └────────────┴─────┬──────┴────────────┘      │
│                          │                          │
│                   ┌──────▼──────┐                    │
│                   │  Adapter    │  ← 각 통로별 변환기  │
│                   │  (변환기)    │                    │
│                   └──────┬──────┘                    │
└──────────────────────────┼──────────────────────────┘
                           │
                    표준 요청 (DesignRequest)
                           │
┌──────────────────────────▼──────────────────────────┐
│                    엔진 계층 (Engine Core)            │
│                                                     │
│  ┌─────────────┐                                    │
│  │  요청 분석기  │  ← 자연어 해석, 유효성 검사          │
│  └──────┬──────┘                                    │
│         │                                           │
│  ┌──────▼──────┐  ┌──────────────┐                   │
│  │  카피 생성기  │  │  브랜드 스타일  │                   │
│  │ (CopyWriter)│  │  (StyleGuide) │                  │
│  └──────┬──────┘  └───────┬──────┘                   │
│         │                 │                          │
│  ┌──────▼─────────────────▼──────┐                   │
│  │       템플릿 매핑기            │                   │
│  │    (TemplateMapper)           │                   │
│  └──────────────┬────────────────┘                   │
│                 │                                    │
│  ┌──────────────▼────────────────┐                   │
│  │         렌더러                │                   │
│  │       (Renderer)             │                   │
│  └──────────────┬────────────────┘                   │
│                 │                                    │
└─────────────────┼───────────────────────────────────┘
                  │
           표준 결과 (DesignResult)
                  │
┌─────────────────▼───────────────────────────────────┐
│                    출력 계층 (Output Layer)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ 파일저장  │ │ Slack    │ │ Figma    │ │ Google  │ │
│  │ (PNG등)  │ │ 전송     │ │ Export   │ │ Drive   │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 3. 표준 요청 형식 (DesignRequest)

모든 입력 통로는 이 형식으로 변환되어 엔진에 들어온다. 
엔진은 "누가 보냈는지"를 모르고, 이 형식만 처리한다.

```
DesignRequest:
  ══════════════════════════════════
   ▣ 첫 입력 목록 (사용자가 직접 입력)
  ══════════════════════════════════

  topic           : "봄맞이 세일"                 ← 주제        (필수)
  target          : "20-30대 직장인 여성"          ← 타겟        (필수)
  purpose         : "click" | "signup" | "info" | "brand_awareness"
                                                 ← 목적        (필수)
                    - click           : 클릭 유도
                    - signup          : 신청 유도
                    - info            : 정보 전달
                    - brand_awareness : 브랜드 인지도

  mood            : "활기찬"                      ← 분위기      (선택)

  copy_mode       : "manual" | "ai" | "refine"    ← 카피 방식   (필수)
                    - manual : 직접 입력 (기획자가 카피 제공, AI 개입 없음)
                    - ai     : AI가 주제 기반으로 자동 카피 생성
                    - refine : AI가 기존 카피를 자연스럽게 다듬기

  cta             : "지금 신청하기"               ← 행동 유도 문구 (선택)

  ══════════════════════════════════
   ▣ 시스템 설정 (기본값 또는 자동 선택)
  ══════════════════════════════════

  ── 콘텐츠 유형 ──
  content_type    : "card_news" | "banner" | "poster" | "ad_creative" | "sns_thumbnail" | ...

  ── 브랜드 ──
  brand           : "albamon" | "jobkorea" | "worxphere" | ""

  ── 템플릿 (선택) ──
  template_id     : "promo_banner_01" | "" (자동 선택)

  ── 이미지 설정 ──
  image_mode      : "none" | "asset" | "generate"
                    - none     : 이미지 없이 텍스트만 (카드뉴스 등)
                    - asset    : 기존 이미지 창고에서 선택
                    - generate : AI로 새로 생성 (Midjourney / Gemini / DALL-E)
  image_prompt    : "밝고 활기찬 봄 배경"  ← AI 생성 시 이미지 설명
  image_generator : "midjourney" | "gemini" | "dalle"
  image_asset_id  : "bg_spring_01"  ← 기존 에셋 사용 시 ID

  ── 스타일 오버라이드 (선택) ──
  style_overrides : { bg_color: "#FF0000", ... }

  ── 출력 설정 ──
  output_format   : "png" | "html" | "pdf"
  output_size     : { width: 1080, height: 1080 }
  output_targets  : ["file", "slack", "drive"]  ← 여러 출력 통로 동시 선택 가능
  slack_channel   : "#design-output"    ← 슬랙 전송 시
  drive_folder    : "콘텐츠/2026/04"    ← 드라이브 업로드 시

  ── 메타정보 ──
  source          : "google_sheets" | "slack" | "web" | "cli"
  request_id      : "uuid"
  requested_at    : "2026-04-10T14:00:00"
```

### 3-1. 첫 입력 목록 요약

사용자(기획자/디자이너)가 실제로 채워야 할 항목은 아래 6가지입니다.
나머지는 시스템이 기본값이나 자동 판별로 채웁니다.

| 순서 | 항목 | 필수/선택 | 예시 |
|------|------|----------|------|
| 1 | **주제** (topic) | 필수 | "봄맞이 세일" |
| 2 | **타겟** (target) | 필수 | "20-30대 직장인 여성" |
| 3 | **목적** (purpose) | 필수 | 클릭 유도 / 신청 유도 / 정보 전달 / 브랜드 인지도 |
| 4 | **분위기** (mood) | 선택 | "활기찬", "세련된", "귀여운" |
| 5 | **카피 방식** (copy_mode) | 필수 | manual / ai / refine |
| 6 | **CTA** (cta) | 선택 | "지금 신청하기" |

---

## 4. 입력 어댑터 (Input Adapter)

각 입력 통로마다 하나의 어댑터가 있다.
어댑터의 역할은 딱 하나: **외부 데이터 → DesignRequest 변환**

### 어댑터 목록 (순서대로 구현)

| 순서 | 어댑터 | 설명 | 입력 형태 |
|------|--------|------|----------|
| 1 | CLI Adapter | 터미널 입력 (현재 main.py) | 커맨드라인 인자 |
| 2 | Google Sheets Adapter | 시트 행 데이터 읽기 | 행(row) dict |
| 3 | Slack Adapter | 슬랙 메시지/명령어 파싱 | 메시지 텍스트 |
| 4 | Web API Adapter | REST API 요청 처리 | JSON body |

### 어댑터 구현 규칙

- 어댑터는 DesignRequest만 생성하고, 엔진 내부 로직을 절대 호출하지 않는다
- 새 통로 추가 = 새 어댑터 파일 하나 추가. 다른 코드 수정 없음
- 어댑터 안에서 입력 유효성 기본 검사 (빈 값 체크 등)

---

## 5. 엔진 코어 (Engine Core)

엔진은 콘텐츠 유형에 상관없이 동일한 파이프라인을 실행한다.

### 5-1. 파이프라인 흐름

```
DesignRequest
  → [1] 요청 분석 (RequestAnalyzer)
      - 자연어 해석 (필요 시 AI)
      - content_type 판별
      - 누락된 필드 기본값 채우기

  → [2] 카피 처리 (CopyWriter) — copy_mode에 따라 동작이 달라짐
      - manual : 이 단계를 건너뜀 (입력받은 카피를 그대로 다음 단계로 전달)
      - ai     : AI가 주제·분위기를 기반으로 카피를 처음부터 생성
      - refine : AI가 입력된 카피를 다듬어서 개선 (원본 유지하며 보완)
      - content_type별 카피 전략 선택
      - 결과: 제목, 설명, 뱃지, 푸터 등 텍스트 세트

  → [3] 이미지 처리 (ImageHandler) — image_mode에 따라 동작이 달라짐
      - none     : 이미지 없이 진행 (텍스트 위주 콘텐츠)
      - asset    : 기존 이미지 창고에서 에셋 선택
      - generate : AI 이미지 생성 도구로 자동 생성 (Midjourney / Gemini / DALL-E)
      - 결과: 템플릿에 들어갈 이미지 파일 경로

  → [4] 스타일 결정 (StyleResolver)
      - 우선순위: 오버라이드 > 브랜드 > 분위기 > 기본값
      - 브랜드 스타일 가이드에서 색상/폰트/로고 가져오기
      - 결과: 완전한 스타일 세트 (색상, 폰트, 간격 등)

  → [5] 템플릿 매핑 (TemplateMapper)
      - content_type + brand 조합으로 적합한 템플릿 선택
      - 텍스트 + 스타일 + 이미지 데이터를 템플릿에 바인딩
      - 결과: 렌더링 가능한 중간 결과물 (HTML 등)

  → [6] 렌더링 (Renderer)
      - Playwright / Pillow / HTML 등 자동 선택
      - output_format에 맞는 최종 파일 생성
      - 결과: 파일 경로

  → DesignResult
```

### 5-2. content_type 확장 방식

카드뉴스, 배너, 포스터 등은 엔진 입장에서 "설정값이 다를 뿐 파이프라인은 같다".

```
content_types/
  ├── card_news.yaml      ← 카드뉴스 기본 설정
  ├── banner.yaml         ← 배너 기본 설정
  ├── poster.yaml         ← 포스터 기본 설정
  ├── sns_thumbnail.yaml  ← SNS 썸네일 기본 설정
  └── smart_store.yaml    ← 스마트스토어 상세페이지
```

각 YAML 파일에 해당 콘텐츠 유형의 기본 크기, 레이아웃, 카피 전략 등을 정의.
새 콘텐츠 유형 추가 = YAML 파일 하나 + 템플릿 파일 추가. 엔진 코드 수정 없음.

예시 (card_news.yaml):
```
name: "카드뉴스"
default_size: { width: 1080, height: 1080 }
default_template: "card_basic"
copy_strategy: "title_badge_desc"
required_fields: ["title"]
optional_fields: ["description", "badge", "footer"]
```

---

## 6. 브랜드 스타일 시스템 (Brand Style Guide)

현재: 색상 4개만 정의
목표: 브랜드의 전체 디자인 시스템을 데이터로 관리

### 6-1. 브랜드 프로필 구조

```
brands/
  ├── albamon/
  │   ├── brand.yaml       ← 브랜드 기본 정보
  │   ├── colors.yaml      ← 컬러 시스템
  │   ├── typography.yaml  ← 폰트/타이포 규칙
  │   ├── assets/          ← 로고, 아이콘 등
  │   │   ├── logo.svg
  │   │   └── icon.png
  │   └── templates/       ← 브랜드 전용 템플릿 (선택)
  │
  ├── jobkorea/
  │   └── ...
  │
  └── worxphere/
      └── ...
```

예시 (albamon/brand.yaml):
```
name: "알바몬"
name_en: "albamon"

tone: "친근하고 밝은"
target: "아르바이트를 찾는 2030"

logo:
  primary: "assets/logo.svg"
  icon: "assets/icon.png"
  min_height: 40
```

예시 (albamon/colors.yaml):
```
primary: "#FF6D00"
secondary: "#FFF8E1"
text:
  heading: "#212121"
  body: "#555555"
  on_primary: "#FFFFFF"
background:
  default: "#FFFFFF"
  light: "#FFF8E1"
  dark: "#212121"
accent: "#FF6D00"
```

### 6-2. 스타일 결정 우선순위

```
높음 ← 오버라이드 (사용자 직접 지정)
       브랜드 스타일 (brand.yaml)
       분위기 프리셋 (mood)
낮음 ← 시스템 기본값 (default)
```

브랜드가 지정되면 분위기(mood)보다 브랜드 컬러가 우선.
사용자가 직접 색상을 지정하면 모든 것을 덮어씀.

---

## 7. 템플릿 시스템

### 7-1. 템플릿 구조

```
templates/
  ├── _base/              ← 공통 레이아웃/컴포넌트
  │   ├── base.html
  │   └── components/
  │       ├── badge.html
  │       ├── divider.html
  │       └── footer.html
  │
  ├── card_news/          ← 콘텐츠 유형별 폴더
  │   ├── basic.html
  │   ├── photo_bg.html
  │   └── multi_column.html
  │
  ├── banner/
  │   ├── promo.html
  │   └── event.html
  │
  ├── poster/
  │   └── ...
  │
  └── sns/
      └── ...
```

### 7-2. 템플릿 레지스트리

```
template_registry.yaml:

card_news:
  basic:
    file: "card_news/basic.html"
    description: "기본 카드뉴스 (뱃지+제목+설명)"
    variables: ["badge", "title", "description", "footer"]
    default_size: { width: 1080, height: 1080 }

  photo_bg:
    file: "card_news/photo_bg.html"
    description: "사진 배경 카드뉴스"
    variables: ["badge", "title", "description", "bg_image"]
    default_size: { width: 1080, height: 1080 }

banner:
  promo:
    file: "banner/promo.html"
    description: "프로모션 배너"
    variables: ["title", "subtitle", "cta_text", "bg_image"]
    default_size: { width: 1200, height: 628 }
```

새 템플릿 추가 = HTML 파일 + 레지스트리에 등록. 엔진 코드 수정 없음.

---

## 8. 폴더 구조 (목표)

현재 card_news_generator → design_agent_system 으로 전환

```
design_agent_system/
│
├── adapters/                 ← 입력 어댑터
│   ├── __init__.py
│   ├── base.py               ← 어댑터 기본 클래스
│   ├── cli_adapter.py
│   ├── sheets_adapter.py
│   ├── slack_adapter.py
│   └── web_adapter.py
│
├── engine/                   ← 엔진 코어
│   ├── __init__.py
│   ├── pipeline.py           ← 메인 파이프라인 (조립 라인 관리자)
│   ├── request_analyzer.py   ← 요청 분석
│   ├── copy_writer.py        ← 카피 처리
│   ├── image_handler.py      ← 이미지 처리 (에셋 선택 or AI 생성)
│   ├── style_resolver.py     ← 스타일 결정
│   ├── template_mapper.py    ← 템플릿 매핑
│   └── renderer.py           ← 렌더링
│
├── image_generators/         ← 이미지 생성 플러그 (AI 도구 연결)
│   ├── __init__.py
│   ├── base.py               ← 공통 규칙 (기본 틀)
│   ├── midjourney_gen.py     ← Midjourney 연결
│   ├── gemini_gen.py         ← Gemini 연결
│   └── dalle_gen.py          ← DALL-E 연결 (나중에 추가 가능)
│
├── output_adapters/          ← 출력 플러그
│   ├── __init__.py
│   ├── base.py               ← 공통 규칙
│   ├── file_adapter.py       ← 파일 저장 (기본)
│   ├── slack_adapter.py      ← 슬랙 전송
│   ├── drive_adapter.py      ← Google Drive 업로드
│   └── figma_adapter.py      ← Figma 내보내기
│
├── schemas/                  ← 데이터 구조 정의
│   ├── __init__.py
│   ├── request.py            ← DesignRequest
│   └── result.py             ← DesignResult
│
├── brands/                   ← 브랜드 스타일 데이터
│   ├── albamon/
│   ├── jobkorea/
│   └── worxphere/
│
├── content_types/            ← 콘텐츠 유형 설정
│   ├── card_news.yaml
│   ├── banner.yaml
│   └── ...
│
├── templates/                ← HTML 템플릿
│   ├── _base/
│   ├── card_news/
│   ├── banner/
│   └── ...
│
├── output/                   ← 생성 결과물
│
├── config/                   ← 전역 설정
│   ├── default.yaml
│   └── template_registry.yaml
│
├── main.py                   ← CLI 진입점
└── requirements.txt
```

---

## 9. 확장 시나리오

### 시나리오 1: "포스터 유형 추가"
수정하는 곳:
- content_types/poster.yaml (새 파일)
- templates/poster/basic.html (새 파일)
- config/template_registry.yaml (포스터 항목 추가)

수정하지 않는 곳: 엔진 코드, 어댑터 코드, 브랜드 데이터

### 시나리오 2: "Slack 입력 연동"
수정하는 곳:
- adapters/slack_adapter.py (새 파일)

수정하지 않는 곳: 엔진 코드, 템플릿, 브랜드 데이터

### 시나리오 3: "새 브랜드 추가"
수정하는 곳:
- brands/new_brand/ 폴더 (새 폴더)

수정하지 않는 곳: 엔진 코드, 어댑터, 템플릿 (브랜드 전용 템플릿이 필요하면 추가)

### 시나리오 4: "웹사이트에서 직접 생성"
수정하는 곳:
- adapters/web_adapter.py (새 파일)

수정하지 않는 곳: 엔진 코드 전체

---

## 10. 현재 코드 → 새 구조 전환 계획

### 10-1. 바로 정리해야 할 것
- 루트의 copy_generator.py, image_renderer.py 제거 (engine/ 안의 코드와 중복)
- CardRequest → DesignRequest로 일반화
- CardNewsEngine → DesignEngine으로 일반화

### 10-2. 단계별 전환

| 단계 | 작업 | 기존 기능 영향 |
|------|------|--------------|
| 1단계 | 폴더 구조 정리 + 스키마 일반화 | 카드뉴스 생성 그대로 작동 |
| 2단계 | 브랜드 스타일을 YAML로 분리 | 카드뉴스 생성 그대로 작동 |
| 3단계 | 템플릿 시스템 구축 | 카드뉴스 템플릿 이관 |
| 4단계 | 어댑터 계층 추가 (CLI 먼저) | main.py가 어댑터 사용 |
| 5단계 | 새 콘텐츠 유형 추가 (배너 등) | 기존 + 신규 모두 작동 |
| 6단계 | Google Sheets 어댑터 | 시트에서 입력 가능 |

각 단계는 독립적이고, 한 단계를 끝낼 때마다 시스템이 정상 작동하는 상태를 유지.

---

## 11. 놓치기 쉬운 것들 — 문제점과 해결 방법

시스템을 키워나갈 때 미리 챙겨야 할 포인트입니다.
구현 우선순위: 🔴 시스템 구축 시 바로 / 🟡 기능 확장 시 / 🟢 실무 적용 후

---

### 11-1. 에러 기록 시스템 🔴

**문제**: 지금은 에러가 화면에 한 줄 뜨고 사라진다. 시스템이 커지면 뭐가 왜 실패했는지 추적 불가.

**해결**: "업무 일지" 시스템을 만든다. 시스템이 뭔가를 할 때마다 날짜, 시간, 작업 내용, 성공/실패를 자동으로 파일에 기록.

```
logs/
  2026-04-10.log    ← 날짜별 자동 기록
  
  기록 예시:
  [2026-04-10 14:30] 카드뉴스 생성 시작 | 제목: 봄맞이 세일 | 브랜드: albamon
  [2026-04-10 14:30] 카피 생성 완료 (AI 모드)
  [2026-04-10 14:31] 렌더링 완료 → output/card_봄맞이_세일.png
  [2026-04-10 14:35] 배너 생성 실패 | 원인: 템플릿 파일 없음 (banner/promo.html)
```

---

### 11-2. 설정 한 곳 관리 🔴

**문제**: API 키, 출력 경로, 폰트 설정 등이 코드 여기저기 흩어져 있다. 뭘 바꾸려면 파일 여러 개를 찾아다녀야 함.

**해결**: 설정 파일 하나에 모든 설정을 모은다. "이 파일만 열면 전체 설정을 볼 수 있다."

```
config/default.yaml:

  # API 설정
  ai:
    provider: "anthropic"
    api_key: "sk-xxx..."
    model: "claude-sonnet"

  # 이미지 생성 AI 설정
  image_ai:
    provider: "midjourney"      ← 또는 "gemini"
    api_key: "xxx..."

  # 출력 설정
  output:
    default_folder: "./output"
    default_format: "png"

  # 기본값
  defaults:
    brand: ""
    mood: "세련된"
    copy_mode: "manual"
```

---

### 11-3. 결과물 히스토리 🟢

**문제**: 같은 요청을 여러 번 돌리면 파일만 쌓인다. 어떤 조건으로 만든 건지 알 수 없음.

**해결**: 결과물을 만들 때마다 "어떤 요청 → 어떤 결과"를 함께 기록한다. 디자인 작업할 때 "v1", "v2" 붙이는 것을 시스템이 자동으로 해주는 것.

```
output/
  history.json    ← 자동 기록

  기록 예시:
  {
    "id": "req_001",
    "created": "2026-04-10 14:30",
    "request": { "title": "봄맞이 세일", "brand": "albamon", "mood": "활기찬" },
    "result": { "file": "card_봄맞이_세일_001.png", "success": true },
    "feedback": "좋아요"    ← 나중에 피드백 기록용
  }
```

이게 있어야 나중에 A/B 테스트("이 배너 vs 저 배너") 가능.

---

### 11-4. 이미지 에셋 처리 (AI 이미지 생성 연동) 🟡

**문제**: 카드뉴스는 텍스트 위주라 괜찮았지만, 배너·포스터·광고소재에는 배경 이미지, 상품 사진, 일러스트가 필수.

**해결**: 이미지 에셋을 두 가지 방식으로 처리한다.

**방식 1: 기존 에셋 사용** — 브랜드별 이미지 창고에서 가져오기
```
assets/
  albamon/
    backgrounds/    ← 배경 이미지 모음
    products/       ← 상품 사진
    illustrations/  ← 일러스트
    icons/          ← 아이콘
  jobkorea/
    ...
```

**방식 2: AI 이미지 생성** — Midjourney / Gemini 등 외부 AI로 자동 생성

이미지 생성도 입력 어댑터(변환 플러그)처럼 "이미지 생성 플러그" 방식으로 만든다.
어떤 AI 도구를 쓰든 엔진 코어는 수정하지 않는 구조.

```
image_generators/           ← 이미지 생성 플러그 모음
  base.py                   ← 공통 규칙 (기본 틀)
  midjourney_generator.py   ← Midjourney 연결 플러그
  gemini_generator.py       ← Gemini 연결 플러그
  dalle_generator.py        ← 나중에 DALL-E 추가도 가능
```

엔진 조립 라인에서의 흐름:
```
요청 분석 → 카피 처리 → 이미지 생성(NEW) → 스타일 결정 → 템플릿 매핑 → 렌더링
                          ↑
                    copy_mode처럼 image_mode로 선택:
                    - "none"      : 이미지 없이 텍스트만 (카드뉴스 등)
                    - "asset"     : 기존 이미지 창고에서 선택
                    - "generate"  : AI로 새로 생성 (Midjourney/Gemini)
```

DesignRequest에 추가되는 항목:
```
  ── 이미지 설정 ──
  image_mode      : "none" | "asset" | "generate"
  image_prompt    : "밝고 활기찬 봄 배경"  ← AI 생성 시 프롬프트
  image_generator : "midjourney" | "gemini" | "dalle"
  image_asset_id  : "bg_spring_01"  ← 기존 에셋 사용 시 ID
```

---

### 11-5. 출력 통로 분리 🟡

**문제**: 지금은 파일 저장만 가능. 실무에서는 "슬랙으로 보내줘", "드라이브에 올려줘" 같은 상황이 필요.

**해결**: 입력에 변환 플러그를 만든 것처럼, 출력에도 똑같이 만든다.

```
output_adapters/            ← 출력 플러그 모음
  base.py                   ← 공통 규칙
  file_adapter.py           ← 파일 저장 (기본)
  slack_adapter.py          ← 슬랙 채널에 전송
  drive_adapter.py          ← Google Drive 업로드
  figma_adapter.py          ← Figma로 내보내기
```

DesignRequest에 추가되는 항목:
```
  ── 출력 통로 (여러 개 동시 선택 가능) ──
  output_targets  : ["file", "slack"]
  slack_channel   : "#design-output"    ← 슬랙 전송 시
  drive_folder    : "콘텐츠/2026/04"    ← 드라이브 업로드 시
```

---

### 11-6. 품질 피드백 루프 🟢

**문제**: "시스템 자체 학습과 고도화" 목표를 위해, 결과물이 좋았는지 아쉬웠는지를 기록해야 한다.

**해결**: 결과물에 대한 평가를 기록하고, 그 데이터를 시스템 개선에 활용한다.

처음에는 간단하게 시작:
```
피드백 옵션:
  - "좋아요"      → 이 조건 조합을 기억 (다음에 비슷한 요청이 오면 참고)
  - "수정 필요"   → 어떤 부분이 아쉬웠는지 기록 (색상? 카피? 레이아웃?)
  - "다시 만들기" → 같은 조건으로 재생성
```

나중에 고도화하면:
```
  - 피드백 데이터 분석 → "알바몬 + 활기찬 조합은 만족도 90%"
  - AI 카피 생성 시 만족도 높았던 패턴 우선 적용
  - 자주 수정되는 패턴 자동 감지 → 스타일 프리셋 자동 조정
```

---

### 구현 우선순위 정리

| 우선순위 | 항목 | 언제 |
|---------|------|------|
| 🔴 1순위 | 에러 기록 + 설정 관리 | 시스템 구축하면서 바로 |
| 🟡 2순위 | 이미지 에셋(AI 생성) + 출력 통로 | 배너·포스터 유형 추가할 때 |
| 🟢 3순위 | 결과물 히스토리 + 피드백 루프 | 실무에 시스템을 돌린 후 |
