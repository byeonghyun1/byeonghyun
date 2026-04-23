"""
포스터 Layer Builder
====================
A4 세로 포스터 — 상단 라벨, 거대 타이틀, 본문, 정보 블록(일시/장소), 푸터.
"""

from engine.layer_tree import (
    Frame, TextLayer, RectLayer, EllipseLayer,
    ALIGN_LEFT, ALIGN_CENTER,
)


def build(context: dict, width: int, height: int) -> Frame:
    bg_color = context.get("bg_color") or "#FFFFFF"
    accent = context.get("accent_color") or "#FF6B35"
    title_color = context.get("title_color") or "#212121"
    desc_color = context.get("desc_color") or "#616161"
    font_family = context.get("primary_font") or "Noto Sans KR"

    badge = context.get("badge") or "POSTER"
    title = context.get("title") or "포스터 타이틀"
    subtitle = context.get("subtitle") or context.get("description") or ""
    date_range = context.get("date_range") or ""
    place = context.get("place") or ""
    footer = context.get("footer") or ""

    pad = int(width * 0.08)
    root = Frame(
        name=f"Poster_{width}x{height}",
        width=width, height=height, bg_color=bg_color,
    )

    # 우상단 장식 큰 원
    root.add(EllipseLayer(
        name="Decoration/Top-Right-Circle",
        cx=width * 0.95, cy=-height * 0.05,
        rx=width * 0.42, ry=width * 0.42,
        fill=accent, opacity=0.18,
    ))

    # 상단 라벨
    label_size = max(12, int(width * 0.035))
    root.add(TextLayer(
        name="Header/Label",
        x=pad, y=pad,
        w=width - pad * 2, h=label_size * 1.5,
        text=badge.upper(),
        font_family=font_family,
        font_size=label_size,
        font_weight=700,
        color=accent,
        align=ALIGN_LEFT,
        letter_spacing=label_size * 0.3,
    ))

    # 메인 타이틀
    title_size = max(40, int(width * 0.13))
    title_y = height * 0.28
    title_h = title_size * 1.2 * 2  # 최대 2줄 가정
    root.add(TextLayer(
        name="Title",
        x=pad, y=title_y,
        w=width - pad * 2, h=title_h,
        text=title,
        font_family=font_family,
        font_size=title_size,
        font_weight=900,
        color=title_color,
        align=ALIGN_LEFT,
        line_height=1.15,
    ))

    # 서브타이틀
    sub_size = max(16, int(width * 0.045))
    if subtitle:
        root.add(TextLayer(
            name="Subtitle",
            x=pad, y=title_y + title_h + sub_size * 0.5,
            w=width - pad * 2, h=sub_size * 1.6 * 2,
            text=subtitle,
            font_family=font_family,
            font_size=sub_size,
            font_weight=400,
            color=desc_color,
            align=ALIGN_LEFT,
            line_height=1.5,
        ))

    # 정보 블록 — 구분선 + 일시/장소
    info_y = height * 0.72
    info_size = max(14, int(width * 0.038))

    root.add(RectLayer(
        name="Info/Divider",
        x=pad, y=info_y,
        w=width - pad * 2, h=3,
        fill=accent,
    ))

    cursor_y = info_y + info_size * 1.2
    if date_range:
        root.add(TextLayer(
            name="Info/DateRange",
            x=pad, y=cursor_y,
            w=width - pad * 2, h=info_size * 1.5,
            text=f"일시   {date_range}",
            font_family=font_family,
            font_size=info_size,
            font_weight=500,
            color=desc_color,
            align=ALIGN_LEFT,
        ))
        cursor_y += info_size * 1.7

    if place:
        root.add(TextLayer(
            name="Info/Place",
            x=pad, y=cursor_y,
            w=width - pad * 2, h=info_size * 1.5,
            text=f"장소   {place}",
            font_family=font_family,
            font_size=info_size,
            font_weight=500,
            color=desc_color,
            align=ALIGN_LEFT,
        ))
        cursor_y += info_size * 1.7

    # 푸터
    if footer:
        footer_size = max(12, int(width * 0.028))
        root.add(TextLayer(
            name="Footer",
            x=pad,
            y=height - pad - footer_size * 1.5,
            w=width - pad * 2, h=footer_size * 1.6,
            text=footer,
            font_family=font_family,
            font_size=footer_size,
            font_weight=400,
            color=desc_color,
            align=ALIGN_LEFT,
            opacity=0.7,
        ))

    return root
