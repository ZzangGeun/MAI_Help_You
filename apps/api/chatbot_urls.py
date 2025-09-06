"""
챗봇 API URL 설정
"""
from django.urls import path
from . import chatbot_views

urlpatterns = [
    path('ask/', chatbot_views.ChatbotAskAPIView.as_view(), name='chatbot-ask'),
    path('history/', chatbot_views.ChatbotHistoryAPIView.as_view(), name='chatbot-history'),
    path('clear-history/', chatbot_views.ChatbotClearHistoryAPIView.as_view(), name='chatbot-clear-history'),
    path('health/', chatbot_views.ChatbotHealthCheckAPIView.as_view(), name='chatbot-health'),
]
