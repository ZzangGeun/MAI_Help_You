# -*- coding: utf-8 -*-
"""
MAI Chat URL Configuration

채팅 API 엔드포인트 라우팅
"""

from django.urls import path
from . import views

app_name = 'mai_chat'

urlpatterns = [
    # 채팅 메시지 전송
    path('api/chat/', views.chat_view, name='chat'),
    
    # 채팅 히스토리 조회
    path('api/chat/history/<uuid:session_id>/', views.chat_history_view, name='chat_history'),
    
    # 세션 생성
    path('api/chat/session/', views.create_session_view, name='create_session'),
    
    # 세션 삭제
    path('api/chat/session/<uuid:session_id>/', views.delete_session_view, name='delete_session'),
]
