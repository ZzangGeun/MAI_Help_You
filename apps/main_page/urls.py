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
    path('api/health/', views.health_check_api, name='health_check_api'),

    ## 네비게이션 버튼 동작 urls
    path('api/character-info/', views.CharacterInfoAPIView.as_view(), name='character_info_api'),
    path('api/validate-api-key/', views.validate_api_key_api, name='validate_api_key_api'),


    path('api/login/', views.LoginAPIView.as_view(), name='login_api'),
    path('api/signup/', views.SignupAPIView.as_view(), name='signup_api'),
]