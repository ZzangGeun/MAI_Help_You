from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages (HTML 렌더링)
    path('', views.main_page, name='main_page'),
    
    # API - Notices (공지사항)
    path('api/notices/cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notices/update/', views.notice_update_api, name='notice_update_api'),
    path('api/notices/event/', views.notice_event_api, name='notice_event_api'),
    path('api/notices/json/', views.notice_json_api, name='notice_json_api'),  # JSON 파일 데이터 조회
    path('api/rankings/json/', views.ranking_json_api, name='ranking_json_api'),  # 랭킹 JSON 파일 데이터 조회
    
    # API - System (시스템)
    # path('api/health/', views.health_check_api, name='health_check_api'),
    
    # API - Legacy (하위 호환성 유지, 추후 제거 예정)
    path('api/messages/', views.chatbot_request_api, name='chatbot_request_api'),  # → /chat/api/message/로 이동 권장
    path('api/character-search/', views.character_search_api, name='character_search_api'),  # → /character/api/search/로 이동 권장
]