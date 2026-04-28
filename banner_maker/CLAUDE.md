# Banner Maker — Claude 작업 지침

잡코리아·알바몬 배너 자동 생성 도구. 이 문서는 Claude가 이 프로젝트에서 작업할 때 따라야 할 규칙을 정의합니다.

상세 아키텍처는 `ARCHITECTURE.md`, 데이터 구조는 `config/README.md`, 요구사항은 `banner-builder-prd.md` 참조.

---

## 1. 데이터 SSoT 원칙 (가장 중요)

**모든 데이터의 진실은 `config/`에 있습니다. 단일 SSoT.**

### 1.1 SSoT 위치

| 데이터 | SSoT 파일 | 비고 |
|---|---|---|
| 배너별 스펙 (사이즈·여백·폰트·규칙) | `config/banners/{id}.json` | 1배너 = 1파일. 배너의 모든 정보 포함 |
| 배너 인덱스 (UI 노출 목록) | `config/banners/_index.json` | fetch 디렉토리 스캔 불가로 별도 인덱스 |
| 전역 폰트 가이드 (사용 가능 폰트·옵션·전역 규칙) | `config/font_guide.json` | 배너별 폰트는 `banners/{id}.json` 우선 |
| 색상 가이드 | `config/color_guide.json` | |
| 디자인 공통 규정 | `config/design_rules.json` | |

### 1.2 SSoT 규칙

- **`guides/*.md`는 사람용 보조 뷰**. 어긋날 경우 `config/`가 우선.
- **`config/font_guide.json`에 `per_banner_fonts` 키를 다시 만들지 마세요.** 폰트 SSoT는 `banners/{id}.json`로 단일화 완료. 두 곳 동기화 부담 영구 차단.
- **prototype.html에 PRESETS 객체 데이터를 다시 하드코딩하지 마세요.** `loadPresets()` 함수가 `config/banners/`에서 동적으로 로드합니다.
- 사용자가 "폰트 바꿔줘", "여백 수정" 등 요청 시 → `config/banners/{id}.json`만 수정. UI는 자동 반영됨.

---

## 2. 현재 구현 상태 (혼동 방지)

| 폴더/파일 | 상태 |
|---|---|
| `prototype.html` | **현재 동작하는 단일 파일 UI**. config/banners를 fetch로 로드 |
| `config/banners/*.json` | **사용 중**. prototype.html이 동적 로드 (11개 배너) |
| `config/banners/_index.json` | **사용 중**. UI 노출 배너 목록 |
| `config/{font,color,design_rules}.json` | **사용 중** (전역 가이드) |
| `engine/`, `checks/`, `dashboard/`, `logs/`, `output/`, `templates/` | **빈 폴더 (미구현)**. ARCHITECTURE.md는 향후 설계도 |
| `config/templates/`, `config/cta_styles/` | **빈 폴더 (미구현)**. CTA는 prototype.html에 하드코딩 (cta1, cta2) |
| `feedback/learned_rules.json` | 학습 데이터 시드 (1개 룰만 있음, 자동 추출 미구현) |

→ **코드 수정 요청은 기본적으로 `prototype.html`에서 작업**합니다. `engine/` 작업 요청은 ARCHITECTURE.md 기준 신규 구현입니다.

---

## 3. prototype.html 실행 방법

`prototype.html`은 fetch로 config/banners를 로드하므로 **file:// 직접 열기는 작동하지 않습니다**. http 서버 필수.

```bash
cd /Users/thdduss/Desktop/workspace/banner_maker
python3 -m http.server 8080
# 브라우저에서 http://localhost:8080/prototype.html
```

배포는 Vercel 등 정적 호스팅 사용 (PRD 참조).

---

## 4. 변경 시 어디 건드리나 (체크리스트)

| 요청 유형 | 수정 파일 | 추가로 해야 할 것 | 절대 만지면 안 되는 것 |
|---|---|---|---|
| **새 배너 추가** | `config/banners/{id}.json` 신규 (`_TEMPLATE.json` 복사) | `config/banners/_index.json`의 `banners` 배열 + (UI 노출 시) `ui_visible` 배열에 ID 추가 | guides/, prototype.html 본문 |
| 기존 배너 스펙 변경 (사이즈·여백·폰트·규칙) | `config/banners/{id}.json` | — | guides/, font_guide.json (전역만 두는 곳) |
| 폰트 패밀리·옵션 전역 변경 | `config/font_guide.json` (font_selection_system 등) | — | 배너별 JSON의 fonts (배너별로 개별 적용 시는 banners/만) |
| 색상 규칙 전역 변경 | `config/color_guide.json` | — | guides/ |
| 디자인 공통 규정 변경 | `config/design_rules.json` | — | guides/ |
| UI/UX 변경 (입력 폼·미리보기·CTA 스타일 등) | `prototype.html` | — | config/ |
| 자간 표기 변경 | JSON에 `"-2%"` 형식 (문자열) | prototype.html의 `parsePercentSpacing`이 `-0.02`로 변환 | prototype.html에 -0.02 직접 하드코딩 |

---

## 5. 작업 방식

- PRD/요구사항 → 코드 직행 **금지**. 항상 어느 파일을 어떻게 바꿀지 의도 먼저 설명하고 확인.
- 큰 변경(파일 이동·삭제·구조 변경) 전 반드시 확인 받기.
- 요청 범위 외 리팩토링·주석 추가·구조 변경 **금지**.
- 모든 응답·문서·커밋 메시지는 **한국어**. 코드 변수명·함수명만 영어.

---

## 6. 데이터 형식 컨벤션

### 6.1 JSON 스타일
- 인덴트 2칸
- 키 순서: `id` → `name` → `last_updated` → `location` → 메타 → 스펙 → `rules` → `tbd`
- 신규 배너 작성 시 `config/banners/_TEMPLATE.json`을 복사해서 시작
- 보강 필요 항목은 `tbd` 배열로 명시

### 6.2 표기 통일
| 항목 | JSON 표기 | prototype.html 내부 표기 | 변환 |
|---|---|---|---|
| 자간 (letter_spacing) | 문자열 `"-2%"`, `"-4%"`, `"0%"` | 숫자 `-0.02`, `-0.04`, `0` | `parsePercentSpacing()` |
| 사이즈 | 숫자 `size_px: 62` | 숫자 `size: 62` | adapter에서 키 변환 |
| 차원 | `dimensions: {width, height}` | `{w, h}` | adapter에서 키 변환 |

→ prototype.html이 사용하는 키 이름이 다른 이유는 옛 PRESETS와의 호환을 위해. JSON 측은 의미 있는 풀네임 유지.

### 6.3 rules 형식
```json
"rules": [
  { "type": "필수", "text": "..." },
  { "type": "권장", "text": "..." },
  { "type": "금지", "text": "..." }
]
```

### 6.4 배너 ID 네이밍
- `{platform}_{location}` 형식: `pc_main_top`, `m_app_splash`, `email_target`
- platform: `pc` / `m` (모바일 웹) / `m_app` (앱) / `email`
- 외부배너 추가 시 prefix `ext_` 사용 검토 (현재는 미정 — 추가 전 확인)

---

## 7. PRD vs 현재 격차

PRD(`banner-builder-prd.md`)는 **슬롯 기반·사용자 정의 사이즈·컴포넌트 라이브러리·AI 이미지 생성** 등 큰 그림.
현재 prototype.html은 **고정 11개 배너 + 텍스트/이미지/CTA 입력**의 MVP 전 단계.

→ "PRD에 적힌 슬롯/컴포넌트 작업해줘" 같은 요청 시: 신규 구현 영역. 사용자에게 어디부터 시작할지 먼저 확인.

---

## 8. 참고 문서

| 상황 | 문서 |
|---|---|
| 전체 아키텍처 이해 | `ARCHITECTURE.md` |
| config/ 사용법 | `config/README.md` |
| PRD (요구사항) | `banner-builder-prd.md` |
| 사람용 가이드 (보조) | `guides/*.md` |
| 신규 배너 템플릿 | `config/banners/_TEMPLATE.json` |
