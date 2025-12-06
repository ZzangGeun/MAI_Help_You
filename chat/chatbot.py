"""
챗봇 기능 구현 - Mock Version (API 개발용)
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Django 모델 import (DB 저장용)
from django.contrib.auth import get_user_model
from .models import ChatSession, ChatMessage

User = get_user_model()
logger = logging.getLogger(__name__)

class MapleChatbot:
    """
    메이플스토리 챗봇 클래스 (Mock)
    """
    def __init__(
            self,
            model_name: str = "MockModel",
            session_id: Optional[str] = None,
            memory_type : str = "window",
            use_rag: bool = False,
            max_history: int = 10
    ):
        self.model_name = model_name
        self.session_id = session_id
        self.memory_type = memory_type
        self.max_history = max_history
        self.db_session = None
        self.is_initialized = False
        self.history = []

    def initialize(self) -> bool:
        self.is_initialized = True
        logger.info("Mock 모델 초기화 완료")
        return True
        
    def generate_response(self, user_input: str) -> Dict[str, any]:
        if not self.is_initialized:
            return {"response": "", "error": "모델 미초기화"}
        
        # Mock 응답 생성
        response = f"'{user_input}'에 대한 Mock 응답입니다. (메이플스토리 챗봇)"
        thinking_content = "Mock 생각 중..."
        
        # Mock 메모리 저장
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})

        return {
            "response": response,
            "thinking_content": thinking_content,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None
        }
    
    def clear_history(self):
        self.history = []
        logger.info("대화 기록 초기화")

    def get_history(self) -> List[Dict[str, str]]:
        return self.history
    
    def load_history_from_db(self, messages: List[Dict[str, str]]):
        self.history = messages
        logger.info(f"DB에서 {len(messages)}개 메시지 로드 완료")
    
    def save_message_to_db(self, user_input: str, bot_response: str):
        if not self.db_session:
            return
        try:
            ChatMessage.objects.create(
                session=self.db_session,
                content=user_input,
                is_user=True
            )
            ChatMessage.objects.create(
                session=self.db_session,
                content=bot_response,
                is_user=False
            )
        except Exception as e:
            logger.error(f"DB 저장 실패: {str(e)}")

# 챗봇 인스턴스 관리
_chatbot_instances = {}

def get_chatbot(session_id: str, user_id: Optional[int] = None, **kwargs) -> MapleChatbot:
    if session_id not in _chatbot_instances:
        chatbot = MapleChatbot(session_id=session_id, **kwargs)
        chatbot.initialize()
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                try:
                    sid = int(session_id)
                    db_session, created = ChatSession.objects.get_or_create(
                        id=sid,
                        defaults={'user': user}
                    )
                    chatbot.db_session = db_session
                    
                    if not created:
                        messages = []
                        for msg in db_session.messages.all():
                            role = "user" if msg.is_user else "assistant"
                            messages.append({"role": role, "content": msg.content})
                        chatbot.load_history_from_db(messages)
                except ValueError:
                    pass
            except User.DoesNotExist:
                pass
        
        _chatbot_instances[session_id] = chatbot
    
    return _chatbot_instances[session_id]

def clear_chatbot(session_id: str):
    if session_id in _chatbot_instances:
        del _chatbot_instances[session_id]