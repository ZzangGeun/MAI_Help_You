"""
테스트 패키지 초기화 파일

이 패키지는 MAI 프로젝트의 모든 테스트들을 포함합니다.

구조:
    tests/
    ├── __init__.py           # 이 파일
    ├── api/                  # API 관련 테스트
    │   ├── test_nexon_api.py        # 독립 실행 API 테스트
    │   └── test_django_integration.py # Django 통합 테스트
    ├── data/                 # 테스트 데이터 저장소
    └── utils/               # 테스트 유틸리티
        └── test_helpers.py   # 테스트 헬퍼 함수들
"""

__version__ = "1.0.0"
__description__ = "MAI 프로젝트 테스트 모음"
