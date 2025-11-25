"""
챗봇 기능 구현 - langchain
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage

# Django 모델 import (DB 저장용)
from django.contrib.auth import get_user_model
from .models import ChatSession, ChatMessage

User = get_user_model()
logger = logging.getLogger(__name__)

class MapleChatbot:
    """
    메이플스토리 챗봇 클래스
    - 모델 기반 대화 생성
    - 랭체인 메모리 관리
    - 세션 대화 기록 유지
    """
    def __init__(
            self,
            model_name: str = "Qwen/Qwen3-0.6B",
            session_id: Optional[str] = None,
            memory_type : str = "window",
            use_rag: bool = False,
            max_history: int = 10
    ):
        """
        Args:
            model_name (str): 사용할 사전학습 모델 이름
            session_id (Optional[str]): 세션 식별자
            memory_type (str): 메모리 유형 ("buffer" 또는 "window")
            max_history (int): 최대 대화 기록 수 (window 메모리용)
            use_rag (bool): RAG 엔진 사용 여부
        """
        
        self.model_name = model_name
        self.session_id = session_id
        self.memory_type = memory_type
        self.max_history = max_history

        # 모델 및 토크나이저
        self.model = None
        self.tokenizer = None

        # RAG 엔진
        self.rag_engine = None

        # 메모리
        self.memory = None

        # DB 세션 객체
        self.db_session = None

        # 초기화 상태
        self.is_initialized = False

    def initialize(self) -> bool:
        """
        모델과 메모리 초기화
        """
        try:
            logger.info(f"모델 로딩 중: {self.model_name}")
            # 토크나이저 및 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                toorch_dtype="auto",
                device_map="auto"
            )
            if self.memory_type == "buffer":
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
            else:
                self.memory = ConversationBufferWindowMemory(
                    memory_key="chat_history",
                    k=self.max_history,
                    return_messages=True
                )

            if self.use_rag:
                self._initialize_rag()
                

            self.is_initialized = True
            logger.info("모델 및 메모리 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"모델 초기화 오류: {e}")
            return False
        
    def _initialize_rag(self):
        """
        RAG 엔진 초기화 (추후 구현 예정)
        """
        pass
    
    def generate_response(self, user_input: str) -> Dict[str, any]:
        """
        사용자 입력에 대한 응답 생성

        Args:
            user_input (str): 사용자 질문

        Returns:
            {
                "response" : str, # 챗봇 응답
                "thinking_content": str, # 생각하는 내용 (있을 경우)
                "timestamp": str,
                "error": Optional[str] # 오류 메시지 (있을 경우)
                
            }
        """
        if not self.is_initialized:
            return {
                "response": "",
                "thinking_content": "",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "모델이 초기화되지 않았습니다."
            }
        
        try:
            # 1. RAG 엔진을 통한 정보 검색 (사용 시)
            context = ""
            if self.use_rag and self.rag_engine:
                context = self._get_rag_context(user_input)

            # 2. 대화 기록 업데이트
            history = self._get_conversation_history()

            # 3. 프롬프트 구성
            prompt = self._build_prompt(user_input, history, context)

            # 4. 모델 추론
            response, thinking_content = self._generate_response(prompt)

            # 5. 메모리에 저장
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response)

            return {
                "response": response,
                "thinking_content": thinking_content,
                "timestamp": datetime.utcnow().isoformat(),
                "error": None
            }
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return {
                "response": "",
                "thinking_content": "",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    def _get_rag_context(self, user_input: str) -> str:
        """
        RAG 엔진을 사용하여 관련 컨텍스트 검색 (추후 구현 예정)

        Args:
            user_input (str): 사용자 질문

        Returns:
            str: 검색된 컨텍스트
        """
        # 추후 RAG 엔진 구현
        return ""
    
    def _get_conversation_history(self) -> List[Dict[str, str]]:
        """메모리에서 대화 기록 가져오기"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history
    
    def _build_prompt(
            self,
            user_input: str,
            history: List[Dict[str, str]],
            context: str = ""
    ) -> str:
        """프롬프트 구성"""
        messages = []

        # 시스템 프롬프트
        system_prompt = """당신은 메이플스토리 전문 도우미입니다.
        메이플스토리 게임에 대한 질문에 친절하고 정확하게 답변해주세요
        """
        
        if context:
            system_prompt += f"\n추가 컨텍스트 정보:\n{context}"
        
        messages.append({"role": "system", "content": system_prompt})
    
        messages.extend(history)

        # 현재 사용자 메세지
        messages.append({"role": "user", "content": user_input})

        return messages
    
    def _generate_response(self, messages: List[Dict[str, str]]) -> tuple[str, str]:
        """모델을 사용하여 응답 생성"""
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        # 모델 입력 준비
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # 생성
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512,  # 적절한 길이로 조정
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        # 출력 파싱
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        
        # Thinking content 분리
        try:
            # </think> 토큰 찾기 (151668)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0
        
        thinking_content = self.tokenizer.decode(
            output_ids[:index],
            skip_special_tokens=True
        ).strip()
        
        response = self.tokenizer.decode(
            output_ids[index:],
            skip_special_tokens=True
        ).strip()
        
        return response, thinking_content
    
    def clear_history(self):
        """대화 기록 초기화"""
        if self.memory:
            self.memory.clear()
            logger.info("대화 기록이 초기화되었습니다.")

    def get_history(self) -> List[Dict[str, str]]:
        """대화 기록 가져오기"""
        if self.memory:
            return self._get_conversation_history()
        return []
    
    def load_history_from_db(self, messages: List[Dict[str, str]]):
        """
        DB에서 로드한 대화 기록을 메모리에 적재
        
        Args:
            messages: [{"role": "user/assistant", "content": "..."}]
        """
        if not self.memory:
            return
        
        for msg in messages:
            if msg["role"] == "user":
                self.memory.chat_memory.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self.memory.chat_memory.add_ai_message(msg["content"])
        
        logger.info(f"DB에서 {len(messages)}개 메시지 로드 완료")
    
    def save_message_to_db(self, user_input: str, bot_response: str):
        """
        대화 메시지를 DB에 저장
        
        Args:
            user_input: 사용자 입력
            bot_response: 챗봇 응답
        """
        if not self.db_session:
            logger.warning("DB 세션이 없어서 저장할 수 없습니다.")
            return
        
        try:
            # 사용자 메시지 저장
            ChatMessage.objects.create(
                session=self.db_session,
                content=user_input,
                is_user=True
            )
            
            # AI 응답 저장
            ChatMessage.objects.create(
                session=self.db_session,
                content=bot_response,
                is_user=False
            )
            
            logger.info(f"세션 {self.session_id}: 메시지 DB 저장 완료")
            
        except Exception as e:
            logger.error(f"DB 저장 실패: {str(e)}")
    
    def get_model_info(self) -> Dict[str, any]:
        """모델 정보 반환"""
        return {
            "model_name": self.model_name,
            "session_id": self.session_id,
            "use_rag": self.use_rag,
            "memory_type": self.memory_type,
            "is_initialized": self.is_initialized,
            "history_length": len(self.memory.chat_memory.messages) if self.memory else 0
        }


# 챗봇 인스턴스 관리 (싱글톤 패턴)
_chatbot_instances = {}


def get_chatbot(session_id: str, user_id: Optional[int] = None, **kwargs) -> MapleChatbot:
    """
    세션별 챗봇 인스턴스 가져오기 (캐싱)
    
    Args:
        session_id: 세션 ID
        user_id: Django User ID (DB 저장용)
        **kwargs: MapleChatbot 생성자 인자
        
    Returns:
        MapleChatbot 인스턴스
    """
    if session_id not in _chatbot_instances:
        chatbot = MapleChatbot(session_id=session_id, **kwargs)
        chatbot.initialize()
        
        # DB 세션 연결
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                db_session, created = ChatSession.objects.get_or_create(
                    id=session_id,
                    defaults={'user': user}
                )
                chatbot.db_session = db_session
                
                # 기존 대화 기록 로드
                if not created:
                    messages = []
                    for msg in db_session.messages.all():
                        role = "user" if msg.is_user else "assistant"
                        messages.append({"role": role, "content": msg.content})
                    chatbot.load_history_from_db(messages)
                    logger.info(f"세션 {session_id}: 기존 대화 {len(messages)}개 로드")
                
            except User.DoesNotExist:
                logger.warning(f"사용자 ID {user_id} 없음")
        
        _chatbot_instances[session_id] = chatbot
        logger.info(f"새 챗봇 인스턴스 생성: {session_id}")
    
    return _chatbot_instances[session_id]


def clear_chatbot(session_id: str):
    """챗봇 인스턴스 제거"""
    if session_id in _chatbot_instances:
        del _chatbot_instances[session_id]
        logger.info(f"챗봇 인스턴스 제거: {session_id}")


# 테스트 함수
def test_chatbot():
    """챗봇 기본 테스트"""
    print("=" * 50)
    print("메이플스토리 챗봇 테스트")
    print("=" * 50)
    
    chatbot = MapleChatbot(model_name="Qwen/Qwen3-0.6B", memory_type="window", max_history=5)
    
    if not chatbot.initialize():
        print("초기화 실패")
        return
    
    test_messages = [
        "메이플스토리가 뭐야?",
        "어떤 직업이 있어?",
        "레벨업은 어떻게 해?"
    ]
    
    for msg in test_messages:
        print(f"\n사용자: {msg}")
        result = chatbot.chat(msg)
        
        if result["thinking"]:
            print(f"[사고 과정]: {result['thinking']}")
        
        print(f"챗봇: {result['response']}")
        
        if result["error"]:
            print(f"오류: {result['error']}")
    
    print("\n대화 기록:")
    for i, msg in enumerate(chatbot.get_history(), 1):
        print(f"{i}. [{msg['role']}] {msg['content']}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_chatbot()
