# -*- coding: utf-8 -*-
"""
MAI Chat URL Configuration

채팅 API 엔드포인트 라우팅
"""

from django.urls import path
from . import views

app_name = 'mai_chat'

urlpatterns = [
    # 세션 관련
    path('api/chat/sessions/', views.get_sessions_view, name='get_sessions'),
    path('api/chat/sessions/create/', views.create_session_view, name='create_session'),
    path('api/chat/sessions/<uuid:session_id>/messages/', views.get_messages_view, name='get_messages'),
    path('api/chat/sessions/<uuid:session_id>/send/', views.send_message_view, name='send_message'),
    path('api/chat/sessions/<uuid:session_id>/delete/', views.delete_session_view, name='delete_session'),
    
    # 레거시 엔드포인트 (호환성 유지)
    path('api/chat/', views.chat_view, name='chat'),
    path('api/chat/history/<uuid:session_id>/', views.chat_history_view, name='chat_history'),
    path('api/chat/session/', views.create_session_view, name='create_session_legacy'),
    path('api/chat/session/<uuid:session_id>/', views.delete_session_view, name='delete_session_legacy'),
]

