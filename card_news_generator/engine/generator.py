"""
콘텐츠 생성 엔진 (콘텐츠 유형 무관 오케스트레이터)
====================================================
DesignRequest를 받아 content_types 레지스트리를 통해
카피 생성 → 렌더링 → DesignResult 반환까지의 전체 파이프라인을 관리합니다.

이 파일은 "카드뉴스"라는 단어를 하나도 모릅니다.
새 콘텐츠 유형(배너/포스터/상세페이지)이 추가되어도 수정하지 않습니다.
"""

import os
from datetime import datetime
from pathlib import Path

from .schema import DesignRequest, DesignResult
from .copy_writer import generate_context
from .renderer import render
from .config import DEFAULT_OUTPUT_DIR
from content_types import get_config
from brands import resolve_brand_for_content


# 포맷별 확장자
FORMAT_EXT = {
    "png": ".png",
    "pdf": ".pdf",
    "html": ".html",
    "svg": ".svg",
    "figma_json": ".figma.json",  # B 방식 자리 확보
}


def _load_callable(dotted_path: str):
    """'pkg.mod.func' 문자열을 실제 호출 가능한 함수로 변환."""
    if not dotted_path:
        return None
    mod_path, _, func_name = dotted_path.rpartition(".")
    if not mod_path:
        return None
    import importlib
    module = importlib.import_module(mod_path)
    return getattr(module, func_name, None)


class DesignEngine:
    """
    콘텐츠 디자인 생성 엔진 (공통 파이프라인).

    파이프라인:
        1. content_type 설정 조회
        2. 필수 필드 검사 (content_type이 선언)
        3. 크기/포맷/템플릿 결정 (오버라이드 > 콘텐츠 유형 기본값)
        4. 출력 경로 결정 (포맷에 맞는 확장자)
        5. 카피 처리 (copy_mode에 따라, copy_fields 동적 사용)
        6. 렌더링 (Playwright → 콘텐츠별 Pillow 폴백 → HTML)
        7. DesignResult 반환
    """

    def __init__(self, output_dir: str = ""):
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    def generate(self, request: DesignRequest) -> DesignResult:
        try:
            # 1) content_type 설정 조회
            config = get_config(request.content_type)

            # 2) 필수 필드 검사
            missing = self._check_required(request, config)
            if missing:
                return DesignResult(
                    success=False,
                    content_type=request.content_type,
                    error=f"필수 항목 누락: {', '.join(missing)}",
                )

            # 3) 사이즈 변형 해석 (규격 축)
            #    content_type 설정이 'sizes' dict를 가지면 variant 선택,
            #    없으면 기존 default_size 튜플 사용 (하위 호환)
            size_cfg = self._resolve_size(request, config)

            # 4) 크기 / 포맷 결정
            width = request.width or size_cfg["width"]
            height = request.height or size_cfg["height"]
            output_format = request.output_format or config.get("default_format", "png")
            pillow_fallback = config.get("pillow_renderer", "")

            # 5) 템플릿 선택 우선순위:
            #   1. request.template (사용자 지정)
            #   2. 브랜드의 content_type별 override 템플릿 (브랜드 전용 레이아웃)
            #   3. 사이즈 변형의 템플릿 (규격별 레이아웃)
            #   4. content_type 기본 템플릿 (공용)
            brand_cfg = resolve_brand_for_content(request.brand, request.content_type)
            template_name = (
                request.template
                or brand_cfg.get("template")
                or size_cfg.get("template")
                or config.get("template")
            )

            # 4) 출력 경로 결정
            output_path, html_path = self._resolve_paths(request, output_format)

            # 5) 카피 → context
            context = generate_context(request)

            # 6) 렌더링 — 포맷에 따라 분기
            #    "both" 는 PNG + SVG 동시 생성 (프로토타입 디자이너 검토용)
            extra_paths = {}
            if output_format == "both":
                # PNG (확인용)
                png_path, _ = self._resolve_paths(request, "png")
                result_path, renderer_used = render(
                    context=context,
                    output_path=png_path,
                    html_path=html_path,
                    template_name=template_name,
                    w=width, h=height,
                    output_format="png",
                    pillow_fallback=pillow_fallback,
                )
                extra_paths["png_path"] = result_path
                # SVG (편집용)
                svg_path, _ = self._resolve_paths(request, "svg")
                svg_result, _ = self._render_layer_output(
                    context=context, output_path=svg_path,
                    width=width, height=height,
                    output_format="svg", config=config,
                )
                extra_paths["svg_path"] = svg_result
                renderer_used = "both"
                result_path = svg_result
            elif output_format in ("svg", "figma_json"):
                # 레이어 기반 출력 (편집 가능한 디자인 파일)
                result_path, renderer_used = self._render_layer_output(
                    context=context,
                    output_path=output_path,
                    width=width,
                    height=height,
                    output_format=output_format,
                    config=config,
                )
            else:
                # 기존 이미지/HTML 렌더링 경로
                result_path, renderer_used = render(
                    context=context,
                    output_path=output_path,
                    html_path=html_path,
                    template_name=template_name,
                    w=width,
                    h=height,
                    output_format=output_format,
                    pillow_fallback=pillow_fallback,
                )

            return DesignResult(
                success=True,
                output_path=result_path,
                html_path=os.path.abspath(html_path),
                renderer_used=renderer_used,
                content_type=request.content_type,
                context={**context, **extra_paths},
            )

        except Exception as e:
            return DesignResult(
                success=False,
                content_type=request.content_type,
                error=str(e),
            )

    def generate_batch(self, requests: list) -> list:
        """여러 콘텐츠를 일괄 생성합니다 (Google Sheets 연동 등)."""
        return [self.generate(req) for req in requests]

    # ─────────────────────────────────────────
    # 내부 보조 메서드
    # ─────────────────────────────────────────
    def _check_required(self, request: DesignRequest, config: dict) -> list:
        """
        필수 필드 확인. required_fields는 두 가지 형태 지원:
          - list : ["topic", "target"]
          - copy_fields dict 내의 {"required": True} 항목
        """
        missing = []

        # 1) 최상위 required_fields
        for field_name in config.get("required_fields", []):
            if not getattr(request, field_name, ""):
                missing.append(field_name)

        # 2) copy_fields에서 required=True로 선언된 필드 (AI 생성 시에는 제외)
        if request.copy_mode == "manual":
            raw_fields = config.get("copy_fields", {})
            if isinstance(raw_fields, dict):
                for name, meta in raw_fields.items():
                    if isinstance(meta, dict) and meta.get("required"):
                        # title이 비어있어도 topic이 있으면 폴백 가능하므로 예외 처리
                        value = getattr(request, name, "")
                        if name == "title" and not value:
                            value = request.topic
                        if not value:
                            missing.append(name)
        return missing

    def _resolve_size(self, request: DesignRequest, config: dict) -> dict:
        """
        사이즈 변형 해석. 두 가지 선언 방식 모두 지원:

          방식 A (신규): config["sizes"] = { "square": {...}, "portrait": {...} }
                       config["default_size"] = "square"

          방식 B (기존): config["default_size"] = (1080, 1080)
                       config["template"] = "card_news/basic.html"
        """
        sizes = config.get("sizes")
        if isinstance(sizes, dict) and sizes:
            variant_key = request.size or config.get("default_size", "")
            if variant_key and variant_key in sizes:
                return sizes[variant_key]
            # variant 키가 없으면 첫 번째 항목 폴백
            return next(iter(sizes.values()))

        # 구형 구조 폴백
        default_size = config.get("default_size", (1080, 1080))
        if isinstance(default_size, tuple):
            return {
                "width": default_size[0],
                "height": default_size[1],
                "template": config.get("template", ""),
            }
        return {"width": 1080, "height": 1080, "template": config.get("template", "")}

    def _render_layer_output(self, context, output_path, width, height,
                              output_format, config):
        """
        레이어 기반 출력 경로.
          1. content_type이 선언한 layer_builder로 LayerTree 생성
          2. output_format에 맞는 exporter로 직렬화
             - "svg"        → SVG 파일 (지금)
             - "figma_json" → Figma 플러그인 JSON (추후)

        exporter가 늘어도 이 함수의 분기만 한 줄씩 늘고,
        content_types/*_layers.py와 LayerTree는 그대로 재사용됨.
        """
        builder_path = config.get("layer_builder", "")
        if not builder_path:
            raise ValueError(
                f"이 content_type은 layer_builder가 없어 '{output_format}' 출력을 지원하지 않습니다. "
                f"content_types/*_layers.py를 추가하고 설정의 layer_builder에 등록하세요."
            )

        build = _load_callable(builder_path)
        if build is None:
            raise ImportError(f"layer_builder 로드 실패: {builder_path}")

        frame = build(context, width, height)

        if output_format == "svg":
            from .svg_exporter import write_svg
            write_svg(frame, output_path)
            return output_path, "svg"

        if output_format == "figma_json":
            # B 방식 — 아직 구현 전. exporter만 추가하면 됨.
            raise NotImplementedError(
                "figma_json exporter는 아직 구현되지 않았습니다. "
                "engine/figma_json_exporter.py를 추가하고 여기서 호출하세요."
            )

        raise ValueError(f"알 수 없는 레이어 포맷: {output_format}")

    def _resolve_paths(self, request: DesignRequest, output_format: str) -> tuple:
        """출력 경로와 HTML 프리뷰 경로를 결정합니다."""
        output_dir = Path(request.output_dir) if request.output_dir else self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        ext = FORMAT_EXT.get(output_format, ".png")

        filename = request.output_filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = (request.topic or request.title or "output").replace(" ", "_")[:20]
            filename = f"{request.content_type}_{safe_topic}_{timestamp}{ext}"
        elif not filename.endswith(ext):
            filename = filename + ext

        output_path = str(output_dir / filename)
        # HTML 프리뷰는 항상 .html로
        html_path = str(Path(output_path).with_suffix(".html"))
        return output_path, html_path


# 하위 호환 alias
CardNewsEngine = DesignEngine
