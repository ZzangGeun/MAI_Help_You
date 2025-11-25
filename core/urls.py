from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages (HTML 렌더링)
    path('', views.main_page, name='main_page'),
    
    # API - Notices (공지사항)
    path('api/notices/', views.notice_list_api, name='notice_list_api'),
    path('api/notices/cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notices/update/', views.notice_update_api, name='notice_update_api'),
    path('api/notices/event/', views.notice_event_api, name='notice_event_api'),
    
    # API - Rankings (랭킹)
    path('api/rankings/', views.ranking_api, name='ranking_api'),  # 통합 랭킹 API (?type=general|power)
    path('api/rankings/overall/', views.ranking_overall_api, name='ranking_overall_api'),  # 레거시 지원
    
    # API - System (시스템)
    path('api/health/', views.health_check_api, name='health_check_api'),
    
    # API - Legacy (하위 호환성 유지, 추후 제거 예정)
    path('api/chatbot/', views.chatbot_request_api, name='chatbot_request_api'),  # → /chat/api/message/로 이동 권장
    path('api/character-search/', views.character_search_api, name='character_search_api'),  # → /character/api/search/로 이동 권장
]