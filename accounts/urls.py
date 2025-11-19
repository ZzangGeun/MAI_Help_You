from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원가입 페이지 뷰
    path('signup/', views.signup_page, name='signup_page'),
    
    # 회원가입 API
    path('api/signup/', views.signup_api, name='signup_api'),
    
    # 로그인 API
    path('api/login/', views.login_api, name='login_api'),
]
