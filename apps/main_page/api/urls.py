"""
메인 페이지 API URL 설정 (도메인 전용)
"""
from django.urls import path
from . import views

urlpatterns = [
    path('notices/', views.NoticeListAPIView.as_view(), name='api-notice-list'),
    path('events/', views.EventListAPIView.as_view(), name='api-event-list'),
    path('health/', views.HealthCheckAPIView.as_view(), name='api-health-check'),
    path('validate-api-key/', views.APIKeyValidationAPIView.as_view(), name='api-validate-key'),
]


