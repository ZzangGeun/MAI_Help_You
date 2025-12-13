# -*- coding: utf-8 -*-
"""
AI Service Module - 학습용 템플릿

AI 모델을 호출하고 응답을 생성하는 서비스 레이어

학습 목표:
1. AI 모델 호출 및 응답 생성
2. 스레드 안전성(Thread-safe) 보장
3. 에러 핸들링 및 검증
"""

import logging
import time
from typing import Optional, Dict, Any
from threading import Lock

# AI 모델 임포트
from services.ai_models.fastapi_model.model import ask_question, model, tokenizer

# 로깅 설정
logger = logging.getLogger(__name__)


# ============================================================================
# TODO 1: 스레드 Lock 생성
# ============================================================================
# 목표: 멀티스레드 환경에서 AI 모델 동시 접근 방지
#
# 참고: https://docs.python.org/3/library/threading.html#lock-objects
#
# 구현해야 할 내용:
# - Lock() 객체 생성
#
# Why?: AI 모델은 GPU 메모리를 사용하므로 동시에 여러 요청이 들어오면
#       충돌이 발생할 수 있습니다. Lock을 사용하여 순차적으로 처리합니다.
# ============================================================================

# TODO: Lock 객체 생성
_model_lock = Lock()


# ============================================================================
# TODO 2: AI 응답 생성 함수
# ============================================================================
# 목표: AI 모델을 호출하여 질문에 대한 답변 생성
#
# 구현해야 할 내용:
# 1. 입력 검증
#    - question이 None이거나 빈 문자열이면 ValueError 발생
# 2. 모델 로드 확인
#    - model과 tokenizer가 None이면 RuntimeError 발생
# 3. Lock을 사용한 스레드 안전한 모델 호출
#    - with _model_lock: 블록 안에서 ask_question() 호출
# 4. 응답 검증
#    - 빈 응답이면 로깅 후 기본 메시지 반환
# 5. 에러 처리
#    - Exception 발생 시 로깅 후 RuntimeError로 래핑
#
# 힌트:
# - question.strip()으로 공백 제거
# - logger.error()로 에러 로깅 (exc_info=True로 스택 트레이스 포함)
# ============================================================================

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
    # TODO: 구현하세요
    # 1. 입력 검증
    # 2. 모델 로드 확인
    # 3. Lock 사용하여 AI 모델 호출
    # 4. 응답 검증 및 반환
    # 5. 에러 처리
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
    


# ============================================================================
# TODO 3: 응답 시간 측정 함수 (선택)
# ============================================================================
# 목표: AI 응답 생성 시간을 측정하여 성능 모니터링
#
# 구현해야 할 내용:
# 1. time.time()으로 시작 시간 기록
# 2. get_ai_response() 호출
# 3. 종료 시간 계산 (밀리초)
# 4. 딕셔너리로 응답과 응답 시간 반환
#    - {'response': ..., 'response_time': ...}
# 5. 에러 발생 시에도 응답 시간 로깅
#
# 힌트:
# - (time.time() - start_time) * 1000 으로 밀리초 계산
# - int()로 정수 변환
# ============================================================================

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
    # TODO: 구현하세요 (선택사항)
    # 1. 시작 시간 기록
    # 2. get_ai_response() 호출
    # 3. 응답 시간 계산
    # 4. 결과 반환
    
    import time
    start_time = time.time()
    response = get_ai_response(question)
    response_time = int((time.time() - start_time) * 1000)
    return {'response': response, 'response_time': response_time}


# ============================================================================
# TODO 4: 모델 로드 확인 함수 (선택)
# ============================================================================
# 목표: AI 모델이 정상적으로 로드되었는지 확인
#
# 구현해야 할 내용:
# - model과 tokenizer가 모두 None이 아니면 True, 아니면 False 반환
#
# 사용처:
# - 앱 시작 시 헬스체크
# - 에러 디버깅
# ============================================================================

def check_model_loaded() -> bool:
    """
    AI 모델이 정상적으로 로드되었는지 확인합니다.
    
    Returns:
        bool: 모델 로드 상태
    """
    # TODO: 구현하세요 (선택사항)
    if model is not None and tokenizer is not None:
        return True
    else:
        return False


# ============================================================================
# 학습 힌트
# ============================================================================
# 
# 1. Lock 사용 패턴:
#    with _model_lock:
#        # 이 블록은 한 번에 하나의 스레드만 실행 가능
#        result = some_function()
#
# 2. 에러 핸들링 패턴:
#    try:
#        result = risky_operation()
#    except SpecificError as e:
#        logger.error(f"Error: {e}", exc_info=True)
#        raise RuntimeError(f"Wrapped error: {e}")
#
# 3. 입력 검증 패턴:
#    if not input_value or not input_value.strip():
#        raise ValueError("Input is empty")
#
# ============================================================================
