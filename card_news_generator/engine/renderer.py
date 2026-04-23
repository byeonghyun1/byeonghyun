"""
렌더러 모듈 (콘텐츠 유형 무관)
===============================
context dict + 템플릿 경로를 받아 실제 이미지/HTML 파일을 생성합니다.
이 파일은 "어떤 콘텐츠 유형인지" 전혀 알지 못합니다.

렌더링 우선순위:
  1. Playwright (HTML → PNG, 최고 품질)
  2. 콘텐츠 유형별 Pillow 폴백 (content_types 설정에서 지정된 경우에만)
  3. HTML 파일만 생성 (브라우저에서 직접 열기)
"""

import os
import asyncio
import importlib
from pathlib import Path

from .config import TEMPLATE_DIR

try:
    from jinja2 import Environment, FileSystemLoader
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False


# ============================================================
# HTML 렌더링
# ============================================================
def render_html(context: dict, template_name: str) -> str:
    """Jinja2 템플릿에 context를 채워 HTML 문자열을 반환합니다."""
    if not HAS_JINJA:
        raise ImportError("jinja2가 필요합니다: pip3 install jinja2")
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(template_name)
    return template.render(**context)


def save_html(html_content: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return os.path.abspath(output_path)


# ============================================================
# Playwright 렌더러 (HTML → PNG/PDF, 범용)
# ============================================================
def _has_playwright() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


async def _capture_playwright(html_content: str, output_path: str, w: int, h: int, fmt: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": w, "height": h})
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        if fmt == "pdf":
            await page.pdf(path=output_path, width=f"{w}px", height=f"{h}px", print_background=True)
        else:
            await page.screenshot(path=output_path, type="png", full_page=(fmt == "png_full"))
        await browser.close()
    return os.path.abspath(output_path)


def render_with_playwright(html_content: str, output_path: str, w: int, h: int, fmt: str = "png") -> str:
    """Playwright로 HTML을 PNG 또는 PDF로 변환합니다."""
    return asyncio.run(_capture_playwright(html_content, output_path, w, h, fmt))


# ============================================================
# 콘텐츠 유형별 Pillow 폴백 (동적 로드)
# ============================================================
def _load_pillow_fallback(dotted_path: str):
    """'content_types.card_news_pillow.render' 같은 문자열을 함수로 변환."""
    if not dotted_path:
        return None
    try:
        module_path, func_name = dotted_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name, None)
    except Exception:
        return None


# ============================================================
# 통합 렌더 함수
# ============================================================
def render(
    context: dict,
    output_path: str,
    html_path: str,
    template_name: str,
    w: int,
    h: int,
    output_format: str = "png",
    pillow_fallback: str = "",
) -> tuple:
    """
    최적의 렌더러를 자동 선택하여 최종 파일을 생성합니다.

    Args:
        context         : 템플릿에 바인딩될 데이터
        output_path     : 최종 파일 경로 (확장자 포함)
        html_path       : HTML 프리뷰 저장 경로
        template_name   : Jinja2 템플릿 (templates/ 기준 상대 경로)
        w, h            : 출력 크기
        output_format   : "png" | "pdf" | "html"
        pillow_fallback : 폴백 렌더러 함수의 dotted path (콘텐츠 유형이 지정)

    Returns:
        (output_path, renderer_used) 튜플
        renderer_used : "playwright" | "pillow" | "html"
    """
    # HTML은 항상 생성 (프리뷰)
    html_content = render_html(context, template_name)
    save_html(html_content, html_path)

    # HTML 포맷 요청이면 HTML만 반환
    if output_format == "html":
        return os.path.abspath(html_path), "html"

    # 1순위: Playwright (모든 콘텐츠 유형 공통)
    if _has_playwright():
        try:
            result = render_with_playwright(html_content, output_path, w, h, output_format)
            return result, "playwright"
        except Exception:
            pass

    # 2순위: 콘텐츠 유형이 지정한 Pillow 폴백
    fallback_fn = _load_pillow_fallback(pillow_fallback)
    if fallback_fn:
        try:
            result = fallback_fn(context, output_path, w, h)
            if result:
                return result, "pillow"
        except Exception:
            pass

    # 3순위: HTML만 반환
    return os.path.abspath(html_path), "html"
