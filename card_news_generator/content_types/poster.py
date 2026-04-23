"""
포스터 설정
===========
A4 인쇄/공지용 세로 포스터. 카드뉴스/배너와 독립된 카피 구조·사이즈 체계.

핵심 포인트:
  - 같은 3축 구조(content_type / size / brand)의 새 콘텐츠 유형 예시
  - 엔진 코드 수정 없이, 이 파일 + 템플릿만 추가해서 동작
"""

POSTER = {
    "name": "포스터",
    "default_format": "png",

    # 포스터 고유의 카피 필드 — 카드뉴스·배너와 섞이지 않음
    "copy_fields": {
        "title": {
            "role": "포스터 메인 타이틀",
            "max_length": 20,
            "required": True,
        },
        "subtitle": {
            "role": "보조 타이틀",
            "max_length": 40,
            "required": False,
            "fallback_field": "description",
        },
        "date_range": {
            "role": "행사/이벤트 기간",
            "max_length": 40,
            "required": False,
            "fallback": "상시",
        },
        "place": {
            "role": "장소/주최",
            "max_length": 40,
            "required": False,
        },
        "footer": {
            "role": "문의/주최 표기",
            "max_length": 60,
            "required": False,
        },
    },

    # 포스터가 허용하는 사이즈 목록 (설정만으로 확장 가능)
    # 새 사이즈(예: A3_vertical, B5_vertical)는 여기에 한 항목만 추가하면 됨.
    "sizes": {
        "A4_vertical": {
            # 72dpi 기준 픽셀. 인쇄 품질이 필요하면 150/300dpi 버전을 별도 키로 추가.
            "width": 595, "height": 842,
            "template": "poster/a4.html",
            "label": "A4 세로 (210×297mm, 72dpi)",
        },
        "A4_vertical_print": {
            "width": 2480, "height": 3508,
            "template": "poster/a4.html",
            "label": "A4 세로 (300dpi 인쇄용)",
        },
    },
    "default_size": "A4_vertical",

    # SVG / Figma JSON 출력용 레이어 빌더
    "layer_builder": "content_types.poster_layers.build",
}
