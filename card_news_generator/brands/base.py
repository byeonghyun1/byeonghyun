"""
브랜드 설정의 기본 구조
========================
각 브랜드 파일이 선언해야 할 키의 형태를 문서화합니다.
실제 값은 brands/albamon.py, brands/jobkorea.py 등에 정의.

브랜드 dict 구조:
    name          : 표시 이름 (예: "알바몬")
    name_en       : 영문 키 (URL/폴더/파일명용)
    tone          : 브랜드 톤 (AI 카피 생성 시 참고)
    target        : 주 타겟층 (AI 카피 생성 시 참고)

    colors        : 컬러 팔레트
        bg_color, accent_color, title_color, desc_color : 기본 4슬롯 (필수)
        on_primary : primary 위 텍스트 색 (선택)
        surface    : 보조 배경색 (선택)
        ... 자유롭게 확장 가능. 템플릿에서 {{ color.button_bg }} 식으로 참조

    typography    : 폰트 설정
        primary_font : 메인 폰트 (웹 폰트 URL 또는 family 이름)
        heading_font : 제목용 폰트 (선택)
        font_url     : 웹에서 로드할 CSS URL

    logo          : 로고 에셋 경로 (templates 기준 상대 경로 또는 절대 경로)
        primary   : 기본 로고
        mono      : 단색 로고 (선택)
        icon      : 아이콘만 (선택)

    overrides     : 콘텐츠 유형별 세부 오버라이드 (선택)
        card_news : { template: "...", ... }  ← 카드뉴스에서만 다른 템플릿 쓰기
        banner    : { ... }
"""

# 새 브랜드 만들 때 복사해서 사용하는 빈 템플릿
BRAND_TEMPLATE = {
    "name": "",
    "name_en": "",
    "tone": "",
    "target": "",
    "colors": {
        "bg_color": "#FFFFFF",
        "accent_color": "#000000",
        "title_color": "#000000",
        "desc_color": "#555555",
    },
    "typography": {
        "primary_font": "Noto Sans KR",
        "heading_font": "Noto Sans KR",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap",
    },
    "logo": {
        "primary": "",
    },
    "overrides": {},
}
