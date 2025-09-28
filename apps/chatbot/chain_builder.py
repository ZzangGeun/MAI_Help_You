# chain_builder.py
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional
from services.ai_models.fastapi_model.model import load_model, ask_question
import logging

logger = logging.getLogger(__name__)

class QwenCustomLLM(LLM):
    """Langchain과 호환되는 Qwen 모델의 래퍼 클래스"""
    
    def __init__(self):
        """모델 초기화"""
        super().__init__()
        success = load_model()
        if not success:
            logger.error("Failed to load model")
            raise ValueError("Model loading failed")
            
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """질문에 대한 응답을 생성합니다."""
        response = ask_question(prompt)
        
        # stop 시퀀스 처리 (있는 경우)
        if stop:
            for sequence in stop:
                if sequence in response:
                    response = response[:response.find(sequence)]
                    
        return response
        
    @property
    def _llm_type(self) -> str:
        """LLM 타입 반환"""
        return "qwen-custom"
        
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """모델 식별 파라미터"""
        return {"name": "qwen-custom-model"}

def create_llm_from_local_model():
    """로컬 모델을 사용하여 LangChain 호환 LLM 생성"""
    try:
        return QwenCustomLLM()
    except Exception as e:
        logger.error(f"Error creating LLM: {str(e)}")
        return None

def build_conversation_chain(memory=None):
    """대화 체인 구성"""
    llm = create_llm_from_local_model()
    
    if not llm:
        logger.error("Failed to create LLM")
        return None
    
    template = """당신은 도움을 주는 AI 어시스턴트입니다.
    
    현재 대화 기록:
    {history}
    
    인간: {input}
    AI: """
    
    prompt = PromptTemplate(
        input_variables=["history", "input"], 
        template=template
    )
    
    return ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )