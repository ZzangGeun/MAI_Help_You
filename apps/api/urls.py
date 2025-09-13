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
    
    # 개별 API URL들 (도메인별로 분리됨)
    # path('chatbot/', include('apps.chatbot.api.urls')),  # 임시 비활성화
    path('character/', include('apps.character_info.api.urls')),
    # path('main/', include('apps.main_page.api.urls')),  # 임시 비활성화
    # path('auth/', include('apps.signup.api.urls')),  # DRF 제거로 비활성화
]
