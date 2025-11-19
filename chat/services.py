from services.ai_models.fastapi_model.model import load_model, ask_question
from django.conf import settings
from .chat_session import ChatSessionManager
from .rag_engine import RagEngine
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 모델 초기화 (처음 한 번만 실행)
_model_loaded = False
_rag_engine = None

def initialize_services():
    """서비스 초기화 - 모델과 RAG 엔진 로드"""
    global _model_loaded, _rag_engine
    
    if not _model_loaded:
        try:
            success = load_model()
            if success:
                _model_loaded = True
                logger.info("Model loaded successfully")
            else:
                logger.error("Failed to load model")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    # RAG 엔진 초기화 (선택적)
    if _rag_engine is None:
        try:
            _rag_engine = RagEngine()
            logger.info("RAG engine initialized successfully")
        except Exception as e:
            logger.warning(f"RAG engine initialization failed: {str(e)}")
            # RAG 엔진 실패해도 계속 진행 (선택적 기능)
    
    return True

def get_chatbot_response(question, use_rag=False, top_k=3):
    """
    챗봇 응답 생성 함수
    
    Args:
        question (str): 사용자 질문
        use_rag (bool): RAG 사용 여부
        top_k (int): RAG 사용 시 검색할 문서 수
    
    Returns:
        str: 챗봇 응답
    """
    # 서비스 초기화 확인
    if not initialize_services():
        return "서비스 초기화에 실패했습니다."
    
    try:
        # RAG 사용하는 경우
        if use_rag and _rag_engine:
            try:
                # RAG로 관련 문서 검색
                relevant_docs = _rag_engine.search(question, top_k=top_k)
                
                # 컨텍스트와 함께 질문 구성
                context = "\n".join([doc.page_content for doc in relevant_docs])
                enhanced_question = f"""다음 컨텍스트를 참고하여 질문에 답변해주세요.

컨텍스트:
{context}

질문: {question}

답변:"""
                
                response = ask_question(enhanced_question)
                logger.info(f"RAG-enhanced response generated for: {question[:50]}...")
                
            except Exception as rag_error:
                logger.warning(f"RAG failed, using direct model: {str(rag_error)}")
                response = ask_question(question)
        else:
            # 직접 모델 호출
            response = ask_question(question)
            logger.info(f"Direct model response generated for: {question[:50]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

def create_chat_session(user=None, session_id=None):
    """
    새로운 채팅 세션 생성
    
    Args:
        user: Django User 객체 (선택적)
        session_id: 기존 세션 ID (선택적)
    
    Returns:
        ChatSessionManager: 세션 관리자 인스턴스
    """
    try:
        # 서비스 초기화 확인
        initialize_services()
        
        session_manager = ChatSessionManager(session_id=session_id, user=user)
        session_manager.initialize_session()
        
        logger.info(f"Chat session created: {session_manager.session_id}")
        return session_manager
        
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise

def process_chat_message(message, session_manager=None, user=None, session_id=None):
    """
    채팅 메시지 처리 (세션 관리 포함)
    
    Args:
        message (str): 사용자 메시지
        session_manager: 기존 세션 관리자 (선택적)
        user: Django User 객체 (선택적)
        session_id: 세션 ID (선택적)
    
    Returns:
        dict: 응답과 세션 정보
    """
    try:
        # 세션 관리자가 없으면 새로 생성
        if not session_manager:
            session_manager = create_chat_session(user=user, session_id=session_id)
        
        # 메시지 처리
        response = session_manager.process_message(message)
        
        return {
            'response': response,
            'session_id': session_manager.session_id,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return {
            'response': f"메시지 처리 중 오류가 발생했습니다: {str(e)}",
            'session_id': session_id,
            'success': False
        }

# 서비스 초기화 (모듈 로드 시 실행)
initialize_services()
