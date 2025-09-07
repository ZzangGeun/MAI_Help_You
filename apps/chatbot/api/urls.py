"""
챗봇 API URL 설정 (도메인 전용)
"""
from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ChatbotAskAPIView.as_view(), name='chatbot-ask'),
    path('history/', views.ChatbotHistoryAPIView.as_view(), name='chatbot-history'),
    path('clear-history/', views.ChatbotClearHistoryAPIView.as_view(), name='chatbot-clear-history'),
    path('health/', views.ChatbotHealthCheckAPIView.as_view(), name='chatbot-health'),
]
