"""
카드뉴스 전용 Pillow 폴백 렌더러
================================
Playwright가 없을 때만 사용되는 보조 렌더러.
이 파일은 "카드뉴스 레이아웃"만 그립니다. 다른 콘텐츠 유형은
각자 자기 파일 (banner_pillow.py 등)을 만들거나, pillow 폴백을 비워둡니다.

규약: render(context, output_path, w, h) -> str | None
    반환값: 저장된 파일 경로. 렌더 불가능하면 None.
"""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from engine.config import FONT_CANDIDATES


def _find_korean_font() -> str:
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            return fp
    return None


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _wrap_text(draw, text: str, font, max_width: int) -> list:
    lines, current = [], ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def render(context: dict, output_path: str, w: int = 1080, h: int = 1080) -> str:
    """카드뉴스 1장을 Pillow로 그립니다. Pillow나 폰트 없으면 None."""
    if not HAS_PILLOW:
        return None
    font_path = _find_korean_font()
    if not font_path:
        return None

    bg = _hex_to_rgb(context["bg_color"])
    accent = _hex_to_rgb(context["accent_color"])
    title_c = _hex_to_rgb(context["title_color"])
    desc_c = _hex_to_rgb(context["desc_color"])

    f_badge = ImageFont.truetype(font_path, 28)
    f_title = ImageFont.truetype(font_path, 64)
    f_desc = ImageFont.truetype(font_path, 30)
    f_footer = ImageFont.truetype(font_path, 20)

    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # 장식 원 (카드뉴스 전용 장식)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([w-230, -120, w+120, 230], fill=(*accent, 38))
    od.ellipse([-80, h-230, 170, h+80], fill=(*accent, 25))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    max_tw = w - 160
    title_lines = _wrap_text(draw, context.get("title", ""), f_title, max_tw)
    desc_lines = _wrap_text(draw, context.get("description", ""), f_desc, max_tw)

    total_h = 52 + 40 + len(title_lines)*80 + 32 + 4 + 32 + len(desc_lines)*48
    y = (h - total_h) // 2

    badge = context.get("badge", "")
    if badge:
        bb = draw.textbbox((0, 0), badge, font=f_badge)
        bw = bb[2] - bb[0] + 60
        bx = (w - bw) // 2
        draw.rounded_rectangle([bx, y, bx+bw, y+52], radius=26, fill=accent)
        tx = bx + (bw - (bb[2]-bb[0])) // 2
        ty = y + (52 - (bb[3]-bb[1])) // 2 - 2
        draw.text((tx, ty), badge, fill=(255, 255, 255), font=f_badge)
        y += 92

    for line in title_lines:
        bb = draw.textbbox((0, 0), line, font=f_title)
        draw.text(((w - bb[2] + bb[0]) // 2, y), line, fill=title_c, font=f_title)
        y += 80
    y += 32

    dx = (w - 80) // 2
    draw.rectangle([dx, y, dx+80, y+4], fill=accent)
    y += 36

    for line in desc_lines:
        bb = draw.textbbox((0, 0), line, font=f_desc)
        draw.text(((w - bb[2] + bb[0]) // 2, y), line, fill=desc_c, font=f_desc)
        y += 48

    footer = context.get("footer", "")
    if footer:
        bb = draw.textbbox((0, 0), footer, font=f_footer)
        draw.text(((w - bb[2] + bb[0]) // 2, h-60), footer, fill=desc_c, font=f_footer)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    return os.path.abspath(output_path)
