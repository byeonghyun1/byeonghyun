"""
콘텐츠 유형 설정의 기본 구조
============================
이 파일은 "설정 dict의 형태"를 문서화하는 역할만 합니다.
실제 설정값은 각 콘텐츠 유형 파일에 정의합니다 (card_news.py, banner.py 등).

설정 dict 필수 키:
    name            : 표시 이름 (예: "카드뉴스")
    default_size    : (width, height) 튜플
    template        : Jinja2 템플릿 파일 경로 (templates/ 기준 상대 경로)
    copy_fields     : 카피 생성 시 채울 필드 목록
    required_fields : 필수 입력 필드 (DesignRequest 기준)
    ai_prompt       : AI 카피 생성 시 사용할 프롬프트 템플릿 (선택)
    badge_keywords  : 뱃지 자동 추출용 키워드 리스트 (선택)
"""

# 빈 템플릿 예시 (새 콘텐츠 유형 만들 때 복사해서 사용)
CONTENT_TYPE_TEMPLATE = {
    "name": "",
    "default_size": (1080, 1080),
    "template": "",
    "copy_fields": [],
    "required_fields": ["topic"],
    "ai_prompt": "",
    "badge_keywords": [],
}
