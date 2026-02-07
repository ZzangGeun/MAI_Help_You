# -*- coding: utf-8 -*-
"""
MAI Chat Django Models

채팅 세션 및 메시지를 저장하는 Django 모델
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """
    하나의 대화방 만들기
    """
    session_id = models.UUIDField(
        primary_key = True,
        default = uuid.uuid4,
        editable = False,
        verbose_name = "세션 ID"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = "chat_sessions",
        null = True,
        blank = True,
        verbose_name = "사용자"
    )

    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.session_id[:8]}"

class ChatMessage(models.Model):
    """
    세션 내 메세지 저장
    """
    session_id = models.ForeignKey(
        ChatSession,
        on_delete = models.CASCADE,
        related_name = "messages",
        verbose_name = "세션"
    )

    user_message =models.TextField()
    ai_response = models.TextField()

    thinking = models.TextField(blank=True, null=True)

    response_time = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"Msg {self.id} in {str(self.session.session_id)[:8]}"
    


