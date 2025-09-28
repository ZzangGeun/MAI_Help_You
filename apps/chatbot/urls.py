from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/sessions/', views.chat_sessions, name='chat_sessions'),
]