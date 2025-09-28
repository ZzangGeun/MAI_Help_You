# chat_session.py
from langchain.memory import ConversationBufferMemory
from services.ai_models.fastapi_model.model import load_model, ask_question
from .chain_builder import build_conversation_chain
from .models import ChatSession, ChatMessage
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatSessionManager:
    """챗봇 세션 관리를 위한 클래스"""
    
    def __init__(self, session_id=None, user=None):
        self.session_id = session_id
        self.user = user
        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = None
        self.db_session = None
        
    def initialize_session(self):
        """세션 초기화 및 DB 저장"""
        if self.user and not self.session_id:
            # DB에 새 유저 세션 생성
            self.db_session = ChatSession.objects.create(user=self.user)
            self.session_id = self.db_session.id
            logger.info(f"새로운 유저 채팅 세션 생성: {self.session_id}")
            return self.session_id
            
        elif self.session_id:
            # 기존 세션 로드
            try:
                self.db_session = ChatSession.objects.get(id=self.session_id)
                # 기존 대화 메시지 로드
                messages = ChatMessage.objects.filter(session=self.db_session).order_by('created_at')
                for msg in messages:
                    if msg.is_user:
                        self.memory.chat_memory.add_user_message(msg.content)
                    else:
                        self.memory.chat_memory.add_ai_message(msg.content)
                logger.info(f"기존 채팅 세션 로드: {self.session_id}")
                return self.session_id
            except ChatSession.DoesNotExist:
                logger.warning(f"Session {self.session_id} not found, creating new")
                # 세션 ID를 None으로 설정하고 새로 생성
                self.session_id = None
                return self.initialize_session()
        else:
            # 익명 세션 처리
            self.db_session = ChatSession.objects.create()
            self.session_id = self.db_session.id
            logger.info(f"새로운 익명 채팅 세션 생성: {self.session_id}")
            return self.session_id
    
    def build_chain(self):
        """Langchain 체인 구성"""
        if not self.chain:
            self.chain = build_conversation_chain(memory=self.memory)
        return self.chain
    
    def process_message(self, user_message):
        """사용자 메시지 처리 및 응답 생성"""
        if not self.chain:
            self.build_chain()
            
        if not self.chain:
            logger.error("Failed to build chain")
            return "죄송합니다. 서비스 초기화에 실패했습니다."
            
        # DB에 사용자 메시지 저장
        if self.db_session:
            ChatMessage.objects.create(
                session=self.db_session,
                content=user_message,
                is_user=True
            )
        
        # 응답 생성
        try:
            # Langchain 체인을 사용하여 응답 생성
            response = self.chain.run(input=user_message)
            
            # DB에 AI 응답 저장
            if self.db_session:
                ChatMessage.objects.create(
                    session=self.db_session,
                    content=response,
                    is_user=False
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # 체인이 실패하면 직접 모델 호출
            try:
                fallback_response = ask_question(user_message)
                
                # DB에 AI 응답 저장 (fallback)
                if self.db_session:
                    ChatMessage.objects.create(
                        session=self.db_session,
                        content=fallback_response,
                        is_user=False
                    )
                
                return fallback_response
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return f"죄송합니다, 오류가 발생했습니다: {str(e)}"


# 호환성을 위한 함수들 (기존 코드에서 사용할 수 있도록)
def initialize_chat_session(user=None, session_id=None):
    """호환성을 위한 함수 - ChatSessionManager 사용을 권장"""
    manager = ChatSessionManager(session_id=session_id, user=user)
    session_id = manager.initialize_session()
    return manager.memory, manager.db_session


def build_chain(memory):
    """체인 빌드 함수"""
    return build_conversation_chain(memory=memory)

