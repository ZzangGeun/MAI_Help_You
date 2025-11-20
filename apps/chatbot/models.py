# models.py에 추가
from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    """채팅 세션 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True, blank=True,  # 익명 사용자 허용
        related_name='chat_sessions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat {self.id} - {'Anonymous' if not self.user else self.user.username}"

class ChatMessage(models.Model):
    """채팅 메시지 모델"""
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True: 사용자, False: AI
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender = "User" if self.is_user else "AI"
        return f"{sender}: {self.content[:30]}..."