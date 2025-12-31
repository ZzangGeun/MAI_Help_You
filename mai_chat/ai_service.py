# -*- coding: utf-8 -*-
"""
AI Service Module

services/ai_models의 AI 모델을 래핑하는 서비스 레이어
멀티스레딩 안전성과 에러 핸들링을 제공합니다.
"""

import logging
import time
from typing import Optional, Dict, Any
from threading import Lock

# AI 모델 임포트
from services.ai_models.fastapi_model.model import ask_question, model, tokenizer

# 로깅 설정
logger = logging.getLogger(__name__)

# 스레드 안전성을 위한 Lock
_model_lock = Lock()


def get_ai_response(question: str) -> str:
    """
    AI 모델을 사용하여 질문에 대한 답변을 생성합니다.
    
    Args:
        question (str): 사용자 질문
    
    Returns:
        str: AI 생성 응답
    
    Raises:
        ValueError: 질문이 비어있거나 None인 경우
        RuntimeError: AI 모델이 로드되지 않은 경우
    """
    # 입력 검증
    if not question or not question.strip():
        raise ValueError("질문이 비어있습니다.")
    
    # 모델 로드 확인
    if model is None or tokenizer is None:
        raise RuntimeError("AI 모델이 로드되지 않았습니다. 앱 초기화를 확인하세요.")
    
    try:
        # 스레드 안전성을 위한 Lock 사용
        # 멀티 요청 시 모델 접근이 순차적으로 이루어지도록 함
        with _model_lock:
            response = ask_question(question.strip())
        
        if not response:
            logger.warning(f"AI 모델이 빈 응답을 반환했습니다. 질문: {question[:50]}...")
            return "죄송합니다. 답변을 생성할 수 없습니다."
        
        return response
    
    except Exception as e:
        logger.error(f"AI 응답 생성 중 오류 발생: {str(e)}", exc_info=True)
        raise RuntimeError(f"AI 응답 생성 실패: {str(e)}")


def get_ai_response_with_timing(question: str) -> Dict[str, Any]:
    """
    AI 응답을 생성하고 응답 시간을 측정합니다.
    
    Args:
        question (str): 사용자 질문
    
    Returns:
        Dict[str, Any]: {
            'response': AI 생성 응답,
            'response_time': 응답 시간 (밀리초)
        }
    
    Raises:
        ValueError: 질문이 비어있거나 None인 경우
        RuntimeError: AI 모델 오류
    """
    start_time = time.time()
    
    try:
        response = get_ai_response(question)
        elapsed_time = int((time.time() - start_time) * 1000)  # 밀리초로 변환
        
        return {
            'response': response,
            'response_time': elapsed_time
        }
    
    except Exception as e:
        # 오류가 발생해도 응답 시간은 기록
        elapsed_time = int((time.time() - start_time) * 1000)
        logger.error(f"응답 생성 실패 (소요 시간: {elapsed_time}ms): {str(e)}")
        raise


def check_model_loaded() -> bool:
    """
    AI 모델이 정상적으로 로드되었는지 확인합니다.
    
    Returns:
        bool: 모델 로드 상태
    """
    return model is not None and tokenizer is not None
