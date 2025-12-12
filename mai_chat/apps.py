# -*- coding: utf-8 -*-
"""
MAI Chat App Configuration

Django 앱 설정 및 초기화
"""

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MaiChatConfig(AppConfig):
    """
    MAI Chat 앱 설정 클래스
    
    앱 시작 시 AI 모델을 한 번만 로드하여 메모리에 유지합니다.
    """
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "mai_chat"
    verbose_name = "MAI 채팅"
    
    def ready(self) -> None:
        """
        Django 앱이 준비되었을 때 호출되는 메서드
        
        AI 모델을 메모리에 로드합니다.
        이렇게 하면 서버 시작 시 한 번만 로드되고,
        각 요청마다 로드하는 오버헤드를 피할 수 있습니다.
        """
        # runserver 재시작 시 중복 로딩 방지
        # Django의 autoreload 기능이 코드를 두 번 실행할 수 있음
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            self._load_ai_model()
    
    def _load_ai_model(self) -> None:
        """AI 모델을 로드합니다."""
        try:
            logger.info("AI 모델 로딩 시작...")
            
            from services.ai_models.fastapi_model.model import load_model, model, tokenizer
            
            # 모델이 이미 로드되어 있는지 확인
            if model is not None and tokenizer is not None:
                logger.info("AI 모델이 이미 로드되어 있습니다.")
                return
            
            # 모델 로드
            success = load_model()
            
            if success:
                logger.info("✅ AI 모델 로딩 완료!")
            else:
                logger.error("❌ AI 모델 로딩 실패")
        
        except Exception as e:
            logger.error(f"AI 모델 로딩 중 오류 발생: {str(e)}", exc_info=True)
            # 앱 시작은 계속되도록 예외를 발생시키지 않음
