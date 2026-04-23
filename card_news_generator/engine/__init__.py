"""
콘텐츠 디자인 생성 엔진
========================
외부에서 이 엔진을 사용할 때:

    from engine import DesignEngine, DesignRequest

    # 카드뉴스
    request = DesignRequest(topic="설날 새해 이벤트", mood="귀여운")
    result = DesignEngine().generate(request)
    print(result.output_path)

    # 추후 배너/포스터/상세페이지
    request = DesignRequest(topic="...", content_type="banner")
    result = DesignEngine().generate(request)

하위 호환을 위해 CardRequest / CardNewsEngine도 그대로 쓸 수 있습니다.
"""

from .schema import DesignRequest, DesignResult
from .generator import DesignEngine

# 하위 호환 alias (구 이름으로 import해도 동작)
CardRequest = DesignRequest
CardResult = DesignResult
CardNewsEngine = DesignEngine

__all__ = [
    "DesignRequest",
    "DesignResult",
    "DesignEngine",
    "CardRequest",
    "CardResult",
    "CardNewsEngine",
]
