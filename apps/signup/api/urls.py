"""
회원 가입/인증 API URL (signup 도메인)
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationAPIView.as_view(), name='api-user-register'),
    path('login/', views.UserLoginAPIView.as_view(), name='api-user-login'),
]


