from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원가입 API
    path('api/signup/', views.signup_api, name='signup_api'),
    
    # 로그인 API
    path('api/login/', views.login_api, name='login_api'),

    # 로그아웃 API
    path('api/logout/', views.logout_api, name='logout_api'),
]
