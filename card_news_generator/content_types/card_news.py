"""
카드뉴스 설정
=============
카드뉴스의 기본 크기, 템플릿, 카피 전략 등을 정의합니다.
"""

CARD_NEWS = {
    "name": "카드뉴스",

    # 사이즈 변형 (규격 축)
    # 같은 카드뉴스라도 피드용 정사각형 / 스토리용 세로형을 분리
    "sizes": {
        "1080x1080": {
            "width": 1080, "height": 1080,
            "template": "card_news/basic.html",
            "label": "인스타 피드 (정사각형)",
        },
        "1080x1350": {
            "width": 1080, "height": 1350,
            "template": "card_news/portrait.html",
            "label": "인스타 세로형 (4:5)",
        },
    },
    "default_size": "1080x1080",

    # 기본 출력 포맷 (png | html | pdf)
    "default_format": "png",

    # 이 콘텐츠 유형이 사용하는 카피 필드 + 각 필드의 기본값/역할
    # → copy_writer와 AI 프롬프트가 이 목록을 기준으로 동작
    "copy_fields": {
        "badge": {
            "role": "라벨 키워드",
            "max_length": 8,
            "required": False,
            # 비어있을 때 topic에서 아래 키워드가 있으면 자동 추출
            "auto_extract_from": "topic",
            "keywords": [
                "이벤트", "할인", "오픈", "런칭", "신규",
                "특가", "무료", "혜택", "안내", "공지",
                "채용", "모집", "업데이트", "세일",
            ],
            "fallback": "EVENT",
        },
        "title": {"role": "메인 제목",       "max_length": 30, "required": True},
        "description": {
            "role": "설명 문구",
            "max_length": 60,
            "required": False,
            # 비어있으면 mood 값으로 대체
            "fallback_field": "mood",
        },
        "footer": {"role": "하단 보조 문구", "max_length": 40, "required": False},
    },

    # Pillow 폴백 렌더러 (이 콘텐츠 유형 전용 레이아웃)
    # None이면 Playwright/HTML만 사용
    "pillow_renderer": "content_types.card_news_pillow.render",

    # 레이어 트리 빌더 (SVG / Figma JSON 출력용)
    # 함수 시그니처: build(context: dict, width: int, height: int) -> Frame
    # 같은 LayerTree가 A(SVG)·B(Figma 플러그인 JSON) 양쪽에 재사용됨.
    "layer_builder": "content_types.card_news_layers.build",

    # 필수 입력 필드 (DesignRequest 기준)
    "required_fields": ["topic"],

    # AI 카피 생성용 프롬프트 (변수: topic, target, mood, purpose)
    "ai_prompt": (
        "카드뉴스 1장용 카피를 만들어줘.\n"
        "주제: {topic}\n"
        "타겟: {target}\n"
        "분위기: {mood}\n"
        "목적: {purpose}\n\n"
        "아래 JSON 형식으로만 응답해줘 (코드블록 없이):\n"
        '{{"badge": "뱃지 텍스트", "title": "제목", '
        '"description": "설명 문구", "footer": "하단 문구"}}'
    ),

    # 뱃지 자동 추출용 키워드
    "badge_keywords": [
        "이벤트", "할인", "오픈", "런칭", "신규",
        "특가", "무료", "혜택", "안내", "공지",
        "채용", "모집", "업데이트", "세일",
    ],
}
