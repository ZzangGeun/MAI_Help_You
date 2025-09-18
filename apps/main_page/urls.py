from django.urls import path
from . import views

# URL 패턴 이름 변경: character_info_view -> character_info
urlpatterns = [
    # HTML 페이지
    path('', views.main_page, name='main_page'),
    
    # JSON API 엔드포인트  
    path('api/notice/', views.notice_list_api, name='notice_list_api'),
    path('api/notice-cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notice-update/', views.notice_update_api, name='notice_update_api'),
    path('api/notice-event/', views.notice_event_api, name='notice_event_api'),

    path('api/login/', views.login_api, name='login_api'),
    path('api/signup/', views.signup_api, name='signup_api'),
]