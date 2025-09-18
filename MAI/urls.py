from django.contrib import admin
from django.urls import path, include
from django.conf import settings # settings.DEBUG를 사용하기 위해 필요

urlpatterns = [
    path('admin/', admin.site.urls),
    # 각 앱의 URL을 포함합니다.
    path('', include('apps.main_page.urls')),
    path('character-info/', include('apps.character_info.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    path('api/', include('apps.api.urls')),
    # 여기에 다른 앱의 URL을 추가할 수 있습니다.
]

# 개발 환경에서만 Django Debug Toolbar를 활성화합니다.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns