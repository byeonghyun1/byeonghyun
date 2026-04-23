"""
콘텐츠 유형 레지스트리
======================
콘텐츠 유형(카드뉴스/배너/포스터/상세페이지 등)을 설정값으로 관리합니다.

새 콘텐츠 유형 추가 방법:
    1. 이 폴더에 새 파일 만들기 (예: banner.py)
    2. 설정 dict 작성 (기본 크기, 템플릿 경로, 카피 필드 등)
    3. 아래 REGISTRY dict에 등록

예:
    from .banner import BANNER
    REGISTRY = {
        "card_news": CARD_NEWS,
        "banner": BANNER,   # ← 한 줄만 추가
    }

엔진 코드는 수정하지 않습니다.
"""

from .card_news import CARD_NEWS
from .banner import BANNER
from .poster import POSTER

# 콘텐츠 유형 레지스트리
REGISTRY = {
    "card_news": CARD_NEWS,
    "banner": BANNER,
    "poster": POSTER,
    # "detail_page": DETAIL_PAGE, ← 추후 추가
}


def list_sizes(content_type: str) -> list:
    """해당 콘텐츠 유형이 허용하는 사이즈 키 목록."""
    cfg = REGISTRY.get(content_type, {})
    sizes = cfg.get("sizes")
    if isinstance(sizes, dict):
        return list(sizes.keys())
    return []


def get_config(content_type: str) -> dict:
    """content_type으로 설정을 가져옵니다. 없으면 KeyError."""
    if content_type not in REGISTRY:
        available = ", ".join(REGISTRY.keys())
        raise KeyError(
            f"지원하지 않는 content_type: '{content_type}'. "
            f"현재 지원 목록: {available}"
        )
    return REGISTRY[content_type]


def list_content_types() -> list:
    """등록된 모든 content_type 목록을 반환합니다."""
    return list(REGISTRY.keys())
