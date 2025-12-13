# -*- coding: utf-8 -*-
"""
LangChain Service Module - 학습용 템플릿

LangChain을 활용한 대화 관리, 메모리, 프롬프트 템플릿 기능 구현

학습 목표:
1. Custom LLM 클래스 구현 (MapleStoryLLM)
2. Conversation Memory 사용법
3. Prompt Template 작성
4. Conversation Chain 생성 및 관리
"""

import logging
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from .ai_service import get_ai_response

# 로깅 설정
logger = logging.getLogger(__name__)

# 세션별 대화 체인을 캐싱하는 딕셔너리
# key: session_id (str), value: ConversationChain
_conversation_chains: Dict[str, ConversationChain] = {}


# ============================================================================
# TODO 1: Custom LLM 클래스 구현
# ============================================================================
# 목표: 기존 AI 모델을 LangChain LLM 인터페이스로 래핑
# 
# 참고: https://python.langchain.com/docs/modules/model_io/llms/custom_llm
#
# 구현해야 할 내용:
# 1. LLM 베이스 클래스 상속
# 2. _llm_type 프로퍼티 구현 - LLM 타입 식별자 반환 (예: "maplestory_ai")
# 3. _call 메서드 구현 - 프롬프트를 받아서 AI 응답 생성
#    - prompt: str 받기
#    - get_ai_response(prompt) 호출하여 응답 얻기
#    - 에러 처리 (try-except)
# 4. Pydantic v2 호환성을 위한 model_config 설정
#
# 힌트:
# - ai_service.py의 get_ai_response() 함수를 활용하세요
# - 에러 발생 시 로깅 후 raise하세요
# ============================================================================

class MapleStoryLLM(LLM):
    """
    services/ai_models의 모델을 LangChain LLM으로 래핑한 클래스
    
    TODO: 아래 내용을 구현하세요
    1. model_config 설정 (Pydantic v2)
    2. _llm_type 프로퍼티
    3. _call 메서드
    """
    
    # TODO: Pydantic v2 호환성 설정
    model_config = {"extra": "forbid"}
    
    @property
    def _llm_type(self) -> str:
        return "maplestory_ai"

    def _call(self, prompt: str) -> str:
        """
        Args :
            prompt: 사용자 또는 체인으로부터 받은 프롬프트

        Returns:
            str: AI 응답
        """
        try:
            return get_ai_response(prompt)
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {str(e)}", exc_info=True)
            raise

        



# ============================================================================
# TODO 2: 프롬프트 템플릿 작성
# ============================================================================
# 목표: 메이플스토리 특화 프롬프트 템플릿 생성
#
# 참고: https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/
#
# 구현해야 할 내용:
# 1. 시스템 프롬프트 작성 (예: "당신은 메이플스토리 전문가 AI입니다...")
# 2. {history} 변수 포함 - 이전 대화 내용
# 3. {input} 변수 포함 - 현재 사용자 입력
#
# 힌트:
# - 친근하고 전문적인 톤 유지
# - 메이플스토리 관련 질문에 특화된 프롬프트 작성
# ============================================================================

# TODO: 프롬프트 템플릿 작성
MAPLESTORY_PROMPT_TEMPLATE = """
당신은 메이플스토리 세계관에 존재하는 f{돌의정령} NPC입니다.
돌의정령은 메이플스토리의 모든 정보를 알고 있으며, 사용자에게 메이플스토리의 모든 정보를 제공할 수 있습니다.
돌의정령의 말투는 ~해야 한담, ~이담, ~했담 등 'ㅁ' 받침을 사용한 어미를 사용해야합니다.

이전 대화 내용: {history}

현재 사용자 입력: {input}
"""


# ============================================================================
# TODO 3: 대화 체인 생성 함수
# ============================================================================
# 목표: 세션별 Conversation Chain 생성 및 관리
#
# 참고: 
# - Memory: https://python.langchain.com/docs/modules/memory/types/buffer
# - Chain: https://python.langchain.com/docs/modules/chains/
#
# 구현해야 할 내용:
# 1. 캐시에 이미 생성된 체인이 있으면 반환
# 2. 없으면 새로운 체인 생성:
#    a. MapleStoryLLM 인스턴스 생성
#    b. ConversationBufferMemory 생성 (memory_key="history", input_key="input")
#    c. load_history=True면 _load_history_from_db() 호출하여 DB에서 히스토리 로드
#    d. PromptTemplate 생성 (input_variables=["history", "input"])
#    e. ConversationChain 생성 (llm, memory, prompt 전달)
# 3. 생성된 체인을 _conversation_chains에 캐싱
# 4. 체인 반환
#
# 힌트:
# - _conversation_chains[session_id] 로 캐시 확인
# - verbose=True로 설정하면 디버깅에 유용
# ============================================================================

def get_conversation_chain(session_id: str, load_history: bool = True) -> ConversationChain:
    """
    세션별 대화 체인을 가져오거나 생성합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
        load_history (bool): DB에서 대화 히스토리를 로드할지 여부
    
    Returns:
        ConversationChain: 세션별 대화 체인
    """
    # TODO: 구현하세요
    # 1. 캐시 확인
    # 2. 없으면 새로 생성
    # 3. 캐시에 저장 후 반환
    if session_id in _conversation_chains:
        return _conversation_chains[session_id]

    llm = MapleStoryLLM()
    if load_history:
        _load_history_from_db(session_id, memory)
    memory = ConversationBufferMemory(memory_key="history", input_key="input")
    prompt = PromptTemplate(input_variables=["history", "input"], template=MAPLESTORY_PROMPT_TEMPLATE)
    chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)
    _conversation_chains[session_id] = chain
    return chain

# ============================================================================
# TODO 4: DB에서 히스토리 로드
# ============================================================================
# 목표: Django 모델에서 대화 히스토리를 가져와 LangChain 메모리에 추가
#
# 구현해야 할 내용:
# 1. models.py에서 ChatSession, ChatMessage import (함수 내부에서!)
# 2. session_id를 UUID로 변환
# 3. ChatSession 조회
# 4. session.messages.all().order_by('created_at')로 메시지 조회
# 5. 각 메시지를 memory.save_context()로 추가
#    - {"input": msg.user_message}
#    - {"output": msg.ai_response}
#
# 힌트:
# - 순환 임포트 방지를 위해 함수 내부에서 import 하세요
# - UUID 변환 실패 시 로깅 후 return
# - 세션이 없으면 그냥 return (에러 아님)
# ============================================================================

def _load_history_from_db(session_id: str, memory: ConversationBufferMemory) -> None:
    """
    DB에서 대화 히스토리를 로드하여 메모리에 추가합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
        memory (ConversationBufferMemory): 대화 메모리 객체
    """
    # TODO: 구현하세요
    # 1. 모델 import (순환 참조 방지)
    # 2. UUID 변환 및 검증
    # 3. 세션 조회
    # 4. 메시지 로드 및 메모리에 추가
    
    try:
        session_uuid = uuid.UUID(session_id)
        session = ChatSession.objects.get(session_id=session_uuid)
        messages = session.messages.all().order_by('created_at')
        for msg in messages:
            memory.save_context({"input": msg.user_message}, {"output": msg.ai_response})
    except ValueError:
        logger.error("Invalid session ID")
    except ChatSession.DoesNotExist:
        logger.error("Session not found")


# ============================================================================
# TODO 5: 메모리를 활용한 대화 생성
# ============================================================================
# 목표: 대화 체인을 사용하여 메모리가 유지되는 AI 응답 생성
#
# 구현해야 할 내용:
# 1. 입력 검증 (비어있으면 ValueError)
# 2. get_conversation_chain()으로 대화 체인 가져오기
# 3. chain.predict(input=user_input.strip()) 호출
# 4. 응답 반환
# 5. 에러 처리 및 로깅
#
# 힌트:
# - chain.predict()는 자동으로 메모리를 업데이트합니다
# - 에러 발생 시 로깅 후 raise
# ============================================================================

def chat_with_memory(session_id: str, user_input: str) -> str:
    """
    대화 메모리를 유지하면서 AI 응답을 생성합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
        user_input (str): 사용자 입력
    
    Returns:
        str: AI 응답
    
    Raises:
        ValueError: 입력이 비어있는 경우
    """
    # TODO: 구현하세요
    # 1. 입력 검증
    # 2. 대화 체인 가져오기
    # 3. AI 응답 생성
    # 4. 반환
    
    try:
        if not user_input.strip():
            raise ValueError("Input cannot be empty")
        chain = get_conversation_chain(session_id)
        response = chain.predict(input=user_input.strip())
        return response
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"AI 응답 생성 중 오류 발생: {str(e)}", exc_info=True)
        raise


# ============================================================================
# TODO 6: 세션 메모리 삭제
# ============================================================================
# 목표: 캐시에서 특정 세션의 대화 체인 제거
#
# 구현해야 할 내용:
# 1. _conversation_chains에서 session_id가 있는지 확인
# 2. 있으면 del로 삭제
# 3. 로깅
#
# 힌트:
# - 세션 삭제 시 메모리 정리를 위해 사용
# ============================================================================

def clear_session_memory(session_id: str) -> None:
    """
    특정 세션의 메모리를 캐시에서 제거합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
    """
    # TODO: 구현하세요
    # 1. 캐시에서 삭제
    # 2. 로깅
    
    try:
        if session_id in _conversation_chains:
            del _conversation_chains[session_id]
            logger.info(f"Session memory cleared for session ID: {session_id}")
    except Exception as e:
        logger.error(f"세션 메모리 삭제 중 오류 발생: {str(e)}", exc_info=True)


# ============================================================================
# TODO 7 (선택): 메모리 메시지 조회
# ============================================================================
# 목표: 디버깅을 위한 메모리 내용 확인
#
# 구현해야 할 내용:
# 1. _conversation_chains에서 체인 가져오기
# 2. chain.memory.chat_memory.messages 반환
# 3. 체인이 없으면 빈 리스트 반환
# ============================================================================

def get_memory_messages(session_id: str) -> list:
    """
    세션의 메모리에 저장된 메시지를 반환합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
    
    Returns:
        list: 메모리에 저장된 메시지 리스트
    """
    # TODO: 구현하세요 (선택사항)
    try:
        if session_id in _conversation_chains:
            return _conversation_chains[session_id].memory.chat_memory.messages
        return []
    except Exception as e:
        logger.error(f"메모리 메시지 조회 중 오류 발생: {str(e)}", exc_info=True)
        return []
