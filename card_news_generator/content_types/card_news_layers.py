"""
카드뉴스 Layer Builder
======================
context(color/font/text 딕셔너리) + (width, height)를 받아
편집 가능한 레이어 트리를 돌려줍니다.

이 파일은 Figma 레이어 구조만 신경 씁니다:
  - SVG로 나갈지, Figma 플러그인 JSON으로 나갈지는 engine/exporter가 결정
  - 따라서 같은 레이아웃을 두 번 만들 필요가 없음
"""

from engine.layer_tree import (
    Frame, TextLayer, RectLayer, EllipseLayer,
    ALIGN_CENTER,
)


def _pick(ctx: dict, *keys, default=""):
    for k in keys:
        v = ctx.get(k)
        if v:
            return v
    return default


def build(context: dict, width: int, height: int) -> Frame:
    """카드뉴스(정사각/세로형 공통) 레이어 트리 생성."""
    # ─ 스타일 슬롯 ─
    bg_color = _pick(context, "bg_color", default="#FFFFFF")
    accent = _pick(context, "accent_color", default="#FF6B35")
    title_color = _pick(context, "title_color", default="#212121")
    desc_color = _pick(context, "desc_color", default="#616161")
    font_family = _pick(context, "primary_font", default="Noto Sans KR")

    # ─ 카피 슬롯 ─
    badge = _pick(context, "badge", default="EVENT")
    title = _pick(context, "title", default="제목을 입력하세요")
    description = _pick(context, "description", default="")
    footer = _pick(context, "footer", default="")

    # 세로형(1080x1350)과 정사각(1080x1080)을 비율로 동일하게 처리
    is_portrait = height >= int(width * 1.2)
    scale = 1.0 if width == 1080 and height == 1080 else (
        height / 1080 if is_portrait else 1.0
    )

    root = Frame(
        name=f"CardNews_{width}x{height}",
        width=width,
        height=height,
        bg_color=bg_color,
    )

    # ─ 장식 원 (우상단) ─
    root.add(EllipseLayer(
        name="Decoration/Top-Right",
        cx=width - 120 * scale + 175 * scale,
        cy=-120 * scale + 175 * scale,
        rx=175 * scale, ry=175 * scale,
        fill=accent, opacity=0.15,
    ))

    # ─ 장식 원 (좌하단) ─
    root.add(EllipseLayer(
        name="Decoration/Bottom-Left",
        cx=-80 * scale + 125 * scale,
        cy=height - 80 * scale + 125 * scale,
        rx=125 * scale, ry=125 * scale,
        fill=accent, opacity=0.10,
    ))

    # ─ 레이아웃 기준값 ─
    center_x = width / 2
    badge_font = int(28 * scale)
    title_font = int(72 * scale) if not is_portrait else int(86 * (height / 1350))
    desc_font = int(32 * scale) if not is_portrait else int(36 * (height / 1350))
    footer_font = int(22 * scale)

    # 수직 배치를 중앙 정렬처럼 맞추기 위해 블록 높이를 합산
    badge_h = 60 * scale
    badge_w = max(200, len(badge) * badge_font + 72)
    gap_after_badge = 40 * scale
    title_h = title_font * 1.3 * max(1, _estimate_lines(title, width - 160, title_font))
    gap_after_title = 32 * scale
    divider_h = 4
    gap_after_divider = 32 * scale
    desc_h = desc_font * 1.6 * max(1, _estimate_lines(description, 800, desc_font))

    total_h = badge_h + gap_after_badge + title_h + gap_after_title + divider_h + gap_after_divider + desc_h
    cursor_y = (height - total_h) / 2

    # ─ 뱃지 (둥근 사각형 + 중앙 텍스트) ─
    root.add(RectLayer(
        name="Badge/Background",
        x=center_x - badge_w / 2,
        y=cursor_y,
        w=badge_w,
        h=badge_h,
        fill=accent,
        corner_radius=badge_h / 2,
    ))
    root.add(TextLayer(
        name="Badge/Text",
        x=center_x - badge_w / 2,
        y=cursor_y + (badge_h - badge_font) / 2 - badge_font * 0.1,
        w=badge_w,
        h=badge_h,
        text=badge,
        font_family=font_family,
        font_size=badge_font,
        font_weight=700,
        color="#FFFFFF",
        align=ALIGN_CENTER,
        letter_spacing=2.0,
    ))
    cursor_y += badge_h + gap_after_badge

    # ─ 타이틀 ─
    root.add(TextLayer(
        name="Title",
        x=80 * scale,
        y=cursor_y,
        w=width - 160 * scale,
        h=title_h,
        text=title,
        font_family=font_family,
        font_size=title_font,
        font_weight=900,
        color=title_color,
        align=ALIGN_CENTER,
        line_height=1.3,
    ))
    cursor_y += title_h + gap_after_title

    # ─ 디바이더 ─
    root.add(RectLayer(
        name="Divider",
        x=center_x - 40,
        y=cursor_y,
        w=80,
        h=divider_h,
        fill=accent,
    ))
    cursor_y += divider_h + gap_after_divider

    # ─ 설명 ─
    if description:
        root.add(TextLayer(
            name="Description",
            x=(width - 800) / 2,
            y=cursor_y,
            w=800,
            h=desc_h,
            text=description,
            font_family=font_family,
            font_size=desc_font,
            font_weight=400,
            color=desc_color,
            align=ALIGN_CENTER,
            line_height=1.6,
        ))

    # ─ 푸터 (하단 고정) ─
    if footer:
        root.add(TextLayer(
            name="Footer",
            x=0,
            y=height - 50 * scale - footer_font,
            w=width,
            h=footer_font * 1.6,
            text=footer,
            font_family=font_family,
            font_size=footer_font,
            font_weight=400,
            color=desc_color,
            align=ALIGN_CENTER,
            opacity=0.6,
        ))

    return root


def _estimate_lines(text: str, width: float, font_size: int) -> int:
    """텍스트가 해당 폭 안에서 몇 줄이 될지 어림."""
    if not text:
        return 0
    char_w = font_size * 0.95
    max_chars = max(1, int(width / char_w))
    return max(1, -(-len(text) // max_chars))  # ceil
