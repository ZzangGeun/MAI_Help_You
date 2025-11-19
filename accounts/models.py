# accounts/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Django의 기본 User 모델을 확장하는 프로필 모델입니다.
    메이플스토리 관련 추가 정보를 저장합니다.
    """
    user = models.OneToOneField()