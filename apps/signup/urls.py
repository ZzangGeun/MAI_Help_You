from django.urls import path
from . import views

app_name = 'signup'

urlpatterns = [
    # 회원가입 페이지
    path('', views.signup_view, name='signup_view'),
    # 회원가입 API
    path('api/signup/', views.signup_api, name='signup_api'),
]
