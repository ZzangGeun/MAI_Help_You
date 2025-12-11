from django.urls import path


app_name = 'accounts'


from . import views

urlpatterns = [
    # API - Authentication (인증)
    path('api/signup/', views.signup_api, name='signup_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
]
