"""
브랜드 레지스트리
=================
브랜드는 "스타일" 축입니다. (콘텐츠 유형은 "형식" 축으로 content_types/에 분리되어 있음)

이 둘은 서로 독립적으로 조합 가능해야 합니다:
  - 카드뉴스 × 알바몬
  - 카드뉴스 × 잡코리아
  - 배너    × 알바몬
  - 배너    × 웍스피어
  - ...

새 브랜드 추가 방법:
    1. 이 폴더에 새 파일 만들기 (예: new_brand.py)
    2. 브랜드 dict 작성 (base.py 참고)
    3. 아래 REGISTRY에 등록

예:
    from .new_brand import NEW_BRAND
    REGISTRY = {
        "albamon": ALBAMON,
        "jobkorea": JOBKOREA,
        "worxphere": WORXPHERE,
        "new_brand": NEW_BRAND,   # ← 한 줄 추가
    }

엔진 코드와 content_types는 수정하지 않습니다.
"""

from .albamon import ALBAMON
from .jobkorea import JOBKOREA
from .worxphere import WORXPHERE

REGISTRY = {
    "albamon": ALBAMON,
    "jobkorea": JOBKOREA,
    "worxphere": WORXPHERE,
}


def get_brand(brand_key: str) -> dict:
    """브랜드 키로 설정을 가져옵니다. 없으면 빈 dict."""
    if not brand_key:
        return {}
    return REGISTRY.get(brand_key, {})


def list_brands() -> list:
    """등록된 모든 브랜드 키 목록을 반환합니다."""
    return list(REGISTRY.keys())


# ============================================================
# 브랜드 × 콘텐츠 유형 결합 헬퍼
# ============================================================
def resolve_brand_for_content(brand_key: str, content_type: str) -> dict:
    """
    브랜드 × 콘텐츠 유형 조합을 적용한 최종 브랜드 설정을 반환합니다.

    동작:
      1. 브랜드 기본 설정을 가져옴
      2. 해당 브랜드의 overrides[content_type]이 있으면 deep-merge로 덮어씀

    예: 알바몬은 기본 컬러가 #FFF8E1인데,
        배너에서는 더 진한 배경을 쓰고 싶으면
        albamon.py의 overrides["banner"]["colors"]["bg_color"]에 선언.
    """
    brand = get_brand(brand_key)
    if not brand:
        return {}

    # 얕은 복사 (overrides를 합칠 때만 깊게)
    merged = {k: v for k, v in brand.items() if k != "overrides"}
    overrides = brand.get("overrides", {}).get(content_type, {})

    # overrides의 최상위 키만 얕게 병합. 중첩된 dict는 키 단위로 병합.
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged
