from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('apps.main_page.urls')),
    path('character_info/', include('apps.character_info.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    path('auth/', include('apps.sns_login.urls')),  # SNS 로그인 추가
]

# 개발 환경에서 미디어 파일 및 정적 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # STATICFILES_DIRS의 첫 번째 디렉토리 사용
    import os
    static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
    urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
