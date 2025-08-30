"""
MAI 프로젝트 메인 설정 파일
환경에 따라 적절한 설정을 로드합니다.
"""
import os
from decouple import config

# 환경 변수에 따른 설정 파일 선택
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from core.settings.production import *
elif ENVIRONMENT == 'testing':
    from core.settings.testing import *
else:
    from core.settings.development import *
