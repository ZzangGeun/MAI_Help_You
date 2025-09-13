from django.urls import path
from . import views

urlpatterns = [
    # HTML 페이지
    path('', views.main_page, name='main_page'),
    path('character_info/', views.character_info_view, name="character_info_view"),
    
    # JSON API 엔드포인트  
    path('api/notice/', views.notice_list_api, name='notice_list_api'),
    path('api/notice-cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notice-update/', views.notice_update_api, name='notice_update_api'),
    path('api/notice-event/', views.notice_event_api, name='notice_event_api'),
    path('api/ranking-overall/', views.ranking_overall_api, name='ranking_overall_api'),
    path('api/health/', views.health_check_api, name='health_check_api'),

    ## 네비게이션 버튼 동작 urls
    path('api/character-search/', views.character_search_api, name='character_search_api'),

    path('api/login/', views.login_api, name='login_api'),
    path('api/signup/', views.signup_api, name='signup_api'),
]