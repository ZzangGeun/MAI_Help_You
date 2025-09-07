"""
개발 환경 설정
"""
from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - 개발 환경에서는 SQLite 사용
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / 'db.sqlite3',
    }
}

# API Keys for development
NEXON_API_KEY = config('NEXON_API_KEY', default='')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Ads settings (개발 환경에서는 비활성화)
ADS_ENABLED = config('ADS_ENABLED', default=False, cast=bool)
ADS_PROVIDER = config('ADS_PROVIDER', default='mock')
ADSENSE_CLIENT = config('ADSENSE_CLIENT', default='')
ADS_SLOTS = {
    'leaderboard': config('ADS_SLOT_LEADERBOARD', default=''),
    'medium_rectangle': config('ADS_SLOT_MEDIUM_RECT', default=''),
    'skyscraper': config('ADS_SLOT_SKYSCRAPER', default=''),
}

# PostgreSQL settings for RAG (optional in development)
PG_HOST = config('PG_HOST', default='localhost')
PG_PORT = config('PG_PORT', default='5432')
PG_DB = config('PG_DB', default='')
PG_USER = config('PG_USER', default='')
PG_PASSWORD = config('PG_PASSWORD', default='')

# Development specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (optional)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass

# =======================
# DRF 개발 환경 설정
# =======================

# 개발 환경에서는 모든 CORS 요청 허용
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 개발 환경에서는 권한을 더 느슨하게 설정
REST_FRAMEWORK.update({
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 개발 환경에서는 모든 접근 허용
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
})