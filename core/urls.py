from django.urls import path
from . import views
from .api.views import HomeDataAPIView

app_name = 'core'

urlpatterns = [
    # Pages (HTML 렌더링)
    path('', views.serve_react, name='main_page'),
    
    # API - Home Data (통합 데이터)
    path('api/home/data/', HomeDataAPIView.as_view(), name='home_data_api'),

    # API - Notices (개별, 레거시)
    path('api/notices/cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notices/update/', views.notice_update_api, name='notice_update_api'),
    path('api/notices/event/', views.notice_event_api, name='notice_event_api'),
    path('api/notices/json/', views.notice_json_api, name='notice_json_api'),
    path('api/rankings/json/', views.ranking_json_api, name='ranking_json_api'),
    
    # API - Legacy
    path('api/messages/', views.chatbot_request_api, name='chatbot_request_api'),
    path('api/character-search/', views.character_search_api, name='character_search_api'),
]
