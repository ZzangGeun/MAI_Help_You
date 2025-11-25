from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # API - Authentication (인증)
    path('api/signup/', views.signup_api, name='signup_api'),
    path('api/login/', views.login_api, name='login_api'),
    # path('api/logout/', views.logout_api, name='logout_api'),  # TODO: 구현 필요
    
    # API - User Profile (사용자 프로필)
    # path('api/profile/', views.profile_api, name='profile_api'),  # TODO: 구현 필요
    # path('api/profile/update/', views.profile_update_api, name='profile_update_api'),  # TODO: 구현 필요
]