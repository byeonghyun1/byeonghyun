# 학습 자료 인덱스

## 빠른 시작 (Quick Start)

새 계정에서 빠르게 프로젝트를 이해하려면:

1. **README.md** (5분) - 전체 개요
2. **conversation_history_full.md** (1시간) - 전체 대화 기록 정독
3. **ARCHITECTURE.md** (20분) - 기술 설계 상세
4. **card_news_generator/코드** - 실제 구현 분석

---

## 파일 설명

| 파일 | 크기 | 용도 | 읽는 시간 |
|---|---|---|---|
| **README.md** | 5.7KB | 프로젝트 개요 및 학습 가이드 | 5분 |
| **conversation_history_full.md** | 94KB | 모든 대화 기록 (132개 메시지) | 60분 |
| **ARCHITECTURE.md** | 27KB | 기술 설계 및 시스템 구조 | 20분 |
| **card_news_generator/** | - | 프로토타입 코드 | 자유 |

---

## 메시지 인덱스

### 주요 마일스톤

| # | 내용 | 상태 |
|---|---|---|
| 1-5 | 프로젝트 초기 분석 및 목표 정의 | 완료 |
| 6-20 | 3축 아키텍처 설계 | 완료 |
| 21-40 | 배너 & 포스터 콘텐츠 유형 추가 | 완료 |
| 41-70 | SVG 렌더링 및 Figma 호환성 | 완료 |
| 71-90 | 한글 폰트 처리 & 더미 카피 생성기 | 완료 |
| 91-100 | 최적화 및 프로토타입 검증 | 완료 |

### 주요 기술 주제

| 주제 | 메시지 범위 | 핵심 내용 |
|---|---|---|
| 3축 아키텍처 | #10-15 | content_type / brand / size 구조 |
| 배너 지원 추가 | #20-30 | 새 콘텐츠 유형 추가 과정 |
| SVG 렌더링 | #35-50 | LayerTree 및 Figma 호환성 |
| 한글 폰트 | #60-70 | Noto Sans KR 및 폴백 스택 |
| API 폴백 | #75-85 | 더미 카피 생성 및 안정성 |

---

## 코드 구조

```
card_news_generator/
├── engine/                  # 핵심 엔진
│   ├── generator.py        # 전체 흐름 조율
│   ├── copy_writer.py      # AI/더미 카피 생성
│   ├── svg_exporter.py     # SVG 렌더링
│   └── color_manager.py    # 색상 관리
├── content_types/          # 콘텐츠 유형별 구현
│   ├── card_news.py        # 카드뉴스
│   ├── card_news_layers.py # 카드뉴스 레이어 구축
│   ├── banner.py           # 배너
│   ├── banner_layers.py    # 배너 레이어 구축
│   ├── poster.py           # 포스터
│   └── poster_layers.py    # 포스터 레이어 구축
├── brands/                 # 브랜드별 스타일
│   ├── albamon.py          # 알바몬
│   ├── jobkorea.py         # 잡코리아
│   └── workspia.py         # 워스피어
├── templates/              # HTML 템플릿 (참고용)
└── output/                 # 결과물 저장소
    └── prototype/          # 샘플 결과물
```

---

## 학습 팁

### 1. 전체 흐름 이해하기
`conversation_history_full.md`를 처음부터 끝까지 순서대로 읽으면, 설계 과정의 모든 의사결정과 시행착오를 함께 이해할 수 있습니다.

### 2. 코드와 함께 읽기
각 메시지에서 언급된 파일을 직접 열어보면서 읽으면 이해가 빨라집니다.

예:
- #15 메시지: 3축 아키텍처 설명 → `engine/generator.py` 열어보기
- #25 메시지: 배너 추가 과정 → `content_types/banner.py` 열어보기
- #60 메시지: 한글 폰트 처리 → `engine/svg_exporter.py` 확인

### 3. 브랜드 시스템 이해하기
`brands/*.py` 파일들을 비교하며 읽으면, 브랜드별 스타일 차이와 확장 방식이 명확합니다.

### 4. 렌더링 파이프라인 추적하기
```
copy_writer.py (카피 생성)
  ↓
[content_type]_layers.py (레이어 트리)
  ↓
svg_exporter.py (SVG 변환)
  ↓
output/*.svg (결과)
```

이 흐름을 따라 코드를 읽으면 전체 시스템이 명확해집니다.

---

## FAQ

**Q. 새 계정에서 이 프로젝트를 시작하려면?**
A. README.md로 개요를 파악한 후, conversation_history_full.md를 전부 읽고, ARCHITECTURE.md로 기술을 정리한 다음, card_news_generator 코드를 실행해보세요.

**Q. 가장 핵심적인 설계가 뭐예요?**
A. 3축 아키텍처(content_type/brand/size)입니다. 이것이 전체 시스템을 유연하게 만듭니다. conversation_history_full.md의 #10-15 메시지를 참고하세요.

**Q. SVG 렌더링이 어떻게 작동하나요?**
A. LayerTree라는 중간 표현을 사용합니다. HTML을 파싱하지 않고, 콘텐츠 유형마다 정의된 레이어 빌더가 직접 트리를 만듭니다. #35-50 메시지를 참고하세요.

**Q. 새로운 콘텐츠 유형을 추가하려면?**
A. 4단계입니다:
1. `content_types/new_type.py` 파일 만들기
2. `content_types/new_type_layers.py` 레이어 빌더 구현
3. `templates/new_type/*.html` 템플릿 (선택)
4. `content_types/__init__.py`에 한 줄 추가

자세한 것은 #20-30 메시지(배너 추가 과정)를 참고하세요.

---

## 생성 정보

- 원본 JSONL: 664줄 (3.4MB)
- 추출 메시지: 131개 (사용자 32개 + 어시스턴트 99개)
- 생성 날짜: 2026-04-14
- 형식: Markdown (한글)

---

**준비 완료. 학습하세요!**
