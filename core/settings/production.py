"""
프로덕션 환경 설정
"""
from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

# Database - 프로덕션에서는 PostgreSQL 사용
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

# API Keys
NEXON_API_KEY = config('NEXON_API_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')

# Ads settings
ADS_ENABLED = config('ADS_ENABLED', default=True, cast=bool)
ADS_PROVIDER = config('ADS_PROVIDER', default='adsense')
ADSENSE_CLIENT = config('ADSENSE_CLIENT')
ADS_SLOTS = {
    'leaderboard': config('ADS_SLOT_LEADERBOARD'),
    'medium_rectangle': config('ADS_SLOT_MEDIUM_RECT'),
    'skyscraper': config('ADS_SLOT_SKYSCRAPER'),
}

# PostgreSQL settings for RAG
PG_HOST = config('PG_HOST')
PG_PORT = config('PG_PORT', default='5432')
PG_DB = config('PG_DB')
PG_USER = config('PG_USER')
PG_PASSWORD = config('PG_PASSWORD')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Use HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['file'],
    },
}
