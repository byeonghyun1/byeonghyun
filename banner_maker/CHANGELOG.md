# Banner Maker 변경 일지

분기점별 작업 이력. 각 버전에 어떤 기능이 추가·수정·보류됐는지 기록.

---

## [v0.1] — 2026-05-08 (첫 분기점)

프로젝트 시작(2026-04-18)부터 첫 분기점까지 모든 작업을 v0.1로 통합.

### 🎯 프로젝트 개요
- **목표**: 비디자이너(기획자)도 사용 가능한 배너 자동 제작 에이전트 — 반복적·패턴화된 단순 배너 작업 자동화
- **기간**: 2026-04-18 ~ 2026-05-08
- **원칙**: 비디자이너 친화 / 자유도 제한 / 확장성 + 유연성

### 📅 타임라인

| 날짜 | 마일스톤 |
|---|---|
| 04/18 | 프로젝트 킥오프 — 폴더 구조·`ARCHITECTURE.md` |
| 04/21 | 프로토타입 웹 첫 빌드 + 피드백 5건 즉시 반영 |
| 04/22 | 폰트 시스템 (Paperlogy 통일) |
| **04/23** | **Canvas 렌더링 통합 — HTML 미리보기 → Canvas (핵심 전환점)** |
| 04/24 | 11개 배너별 가이드 MD+JSON |
| **04/27** | **SSoT 구조 확립 — config/ 단일 진실 원천, 동적 fetch 로딩** |
| 04/28 | 이미지 배치 (투명 PNG 감지·수동 조정) |
| 04/29 | 코드 통합·텍스트 컬러·강조 컬러·contain/crop 전 배너 |
| 04/30 | 로고 시스템 확장 — 출처표기 이미지 + 콜라보 + 자체점검 13건 |
| 05/04 | 학습 시스템 고도화 (contain/crop 분리·manual 클립 해제·듀얼) |
| 05/06 | 자체점검 #1~#17 처리 (high 3·mid 5·lower 7) |
| 05/07 | 카드별 텍스트 편집 모달 + 이벤트 리스트 1~4 추가 |
| **05/08** | **v0.1 분기점 — 시리즈 base · m_event_list_5 · #18~#26 · Git 도입 · 카드별 PNG 다운로드** |

### 🏗 핵심 아키텍처
- **SSoT**: `config/banners/{id}.json`이 유일한 데이터 원천. 코드는 동적 fetch
- **Canvas 렌더링**: 미리보기 = 출력물 (PNG 다운로드와 동일)
- **동적 프리셋 로딩**: `_index.json` 기반 자동 로드 + JSON 필수 키 검증
- **시리즈 base + `_extends`**: 같은 시리즈(이벤트 리스트) 정책 한 곳 통합
- **학습 자동화**: 사용자 manual 조정 → 다운로드 시 자동 학습 → 다음 업로드 평균 적용

### 🆕 추가된 기능

#### 배너 라인업 (총 16개 등록 / 9개 UI 노출)
- **PC 4종 노출**: 메인 커튼 / 메인 탑 / 공고 스카이 / **로그인 우측**
- **모바일 이벤트 리스트 5종 신규**:
  - m_event_list_1 (288×206) · main 32px
  - m_event_list_2 (238×140) · main 24px · scale_min 0.4
  - m_event_list_3 (210×140) · main 24px · max 16자
  - m_event_list_4 (464×344) · main 54px · max 20자
  - m_event_list_5 (600×200) · main 40px · 우측 200px 이미지 영역
- **숨김 7개**: pc_recruit_bottom·pc_recruit_bottom_text·pc_search_right·pc_company_left·m_app_splash·m_sub_banner·email_target

#### 카드별 텍스트 편집 (펜 아이콘 모달)
- 미리보기 카드 ✎ 클릭 → **80% 반투명 팝오버**
- 메인은 **textarea** (Enter 줄바꿈), 서브는 **input**
- 한 줄 고정 배너(메인 커튼·메인 탑) **줄바꿈 자동 차단**
- 서브 미지원 배너(이벤트 리스트) **서브 입력란 비활성화**
- **실시간 미리보기** (입력 즉시 카드 갱신)
- **ESC 닫기** (외부 클릭 무시)
- 사이드바 카피 변경해도 카드별 override 유지

#### 카드별 PNG 다운로드 (⬇ 아이콘)
- 미리보기 카드 ctrl-row에 펜 아이콘(✎) 옆 ⬇ 버튼
- 일괄 다운로드와 **동일 동작** (학습 데이터 자동 저장 포함)
- `card-icon-btn` 공통 base 클래스로 ✎/⬇ 스타일 통일
- 다중선택 여부와 무관하게 그 배너만 직접 다운로드

#### 이미지 학습 자동화
- **manual 모드**에서 슬라이더·드래그로 조정 → PNG 다운로드 시 자동 학습
- **contain/crop 모드별 분리** 학습·적용
- **단일/듀얼 이미지 슬롯별** 분리 (커튼배너 좌·우 등)
- **cal+manual 합산** 저장 (발산 방지)
- **manual 클립 해제** (텍스트와 의도적 겹침 가능)
- 학습 파일: `config/banners/{id}_calibration.json` (자동 생성)

#### 텍스트 컬러
- auto / Black / White 전환
- 강조 컬러 (`{단어}` 마크업 시 일부 단어 색상 변경)

#### 로고 시스템
- **출처 표기 이미지 모드** (우상단 영역)
- **콜라보 로고** (logo_box)
- **unified 모드** — 출처/콜라보 한 자리 (둘 중 하나만)
- 미리보기 카드 토글로 활성/비활성

#### CTA
- 배너별 지원 여부 (`builder_io.cta.supported`)
- 디폴트 높이 9% (배너별 명시 가능)
- 폰트·자간·화살표 사이즈 비율 명시

#### 자동 구성
- 글자수 기반 메인/서브 크기 자동 결정 (`font_size_rules`)
- 배경 밝기 기반 텍스트 색상 (luminance)
- 자동 줄바꿈 (단어 단위 → 2줄 초과 시 강제 분할)

### 🔑 배너별 정책 키
- `copy.sub_supported: false` — 서브 카피 미지원
- `copy.main_max_chars_kr` — 글자수 제한
- `copy.main_line_break_allowed` — 수동 줄바꿈 허용
- `copy.main_auto_wrap` — 단어 단위 자동 줄바꿈
- `copy.composition_type` — 명시적 구성 타입
- `image_box.anchor` — `below_text` / `right_zone_center` / 기존 anchor
- `image_box.crop_clip_in_auto: false` — crop 모드 영역 밖 잘림 해제
- `image_box.scale_min` / `scale_max` — 슬라이더 범위
- `builder_io.cta.supported` — CTA 지원 여부
- `_extends` — 시리즈 base 상속

### 🔧 자체점검 (#1~#26)
- **처리 완료 21건**: 학습 누적 발산 방지, cal+manual 합산, contentBoundsCaches 객체화, _index.json 검증, JSON 필수 키 검증, drawFullImage crop·contain 통합, 변수명 일관화, getEffectiveTransform·getCalibrationBoost·getImageBoxOpt 헬퍼, 시리즈 base, zone anchor 패턴, getAnchorKind 디스패치, resolveCompositionType, setupModalField 추출, 매직 넘버 주석 등
- **보류 5건**: #6 fitMode 전략 패턴, #14 옛 호환 키, #16 cal 반환 일부, #22 image_box 그룹화, #10·#20 부분만

### 🛠 버전 관리 도입
- **Git 저장소** + **CHANGELOG.md**
- **SELF_REVIEW.md** 자체점검 누적 리스트
- **첫 분기점 v0.1** (2026-05-08)
- 학습 데이터(`*_calibration.json`)는 `.gitignore`로 제외 (사용자별 누적 데이터)

### 📝 알려진 한계
- horizontal_sub_main / fallback 분기는 textBoxes 미기록 (인라인 편집 v0.1에서 제거됨)
- pc_main_top·pc_main_curtain 등은 시리즈 패턴 미적용 (이벤트 리스트만)
- image_box 객체에 키 다수 누적 (#22 보류)

### 📂 v0.1 파일 변경 요약
- `prototype.html` 단일 파일 UI (모든 로직)
- `config/banners/_index.json` `_series.event_list` 추가
- `config/banners/m_event_list_1~5.json` 신규 (`_extends` 적용)
- `config/banners/pc_login_right.json` 가이드 보강
- `SELF_REVIEW.md` 자체점검 누적 리스트 (#1~#26)
- `server.py` calibration POST + 정적 서빙
- `CHANGELOG.md` (이 파일) + `.gitignore`

---

## 사용 방법

### 새 분기점 만들기 (v0.2 이후)
사용자: "v0.2로 분기해줘" → Claude가 자동 처리
1. CHANGELOG.md에 [v0.2] 섹션 추가
2. `git add . && git commit -m "v0.2: ..."` + `git tag v0.2`

### 특정 버전 모습 보기
사용자: "v0.1 모습 보여줘" → `git checkout v0.1` 후 `main` 복귀

### 두 버전 차이 보기
사용자: "v0.1과 지금 뭐가 다른지" → `git diff v0.1` 결과 정리

---

> 코드 자체 백업은 git이 자동 처리. 이 문서는 사람이 읽는 변경 일지.
> 회고 (시각 자료·디자인 의도 등 상세): [노션 회고](https://www.notion.so/Banner-Maker-3517d8322b04802484c7e849594025a7)
