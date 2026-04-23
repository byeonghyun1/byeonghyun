"""
카피 생성 모듈 (콘텐츠 유형 무관)
===================================
DesignRequest를 받아서 렌더링에 필요한 context dict를 생성합니다.

이 파일은 "카드뉴스 4필드 고정"이 아니라, content_types 레지스트리가 선언한
copy_fields를 그대로 따라갑니다. 배너/포스터/상세페이지가 각자 다른 필드를
쓰더라도 이 파일은 수정할 필요 없습니다.

copy_mode 지원:
  - manual : 직접 입력한 카피 그대로 사용
  - ai     : AI가 처음부터 생성 (copy_fields 목록을 AI에게 전달)
  - refine : AI가 입력된 카피를 다듬음 (원본 필드만 대상으로)
"""

import json
import re
from .schema import DesignRequest
from .config import get_mood_colors, DEFAULT_TYPOGRAPHY, DEFAULT_COLORS
from content_types import get_config
from brands import resolve_brand_for_content


def generate_context(request: DesignRequest) -> dict:
    """
    DesignRequest + content_type 설정 → 템플릿 렌더링용 context 생성.
    """
    config = get_config(request.content_type)
    copy_fields = _normalize_copy_fields(config.get("copy_fields", {}))

    # copy_mode에 따라 분기
    #   api_key가 있으면 실제 AI 호출, 없으면 규칙 기반 더미로 폴백
    #   (프로토타입 단계에서 외부 API 없이도 ai/refine 모드 동작 확인용)
    from .dummy_copy import generate_dummy, refine_dummy

    if request.copy_mode == "ai":
        if request.api_key:
            copy = _generate_with_ai(request, config, copy_fields)
            if copy is None:
                copy = generate_dummy(request, copy_fields)
        else:
            copy = generate_dummy(request, copy_fields)
    elif request.copy_mode == "refine":
        if request.api_key:
            copy = _refine_with_ai(request, config, copy_fields)
            if copy is None:
                copy = refine_dummy(request, copy_fields)
        else:
            copy = refine_dummy(request, copy_fields)
    else:
        copy = _build_manual_copy(request, copy_fields)

    # 브랜드 × 콘텐츠 유형 결합 → 스타일 세트(colors/typography/logo/...)
    style = _resolve_style(request)
    return {**copy, **style}


# ============================================================
# copy_fields 정규화 (list / dict 두 형태 모두 허용)
# ============================================================
def _normalize_copy_fields(raw) -> dict:
    """
    copy_fields가 list(["title", "desc"])이든
    dict({"title": {"role": "..."}, ...})이든
    { field_name: meta_dict } 형태로 통일합니다.
    """
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {name: {} for name in raw}
    return {}


# ============================================================
# copy_mode별 카피 생성
# ============================================================
def _build_manual_copy(request: DesignRequest, copy_fields: dict) -> dict:
    """
    DesignRequest의 값을 copy_fields 선언에 맞춰 채웁니다.

    각 필드는 메타데이터로 폴백 규칙을 선언할 수 있습니다 (콘텐츠 유형 파일에 선언):
      - fallback_field    : 해당 필드가 비면 다른 request 속성 값을 사용
      - auto_extract_from : 해당 필드가 비면 다른 속성에서 keywords를 찾아 추출
      - keywords          : auto_extract_from과 함께 사용
      - fallback          : 최후 폴백 문자열
    """
    copy = {}
    for field_name, meta in copy_fields.items():
        # 1순위: DesignRequest에 동일 이름의 속성이 있으면 그 값 (title/description 등 공용 슬롯)
        # 2순위: copy_inputs dict에 있으면 그 값 (subtitle/cta_text 같은 유형 고유 필드)
        value = getattr(request, field_name, "") or ""
        if not value:
            value = (request.copy_inputs or {}).get(field_name, "") or ""

        # 폴백 1: 다른 필드 값 사용
        if not value and isinstance(meta, dict):
            fb_field = meta.get("fallback_field")
            if fb_field:
                value = getattr(request, fb_field, "") or ""

        # 폴백 2: 다른 필드에서 키워드 자동 추출
        if not value and isinstance(meta, dict):
            extract_from = meta.get("auto_extract_from")
            keywords = meta.get("keywords", [])
            if extract_from and keywords:
                source = getattr(request, extract_from, "") or ""
                for kw in keywords:
                    if kw in source:
                        value = kw
                        break

        # 폴백 3: 고정 문자열
        if not value and isinstance(meta, dict):
            value = meta.get("fallback", "") or ""

        copy[field_name] = value

    # 공통 폴백: title이 비면 topic 사용 (콘텐츠 유형 불문 자연스러운 기본값)
    if "title" in copy and not copy["title"]:
        copy["title"] = request.topic
    # footer가 비면 cta
    if "footer" in copy and not copy["footer"]:
        copy["footer"] = request.cta

    return copy


def _generate_with_ai(request: DesignRequest, config: dict, copy_fields: dict) -> dict:
    """
    AI가 copy_fields 목록대로 처음부터 카피를 생성합니다.
    content_type이 선언한 필드만 요청하므로, 카드뉴스/배너/상세페이지 모두 적용됩니다.
    """
    try:
        prompt = _build_ai_prompt(request, config, copy_fields, mode="generate")
        result = _call_ai(request.api_key, prompt)
        if not result:
            return None
        # AI가 copy_fields에 없는 키를 반환해도 무시, 누락 필드는 입력값/빈 값으로 채움
        filtered = {k: result.get(k, getattr(request, k, "")) for k in copy_fields.keys()}
        return filtered
    except Exception as e:
        print(f"  [AI 카피 생성 실패, 로컬 폴백] {e}")
        return None


def _refine_with_ai(request: DesignRequest, config: dict, copy_fields: dict) -> dict:
    """
    입력된 카피를 AI가 자연스럽게 다듬습니다.
    copy_fields에 선언된 필드만 대상으로 합니다.
    """
    try:
        original = {
            name: (getattr(request, name, "") or "")
            for name in copy_fields.keys()
        }
        prompt = _build_ai_prompt(request, config, copy_fields, mode="refine", original=original)
        result = _call_ai(request.api_key, prompt)
        if not result:
            return None
        return {k: result.get(k, original.get(k, "")) for k in copy_fields.keys()}
    except Exception as e:
        print(f"  [AI 카피 다듬기 실패, 로컬 폴백] {e}")
        return None


# ============================================================
# AI 프롬프트 빌더
# ============================================================
def _build_ai_prompt(
    request: DesignRequest,
    config: dict,
    copy_fields: dict,
    mode: str,
    original: dict = None,
) -> str:
    """콘텐츠 유형의 copy_fields + 브랜드 톤을 조합해 프롬프트 생성."""
    ct_name = config.get("name", request.content_type)

    # 브랜드 톤/타겟 가져오기 (있으면 프롬프트에 주입)
    brand = resolve_brand_for_content(request.brand, request.content_type)
    brand_line = ""
    if brand:
        brand_line = (
            f"브랜드: {brand.get('name', '')}\n"
            f"브랜드 톤: {brand.get('tone', '')}\n"
            f"브랜드 주 타겟: {brand.get('target', '')}\n"
        )

    # 필드 설명 라인 생성
    field_lines = []
    json_keys = []
    for name, meta in copy_fields.items():
        role = meta.get("role", "")
        max_len = meta.get("max_length")
        hint = f" ({role}"
        if max_len:
            hint += f", {max_len}자 이내"
        hint += ")"
        field_lines.append(f"  - {name}{hint}")
        json_keys.append(f'"{name}": "..."')

    fields_text = "\n".join(field_lines)
    json_template = "{" + ", ".join(json_keys) + "}"

    if mode == "refine":
        original_json = json.dumps(original or {}, ensure_ascii=False)
        return (
            f"{ct_name} 카피를 자연스럽고 매력적으로 다듬어줘. "
            f"의미는 유지하되 표현만 보완해줘.\n\n"
            f"{brand_line}"
            f"타겟: {request.target}\n"
            f"분위기: {request.mood}\n"
            f"목적: {request.purpose}\n\n"
            f"원본 카피:\n{original_json}\n\n"
            f"아래 필드를 모두 포함해서 동일한 JSON 구조로만 응답해줘 (코드블록 없이):\n"
            f"{fields_text}\n\n"
            f"응답 형식: {json_template}"
        )

    # generate 모드
    return (
        f"{ct_name}용 카피를 만들어줘.\n\n"
        f"{brand_line}"
        f"주제: {request.topic}\n"
        f"타겟: {request.target}\n"
        f"분위기: {request.mood}\n"
        f"목적: {request.purpose}\n"
        f"CTA: {request.cta or '(없음)'}\n\n"
        f"아래 필드를 모두 채워서 JSON으로만 응답해줘 (코드블록 없이):\n"
        f"{fields_text}\n\n"
        f"응답 형식: {json_template}"
    )


def _call_ai(api_key: str, prompt: str) -> dict:
    """Anthropic API 호출. 실패 시 None."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  [AI 호출 실패] {e}")
    return None


# ============================================================
# 스타일 결정 (브랜드 × 콘텐츠 유형 × 분위기의 조합)
# ============================================================
def _resolve_style(request: DesignRequest) -> dict:
    """
    최종 스타일(colors/typography/logo/brand_meta)을 결정합니다.

    우선순위:
      1. 사용자 오버라이드 (request.bg_color 등)
      2. 브랜드 (content_type별 override 반영)
      3. 분위기 (mood)
      4. 시스템 기본값

    반환 context에는 색상 뿐 아니라 typography/logo/brand 메타도 포함되어
    템플릿에서 {{ primary_font }}, {{ logo }}, {{ tone }} 등으로 사용 가능.
    """
    # 1) 브랜드 × 콘텐츠 유형 결합
    brand = resolve_brand_for_content(request.brand, request.content_type)

    # 2) 색상 세트 결정
    if request.bg_color and request.accent_color:
        colors = {
            "bg_color": request.bg_color,
            "accent_color": request.accent_color,
            "title_color": request.title_color or "#2D2D2D",
            "desc_color": request.desc_color or "#555555",
        }
    elif brand.get("colors"):
        colors = {**DEFAULT_COLORS, **brand["colors"]}
    elif request.mood:
        colors = get_mood_colors(request.mood)
    else:
        colors = DEFAULT_COLORS.copy()

    # 3) 타이포그래피 (브랜드 > 기본)
    typography = {**DEFAULT_TYPOGRAPHY, **brand.get("typography", {})}

    # 4) 로고 (브랜드에만 존재)
    logo = brand.get("logo", {}) or {}

    # 5) 브랜드 메타 (AI 카피 생성 시 톤·타겟 주입에 유용)
    brand_meta = {
        "brand_name": brand.get("name", ""),
        "brand_key": brand.get("name_en", request.brand),
        "brand_tone": brand.get("tone", ""),
        "brand_target": brand.get("target", ""),
    }

    return {
        **colors,
        **typography,
        "logo_primary": logo.get("primary", ""),
        "logo_mono": logo.get("mono", ""),
        "logo_icon": logo.get("icon", ""),
        **brand_meta,
    }
