"""
API v1 통합 URL 설정
모든 DRF API 엔드포인트를 여기서 관리
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 라우터 설정
router = DefaultRouter()

app_name = 'api'

urlpatterns = [
    # 라우터 기반 URL (ViewSet용)
    path('', include(router.urls)),
    
    # 개별 API URL들
    path('chatbot/', include('apps.api.chatbot_urls')),
    path('character/', include('apps.api.character_urls')),
    path('auth/', include('apps.api.auth_urls')),
]
