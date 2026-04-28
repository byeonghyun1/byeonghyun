# config/ — 데이터 SSoT

이 폴더는 배너 메이커가 사용하는 **모든 설정의 단일 진실 소스(SSoT)** 입니다.
엔진 코드(`engine/`)는 이 폴더의 JSON만 읽습니다. `guides/*.md`는 사람용 보조 문서이며, 어긋날 경우 이 폴더가 우선합니다.

---

## 파일 구조

| 파일 / 폴더 | 용도 | 수정 빈도 |
|---|---|---|
| `banners/{id}.json` | 배너 1개당 1파일. 사이즈·여백·폰트·카피규칙·few-shot 사례·빌더 매핑 등 모든 스펙 | 자주 |
| `font_guide.json` | 전역 폰트 가이드 (사이즈 범위, 자간 규칙) | 가끔 |
| `color_guide.json` | 전역 색상 가이드 (배경색 규칙, 금지 컬러) | 가끔 |
| `design_rules.json` | 전 배너 공통 디자인 규정 | 드물게 |
| `templates/` | 레이아웃 템플릿 (left_align, right_align 등) | 드물게 |
| `cta_styles/` | CTA 버튼 스타일 정의 | 드물게 |

---

## 변경 가이드

| 하고 싶은 일 | 수정할 파일 | 코드 수정 필요? |
|---|---|---|
| 새 배너 추가 | `banners/{id}.json` 신규 작성 | ❌ |
| 기존 배너 폰트·여백·규칙 변경 | `banners/{id}.json` 수정 | ❌ |
| 폰트 종류·사이즈 범위 전역 변경 | `font_guide.json` | ❌ |
| 색상 규칙 전역 변경 | `color_guide.json` | ❌ |
| 디자인 규정 숫자 변경 | `design_rules.json` | ❌ |

---

## 배너 JSON 스키마 (banners/{id}.json)

각 배너 파일은 다음 키를 가질 수 있습니다 (배너 성격에 따라 일부 생략 가능):

- `id`, `name`, `last_updated`, `location` — 식별/메타
- `dimensions`, `display_size`, `margins` — 사이즈/여백
- `fonts`, `min_font_size_px` — 타이포
- `color_rules`, `text_color_rule` — 색상
- `text_rules`, `copy` — 텍스트 규칙
- `layout_pattern`, `layout_cases` — 레이아웃
- `character_policy` — 캐릭터(MONI 등) 사용 규칙
- `few_shot_refs` — AI 빌더 참고 사례
- `builder_io` — 빌더 입력 매핑 / CTA 지원 여부
- `rules` — 필수/권장/금지 규정 리스트
- `tbd` — 보강 필요 항목 메모

신규 배너 작성 시 `pc_main_top.json`을 템플릿으로 복사 후 수정하세요.

---

## 외부배너 추가 (예정)

외부 광고주 배너도 동일하게 `banners/{id}.json`으로 추가합니다. 카테고리 분리가 필요해지면 `id` prefix(`ext_`)로 구분하거나 폴더 분리(`banners/internal/`, `banners/external/`)를 고려하세요.
