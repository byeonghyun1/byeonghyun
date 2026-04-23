"""
독립 실행형 프로토타입 종합 테스트
==================================
외부 API 없이 3개 콘텐츠 유형 × 여러 사이즈 × 3개 브랜드 × 3가지 카피 모드를
모두 PNG + SVG로 생성합니다.
"""

import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.schema import DesignRequest
from engine.generator import DesignEngine

engine = DesignEngine(output_dir="output/prototype")

cases = [
    # (label, content_type, size, brand, copy_mode, extras)
    ("카드뉴스/정사각/알바몬/manual",
        "card_news", "1080x1080", "albamon", "manual",
        dict(topic="여름 이벤트", title="여름 특가 할인", description="지금 신청하세요",
             footer="2026.06.01 ~ 06.30")),
    ("카드뉴스/세로형/잡코리아/ai",
        "card_news", "1080x1350", "jobkorea", "ai",
        dict(topic="대기업 신입 채용 오픈", target="신입 구직자", purpose="signup", mood="세련된")),
    ("카드뉴스/정사각/웍스피어/refine",
        "card_news", "1080x1080", "worxphere", "refine",
        dict(topic="AI 자동화 도입", title="AI로 운영을 자동화하세요",
             description="반복 업무를 줄이고 본질에 집중하세요", mood="세련된", purpose="brand_awareness")),

    ("배너/1200x628/알바몬/manual",
        "banner", "1200x628", "albamon", "manual",
        dict(topic="신규 가입 이벤트", title="첫 지원하면 5,000원",
             description="지금 가입하고 받기",
             copy_inputs={"cta_text": "지금 받기", "bg_tagline": "EVENT"})),
    ("배너/970x250/잡코리아/ai",
        "banner", "970x250", "jobkorea", "ai",
        dict(topic="채용 공고 한눈에", target="이직 희망자", purpose="click", mood="활기찬")),

    ("포스터/A4/알바몬/manual",
        "poster", "A4_vertical", "albamon", "manual",
        dict(topic="알바 페스티벌", title="알바 페스티벌",
             copy_inputs={
                 "subtitle": "전국 대학생을 위한 알바 박람회",
                 "date_range": "2026.05.10 (토) 10:00 ~ 18:00",
                 "place": "서울 코엑스 D홀",
             },
             footer="주최: 알바몬 · 문의 02-0000-0000")),
    ("포스터/A4/웍스피어/ai",
        "poster", "A4_vertical", "worxphere", "ai",
        dict(topic="웍스피어 도입 사내 설명회",
             target="실무 매니저", purpose="info", mood="세련된")),
]

print("=" * 78)
print("프로토타입 종합 테스트 — PNG + SVG 동시 생성, 외부 API 없음")
print("=" * 78)

for label, ct, size, brand, mode, extras in cases:
    req = DesignRequest(
        content_type=ct, size=size, brand=brand, copy_mode=mode,
        output_format="both",
        output_filename=f"{ct}_{size}_{brand}_{mode}",
        **extras,
    )
    r = engine.generate(req)
    if r.success:
        png = r.context.get("png_path", "?")
        svg = r.context.get("svg_path", "?")
        copy_preview = " | ".join(
            f"{k}={r.context.get(k, '')[:18]}"
            for k in ("badge", "title", "subtitle", "cta_text") if r.context.get(k)
        )
        print(f"✅ {label}")
        print(f"    카피: {copy_preview}")
        print(f"    PNG: {Path(png).name}   SVG: {Path(svg).name}")
    else:
        print(f"❌ {label}  → {r.error}")
    print()

# 출력 폴더 요약
out_dir = Path("output/prototype")
files = sorted(out_dir.glob("*"))
png_count = sum(1 for f in files if f.suffix == ".png")
svg_count = sum(1 for f in files if f.suffix == ".svg")
print("=" * 78)
print(f"output/prototype/ 안에 PNG {png_count}개, SVG {svg_count}개 생성됨")
print("=" * 78)
