from django.urls import path
from .api import views as api_views

app_name = 'accounts'

urlpatterns = [
    # API - Authentication (인증)
    path('api/signup/', api_views.SignupAPIView.as_view(), name='signup_api'),
    path('api/login/', api_views.LoginAPIView.as_view(), name='login_api'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='logout_api'),
    path('api/user/', api_views.UserInfoAPIView.as_view(), name='user_info_api'),
]
