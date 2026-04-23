"""
Layer Tree (중간 표현)
======================
콘텐츠 유형이 "어떤 레이어들이 어디에 있는지"를 선언하는 중립 자료구조.

이 LayerTree 하나를 만들어 두면:
  - 지금은 svg_exporter가 SVG로 직렬화 (A 방식)
  - 나중에 figma_json_exporter가 Figma 플러그인 JSON으로 직렬화 (B 방식)
  - Pillow/Playwright 경로와도 공존 가능

즉, 출력 방식이 늘어나도 content_types/*_layers.py는 건드리지 않습니다.

레이어 종류는 Figma 기본 레이어 타입에 맞춰 최소셋만 노출:
  Frame    — Figma Frame
  Text     — Figma Text
  Rect     — Figma Rectangle (corner_radius로 둥근 사각형/버튼/뱃지까지 커버)
  Ellipse  — Figma Ellipse (장식 원)
  Image    — Figma Image (추후 사진 교체용 슬롯)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union


# ───────────────────────────────────────
# 텍스트 정렬 / 폰트 스펙
# ───────────────────────────────────────
ALIGN_LEFT = "left"
ALIGN_CENTER = "center"
ALIGN_RIGHT = "right"


@dataclass
class TextLayer:
    """수정 가능한 텍스트 레이어. Figma Text 노드로 1:1 매핑."""
    name: str
    x: float
    y: float
    w: float
    h: float
    text: str
    font_family: str = "Noto Sans KR"
    font_size: int = 32
    font_weight: int = 400
    color: str = "#111111"
    align: str = ALIGN_LEFT            # left | center | right
    line_height: float = 1.4           # multiplier
    letter_spacing: float = 0.0
    opacity: float = 1.0


@dataclass
class RectLayer:
    """사각형 / 둥근 사각형 / 뱃지 / 버튼 / 디바이더."""
    name: str
    x: float
    y: float
    w: float
    h: float
    fill: str = ""                      # "#RRGGBB" or "" (투명)
    stroke: str = ""
    stroke_width: float = 0
    corner_radius: float = 0
    opacity: float = 1.0


@dataclass
class EllipseLayer:
    """원/타원. 장식용 원도 여기로."""
    name: str
    cx: float
    cy: float
    rx: float
    ry: float
    fill: str = ""
    stroke: str = ""
    stroke_width: float = 0
    opacity: float = 1.0


@dataclass
class ImageLayer:
    """이미지 슬롯. 지금은 placeholder 경로만 담고, Figma에서 교체."""
    name: str
    x: float
    y: float
    w: float
    h: float
    href: str = ""                      # 파일 경로 or data URL
    opacity: float = 1.0


Layer = Union[TextLayer, RectLayer, EllipseLayer, ImageLayer, "Frame"]


@dataclass
class Frame:
    """
    Figma Frame (또는 그룹) 대응. 모든 레이어 트리의 루트.
    Frame 안에 또 다른 Frame을 중첩할 수 있어서 그룹 계층도 표현 가능.
    """
    name: str
    width: float
    height: float
    bg_color: str = "#FFFFFF"
    x: float = 0
    y: float = 0
    opacity: float = 1.0
    children: List[Layer] = field(default_factory=list)

    def add(self, layer: Layer) -> Layer:
        self.children.append(layer)
        return layer
