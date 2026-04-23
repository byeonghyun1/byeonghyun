"""
3축 구조 유연성 검증 테스트
============================
content_type × size × brand 축이 서로 독립적으로 조합 가능한지 확인.

검증 조합 (사용자가 제시한 예시 그대로):
  1. 카드뉴스 + 1080x1080 + 알바몬
  2. 카드뉴스 + 1080x1350 + 잡코리아
  3. 배너    + 1200x628  + worxphere
  4. 포스터  + A4_vertical + 알바몬
"""

import sys
import os
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from engine.schema import DesignRequest
from engine.generator import DesignEngine

engine = DesignEngine(output_dir="output/3axis_test")

cases = [
    {
        "label": "카드뉴스 + 1080x1080 + 알바몬",
        "request": DesignRequest(
            topic="신규 가입 이벤트",
            mood="밝은",
            content_type="card_news",
            size="1080x1080",
            brand="albamon",
            title="첫 지원 5,000원",
            description="지금 가입하고 바로 받기",
            output_filename="case1_cardnews_1080x1080_albamon",
        ),
        "expected": (1080, 1080),
    },
    {
        "label": "카드뉴스 + 1080x1350 + 잡코리아",
        "request": DesignRequest(
            topic="채용 공고 오픈",
            mood="세련된",
            content_type="card_news",
            size="1080x1350",
            brand="jobkorea",
            title="대기업 채용 오픈",
            description="이번 주 마감되는 채용 공고 모음",
            output_filename="case2_cardnews_1080x1350_jobkorea",
        ),
        "expected": (1080, 1350),
    },
    {
        "label": "배너 + 1200x628 + worxphere",
        "request": DesignRequest(
            topic="웍스피어 도입 안내",
            mood="세련된",
            content_type="banner",
            size="1200x628",
            brand="worxphere",
            title="AI로 운영 자동화",
            description="반복 업무를 하루 안에 자동화하세요",
            copy_inputs={"cta_text": "도입 문의", "bg_tagline": "AUTOMATE"},
            output_filename="case3_banner_1200x628_worxphere",
        ),
        "expected": (1200, 628),
    },
    {
        "label": "포스터 + A4_vertical + 알바몬",
        "request": DesignRequest(
            topic="대학생 알바 페스티벌",
            mood="활기찬",
            content_type="poster",
            size="A4_vertical",
            brand="albamon",
            title="알바 페스티벌",
            description="전국 대학생을 위한 알바 박람회",
            copy_inputs={
                "subtitle": "전국 대학생을 위한 알바 박람회",
                "date_range": "2026.05.10 (토) 10:00 ~ 18:00",
                "place": "서울 코엑스 D홀",
            },
            footer="주최: 알바몬  ·  문의 02-0000-0000",
            output_filename="case4_poster_A4_vertical_albamon",
        ),
        "expected": (595, 842),
    },
]

print("=" * 72)
print("3축 조합 검증: content_type × size × brand")
print("=" * 72)

results = []
for c in cases:
    r = engine.generate(c["request"])
    ok = r.success
    actual_size = None
    if ok and r.output_path and os.path.exists(r.output_path):
        actual_size = Image.open(r.output_path).size
    match = actual_size == c["expected"]
    status = "✅" if (ok and match) else "❌"
    print(f"{status} {c['label']}")
    print(f"    renderer={r.renderer_used}  expected={c['expected']}  actual={actual_size}")
    if not ok:
        print(f"    error={r.error}")
    results.append((c["label"], ok and match))

print()
print("=" * 72)
success = sum(1 for _, ok in results if ok)
print(f"총 {len(results)}건 중 {success}건 성공")
print("=" * 72)
