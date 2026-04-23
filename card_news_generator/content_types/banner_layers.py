"""
배너 Layer Builder
==================
가로형 프로모션 배너용 레이어 트리.
좌측 카피 블록 + 우측 CTA 버튼 + 배경 장식 태그라인.
"""

from engine.layer_tree import (
    Frame, TextLayer, RectLayer,
    ALIGN_LEFT, ALIGN_CENTER,
)


def build(context: dict, width: int, height: int) -> Frame:
    bg_color = context.get("bg_color") or "#FFFFFF"
    accent = context.get("accent_color") or "#FF6B35"
    title_color = context.get("title_color") or "#212121"
    desc_color = context.get("desc_color") or "#616161"
    font_family = context.get("primary_font") or "Noto Sans KR"

    title = context.get("title") or "메인 헤드라인"
    subtitle = context.get("subtitle") or context.get("description") or ""
    cta_text = context.get("cta_text") or "자세히 보기"
    bg_tagline = context.get("bg_tagline") or "PROMOTION"

    root = Frame(
        name=f"Banner_{width}x{height}",
        width=width, height=height, bg_color=bg_color,
    )

    # 배경 거대 장식 텍스트 (옅게)
    root.add(TextLayer(
        name="Decoration/Tagline",
        x=0, y=height * 0.05,
        w=width, h=height * 0.9,
        text=bg_tagline,
        font_family=font_family,
        font_size=int(height * 0.85),
        font_weight=900,
        color=accent,
        align=ALIGN_CENTER,
        opacity=0.08,
    ))

    # 좌측 텍스트 블록
    pad_x = max(40, int(width * 0.05))
    title_size = max(28, int(height * 0.22))
    sub_size = max(18, int(height * 0.09))

    root.add(TextLayer(
        name="Title",
        x=pad_x,
        y=height * 0.22,
        w=width * 0.6,
        h=title_size * 1.3,
        text=title,
        font_family=font_family,
        font_size=title_size,
        font_weight=900,
        color=title_color,
        align=ALIGN_LEFT,
        line_height=1.2,
    ))

    if subtitle:
        root.add(TextLayer(
            name="Subtitle",
            x=pad_x,
            y=height * 0.55,
            w=width * 0.6,
            h=sub_size * 1.5,
            text=subtitle,
            font_family=font_family,
            font_size=sub_size,
            font_weight=400,
            color=desc_color,
            align=ALIGN_LEFT,
            line_height=1.5,
        ))

    # 우측 CTA 버튼
    btn_w = max(160, len(cta_text) * sub_size + 80)
    btn_h = max(50, int(height * 0.22))
    btn_x = width - pad_x - btn_w
    btn_y = (height - btn_h) / 2

    root.add(RectLayer(
        name="CTA/Background",
        x=btn_x, y=btn_y, w=btn_w, h=btn_h,
        fill=accent, corner_radius=btn_h / 2,
    ))
    root.add(TextLayer(
        name="CTA/Text",
        x=btn_x,
        y=btn_y + (btn_h - sub_size) / 2 - sub_size * 0.1,
        w=btn_w, h=btn_h,
        text=cta_text,
        font_family=font_family,
        font_size=sub_size,
        font_weight=700,
        color="#FFFFFF",
        align=ALIGN_CENTER,
    ))

    return root
