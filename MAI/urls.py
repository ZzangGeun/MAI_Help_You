from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # 기존 웹페이지 URLs (Django 템플릿)
    path('', include('apps.main_page.urls')),
    path('character_info/', include('apps.character_info.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    path('auth/', include('apps.signup.urls')),  # signup으로 변경됨
    
    # 새로운 API URLs (DRF) - 버전 관리
    path('api/v1/', include('apps.api.urls')),  # API v1
]

# 개발 환경에서 미디어 파일 서빙 및 API 문서화
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    urlpatterns += [
        # API 문서화 (Swagger UI)
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
