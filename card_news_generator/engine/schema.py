"""
데이터 스키마
============
입력(DesignRequest)과 출력(DesignResult)의 구조를 정의합니다.
dataclass 기반이라 dict 변환이 자유롭고,
Google Sheets / Web API 등 어디서든 동일한 형태로 사용합니다.

설계서(ARCHITECTURE.md) 3장의 "첫 입력 목록"과 동일한 구조:
    주제, 타겟, 목적, 분위기, 카피 방식, CTA
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class DesignRequest:
    """
    콘텐츠 생성 요청 스키마. (카드뉴스, 배너, 포스터 등 모든 유형 공통)

    사용 예시:
        # 최소 입력 (카드뉴스 기본)
        DesignRequest(topic="설날 새해 이벤트", mood="귀여운")

        # 전체 커스텀
        DesignRequest(
            topic="여름 특가 세일",
            target="20-30대 직장인",
            purpose="click",
            mood="활기찬",
            copy_mode="ai",
            cta="지금 신청하기",
            content_type="card_news",
            brand="albamon",
        )

        # dict에서 생성 (Google Sheets / Web API 연동 시)
        DesignRequest.from_dict(row_dict)
    """
    # ══════════════════════════════════
    #  첫 입력 목록 (사용자가 직접 입력)
    # ══════════════════════════════════
    topic: str = ""                       # 주제 (필수)
    target: str = ""                      # 타겟 (필수)
    purpose: str = ""                     # 목적 (필수) - click | signup | info | brand_awareness
    mood: str = ""                        # 분위기 (선택)
    copy_mode: str = "manual"             # 카피 방식 (필수) - manual | ai | refine
    cta: str = ""                         # CTA (선택)

    # ══════════════════════════════════
    #  시스템 설정 (기본값/자동)
    # ══════════════════════════════════
    # 콘텐츠 유형 (형식 축)
    content_type: str = "card_news"       # card_news | banner | poster | detail_page ...

    # 사이즈 (규격 축) — 콘텐츠 유형이 허용하는 사이즈 키 중 하나
    #   예: card_news 안에 "1080x1080" / "1080x1350"
    #       banner    안에 "1200x628" / "970x250"
    #       poster    안에 "A4_vertical"
    #   비어있으면 content_type의 default_size 사용
    size: str = ""

    # 브랜드 (스타일 축)
    brand: str = ""                       # albamon | jobkorea | worxphere | ""

    # 콘텐츠 유형 고유 카피 (badge/title 같은 공통 슬롯에 없는 필드용)
    #   예: banner의 subtitle/cta_text, detail_page의 section_1 등
    copy_inputs: dict = field(default_factory=dict)

    # 카피 입력 (copy_mode에 따라 다르게 사용)
    #   manual : 이 필드들을 그대로 사용
    #   ai     : 비어있으면 AI가 생성
    #   refine : 이 필드들을 AI가 다듬음
    title: str = ""                       # 제목
    description: str = ""                 # 설명
    badge: str = ""                       # 뱃지
    footer: str = ""                      # 하단 문구

    # 템플릿 (비어있으면 content_type의 기본 템플릿)
    template: str = ""

    # 스타일 오버라이드
    bg_color: str = ""
    accent_color: str = ""
    title_color: str = ""
    desc_color: str = ""

    # 이미지 설정 (추후 배너/포스터 확장 시 사용)
    image_mode: str = "none"              # none | asset | generate
    image_prompt: str = ""
    image_generator: str = ""             # midjourney | gemini | dalle
    image_asset_id: str = ""

    # 출력 설정
    output_format: str = "png"            # png | html | pdf
    output_dir: str = ""
    output_filename: str = ""
    width: int = 0                        # 0이면 content_type 기본값 사용
    height: int = 0

    # AI 설정
    api_key: str = ""

    # ── 메타정보 ──
    source: str = "cli"                   # cli | google_sheets | slack | web

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DesignRequest":
        """dict에서 DesignRequest를 생성합니다. 알 수 없는 키는 무시합니다."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class DesignResult:
    """
    콘텐츠 생성 결과 스키마.
    """
    success: bool = False
    output_path: str = ""
    html_path: str = ""
    renderer_used: str = ""               # playwright | pillow | html
    content_type: str = ""
    context: dict = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
