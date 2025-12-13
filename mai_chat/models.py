# -*- coding: utf-8 -*-
"""
MAI Chat Django Models

채팅 세션 및 메시지를 저장하는 Django 모델
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """
    채팅 세션 모델
    
    사용자별 채팅 세션을 관리합니다.
    익명 사용자도 세션을 가질 수 있도록 user는 null 허용합니다.
    """
    
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="세션 ID"
    )
    user = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        null=True,
        blank=True,
        verbose_name="사용자"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 시각"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="마지막 업데이트 시각"
    )
    
    class Meta:
        db_table = "mai_chat_session"
        verbose_name = "채팅 세션"
        verbose_name_plural = "채팅 세션"
        ordering = ["-updated_at"]
    
    def __str__(self) -> str:
        user_str = self.user.user.username if self.user else "익명"
        return f"{user_str} - {self.session_id}"

class ChatMessage(models.Model):
    """
    채팅 메시지 모델
    
    개별 채팅 메시지와 AI 응답을 저장합니다.
    """
    
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="채팅 세션"
    )
    user_message = models.TextField(
        verbose_name="사용자 질문"
    )
    ai_response = models.TextField(
        verbose_name="AI 응답"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 시각"
    )
    response_time = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="응답 시간 (밀리초)",
        help_text="AI 응답 생성에 걸린 시간"
    )
    
    class Meta:
        db_table = "mai_chat_message"
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지"
        ordering = ["created_at"]
    
    def __str__(self) -> str:
        # 질문이 길 경우 50자로 제한하여 표시
        question_preview = self.user_message[:50] + "..." if len(self.user_message) > 50 else self.user_message
        return f"{self.session.session_id} - {question_preview}"