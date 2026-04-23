"""
엔진 공통 설정 (콘텐츠 유형/브랜드와 무관한 공용 리소스)
==========================================================
여기에는 "어떤 콘텐츠 유형이든, 어떤 브랜드든 공통으로 쓰는 것"만 둡니다.
  - 경로 상수
  - 분위기(mood) 팔레트 ← 분위기는 콘텐츠 유형/브랜드와 독립된 축
  - 기본 색상 폴백
  - Pillow 폴백용 폰트 후보 경로

브랜드 데이터는 brands/ 패키지에,
콘텐츠 유형 데이터는 content_types/ 패키지에 있습니다.
"""

from pathlib import Path

# ============================================================
# 경로
# ============================================================
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"


# ============================================================
# 분위기(mood) 팔레트 — 브랜드·콘텐츠 유형과 독립된 축
# 브랜드 미지정 시 mood가 색상을 결정
# ============================================================
MOOD_PRESETS = {
    "귀여운": {
        "bg_color": "#FFF0F5",
        "accent_color": "#FF6B9D",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
    "따뜻한": {
        "bg_color": "#FFF8F0",
        "accent_color": "#FF8C42",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
    "세련된": {
        "bg_color": "#1A1A2E",
        "accent_color": "#E94560",
        "title_color": "#FFFFFF",
        "desc_color": "#CCCCCC",
    },
    "신뢰감": {
        "bg_color": "#F0F4FF",
        "accent_color": "#3B5BDB",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
    "활기찬": {
        "bg_color": "#FFFDE7",
        "accent_color": "#FFB300",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
    "자연스러운": {
        "bg_color": "#F1F8E9",
        "accent_color": "#66BB6A",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
    "차분한": {
        "bg_color": "#F3E5F5",
        "accent_color": "#AB47BC",
        "title_color": "#2D2D2D",
        "desc_color": "#555555",
    },
}

DEFAULT_COLORS = {
    "bg_color": "#F5F5F5",
    "accent_color": "#333333",
    "title_color": "#2D2D2D",
    "desc_color": "#555555",
}


# ============================================================
# 기본 타이포그래피 (브랜드 미지정 시 폴백)
# ============================================================
DEFAULT_TYPOGRAPHY = {
    "primary_font": "Noto Sans KR",
    "heading_font": "Noto Sans KR",
    "font_url": (
        "https://fonts.googleapis.com/css2?"
        "family=Noto+Sans+KR:wght@400;700;900&display=swap"
    ),
}


# ============================================================
# 한글 폰트 후보 경로 (Pillow 폴백 렌더러용)
# ============================================================
FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/NanumGothic.ttf",
    "/Library/Fonts/NanumGothicBold.ttf",
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
]


# ============================================================
# mood 헬퍼
# ============================================================
def get_mood_colors(mood: str) -> dict:
    """분위기 텍스트에서 색상 프리셋을 매칭합니다."""
    for keyword, preset in MOOD_PRESETS.items():
        if keyword in mood:
            return preset.copy()
    return DEFAULT_COLORS.copy()
