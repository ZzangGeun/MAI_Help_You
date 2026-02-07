from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import serve_react

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Core (Main Page)
    path('', include('core.urls')),
    
    # Character
    path('character/', include('character.urls')),
    
    # Accounts
    path('accounts/', include('accounts.urls')),
    
    # MAI Chat (AI Chatbot)
    path('mai_chat/', include('mai_chat.urls')),

    # Catch-all for React Client-side Routing
    re_path(r'^.*$', serve_react, name='react_app'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
