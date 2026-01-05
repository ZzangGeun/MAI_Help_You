# -*- coding: utf-8 -*-
"""
MAI Chat URL Configuration

채팅 API 엔드포인트 라우팅
"""

from django.urls import path
from . import views

app_name = 'mai_chat'

urlpatterns = [
    # 채팅방 페이지
    path('chat/', views.chat_page, name='chatbot'),
    
    # API Endpoints
    path('api/chat/sessions/', views.get_sessions_view, name='get_sessions'),
    path('api/chat/sessions/create/', views.create_session_view, name='create_session'),
    path('api/chat/sessions/<uuid:session_id>/messages/', views.get_messages_view, name='get_messages'),
    path('api/chat/sessions/<uuid:session_id>/send/', views.send_message_view, name='send_message'),
    path('api/chat/sessions/<uuid:session_id>/stream/', views.stream_message_view, name='stream_message'),
    path('api/chat/sessions/<uuid:session_id>/delete/', views.delete_session_view, name='delete_session'),
]

