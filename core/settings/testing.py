"""
테스트 환경 설정
"""
from .base import *

DEBUG = True

# Test database - 메모리 내 SQLite 사용
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mai_web',        
        'USER': 'postgres',       
        'PASSWORD': '2559',   
        'HOST': 'localhost',      
        'PORT': '5432',           
    }
}

# 테스트에서는 비밀번호 해싱을 빠르게
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 이메일을 실제로 보내지 않음
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 로깅 비활성화
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 테스트 실행 시 마이그레이션 건너뛰기
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
