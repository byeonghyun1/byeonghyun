# Banner Maker — 설계서

> 키비주얼 이미지 + 텍스트만 넣으면, 다양한 사이즈의 배너를 자동으로 만들어주는 에이전트
> 비디자이너(기획자, 마케터)도 웹 대시보드에서 쉽게 사용 가능

---

## Part 1. 개요

### 1.1 이 시스템은 뭘 하는 건가요?

사용자가 **키비주얼 이미지 1장**(PNG/JPG)과 **텍스트**(제목, 부제목)를 주면,
시스템이 자동으로 배너를 만들어줍니다.

- 이미지 영역과 텍스트 영역을 자동으로 구분해서 배치
- 선택한 사이즈에 맞게 레이아웃 자동 조정
- 결과물은 **이미지 파일(PNG)** + **Figma 편집 가능 프레임** 두 가지로 출력

### 1.2 기존 시스템과 뭐가 다른가요?

| 구분 | Design Variation Agent (기존) | Banner Maker (신규) |
|---|---|---|
| 입력 | Figma에서 완성된 디자인 | 키비주얼 이미지 + 텍스트 |
| 사용자 | 디자이너 | 비디자이너 (기획자, 마케터) |
| 하는 일 | 완성된 배너를 다른 사이즈로 변환 | 배너를 처음부터 제작 |
| UI | 없음 (CLI/대화) | 웹 대시보드 |

### 1.3 설계 원칙

1. **높은 퀄리티, 낮은 자유도** — 사용자 선택지를 최소화하되, 결과물은 디자이너급. 변수를 줄여야 퀄리티가 일관됨.
2. **가이드 절대 준수** — 디자이너가 제공한 템플릿·폰트·색상 가이드를 철저히 따름. 에이전트의 자유도는 "가이드 범위 안의 미세 조정"으로 한정.
3. **설정과 코드의 완전 분리** — "뭘 할지"는 설정 파일(JSON)이 결정하고, "어떻게 할지"만 코드가 담당. 사이즈 추가, 폰트 변경, 템플릿 수정 시 코드를 건드리지 않음.
4. **품질 안전장치** — 배너가이드 규정을 자동 검증. 규정에 어긋나면 시스템이 알아서 수정.
5. **학습으로 진화** — 가이드로 커버 안 되는 변수는 디자이너 피드백으로 학습해서 점점 정교해짐.
6. **확장 가능** — 새 사이즈/매체/템플릿/CTA 스타일을 JSON 파일 하나 추가하면 끝.

### 1.4 전체 흐름 (한눈에 보기)

```
사용자 입력                    시스템 처리                      결과물
─────────                    ──────────                      ──────
                              ┌─────────────┐
키비주얼 이미지 ──────────────▶│ 이미지 분석  │
(PNG/JPG) 또는 배경색          │ (피사체 감지  │
                              │  투명/불투명) │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
텍스트 입력 ─────────────────▶│ 레이아웃 엔진 │──────▶ PNG 이미지
(제목, 부제)                   │ (디자이너     │──────▶ Figma 프레임
                              │  가이드 기반)  │
CTA 버튼 (선택) ────────────▶│              │
                              └──────┬──────┘
                                     │
사이즈 선택 ─────────────────▶│ 멀티사이즈    │
(메인탑, 공고스카이 등)        │ 일괄 생성     │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │ 품질 검증     │
                              │ (가이드 규정)  │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │ 대시보드 미리보기│
                              └─────────────┘
```

### 1.5 폴더 구조

```
banner_maker/
├── ARCHITECTURE.md          ← 이 설계서
│
├── engine/                  ← 핵심 엔진 (코드, 잘 안 바뀜)
│   ├── image_analyzer.py        ← 이미지 분석
│   ├── layout_engine.py         ← 레이아웃 배치
│   ├── renderer.py              ← PNG 렌더링
│   └── figma_writer.py          ← Figma 프레임 생성
│
├── guides/                  ← 가이드 문서 + 설정 데이터 (MD+JSON 쌍, SSoT)
│   ├── color_guide.md / .json    ← 컬러 가이드
│   ├── font_guide.md / .json     ← 폰트 가이드
│   ├── design_rules.md / .json   ← 공통 디자인 규정
│   └── banners/                  ← 배너별 개별 가이드 (MD+JSON 쌍)
│       ├── pc_main_curtain.md / .json
│       ├── pc_main_top.md / .json
│       ├── pc_job_sky.md / .json
│       ├── pc_login_right.md / .json
│       ├── pc_search_right.md / .json
│       ├── pc_recruit_bottom.md / .json
│       ├── pc_recruit_bottom_text.md / .json
│       ├── pc_company_left.md / .json
│       ├── m_sub_banner.md / .json
│       ├── m_app_splash.md / .json
│       └── email_target.md / .json
│
├── checks/                  ← 검증 체크 모듈 (플러그인 방식)
├── dashboard/               ← 웹 대시보드 UI
├── feedback/                ← 피드백 & 학습 데이터
│   └── learned_rules.json
├── logs/                    ← 에러 로그
└── output/                  ← 생성된 결과물
```

> **핵심 구조:** `engine/`(코드)과 `guides/`(설정+문서)이 분리.
> 사이즈 추가 → `guides/banners/`에 MD+JSON 추가. 폰트 변경 → `guides/font_guide.json` 수정. 코드는 건드리지 않음.
> MD는 사람이 읽는 문서, JSON은 엔진이 읽는 데이터. 항상 쌍으로 관리.

---

## Part 2. 입력 & 설정

### 2.1 사용자가 하는 것

기획자/마케터가 대시보드에서 하는 건 이것뿐입니다:

| 순서 | 할 일 | 설명 |
|---|---|---|
| ① | 이미지 올리기 | 키비주얼 PNG/JPG 1장 드래그 앤 드롭. 안 올리면 배경색만으로 생성 |
| ② | 텍스트 쓰기 | 제목 (필수) + 부제목 (선택) |
| ③ | CTA 버튼 | 별도 영역에서 추가 여부 선택. 넣으면 텍스트 입력 + 스타일 택1 |
| ④ | 사이즈 고르기 | 만들 배너 사이즈 체크 (복수 가능) |

**그 외 모든 건 시스템이 알아서 합니다:**
- 텍스트 위치, 정렬 → 디자이너 템플릿 기반 자동 배치
- 텍스트 색상 → 이미지/배경 밝기 분석해서 가독성 좋은 색 자동 선택
- 폰트 크기 → 디자이너 폰트 가이드 범위 내에서 자동 계산
- 이미지 크롭/배치 → AI가 피사체를 감지해서 자동 조정

### 2.2 이미지 입력 — 3가지 케이스 자동 대응

사용자가 이미지를 올리면 시스템이 자동으로 어떤 케이스인지 판단합니다:

```
이미지를 올렸다
  └─ 투명 배경 PNG인가? (알파 채널 감지)
       ├─ Yes → 케이스 B: 오브제 PNG
       │        → 배경색 입력칸 자동 노출
       │        → 오브제를 이미지 영역에 배치, 배경은 입력된 색상으로
       │
       └─ No  → 케이스 A: 풀 배경 이미지
                → 배경색 입력칸 없음
                → 이미지가 이미지 영역 전체를 덮음

이미지를 안 올렸다
  └─ 케이스 C: 배경색 + 텍스트만
     → 배경색 입력칸만 노출
     → 이미지 없이 배경색 + 텍스트 + CTA로만 구성
```

> 사용자는 별도 모드를 선택할 필요 없이, 이미지를 올렸냐 안 올렸냐에 따라 화면이 알아서 바뀝니다.

### 2.3 텍스트 입력

사용자에게 보이는 입력칸은 2개입니다:

```
① 제목        — 필수 (예: "2026 상반기 공채")
② 부제목      — 선택 (예: "지금 바로 지원하세요")
```

### 2.4 CTA 버튼 — 별도 영역

CTA는 텍스트 입력과 분리된 별도 영역으로 제공합니다.

```
┌─ CTA 버튼 추가 ──────────────────────────────┐
│                                               │
│  [  ] CTA 버튼 넣기                            │
│                                               │
│  (토글 ON 하면 아래가 나타남)                    │
│                                               │
│  버튼 텍스트: [지원하기           ]              │
│                                               │
│  스타일 선택:                                   │
│  ┌──────────┐  ┌──────────┐                   │
│  │ ■■■■■■■■ │  │  [버튼]   │                   │
│  │ 하단 바   │  │ 인라인   │                    │
│  └──────────┘  └──────────┘                   │
│                                               │
└───────────────────────────────────────────────┘
```

**CTA 스타일 2가지:**

| 스타일 | 설명 | 예시 |
|---|---|---|
| 하단 바 | 배너 최하단에 색상 띠를 쭉 깔고 텍스트 배치. 배너 전체 너비 차지. | 엽떡 배너처럼 하단에 주황색 바 + "지원하고 엽떡 받기 >" |
| 인라인 버튼 | 텍스트 아래에 둥근 버튼 형태로 배치. 버튼만 색이 들어감. | 부제목 아래에 [지원하기] 버튼 |

> CTA를 안 넣으면 이 영역을 통째로 스킵합니다.
> 나중에 CTA 스타일을 추가할 수 있도록 확장 가능하게 설계합니다.

### 2.5 매체 프리셋 — 내부배너

> 잡코리아·알바몬 통합 배너가이드 기반

**PC 배너**

| 배너명 | 사이즈 (px) | 비율 | 비고 |
|---|---|---|---|
| 메인커튼 | 2160 × 160 | 초가로형 | 얇고 넓은 띠 배너 |
| 메인탑 | 1556 × 232 | 가로형 | 메인 상단 |
| 공고스카이 | 560 × 700 | 세로형 | 채용공고 옆 |
| 채용하단 | 495 × 110 | 가로형 | 채용 페이지 하단 |
| 로그인우측 | 325 × 310 | 정사각 유사 | 로그인 옆 |
| 검색우측 | 320 × 155 | 가로형 | 검색결과 옆 |
| 기업좌측 | 200 × 275 | 세로형 | 기업 페이지 좌측 |

**모바일 배너**

| 배너명 | 사이즈 (px) | 비율 | 비고 |
|---|---|---|---|
| 앱스플래시 | 1440 × 976 | 가로형 | 앱 시작 화면 |
| M서브 | 1029 × 258 | 가로형 | 모바일 서브 페이지 |

**이메일**

| 배너명 | 사이즈 (px) | 비율 | 비고 |
|---|---|---|---|
| 타겟메일 | 700 × 1500 이내 | 세로형 | HTML 이메일 |

### 2.6 공통 디자인 규정

배너가이드에서 가져온 필수 규정입니다. 모든 배너에 자동 적용됩니다.

| 항목 | 규정 |
|---|---|
| 서체 | 고딕 계열만 사용 |
| PC 최소 폰트 | 12px 이상 |
| 모바일 최소 폰트 | 22px 이상 |
| 행간 (한 줄) | 100% |
| 행간 (두 줄 이상) | 120% |
| 텍스트 컬러 | 최대 2가지 |
| 출처 표기 | 우상단, 8px |
| 배경 | 단색 권장 |
| 모바일 가변 영역 | 좌우 10px 단색 |
| 파일명 | 제작일_가로_세로_컬러값 |

### 2.7 디자이너 가이드 (추후 입력)

디자이너가 별도로 제공하는 가이드입니다. 에이전트는 이 범위 안에서만 판단합니다.

**폰트 가이드** (guides/font_guide.json)
- 사용 가능한 폰트 목록
- 사이즈별 최소/최대 크기
- 굵기 규칙
- → 디자이너가 가이드 제공 시 반영 예정

**템플릿** (guides/templates/ (추후))
- 이미지 영역과 텍스트 영역의 배치 정의
- → 디자이너가 템플릿 제공 시 반영 예정

> 에이전트의 역할: 가이드를 철저히 따르되, 가이드가 커버하지 못하는 변수(이미지마다 다른 여백, 텍스트 길이 차이 등)만 자체 판단. 자체 판단한 결과는 피드백을 통해 학습.

---

## Part 3. 설정과 코드의 분리 (확장성 핵심)

이 시스템에서 가장 중요한 구조적 원칙입니다.
**"자주 바뀌는 것"과 "안 바뀌는 것"을 완전히 분리**해서, 설정을 아무리 바꿔도 코드가 꼬이지 않게 합니다.

### 3.1 바뀌는 것 vs 안 바뀌는 것

| 구분 | 위치 | 바뀌는 빈도 | 수정 방법 |
|---|---|---|---|
| **바뀌는 것 (설정)** | | | |
| 배너 사이즈 | guides/banners/ | 수시로 | JSON 수정 |
| 폰트 가이드 | guides/font_guide.json | 자주 | JSON 수정 |
| 색상 가이드 | guides/color_guide.json | 가끔 | JSON 수정 |
| 레이아웃 템플릿 | guides/templates/ (추후) | 가끔 | JSON 추가/수정 |
| CTA 스타일 | guides/cta_styles/ (추후) | 가끔 | JSON 추가 |
| 디자인 규정 | guides/design_rules.json | 드물게 | JSON 수정 |
| 학습 규칙 | feedback/learned_rules.json | 계속 | 자동 |
| **안 바뀌는 것 (코드)** | | | |
| 이미지 분석 로직 | engine/image_analyzer.py | 거의 안 바뀜 | 코드 수정 |
| 레이아웃 엔진 | engine/layout_engine.py | 거의 안 바뀜 | 코드 수정 |
| 렌더러 | engine/renderer.py | 거의 안 바뀜 | 코드 수정 |
| Figma 생성기 | engine/figma_writer.py | 거의 안 바뀜 | 코드 수정 |
| 검증 파이프라인 구조 | checks/ | 거의 안 바뀜 | 코드 수정 |
| 에러 처리 체계 | engine/ | 안 바뀜 | 코드 수정 |

### 3.2 설정 파일(JSON) 구조 예시

#### 프리셋 — guides/banners/internal.json

```json
{
    "category": "내부배너",
    "sizes": [
        {
            "id": "main_curtain",
            "name": "메인커튼",
            "width": 2160,
            "height": 160,
            "platform": "pc",
            "ratio_type": "ultra_wide",
            "safe_zone": {"top": 10, "bottom": 10, "left": 20, "right": 20},
            "default_template": "overlay",
            "notes": "얇고 넓은 띠 배너"
        },
        {
            "id": "main_top",
            "name": "메인탑",
            "width": 1556,
            "height": 232,
            "platform": "pc",
            "ratio_type": "wide",
            "safe_zone": {"top": 16, "bottom": 16, "left": 24, "right": 24},
            "default_template": null,
            "notes": "메인 상단"
        }
    ]
}
```

> **사이즈 추가:** 이 JSON에 객체 하나만 추가하면 끝. 코드 수정 없음.
> **사이즈 삭제:** 해당 객체를 지우면 끝.
> **사이즈 변경:** width/height 숫자만 바꾸면 끝.

#### 폰트 가이드 — guides/font_guide.json

```json
{
    "allowed_fonts": ["Pretendard", "Noto Sans KR"],
    "default_font": "Pretendard",
    "size_rules": {
        "headline": {
            "pc": {"min": 20, "max": 48, "default_weight": "bold"},
            "mobile": {"min": 28, "max": 64, "default_weight": "bold"}
        },
        "subhead": {
            "pc": {"min": 14, "max": 28, "default_weight": "regular"},
            "mobile": {"min": 22, "max": 36, "default_weight": "regular"}
        },
        "cta": {
            "pc": {"min": 12, "max": 24, "default_weight": "bold"},
            "mobile": {"min": 22, "max": 32, "default_weight": "bold"}
        }
    }
}
```

> **폰트 바꾸기:** allowed_fonts, default_font만 수정.
> **사이즈 범위 바꾸기:** min/max 숫자만 수정.
> 엔진은 이 파일을 읽어서 범위 안에서 자동 계산. 코드 수정 없음.

#### CTA 스타일 — guides/cta_styles/ (추후)bottom_bar.json

```json
{
    "id": "bottom_bar",
    "name": "하단 바",
    "description": "배너 최하단에 색상 띠를 쭉 깔고 텍스트 배치",
    "layout": {
        "position": "bottom",
        "width_ratio": 1.0,
        "height_ratio": 0.18,
        "min_height": 36,
        "max_height": 64
    },
    "style": {
        "bg_color_source": "dominant_color",
        "text_color": "auto",
        "text_align": "center",
        "padding": {"left": 20, "right": 20},
        "border_radius": 0
    }
}
```

> **새 CTA 스타일 추가:** guides/cta_styles/ (추후)에 JSON 파일 하나 추가.
> 엔진이 자동으로 인식해서 대시보드 선택지에 추가됨. 코드 수정 없음.

#### 디자인 규정 — guides/design_rules.json

```json
{
    "font_family": "gothic_only",
    "min_font_size": {
        "pc": 12,
        "mobile": 22
    },
    "line_height": {
        "single_line": 1.0,
        "multi_line": 1.2
    },
    "max_text_colors": 2,
    "source_label": {
        "position": "top_right",
        "font_size": 8
    },
    "background": "solid_recommended",
    "mobile_flexible_zone": {
        "left": 10,
        "right": 10,
        "fill": "solid_color"
    },
    "file_naming": "{date}_{width}x{height}_{color}"
}
```

> **규정 변경:** 숫자만 수정. 검증 모듈이 이 파일을 직접 참조하므로 자동 반영.

### 3.3 엔진이 설정을 읽는 방식

```python
# 엔진 코드는 설정 파일의 "구조"만 알면 됨.
# 설정 파일의 "값"은 몰라도 됨.

class LayoutEngine:
    def __init__(self, config_path="guides/"):
        # 시작할 때 설정 파일을 전부 로드
        self.presets = load_all_json(config_path + "presets/")
        self.templates = load_all_json(config_path + "templates/")
        self.cta_styles = load_all_json(config_path + "cta_styles/")
        self.font_guide = load_json(config_path + "font_guide.json")
        self.design_rules = load_json(config_path + "design_rules.json")
    
    def generate(self, user_input):
        # 사이즈 프리셋 찾기 — JSON에서 가져옴
        preset = self.find_preset(user_input["target_size"])
        
        # 폰트 계산 — font_guide.json 범위 안에서
        font_size = self.calc_font(preset, self.font_guide)
        
        # 검증 — design_rules.json을 직접 참조
        self.validate(layout_plan, self.design_rules)
```

> **핵심:** 엔진 코드에 "메인탑은 1556×232", "최소 폰트는 12px" 같은 숫자가 없음.
> 모든 숫자는 JSON에서 읽어옴. JSON이 바뀌면 엔진이 바뀐 값을 자동으로 사용.

### 3.4 검증 모듈이 가이드를 참조하는 방식

검증 모듈(checks/)도 설정 파일을 직접 참조합니다.
폰트 가이드를 바꿔도 검증이 자동으로 새 기준을 사용합니다.

```python
# checks/font_guide_range.py

class FontGuideRangeCheck:
    phase = "post_layout"
    
    def run(self, layout_plan, config):
        # ※ 하드코딩된 숫자가 없음!
        # config에서 font_guide.json을 읽어서 사용
        font_guide = config["font_guide"]
        platform = config["preset"]["platform"]
        
        for text in layout_plan["text_placements"]:
            slot = text["slot"]  # "headline", "subhead", "cta"
            rules = font_guide["size_rules"][slot][platform]
            
            if text["font_size"] < rules["min"]:
                return {
                    "result": "fail",
                    "message": f"{slot} 폰트({text['font_size']}px)가 "
                               f"가이드 최소({rules['min']}px)보다 작습니다",
                    "auto_fix": {"font_size": rules["min"]}
                }
            if text["font_size"] > rules["max"]:
                return {
                    "result": "fail",
                    "message": f"{slot} 폰트({text['font_size']}px)가 "
                               f"가이드 최대({rules['max']}px)보다 큽니다",
                    "auto_fix": {"font_size": rules["max"]}
                }
        
        return {"result": "pass"}
```

> **폰트 가이드가 바뀌면?** font_guide.json만 수정하면 검증도 자동으로 새 기준 적용.
> **규정이 바뀌면?** design_rules.json만 수정하면 관련 검증 전부 자동 반영.

### 3.5 새 기능 추가 시나리오

이 구조에서 실제로 기능을 추가할 때 뭘 건드리는지 정리합니다:

| 시나리오 | 하는 일 | 코드 수정 |
|---|---|---|
| 새 배너 사이즈 추가 | guides/banners/ JSON에 객체 추가 | 없음 |
| 폰트 종류 변경 | guides/font_guide.json 수정 | 없음 |
| 폰트 사이즈 범위 변경 | guides/font_guide.json min/max 수정 | 없음 |
| 새 CTA 스타일 추가 | guides/cta_styles/ (추후)에 JSON 추가 | 없음 |
| 디자인 규정 숫자 변경 | guides/design_rules.json 수정 | 없음 |
| 새 템플릿 추가 | guides/templates/ (추후)에 JSON 추가 | 없음 |
| 새 검증 규칙 추가 | checks/에 Python 파일 추가 (플러그인) | 최소한 |
| 새 이미지 분석 방법 | engine/image_analyzer.py 수정 | 엔진 수정 |

> 위 6줄이 "코드 수정 없음"인 게 핵심입니다.
> 디자이너가 가이드를 아무리 바꿔도, JSON만 수정하면 되고 코드는 안전합니다.

---

## Part 4. 파이프라인 (데이터가 흐르는 순서)

### 4.1 전체 데이터 흐름

```
[1] UserInput ──▶ [2] ImageAnalysis ──▶ [3] LayoutPlan ──▶ [4] RenderResult ──▶ [5] Output
    사용자 입력      이미지 분석 결과       배치 계획          렌더링 결과           최종 파일
```

각 단계에서 다음 단계로 넘어가는 데이터의 형태가 정해져 있습니다.
이렇게 하면 각 모듈을 독립적으로 수정하거나 교체할 수 있어요.

### 4.2 단계별 데이터 구조

#### [1] UserInput — 사용자가 입력한 것

```python
UserInput = {
    "image": {
        "file_path": "uploads/key_visual.png",   # 없으면 null (케이스 C)
        "format": "png",
        "original_size": [1200, 800]
    },
    "bg_color": "#FF6B00",                       # 투명 PNG 또는 이미지 없을 때만
    "texts": {
        "headline": "2026 상반기 공채",           # 필수
        "subhead": "지금 지원하세요"              # 선택
    },
    "cta": {                                     # null이면 CTA 없음
        "text": "지원하기",
        "style": "bottom_bar"                    # "bottom_bar" 또는 "inline_button"
    },
    "target_sizes": ["메인탑", "공고스카이", "로그인우측"]
}
```

#### [2] ImageAnalysis — 이미지를 분석한 결과

```python
ImageAnalysis = {
    "source_image": "uploads/key_visual.png",
    "dimensions": [1200, 800],
    "image_type": "full_bg",                     # "full_bg" / "transparent_obj" / "none"
    "subject_area": {                            # 피사체(주요 대상)가 있는 영역
        "x": 300, "y": 100,
        "width": 600, "height": 500
    },
    "empty_zones": [                             # 텍스트를 놓을 수 있는 여백 영역
        {"position": "left", "x": 0, "y": 0, "width": 280, "height": 800},
        {"position": "top", "x": 0, "y": 0, "width": 1200, "height": 90}
    ],
    "dominant_colors": ["#1A2B3C", "#F5F5F5"],
    "brightness_map": {
        "left": "dark",
        "right": "light",
        "top": "light",
        "bottom": "dark"
    }
}
```

#### [3] LayoutPlan — 어디에 뭘 배치할지 계획

```python
LayoutPlan = {
    "target_size": "메인탑",
    "canvas": {"width": 1556, "height": 232},
    "template_used": "left_align",
    "background": {
        "type": "image",                         # "image" / "color"
        "color": null                            # 케이스 B/C일 때 색상값
    },
    "image_placement": {                         # 케이스 C면 null
        "x": 778, "y": 0,
        "width": 778, "height": 232,
        "crop": {                                # 피사체 중심 자동 크롭
            "x": 200, "y": 150,
            "width": 800, "height": 400
        },
        "fit_mode": "cover"
    },
    "text_placements": [
        {
            "slot": "headline",
            "text": "2026 상반기 공채",
            "x": 40, "y": 60,
            "width": 700, "height": 80,
            "font_size": 36,
            "font_weight": "bold",
            "color": "#222222",
            "line_height": 1.0
        },
        {
            "slot": "subhead",
            "text": "지금 지원하세요",
            "x": 40, "y": 140,
            "width": 700, "height": 40,
            "font_size": 20,
            "font_weight": "regular",
            "color": "#666666",
            "line_height": 1.2
        }
    ],
    "cta": {                                     # null이면 CTA 없음
        "style": "bottom_bar",
        "text": "지원하기",
        "bar_height": 48,
        "bar_color": "#FF6B00",
        "text_color": "#FFFFFF",
        "font_size": 16
    },
    "validation_passed": true
}
```

#### [4] RenderResult — 렌더링 결과

```python
RenderResult = {
    "layout_plan": { ... },
    "outputs": {
        "png": "output/메인탑_20260424_1556x232.png",
        "figma_node_id": "123:456"
    },
    "validation": {
        "passed": true,
        "checks": [
            {"name": "min_font_size", "result": "pass"},
            {"name": "text_overflow", "result": "pass"},
            {"name": "safe_zone", "result": "pass"}
        ]
    },
    "metadata": {
        "generated_at": "2026-04-24T14:30:00",
        "generation_time_ms": 1200
    }
}
```

### 4.3 모듈 간 의존성 규칙

```
image_analyzer  ──읽기──▶  키비주얼 이미지 (사용자 업로드)
layout_engine   ──읽기──▶  ImageAnalysis + UserInput + 템플릿 + 프리셋 + 디자이너 가이드
renderer        ──읽기──▶  LayoutPlan + 키비주얼 이미지
figma_writer    ──읽기──▶  LayoutPlan + 키비주얼 이미지

※ 핵심 규칙: 이미지 파일 직접 접근은 image_analyzer, renderer, figma_writer만 가능
※ layout_engine은 이미지 파일을 직접 열지 않고, ImageAnalysis 결과만 사용
※ layout_engine은 반드시 디자이너 가이드(폰트, 템플릿)를 참조해서 판단
```

---

## Part 5. 엔진 모듈 상세

### 5.1 이미지 분석기 (image_analyzer.py)

키비주얼 이미지를 받아서 "어떤 이미지인지, 어디에 텍스트를 놓을 수 있는지" 분석합니다.

**하는 일:**

1. **이미지 타입 감지** — 투명 배경 PNG(오브제)인지, 풀 배경 이미지인지 자동 판별 (알파 채널 감지)
2. **피사체 영역 감지** — 이미지에서 주요 대상이 어디 있는지 찾기 (AI)
3. **여백 영역 감지** — 텍스트를 놓아도 괜찮은 빈 공간 찾기 (AI)
4. **색상 분석** — 주요 색상 추출 (텍스트 색 자동 결정에 사용)
5. **밝기 분석** — 영역별 밝기 파악 (밝은 곳엔 어두운 텍스트, 어두운 곳엔 밝은 텍스트)

**피사체 자동 크롭:**

다른 사이즈로 배너를 만들 때, 이미지를 잘라야 하는 경우가 생깁니다.
이때 피사체가 잘리면 안 되므로, 피사체 영역을 중심으로 크롭합니다.

```
원본 이미지 (1200×800)              메인탑용 크롭 (가로형)
┌──────────────────────┐           ┌──────────────────────┐
│                      │           │   ┌──────────────┐   │
│    ┌──────────┐      │    →      │   │  피사체 영역  │   │
│    │ 피사체   │      │           │   │  (항상 포함)  │   │
│    │          │      │           │   └──────────────┘   │
│    └──────────┘      │           └──────────────────────┘
│                      │           피사체 중심으로 좌우를 넓게 잡음
└──────────────────────┘
```

> 현재는 AI 자동 감지로 진행. 감지가 부정확한 케이스가 누적되면,
> 향후 사용자가 이미지 영역을 직접 조정할 수 있는 기능 추가 가능 (참고 사항).

**사용 기술:**
- Python Pillow — 이미지 처리, 알파 채널 감지
- Claude Vision API — 피사체 위치 및 여백 판단 (AI)

### 5.2 레이아웃 엔진 (layout_engine.py)

이미지 분석 결과 + 텍스트 + 사이즈 정보를 받아서, 최종 배치를 결정합니다.
**디자이너가 제공한 가이드(템플릿, 폰트)를 최우선으로 따릅니다.**

**작동 순서:**

```
1. 사이즈별 프리셋 로드 (캔버스 크기, 세이프존)
     ↓
2. 텍스트 슬롯 확인 (제목만? 부제목도? CTA도?)
     ↓
3. 디자이너 템플릿 적용
   - 디자이너가 제공한 템플릿에 따라 이미지/텍스트 영역 배치
   - 에이전트가 임의로 바꾸지 않음
     ↓
4. AI 미세 조정 (가이드 범위 안에서만)
   - 피사체를 가리지 않도록 텍스트 위치 미세 보정
   - 이미지 밝기 기반으로 텍스트 색상 자동 결정
   - 텍스트 길이에 따른 폰트 사이즈 미세 조정
     ↓
5. 폰트 사이즈 계산
   - 디자이너 폰트 가이드의 최소/최대 범위 안에서 계산
   - 배너가이드 최소 폰트(PC 12px, Mobile 22px) 보장
     ↓
6. CTA 배치 (있을 경우)
   - 하단 바: 캔버스 최하단에 색상 띠 + 텍스트
   - 인라인 버튼: 텍스트 아래에 버튼 형태 배치
     ↓
7. 검증 통과 확인
```

### 5.3 템플릿 시스템

템플릿은 **디자이너가 제공하는 "이미지와 텍스트를 어디에 놓을지"의 규칙**입니다.
에이전트는 이 규칙을 따르고, 가이드에 없는 디테일만 자체 조정합니다.

**기본 템플릿 4종 (디자이너 가이드로 교체/추가 가능):**

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ TEXT   │  IMAGE  │  │  IMAGE  │  TEXT  │  │      IMAGE      │  │     IMAGE       │
│        │         │  │         │        │  │─────────────────│  │  ┌───────────┐  │
│ title  │         │  │         │ title  │  │      TEXT        │  │  │   TEXT    │  │
│ sub    │         │  │         │ sub    │  │   title / sub    │  │  │ title/sub │  │
│ cta    │         │  │         │ cta    │  │      cta         │  │  │   cta     │  │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
   left_align            right_align           top_image            overlay
```

**템플릿 자동 선택 로직:**

```
시스템이 이미지 분석 결과(empty_zones)와 캔버스 비율을 조합해서 자동 판단:

  이미지 여백 기준:
  - 왼쪽 여백이 넓으면 → left_align
  - 오른쪽 여백이 넓으면 → right_align
  - 위/아래 여백이 넓으면 → top_image
  - 여백이 없으면 → overlay (반투명 배경 위에 텍스트)

  캔버스 비율 보정:
  - 초가로형(4:1 이상) → overlay 강제 (텍스트 놓을 공간이 좁음)
  - 세로형(1:2 이상) → top_image 우선

  ※ 사용자는 선택하지 않음. 모든 판단은 시스템이 자동으로 수행.
  ※ 디자이너가 특정 사이즈에 특정 템플릿을 지정하면 그것을 우선 사용.
```

### 5.4 렌더러 (renderer.py)

LayoutPlan을 받아서 실제 PNG 이미지를 만듭니다.

**하는 일:**

1. 캔버스 생성 (배경: 이미지 또는 단색)
2. 키비주얼 이미지를 피사체 중심으로 crop/resize해서 배치 (있을 경우)
3. 텍스트를 디자이너 가이드에 맞는 폰트/크기/색상으로 렌더링
4. CTA 버튼 렌더링 (있을 경우: 하단 바 또는 인라인 버튼)
5. 출처 표기가 있으면 우상단 8px로 배치
6. PNG로 저장

**사용 기술:** Python Pillow, 디자이너 지정 폰트

### 5.5 Figma 생성기 (figma_writer.py)

LayoutPlan을 받아서 Figma에 편집 가능한 프레임을 만듭니다.

**하는 일:**

1. Figma에 지정된 크기의 프레임 생성
2. 배경 처리 (이미지 또는 단색)
3. 키비주얼 이미지를 이미지 노드로 삽입 (있을 경우)
4. 텍스트를 텍스트 노드로 삽입 (편집 가능)
5. CTA 컴포넌트 삽입 (있을 경우)
6. 레이어 구조 정리

**접근:** Figma MCP (읽기/쓰기) 사용

---

## Part 6. 멀티사이즈 처리

### 6.1 한 번에 여러 사이즈 만들기

사용자가 여러 사이즈를 선택하면, 각 사이즈별로 독립적으로 레이아웃을 계산합니다.
단순 축소/확대가 아니라, 각 사이즈의 비율에 맞게 레이아웃을 새로 잡습니다.

**처리 흐름:**

```
UserInput (사이즈 3개 선택)
    │
    ├──▶ 메인탑 (1556×232) ──▶ LayoutPlan ──▶ 렌더링 ──▶ PNG + Figma
    │     가로형, 피사체 중심 가로 크롭
    │
    ├──▶ 공고스카이 (560×700) ──▶ LayoutPlan ──▶ 렌더링 ──▶ PNG + Figma
    │     세로형, 피사체 중심 세로 크롭
    │
    └──▶ 로그인우측 (325×310) ──▶ LayoutPlan ──▶ 렌더링 ──▶ PNG + Figma
          정사각, 피사체 중심 정사각 크롭
```

### 6.2 사이즈별 적응 규칙

| 비율 타입 | 설명 | 적합한 템플릿 |
|---|---|---|
| 초가로형 (4:1 이상) | 메인커튼 등 | overlay (텍스트와 이미지 겹침) |
| 가로형 (2:1~4:1) | 메인탑, M서브 등 | left_align, right_align |
| 정사각 유사 (1:1 근처) | 로그인우측 등 | overlay |
| 세로형 (1:2 이상) | 공고스카이, 기업좌측 등 | top_image |

### 6.3 폰트 사이즈 스케일링

디자이너 폰트 가이드의 최소/최대 범위 안에서, 캔버스 크기에 따라 자동 조정합니다.

```
기준: 캔버스 면적의 제곱근을 기반으로 비례 계산

headline_size = clamp(기준값 × 스케일팩터, 가이드_최소, 가이드_최대)
subhead_size  = headline_size × 0.6
cta_size      = headline_size × 0.5

절대 최소폰트 (가이드보다 우선):
  - PC 배너: 12px
  - 모바일 배너: 22px
```

---

## Part 7. 품질 관리

### 7.1 검증 파이프라인 (플러그인 방식)

각 체크 항목을 독립 모듈로 만들어서, 새 규칙을 쉽게 추가할 수 있습니다.

**검증 시점:**

```
[레이아웃 계산 후] ──▶ post_layout 검증 ──▶ [렌더링 후] ──▶ post_render 검증
```

**기본 체크 목록:**

| 체크 이름 | 시점 | 검증 내용 |
|---|---|---|
| min_font_size | post_layout | 최소 폰트 사이즈 (PC 12px, Mobile 22px) |
| font_guide_range | post_layout | 디자이너 가이드 최소/최대 범위 내인지 |
| text_overflow | post_layout | 텍스트가 영역 밖으로 넘치지 않는지 |
| safe_zone | post_layout | 세이프존 침범 여부 |
| text_color_count | post_layout | 텍스트 컬러 2가지 이내 |
| line_height | post_layout | 행간 규정 (한줄 100%, 두줄 120%) |
| subject_overlap | post_layout | 텍스트가 피사체를 가리지 않는지 |
| cta_visibility | post_layout | CTA 버튼이 충분히 보이는지 |
| file_naming | post_render | 파일명 규정 (제작일_가로_세로_컬러값) |

**체크 모듈 구조:**

```python
# checks/min_font_size.py

class MinFontSizeCheck:
    phase = "post_layout"
    
    def run(self, layout_plan, preset):
        platform = preset["platform"]  # "pc" 또는 "mobile"
        min_size = 12 if platform == "pc" else 22
        
        for text in layout_plan["text_placements"]:
            if text["font_size"] < min_size:
                return {
                    "result": "fail",
                    "message": f"{text['slot']} 폰트({text['font_size']}px)가 "
                               f"최소({min_size}px)보다 작습니다",
                    "auto_fix": {"font_size": min_size}
                }
        
        return {"result": "pass"}
```

### 7.2 자동 수정 (Auto-Fix)

검증에서 실패하면, 가능한 경우 자동으로 수정합니다.
사용자는 이 과정을 모르고, 항상 규정에 맞는 결과만 받습니다.

```
검증 실패 → auto_fix 있음? 
  → Yes → 자동 수정 후 재검증
  → No → WARNING/FATAL로 분류 후 대시보드에 표시
```

### 7.3 에러 처리 (3단계)

| 레벨 | 의미 | 처리 |
|---|---|---|
| FATAL | 진행 불가 | 즉시 중단, 에러 메시지 표시 |
| RECOVERABLE | 자동 수정 가능 | auto_fix 적용 후 계속 |
| WARNING | 주의 필요 | 경고 표시, 진행은 계속 |

**기본 원칙:** 정의되지 않은 에러는 FATAL로 처리 (안전 우선)

---

## Part 8. 대시보드 (웹 UI)

### 8.1 화면 구성

기획자가 쓰는 화면이므로 최대한 단순하게 설계합니다.

```
┌──────────────────────────────────────────────────────────────┐
│  Banner Maker                                                 │
├───────────────────────┬──────────────────────────────────────┤
│                       │                                      │
│  ① 이미지             │         미리보기 영역                  │
│  ┌─────────────────┐  │                                      │
│  │  이미지를 여기에  │  │    ┌──────────────────────┐          │
│  │  끌어다 놓으세요  │  │    │                      │          │
│  └─────────────────┘  │    │   실시간 미리보기      │          │
│  배경색: [#______]     │    │                      │          │
│  (이미지 없거나        │    │                      │          │
│   투명 PNG일 때만 노출) │    └──────────────────────┘          │
│                       │                                      │
│  ② 텍스트             │    ◀ 메인탑 | 공고스카이 | ... ▶      │
│  제목: [            ]  │    (선택한 사이즈별 미리보기 전환)      │
│  부제: [            ]  │                                      │
│                       │                                      │
│  ③ CTA 버튼           │                                      │
│  [  ] CTA 버튼 넣기    │                                      │
│  (토글 시 텍스트 입력   │                                      │
│   + 스타일 2가지 선택)  │                                      │
│                       │                                      │
│  ④ 사이즈 선택         │                                      │
│  ☑ 메인탑             │                                      │
│  ☑ 공고스카이          │                                      │
│  ☐ 로그인우측          │                                      │
│                       │                                      │
│  [배너 생성하기]       │  [PNG 다운로드]  [Figma로 보내기]     │
└───────────────────────┴──────────────────────────────────────┘
```

### 8.2 대시보드 기능

| 기능 | 설명 |
|---|---|
| 이미지 업로드 | 드래그 앤 드롭. 투명 PNG 감지 시 배경색 입력칸 자동 노출 |
| 배경색 입력 | 이미지가 없거나 투명 PNG일 때만 나타남 |
| 텍스트 입력 | 제목(필수) + 부제목(선택) |
| CTA 영역 | 토글로 on/off. on이면 텍스트 입력 + 스타일 선택(하단 바/인라인 버튼) |
| 사이즈 선택 | 체크박스로 복수 선택 |
| 실시간 미리보기 | 입력하면 바로 미리보기 업데이트 |
| 사이즈 탭 전환 | 선택한 사이즈별로 미리보기 전환 |
| PNG 다운로드 | 생성된 이미지 파일 일괄 다운로드 |
| Figma 전송 | Figma에 프레임 생성 |

### 8.3 프로토타입 전용 기능 (디자이너 테스트 모드)

프로토타입 기간에만 활성화되는 기능입니다.
디자이너들이 테스트하면서 피드백을 남기고, 시스템을 학습시키는 용도입니다.

```
┌─ 디자이너 피드백 (프로토타입 전용) ───────────────────────────┐
│                                                              │
│  이 배너 결과물에 대한 피드백:                                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │  (자유 입력)                                          │    │
│  │  예: "공고스카이에서 제목이 너무 작다"                    │    │
│  │  예: "이 이미지는 크롭이 어색하다, 좀 더 위로"            │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│  [피드백 제출]                                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**배포 시:** 이 피드백 영역을 비활성화합니다. 기획자에게는 보이지 않습니다.
설정 파일에서 `prototype_mode: true/false`로 토글합니다.

### 8.4 기술 스택 (대시보드)

- **프론트엔드:** React + Tailwind CSS
- **백엔드:** Python FastAPI
- **통신:** REST API
- **미리보기:** SVG 실시간 렌더링 (빠른 피드백용)

---

## Part 9. 학습 & 확장

### 9.1 피드백 학습 시스템

**프로토타입 단계**에서 디자이너들이 남긴 피드백을 규칙화해서 시스템에 반영합니다.

```
디자이너 피드백 (프로토타입 대시보드)
    │
    ▼
피드백 수집 → 규칙화 → learned_rules.json 저장
    │
    ▼
다음 생성 시 학습된 규칙 자동 적용
```

**학습 흐름 예시:**

```
피드백: "공고스카이(560×700)에서 제목 폰트가 너무 작다"
    ↓
규칙화: 세로형 배너(1:2 이상)에서 headline_size 스케일팩터를 1.2로 상향
    ↓
learned_rules.json에 저장
    ↓
다음에 세로형 배너 생성 시 자동 적용
```

**학습 범위 — 가이드가 커버 못 하는 변수들:**
- 이미지별 여백 차이에 따른 텍스트 위치 미세 조정
- 텍스트 길이에 따른 폰트 사이즈 보정
- 특정 사이즈에서의 크롭 방향 선호도
- 사이즈별 템플릿 적합도 보정

### 9.2 규칙 우선순위

학습된 규칙이 기존 규정과 충돌할 수 있습니다.

**우선순위 (높은 순):**

1. 배너가이드 규정 (최소 폰트, 행간 등) — 절대 불변
2. 디자이너 가이드 (폰트 종류, 사이즈 범위, 템플릿) — 절대 불변
3. 매체별 프리셋 규정 (사이즈, 세이프존)
4. 학습된 규칙 (디자이너 피드백)
5. AI 판단

→ 학습된 규칙이 디자이너 가이드와 충돌하면, 디자이너 가이드가 우선합니다.
→ AI의 자유 판단은 항상 최하위. 가이드와 학습 규칙으로 해결 안 될 때만 작동.

### 9.3 확장 계획

| 단계 | 내용 | 시기 |
|---|---|---|
| Phase 1 | 내부배너 + 웹 대시보드 MVP + 디자이너 테스트 | 현재 |
| Phase 2 | 디자이너 피드백 기반 학습 완료 → 기획자 배포 | 테스트 안정화 후 |
| Phase 3 | 외부배너 프리셋 추가 | 외부 가이드 확보 후 |
| Phase 4 | CTA 스타일 추가, 템플릿 추가 | 필요 시 |
| Phase 5 | 브랜드별 프리셋 (잡코리아 vs 알바몬 톤 분리) | 필요 시 |
| Phase 6 | 배치 생성 (엑셀 데이터로 대량 배너 자동 생성) | 고도화 |

### 9.4 기존 프로젝트와의 관계

```
콘텐츠 자동화/
├── banner_maker/              ← 이 프로젝트 (신규)
│   배너를 처음부터 만드는 제작 도구
│
├── design_variation_agent/    ← 기존 프로젝트 (보관)
│   완성된 디자인을 사이즈 변환하는 도구
│
└── card_news_generator/       ← 이전 프로젝트 (보관)
    카드뉴스/배너/포스터 자동 생성 프로토타입
```

---

## 부록. 기존 시스템에서 가져온 것

| 모듈 | 출처 | 변경 사항 |
|---|---|---|
| 매체 프리셋 | design_variation_agent | 내부/외부 분류 그대로 사용 |
| 검증 파이프라인 | design_variation_agent | post_layout + post_render 2시점, font_guide_range/cta_visibility 체크 추가 |
| 에러 처리 3단계 | design_variation_agent | 그대로 사용 |
| 피드백 학습 | design_variation_agent | 프로토타입 모드 토글 추가 (디자이너 전용 → 배포 시 비활성화) |
| 공통 디자인 규정 | 배너가이드 PDF | 그대로 사용 |
