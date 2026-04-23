"""
LayerTree → SVG 직렬화기 (A 방식)
=================================
Figma에 드래그&드롭하면 다음과 같이 들어갑니다:
  - Frame           → Group (최상위는 Frame 크기 기준)
  - TextLayer       → 편집 가능한 Text 레이어
  - RectLayer       → Rectangle (둥근 모서리 포함)
  - EllipseLayer    → Ellipse
  - ImageLayer      → Image 슬롯 (href 유지)

이후 B 방식(Figma 플러그인 JSON)을 추가할 때도
같은 LayerTree를 입력으로 받아 다른 포맷을 출력합니다.
이 파일은 수정하지 않습니다.
"""

from xml.sax.saxutils import escape
from .layer_tree import Frame, TextLayer, RectLayer, EllipseLayer, ImageLayer


# ───────────────────────────────────────
# 간단한 텍스트 줄바꿈 (한글/영문 혼용 근사치)
# ───────────────────────────────────────
def _approx_char_width(font_size: int) -> float:
    """한글 기준 폭 근사. Figma에서 자동 조정되니 정확할 필요는 없음."""
    return font_size * 0.95


def _wrap_text(text: str, width: float, font_size: int) -> list:
    """주어진 픽셀 너비에 맞춰 문자열을 여러 줄로 나눔."""
    if not text:
        return [""]
    char_w = _approx_char_width(font_size)
    max_chars = max(1, int(width / char_w))
    # 공백 단위 우선, 그게 안 되면 문자 단위 강제 자르기
    lines = []
    for paragraph in text.split("\n"):
        if len(paragraph) <= max_chars:
            lines.append(paragraph)
            continue
        words = paragraph.split(" ")
        current = ""
        for w in words:
            candidate = (current + " " + w).strip() if current else w
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                # 단어 자체가 너무 길면 강제 절단
                while len(w) > max_chars:
                    lines.append(w[:max_chars])
                    w = w[max_chars:]
                current = w
        if current:
            lines.append(current)
    return lines or [""]


# ───────────────────────────────────────
# 개별 레이어 직렬화
# ───────────────────────────────────────
def _emit_rect(r: RectLayer) -> str:
    if not r.fill and not r.stroke:
        return ""
    attrs = [
        f'id="{escape(r.name)}"',
        f'data-figma-name="{escape(r.name)}"',
        f'x="{r.x}"', f'y="{r.y}"',
        f'width="{r.w}"', f'height="{r.h}"',
    ]
    if r.corner_radius:
        attrs += [f'rx="{r.corner_radius}"', f'ry="{r.corner_radius}"']
    if r.fill:
        attrs.append(f'fill="{r.fill}"')
    else:
        attrs.append('fill="none"')
    if r.stroke:
        attrs += [f'stroke="{r.stroke}"', f'stroke-width="{r.stroke_width}"']
    if r.opacity != 1.0:
        attrs.append(f'opacity="{r.opacity}"')
    return f'<rect {" ".join(attrs)} />'


def _emit_ellipse(e: EllipseLayer) -> str:
    attrs = [
        f'id="{escape(e.name)}"',
        f'data-figma-name="{escape(e.name)}"',
        f'cx="{e.cx}"', f'cy="{e.cy}"',
        f'rx="{e.rx}"', f'ry="{e.ry}"',
    ]
    if e.fill:
        attrs.append(f'fill="{e.fill}"')
    if e.stroke:
        attrs += [f'stroke="{e.stroke}"', f'stroke-width="{e.stroke_width}"']
    if e.opacity != 1.0:
        attrs.append(f'opacity="{e.opacity}"')
    return f'<ellipse {" ".join(attrs)} />'


def _emit_text(t: TextLayer) -> str:
    # Figma가 SVG text를 편집 가능 text로 인식하게 하려면
    # <text> 내부에 <tspan>으로 줄을 나누는 게 호환성이 가장 좋음.
    lines = _wrap_text(t.text, t.w, t.font_size)
    line_h_px = t.font_size * t.line_height

    anchor = {"left": "start", "center": "middle", "right": "end"}[t.align]
    if t.align == "left":
        anchor_x = t.x
    elif t.align == "center":
        anchor_x = t.x + t.w / 2
    else:
        anchor_x = t.x + t.w

    # 첫 줄 baseline을 박스 상단 + font_size 위치로
    first_y = t.y + t.font_size

    style = (
        f'font-family:&quot;{escape(t.font_family)}&quot;, '
        f'&quot;Noto Sans KR&quot;, sans-serif;'
        f'font-size:{t.font_size}px;font-weight:{t.font_weight};'
        f'fill:{t.color};'
    )
    if t.letter_spacing:
        style += f'letter-spacing:{t.letter_spacing}px;'

    tspans = []
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else line_h_px
        tspans.append(
            f'<tspan x="{anchor_x}" dy="{dy}">{escape(line)}</tspan>'
        )

    attrs = [
        f'id="{escape(t.name)}"',
        f'data-figma-name="{escape(t.name)}"',
        f'x="{anchor_x}"', f'y="{first_y}"',
        f'text-anchor="{anchor}"',
        f'style="{style}"',
    ]
    if t.opacity != 1.0:
        attrs.append(f'opacity="{t.opacity}"')
    return f'<text {" ".join(attrs)}>{"".join(tspans)}</text>'


def _emit_image(i: ImageLayer) -> str:
    attrs = [
        f'id="{escape(i.name)}"',
        f'data-figma-name="{escape(i.name)}"',
        f'x="{i.x}"', f'y="{i.y}"',
        f'width="{i.w}"', f'height="{i.h}"',
        f'href="{escape(i.href)}"',
        f'preserveAspectRatio="xMidYMid slice"',
    ]
    if i.opacity != 1.0:
        attrs.append(f'opacity="{i.opacity}"')
    return f'<image {" ".join(attrs)} />'


def _emit_layer(layer) -> str:
    if isinstance(layer, TextLayer):
        return _emit_text(layer)
    if isinstance(layer, RectLayer):
        return _emit_rect(layer)
    if isinstance(layer, EllipseLayer):
        return _emit_ellipse(layer)
    if isinstance(layer, ImageLayer):
        return _emit_image(layer)
    if isinstance(layer, Frame):
        return _emit_group(layer)
    return ""


def _emit_group(frame: Frame) -> str:
    """중첩 Frame은 SVG <g>로. 최상위 Frame은 export_svg가 따로 처리."""
    inner = "\n  ".join(_emit_layer(c) for c in frame.children)
    transform = ""
    if frame.x or frame.y:
        transform = f' transform="translate({frame.x},{frame.y})"'
    return (
        f'<g id="{escape(frame.name)}" data-figma-name="{escape(frame.name)}"{transform}>\n'
        f'  {inner}\n'
        f'</g>'
    )


# ───────────────────────────────────────
# 공개 API
# ───────────────────────────────────────
# Google Fonts 한글 웹폰트 임포트 — SVG를 브라우저/Figma에서 열었을 때
# 한글이 □(두부) 로 깨지지 않도록 폰트 패밀리를 보장.
KOREAN_WEBFONT_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Noto+Sans+KR:wght@400;500;700;900&"
    "family=Black+Han+Sans&"
    "family=Gowun+Dodum&display=swap');"
    "text{font-family:'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',"
    "sans-serif;}"
)


def export_svg(frame: Frame) -> str:
    """Frame(LayerTree 루트)을 SVG 문자열로 변환."""
    # 루트 배경
    bg = (
        f'<rect id="{escape(frame.name)}_BG" '
        f'data-figma-name="Background" '
        f'x="0" y="0" width="{frame.width}" height="{frame.height}" '
        f'fill="{frame.bg_color}" />'
    )
    body = "\n  ".join(_emit_layer(c) for c in frame.children)
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{frame.width}" height="{frame.height}" '
        f'viewBox="0 0 {frame.width} {frame.height}">\n'
        f'  <title>{escape(frame.name)}</title>\n'
        f'  <defs><style type="text/css"><![CDATA[{KOREAN_WEBFONT_CSS}]]></style></defs>\n'
        f'  {bg}\n'
        f'  {body}\n'
        f'</svg>\n'
    )


def write_svg(frame: Frame, path: str) -> str:
    """SVG 파일로 저장하고 경로 반환."""
    svg = export_svg(frame)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path
