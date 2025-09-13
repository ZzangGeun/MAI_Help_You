"""
회원 가입/인증 API URL (signup 도메인) - 기본 Django 뷰
"""
from django.urls import path
from .. import views

urlpatterns = [
    path('register/', views.signup_api, name='api-user-register'),
    # 로그인은 main_page 앱에서 처리
]


