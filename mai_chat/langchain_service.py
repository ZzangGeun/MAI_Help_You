# -*- coding: utf-8 -*-
"""
LangChain Service Module

LangChain을 활용한 대화 관리, 메모리, 프롬프트 템플릿 기능 구현
"""

import logging
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from pydantic import Field

from .ai_service import get_ai_response

# 로깅 설정
logger = logging.getLogger(__name__)

# 세션별 대화 체인을 캐싱하는 딕셔너리
# key: session_id (str), value: ConversationChain
_conversation_chains: Dict[str, ConversationChain] = {}


class MapleStoryLLM(LLM):
    """
    services/ai_models의 모델을 LangChain LLM으로 래핑한 클래스
    
    LangChain의 LLM 인터페이스를 구현하여 기존 AI 모델을
    LangChain 생태계에서 사용할 수 있도록 합니다.
    """
    
    # Pydantic v2 호환성을 위한 설정
    model_config = {"extra": "forbid"}
    
    @property
    def _llm_type(self) -> str:
        """LLM 타입 식별자를 반환합니다."""
        return "maplestory_ai"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        프롬프트를 받아 AI 응답을 생성합니다.
        
        Args:
            prompt (str): 입력 프롬프트
            stop (Optional[list]): 생성 중단 토큰 리스트 (현재 미사용)
            run_manager (Optional[Any]): 실행 관리자 (현재 미사용)
        
        Returns:
            str: AI 생성 응답
        """
        try:
            response = get_ai_response(prompt)
            return response
        except Exception as e:
            logger.error(f"LangChain LLM 호출 중 오류: {str(e)}", exc_info=True)
            raise


# 메이플스토리 특화 프롬프트 템플릿
MAPLESTORY_PROMPT_TEMPLATE = """당신은 메이플스토리 전문가 AI 어시스턴트입니다.
사용자의 메이플스토리 관련 질문에 친절하고 정확하게 답변해주세요.

이전 대화 내용:
{history}

사용자: {input}
AI 어시스턴트:"""


def get_conversation_chain(session_id: str, load_history: bool = True) -> ConversationChain:
    """
    세션별 대화 체인을 가져오거나 생성합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
        load_history (bool): DB에서 대화 히스토리를 로드할지 여부
    
    Returns:
        ConversationChain: 세션별 대화 체인
    """
    # 이미 생성된 체인이 있으면 반환
    if session_id in _conversation_chains:
        return _conversation_chains[session_id]
    
    # 새로운 체인 생성
    llm = MapleStoryLLM()
    
    # 대화 메모리 생성
    memory = ConversationBufferMemory(
        memory_key="history",
        input_key="input"
    )
    
    # DB에서 이전 대화 히스토리 로드
    if load_history:
        _load_history_from_db(session_id, memory)
    
    # 프롬프트 템플릿 생성
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=MAPLESTORY_PROMPT_TEMPLATE
    )
    
    # 대화 체인 생성
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=False  # 프로덕션에서는 False, 디버깅 시 True
    )
    
    # 캐시에 저장
    _conversation_chains[session_id] = chain
    
    logger.info(f"새로운 대화 체인 생성: session_id={session_id}")
    
    return chain


def _load_history_from_db(session_id: str, memory: ConversationBufferMemory) -> None:
    """
    DB에서 대화 히스토리를 로드하여 메모리에 추가합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
        memory (ConversationBufferMemory): 대화 메모리 객체
    """
    try:
        from .models import ChatSession, ChatMessage
        import uuid
        
        # UUID 변환
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            logger.warning(f"잘못된 세션 ID 형식: {session_id}")
            return
        
        # 세션 존재 확인
        try:
            session = ChatSession.objects.get(session_id=session_uuid)
        except ChatSession.DoesNotExist:
            logger.info(f"세션을 찾을 수 없음: {session_id}")
            return
        
        # 대화 히스토리 로드 (시간순)
        messages = session.messages.all().order_by('created_at')
        
        for msg in messages:
            # 메모리에 대화 추가
            memory.save_context(
                {"input": msg.user_message},
                {"output": msg.ai_response}
            )
        
        logger.info(f"세션 {session_id}의 대화 히스토리 {messages.count()}개 로드 완료")
    
    except Exception as e:
        logger.error(f"대화 히스토리 로드 중 오류: {str(e)}", exc_info=True)


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
    if not user_input or not user_input.strip():
        raise ValueError("사용자 입력이 비어있습니다.")
    
    try:
        # 대화 체인 가져오기
        chain = get_conversation_chain(session_id)
        
        # AI 응답 생성 (메모리 자동 업데이트)
        response = chain.predict(input=user_input.strip())
        
        return response
    
    except Exception as e:
        logger.error(f"대화 생성 중 오류 (session={session_id}): {str(e)}", exc_info=True)
        raise


def clear_session_memory(session_id: str) -> None:
    """
    특정 세션의 메모리를 캐시에서 제거합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
    """
    if session_id in _conversation_chains:
        del _conversation_chains[session_id]
        logger.info(f"세션 메모리 삭제: {session_id}")


def get_memory_messages(session_id: str) -> list:
    """
    세션의 메모리에 저장된 메시지를 반환합니다.
    
    Args:
        session_id (str): 채팅 세션 ID
    
    Returns:
        list: 메모리에 저장된 메시지 리스트
    """
    if session_id not in _conversation_chains:
        return []
    
    chain = _conversation_chains[session_id]
    memory = chain.memory
    
    # 메모리의 대화 히스토리 가져오기
    return memory.chat_memory.messages
