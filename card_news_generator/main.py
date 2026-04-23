"""
콘텐츠 디자인 자동 생성기 - CLI 진입점
======================================
터미널에서 실행할 때의 입력 처리만 담당합니다.
실제 생성 로직은 engine/ 모듈에 있습니다.

사용법:
    # 카드뉴스 (기본)
    python3 main.py "설날 새해 이벤트" --mood "귀여운"
    python3 main.py "여름 특가 세일" --mood "활기찬" --brand albamon
    python3 main.py   (대화형 입력)

    # 추후: 배너/포스터 (content_types에 등록 후)
    python3 main.py "봄맞이 세일" --type banner --mood "활기찬"
"""

import os
import sys
import argparse

from engine import DesignEngine, DesignRequest
from content_types import list_content_types


def parse_args():
    parser = argparse.ArgumentParser(
        description="콘텐츠 디자인 자동 생성기",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("topic", nargs="?", default="", help="주제 (필수)")
    parser.add_argument("--target", default="", help="타겟")
    parser.add_argument("--purpose", default="", help="목적: click | signup | info | brand_awareness")
    parser.add_argument("--mood", default="", help="분위기 (귀여운, 세련된, 활기찬 등)")
    parser.add_argument("--copy-mode", default="manual", choices=["manual", "ai", "refine"],
                        help="카피 방식 (manual | ai | refine)")
    parser.add_argument("--cta", default="", help="행동 유도 문구")
    parser.add_argument("--type", dest="content_type", default="card_news",
                        help=f"콘텐츠 유형 ({' | '.join(list_content_types())})")
    parser.add_argument("--size", default="",
                        help="사이즈 키 (예: 1080x1080, 1080x1350, 1200x628, A4_vertical)")
    parser.add_argument("--brand", default="", help="브랜드 (albamon, jobkorea, worxphere)")
    parser.add_argument("--title", default="", help="제목 (비어있으면 topic 사용)")
    parser.add_argument("--desc", dest="description", default="", help="설명 문구")
    parser.add_argument("--badge", default="", help="뱃지 텍스트")
    parser.add_argument("--output-dir", default="", help="출력 폴더")
    parser.add_argument("--format", dest="output_format", default="both",
                        choices=["png", "html", "svg", "both"],
                        help="출력 형식 (both = PNG[확인용] + SVG[Figma 편집용] 동시 생성)")
    return parser.parse_args()


def interactive_input() -> dict:
    """대화형으로 필수 입력을 받습니다."""
    print("\n콘텐츠 디자인 자동 생성기")
    print("-" * 30)
    topic = input("주제를 입력하세요: ").strip()
    mood = input("분위기 (귀여운/따뜻한/세련된/활기찬/자연스러운/차분한): ").strip()
    return {
        "topic": topic or "설날 새해 이벤트",
        "mood": mood or "귀여운",
    }


def main():
    args = parse_args()

    if not args.topic:
        inputs = interactive_input()
        topic = inputs["topic"]
        mood = inputs["mood"]
    else:
        topic = args.topic
        mood = args.mood

    request = DesignRequest(
        # 첫 입력 목록
        topic=topic,
        target=args.target,
        purpose=args.purpose,
        mood=mood,
        copy_mode=args.copy_mode,
        cta=args.cta,
        # 시스템 설정 — 3축 (형식 / 규격 / 스타일)
        content_type=args.content_type,
        size=args.size,
        brand=args.brand,
        title=args.title or topic,
        description=args.description,
        badge=args.badge,
        output_format=args.output_format,
        output_dir=args.output_dir,
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        source="cli",
    )

    print("=" * 50)
    print(f"  콘텐츠 디자인 생성 ({request.content_type})")
    print("=" * 50)
    print(f"\n  주제 : {request.topic}")
    print(f"  타겟 : {request.target or '-'}")
    print(f"  목적 : {request.purpose or '-'}")
    print(f"  분위기 : {request.mood or '-'}")
    print(f"  카피 방식 : {request.copy_mode}")
    if request.cta:
        print(f"  CTA : {request.cta}")
    if request.brand:
        print(f"  브랜드 : {request.brand}")

    engine = DesignEngine()
    result = engine.generate(request)

    if result.success:
        print(f"\n  뱃지 : {result.context.get('badge', '')}")
        print(f"  배경색 : {result.context.get('bg_color', '')}")
        print(f"  강조색 : {result.context.get('accent_color', '')}")
        print(f"  렌더러 : {result.renderer_used}")
        print(f"\n  출력 : {result.output_path}")
        print(f"  HTML : {result.html_path}")
        print("=" * 50)
    else:
        print(f"\n  [실패] {result.error}")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
