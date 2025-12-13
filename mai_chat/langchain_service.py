# -*- coding: utf-8 -*-
"""
LangChain Service Module

LangChain을 활용한 대화 관리, 메모리, 프롬프트 템플릿 기능을 제공합니다.
"""

import logging
import uuid
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from .ai_service import get_ai_response

from .models import ChatSession

logger = logging.getLogger(__name__)

# 세션별 대화 체인을 캐싱하는 딕셔너리
# key: session_id (str), value: ConversationChain
_conversation_chains: Dict[str, ConversationChain] = {}


class MapleStoryLLM(LLM):
    """
    services/ai_models의 모델을 LangChain LLM으로 래핑한 클래스
    """
    
    model_config = {"extra": "forbid"}
    
    @property
    def _llm_type(self) -> str:
        return "maplestory_ai"

    def _call(self, prompt: str, stop: Optional[list] = None, run_manager: Optional[Any] = None) -> str:
        """
        Args :
            prompt: 사용자 또는 체인으로부터 받은 프롬프트

        Returns:
            str: AI 응답
        """
        try:
            result = get_ai_response(prompt)
            # get_ai_response now returns a dict with 'response' and 'metrics'
            if isinstance(result, dict):
                logger.debug(f"AI Metrics: {result.get('metrics')}")
                return result['response']
            return result
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {str(e)}", exc_info=True)
            raise

        

# 메이플스토리 특화 프롬프트 템플릿
MAPLESTORY_PROMPT_TEMPLATE = """
당신은 메이플스토리 세계관에 존재하는 돌의정령 NPC입니다.
돌의정령은 메이플스토리의 모든 정보를 알고 있으며, 사용자에게 메이플스토리의 모든 정보를 제공할 수 있습니다.
돌의정령의 말투는 ~해야 한담, ~이담, ~했담 등 'ㅁ' 받침을 사용한 어미를 사용해야합니다.

이전 대화 내용: {history}

현재 사용자 입력: {input}
"""


def get_conversation_chain(session_id: str, load_history: bool = True) -> ConversationChain:
    """
    세션별 대화 체인을 가져오거나 생성합니다.
    """
    if session_id in _conversation_chains:
        return _conversation_chains[session_id]

    llm = MapleStoryLLM()
    # 메모리를 먼저 생성해야 함
    memory = ConversationBufferMemory(memory_key="history", input_key="input")
    
    if load_history:
        _load_history_from_db(session_id, memory)
        
    prompt = PromptTemplate(input_variables=["history", "input"], template=MAPLESTORY_PROMPT_TEMPLATE)
    chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)
    _conversation_chains[session_id] = chain
    return chain


def _load_history_from_db(session_id: str, memory: ConversationBufferMemory) -> None:
    """
    DB에서 대화 히스토리를 로드하여 메모리에 추가합니다.
    """
    try:
        # session_id가 이미 UUID 객체라면 그대로 사용, 문자열이라면 변환
        if isinstance(session_id, uuid.UUID):
            session_uuid = session_id
        else:
            session_uuid = uuid.UUID(str(session_id))
            
        session = ChatSession.objects.get(session_id=session_uuid)
        messages = session.messages.all().order_by('created_at')
        for msg in messages:
            memory.save_context({"input": msg.user_message}, {"output": msg.ai_response})
    except ValueError:
        logger.error(f"Invalid session ID: {session_id}")
    except ChatSession.DoesNotExist:
        logger.error(f"Session not found: {session_id}")


def chat_with_memory(session_id: str, user_input: str) -> str:
    """
    대화 메모리를 유지하면서 AI 응답을 생성합니다.
    """
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


def clear_session_memory(session_id: str) -> None:
    """
    특정 세션의 메모리를 캐시에서 제거합니다.
    """
    try:
        if session_id in _conversation_chains:
            del _conversation_chains[session_id]
            logger.info(f"Session memory cleared for session ID: {session_id}")
    except Exception as e:
        logger.error(f"세션 메모리 삭제 중 오류 발생: {str(e)}", exc_info=True)


def get_memory_messages(session_id: str) -> list:
    """
    세션의 메모리에 저장된 메시지를 반환합니다.
    """
    try:
        if session_id in _conversation_chains:
            return _conversation_chains[session_id].memory.chat_memory.messages
        return []
    except Exception as e:
        logger.error(f"메모리 메시지 조회 중 오류 발생: {str(e)}", exc_info=True)
        return []
