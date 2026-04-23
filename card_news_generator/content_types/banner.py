"""
배너 설정 (가로형 프로모션 배너)
================================
카드뉴스와 완전히 다른 구조 (세로 긴 글 X, 가로 넓은 구도 O).
copy_fields가 카드뉴스(badge/title/description/footer)와 다른지 의도적으로 확인용:
  배너: title / subtitle / cta_text / bg_tagline
"""

BANNER = {
    "name": "배너",
    "default_format": "png",

    # 배너는 카드뉴스와 다른 카피 필드 구조
    "copy_fields": {
        "title": {
            "role": "메인 헤드라인",
            "max_length": 22,
            "required": True,
        },
        "subtitle": {
            "role": "서브 카피 (한 줄)",
            "max_length": 35,
            "required": False,
            "fallback_field": "description",
        },
        "cta_text": {
            "role": "버튼 문구",
            "max_length": 10,
            "required": False,
            "fallback_field": "cta",
            "fallback": "자세히 보기",
        },
        "bg_tagline": {
            "role": "배경 장식용 영문/숫자",
            "max_length": 12,
            "required": False,
            "fallback": "PROMOTION",
        },
    },

    # 배너는 사이즈 변형 다양 (OG 이미지, 웹 상단 등)
    "sizes": {
        "1200x628": {
            "width": 1200, "height": 628,
            "template": "banner/promo.html",
            "label": "웹 배너 / OG 이미지",
        },
        "970x250": {
            "width": 970, "height": 250,
            "template": "banner/promo.html",
            "label": "빌보드 배너",
        },
    },
    "default_size": "1200x628",

    # Pillow 폴백 없음 — Playwright 또는 HTML만 사용
    # (배너는 카드뉴스 전용 Pillow 레이아웃을 쓸 수 없음)

    # SVG / Figma JSON 출력용 레이어 빌더
    "layer_builder": "content_types.banner_layers.build",
}
