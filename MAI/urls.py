from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('main_page.urls')),
    path('character_info/', include('character_info.urls')),
    path('chatbot/', include('chatbot.urls'))
]
