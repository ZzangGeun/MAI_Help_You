from django.urls import path
from . import views
from core.views import serve_react

app_name = 'character'

urlpatterns = [
    # Pages (HTML 렌더링)
    path('', serve_react, name='character_info_page'),
    
    # API - Character Info (캐릭터 정보)
    path('api/search/', views.character_info_view, name='character_search_api'),
    # path('api/<str:ocid>/', views.character_detail_api, name='character_detail_api'),  # TODO: OCID로 상세 조회
]