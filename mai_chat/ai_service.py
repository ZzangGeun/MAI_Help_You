# -*- coding: utf-8 -*-
"""
AI Service Module

AI 모델을 호출하고 응답을 생성하는 서비스 레이어입니다.
"""

import logging
import time
from typing import Optional, Dict, Any
from threading import Lock

# AI 모델 임포트
from services.ai_models.fastapi_model.model import ask_question, model, tokenizer

# 로깅 설정
logger = logging.getLogger(__name__)

# 모델 접근을 제어하는 Lock 객체
_model_lock = Lock()


# 성능 측정 데코레이터
def measure_performance(func):
    def wrapper(question: str, *args, **kwargs):
        start_time = time.time()
        
        # 입력 토큰 계산
        prompt_tokens = 0
        if tokenizer:
            prompt_tokens = len(tokenizer.encode(question))
            
        try:
            # 원본 함수 실행 (문자열 반환)
            response_text = func(question, *args, **kwargs)
            
            # 출력 토큰 계산
            completion_tokens = 0
            if tokenizer:
                completion_tokens = len(tokenizer.encode(response_text))
                
            execution_time = int((time.time() - start_time) * 1000)
            
            # 메트릭 로깅
            logger.info(
                f"Performance: time={execution_time}ms, "
                f"prompt={prompt_tokens}, completion={completion_tokens}, "
                f"total={prompt_tokens + completion_tokens}"
            )
            
            return {
                'response': response_text,
                'metrics': {
                    'response_time': execution_time,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise e
            
    return wrapper

@measure_performance
def get_ai_response(question: str) -> Dict[str, Any]:
    """
    AI 모델을 사용하여 질문에 대한 답변을 생성합니다.
    @measure_performance 데코레이터가 적용되어 있어, 
    반환값은 딕셔너리 형태({'response': str, 'metrics': dict})입니다.
    """
    if not question or not question.strip():
        raise ValueError("질문이 비어있거나 None입니다.")

    if model is None or tokenizer is None:
        raise RuntimeError("AI 모델이 로드되지 않았습니다.")

    with _model_lock:
        try:
            response = ask_question(question)
            if not response or not response.strip():
                raise ValueError("AI 모델이 빈응답을 반환했습니다.")
            else:
                return response
        except Exception as e:
            logger.error(f"AI 응답 생성 중 오류: {str(e)}", exc_info=True)
            raise RuntimeError(f"AI 응답 생성 중 오류: {str(e)}")
    


def get_ai_response_with_timing(question: str) -> Dict[str, Any]:
    """호환성을 위한 래퍼 함수입니다."""
    result = get_ai_response(question)
    return {
        'response': result['response'],
        'response_time': result['metrics']['response_time']
    }


def check_model_loaded() -> bool:
    """
    AI 모델이 정상적으로 로드되었는지 확인합니다.
    """
    if model is not None and tokenizer is not None:
        return True
    else:
        return False
