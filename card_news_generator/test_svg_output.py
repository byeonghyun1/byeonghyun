"""
SVG 레이어 출력 검증
====================
Figma에 드래그&드롭해서 편집 가능한지 확인하기 위한 샘플 파일 생성.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.schema import DesignRequest
from engine.generator import DesignEngine

engine = DesignEngine(output_dir="output/svg_test")

cases = [
    DesignRequest(
        topic="신규 가입 이벤트",
        mood="밝은",
        content_type="card_news",
        size="1080x1080",
        brand="albamon",
        title="첫 지원 5,000원",
        description="지금 가입하고 바로 받아가세요",
        footer="2026.04.13 ~ 04.30",
        output_format="svg",
        output_filename="svg_cardnews_1080x1080_albamon",
    ),
    DesignRequest(
        topic="채용 공고 오픈",
        mood="세련된",
        content_type="card_news",
        size="1080x1350",
        brand="jobkorea",
        title="이번 주 대기업 채용",
        description="마감 임박 공고를 한번에 확인하세요",
        footer="jobkorea.co.kr",
        output_format="svg",
        output_filename="svg_cardnews_1080x1350_jobkorea",
    ),
    DesignRequest(
        topic="웍스피어 도입 안내",
        mood="세련된",
        content_type="card_news",
        size="1080x1080",
        brand="worxphere",
        title="AI로 운영 자동화",
        description="반복 업무를 하루 안에 자동화하세요",
        output_format="svg",
        output_filename="svg_cardnews_1080x1080_worxphere",
    ),
]

print("=" * 70)
print("SVG (편집 가능한 Figma 레이어) 출력 검증")
print("=" * 70)

for req in cases:
    r = engine.generate(req)
    tag = f"{req.content_type} × {req.size} × {req.brand}"
    if r.success:
        size = Path(r.output_path).stat().st_size
        print(f"✅ {tag:<40} → {Path(r.output_path).name} ({size:,} bytes)  renderer={r.renderer_used}")
    else:
        print(f"❌ {tag:<40} → {r.error}")

# 한 파일의 레이어 구조 요약
import xml.etree.ElementTree as ET
sample = "output/svg_test/svg_cardnews_1080x1080_albamon.svg"
tree = ET.parse(sample)
root = tree.getroot()
ns = "{http://www.w3.org/2000/svg}"
print()
print("=" * 70)
print(f"레이어 구조 샘플: {sample}")
print("=" * 70)
for el in root.iter():
    tag = el.tag.replace(ns, "")
    if tag in ("rect", "ellipse", "text", "image", "g"):
        name = el.get("data-figma-name") or el.get("id") or "(unnamed)"
        if tag == "text":
            text = "".join(ts.text or "" for ts in el.iter(f"{ns}tspan"))
            print(f"  [{tag:7}] {name}  — \"{text}\"")
        else:
            print(f"  [{tag:7}] {name}")
