"""알바몬 브랜드 설정"""

ALBAMON = {
    "name": "알바몬",
    "name_en": "albamon",
    "tone": "친근하고 밝은, 2030이 편하게 읽을 수 있는 구어체",
    "target": "아르바이트를 찾는 20-30대",

    "colors": {
        "bg_color": "#FFF8E1",
        "accent_color": "#FF6D00",
        "title_color": "#212121",
        "desc_color": "#555555",
        "on_primary": "#FFFFFF",
        "surface": "#FFFDF5",
    },

    "typography": {
        "primary_font": "Noto Sans KR",
        "heading_font": "Noto Sans KR",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap",
    },

    "logo": {
        "primary": "",  # 추후 assets/albamon/logo.svg
    },

    # 콘텐츠 유형별 세부 설정 (필요할 때만 채움)
    "overrides": {
        # "card_news": { "template": "card_news/albamon.html" },
        # "banner":    { "template": "banner/albamon.html" },
    },
}
