"""
규칙 기반 더미 카피 생성기 (외부 API 없음)
============================================
프로토타입 단계에서 '--copy-mode ai' 또는 'refine'을 써도
외부 API 호출 없이 그럴듯한 카피가 채워지도록 하는 로컬 더미 생성기.

핵심 원칙:
  - copy_fields의 구조(role / max_length / fallback)만 읽어서 동작
  - 특정 콘텐츠 유형 이름을 하드코딩하지 않음
  - 실제 AI 붙일 때(_call_ai 안) 이 함수는 손댈 필요 없음
"""

import re
from .schema import DesignRequest


# 목적/분위기 → 문구 톤 테이블 (규칙 기반 더미)
PURPOSE_PHRASES = {
    "click":           {"cta": "지금 확인하기", "closer": "자세한 내용을 확인해보세요"},
    "signup":          {"cta": "무료 가입하기", "closer": "지금 가입하고 혜택 받아가세요"},
    "info":            {"cta": "자세히 보기",   "closer": "꼭 알아두셔야 할 정보입니다"},
    "brand_awareness": {"cta": "더 알아보기",   "closer": "새로운 변화를 경험해보세요"},
}

MOOD_ADJECTIVES = {
    "귀여운":     ["깜찍한", "사랑스러운", "반짝이는"],
    "따뜻한":     ["포근한", "따스한", "다정한"],
    "세련된":     ["프리미엄", "엣지있는", "모던한"],
    "활기찬":     ["특별한", "역동적인", "폭발적인"],
    "자연스러운": ["편안한", "자연스러운", "부드러운"],
    "차분한":     ["잔잔한", "담담한", "고요한"],
    "밝은":       ["산뜻한", "경쾌한", "밝은"],
}

BADGE_BY_PURPOSE = {
    "click": "NOW",
    "signup": "SIGNUP",
    "info": "NOTICE",
    "brand_awareness": "BRAND",
}


def generate_dummy(request: DesignRequest, copy_fields: dict) -> dict:
    """
    copy_fields를 돌면서 각 필드에 규칙 기반으로 값을 채웁니다.
    이미 사용자가 입력한 값이 있으면 그대로 둡니다.
    """
    topic = request.topic or "새로운 소식"
    target = request.target or "모든 고객"
    mood = request.mood or ""
    purpose = request.purpose or "info"
    cta_fallback = PURPOSE_PHRASES.get(purpose, PURPOSE_PHRASES["info"])["cta"]

    adj = MOOD_ADJECTIVES.get(mood, [""])[0]

    result = {}
    for name, meta in copy_fields.items():
        # 이미 입력됐으면 유지
        user_val = getattr(request, name, "") or (request.copy_inputs or {}).get(name, "")
        if user_val:
            result[name] = user_val
            continue

        # 필드 이름 기반 규칙 (범용적으로 자주 쓰는 필드명만)
        generated = _guess_by_name(
            name=name,
            meta=meta if isinstance(meta, dict) else {},
            topic=topic,
            target=target,
            adj=adj,
            purpose=purpose,
            cta_fallback=request.cta or cta_fallback,
        )
        result[name] = _truncate(generated, meta)

    return result


def refine_dummy(request: DesignRequest, copy_fields: dict) -> dict:
    """
    '다듬기' 모드의 더미 버전: 사용자가 쓴 문구 끝에 분위기 형용사나 CTA 훅을
    약하게 덧붙여 살짝 다른 결과물을 돌려줍니다. (실제 AI refine 느낌만 흉내)
    """
    adj = MOOD_ADJECTIVES.get(request.mood or "", [""])[0]
    cta_hook = PURPOSE_PHRASES.get(request.purpose or "info", {}).get("closer", "")

    refined = {}
    for name, meta in copy_fields.items():
        original = getattr(request, name, "") or (request.copy_inputs or {}).get(name, "")
        if not original:
            # 비어있으면 generate_dummy 규칙으로
            refined[name] = generate_dummy(request, {name: meta}).get(name, "")
            continue

        # 필드 이름에 따라 다듬는 방식이 다름
        if "title" in name:
            # 제목: 형용사 접두만
            new_val = f"{adj} {original}".strip() if adj and adj not in original else original
        elif "description" in name or name == "subtitle":
            # 설명: 끝에 클로저 덧붙이기
            new_val = original if original.endswith(("!", "?", ".")) else original + "."
            if cta_hook and cta_hook not in new_val:
                new_val = f"{new_val} {cta_hook}"
        elif "cta" in name:
            # CTA는 그대로
            new_val = original
        else:
            new_val = original

        refined[name] = _truncate(new_val, meta)

    return refined


# ────────────────────────────────────────
# 내부 규칙
# ────────────────────────────────────────
def _guess_by_name(name, meta, topic, target, adj, purpose, cta_fallback):
    """필드 이름과 메타로 합리적 더미를 만든다."""
    # fallback 고정 문자열 우선
    if meta.get("fallback"):
        return meta["fallback"]

    n = name.lower()

    if n in ("badge",):
        return _extract_keyword_badge(topic) or BADGE_BY_PURPOSE.get(purpose, "EVENT")
    if n in ("title",):
        return f"{adj} {topic}".strip() if adj else topic
    if n in ("subtitle",):
        return f"{target}을 위한 특별한 제안" if target else "지금 바로 확인하세요"
    if n in ("description",):
        return f"{target} 여러분께 드리는 {adj} 소식입니다.".strip()
    if n in ("cta_text", "cta"):
        return cta_fallback
    if n in ("bg_tagline",):
        return BADGE_BY_PURPOSE.get(purpose, "PROMO")
    if n in ("date_range",):
        return "상시 진행"
    if n in ("place",):
        return "온라인"
    if n in ("footer",):
        return cta_fallback

    # 마지막 폴백
    return topic


_BADGE_KEYWORDS = [
    "이벤트", "할인", "오픈", "런칭", "신규",
    "특가", "무료", "혜택", "안내", "공지",
    "채용", "모집", "업데이트", "세일",
]


def _extract_keyword_badge(text: str) -> str:
    for kw in _BADGE_KEYWORDS:
        if kw in (text or ""):
            return kw
    return ""


def _truncate(value, meta) -> str:
    if not isinstance(meta, dict):
        return value
    max_len = meta.get("max_length")
    if max_len and isinstance(value, str) and len(value) > max_len:
        return value[: max_len - 1] + "…"
    return value
