from django.urls import path
from . import views

urlpatterns = [
    # HTML 페이지
    path('', views.main_page, name='main_page'),
    path('character_info/', views.character_info_view, name="character_info_view"),
    
    # JSON API 엔드포인트  
    path('api/notice/', views.notice_list_api, name='notice_list_api'),
    path('api/notice/<int:notice_id>/', views.notice_detail_api, name='notice_detail_api'),
    path('api/events/', views.event_list_api, name='event_list_api'),
    path('api/health/', views.health_check_api, name='health_check_api'),
]