# -*- coding: utf-8 -*-
"""
MAI Chat Django Admin

Django admin 인터페이스 설정
"""

from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """채팅 세션 관리 인터페이스"""
    
    list_display = ('session_id', 'user', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    def message_count(self, obj):
        """세션의 메시지 개수를 표시합니다."""
        return obj.messages.count()
    
    message_count.short_description = '메시지 수'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """채팅 메시지 관리 인터페이스"""
    
    list_display = ('id', 'session', 'user_message_preview', 'created_at', 'response_time')
    list_filter = ('created_at',)
    search_fields = ('user_message', 'ai_response')
    readonly_fields = ('created_at',)
    
    def user_message_preview(self, obj):
        """질문 미리보기 (50자 제한)"""
        if len(obj.user_message) > 50:
            return obj.user_message[:50] + '...'
        return obj.user_message
    
    user_message_preview.short_description = '사용자 질문'
