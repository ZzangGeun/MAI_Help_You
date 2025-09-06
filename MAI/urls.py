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
    path('auth/', include('apps.sns_login.urls')),
    
    # 새로운 API URLs (DRF)
    path('api/v1/', include('apps.api.urls')),  # 통합 API
]

# API 문서화 (개발 환경에서만)
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
