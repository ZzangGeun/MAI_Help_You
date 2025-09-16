# -*- coding: utf-8 -*-

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from .models import ChatbotModelService
from .rag_engine import ChatbotRAGService

logger = logging.getLogger(__name__)

class ChatbotAPIService:
    """통합 챗봇 API 서비스 - 로컬/원격 모드 지원"""
    
    def __init__(self):
        self.remote_mode = self._should_use_remote_mode()
        self.fastapi_url = os.getenv("FASTAPI_MODEL_URL", "http://127.0.0.1:8001/api/chat")
        
        # 로컬 모드 구성 요소
        self.model_service: Optional[ChatbotModelService] = None
        self.rag_service: Optional[ChatbotRAGService] = None
        
        # 사용자별 히스토리 저장
        self.user_histories: Dict[str, List[Dict[str, str]]] = {}
        
        self._initialize_services()
    
    def _should_use_remote_mode(self) -> bool:
        """원격 모드 사용 여부를 결정합니다."""
        use_remote = os.getenv("USE_REMOTE_LLM", "auto").lower()
        if use_remote not in {"true", "false"}:
            # auto 모드: 환경 변수 FASTAPI_MODEL_URL이 지정되어 있으면 원격 사용
            return bool(os.getenv("FASTAPI_MODEL_URL"))
        return use_remote == "true"
    
    def _initialize_services(self):
        """서비스를 초기화합니다."""
        try:
            if not self.remote_mode:
                logger.info("로컬 모드로 챗봇 서비스를 초기화합니다.")
                self.model_service = ChatbotModelService()
                self.rag_service = ChatbotRAGService()
            else:
                logger.info("원격 모드로 챗봇 서비스를 초기화합니다.")
                # 원격 모드에서는 로컬 서비스 초기화 생략
                
        except Exception as e:
            logger.error(f"챗봇 서비스 초기화 중 오류: {str(e)}")
            self.model_service = None
            self.rag_service = None
    
    def get_response(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """질문에 대한 답변을 생성합니다."""
        try:
            uid = user_id or "anonymous"
            
            if self.remote_mode:
                return self._get_remote_response(question, uid)
            else:
                return self._get_local_response(question, uid)
                
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {str(e)}")
            return {
                "response": f"오류가 발생했습니다: {str(e)}",
                "sources": [],
                "has_rag": False
            }
    
    def _get_remote_response(self, question: str, user_id: str) -> Dict[str, Any]:
        """원격 모드에서 답변을 생성합니다."""
        try:
            # 최근 히스토리 몇 개(최대 5쌍) 프롬프트에 포함
            prior = self.get_chat_history(user_id)
            condensed = "".join([f"사용자: {p['user']}\nAI: {p['assistant']}\n" for p in prior[-5:]])
            final_question = question if not condensed else (
                "다음은 지금까지의 대화입니다:\n" + condensed + "\n사용자 질문: " + question + "\nAI 답변:"
            )
            
            # FastAPI 서비스 호출
            resp = requests.post(
                self.fastapi_url,
                json={"question": final_question, "user_id": user_id},
                timeout=60,
            )
            
            if resp.status_code == 200:
                j = resp.json()
                response = j.get("response") or j.get("answer") or "응답을 가져오지 못했습니다."
            else:
                response = f"원격 모델 오류: HTTP {resp.status_code}"
            
            # 히스토리 저장
            self._save_to_history(user_id, question, response)
            
            return {
                "response": response,
                "sources": [],
                "has_rag": False
            }
            
        except Exception as e:
            logger.error(f"원격 모드 응답 생성 중 오류: {str(e)}")
            return {
                "response": f"원격 모델 호출 실패: {e}",
                "sources": [],
                "has_rag": False
            }
    
    def _get_local_response(self, question: str, user_id: str) -> Dict[str, Any]:
        """로컬 모드에서 답변을 생성합니다."""
        try:
            # RAG 검색
            context_blocks = []
            if self.rag_service and self.rag_service.is_ready():
                hits = self.rag_service.retrieve_texts(question, top_k=3)
                for text, meta in hits:
                    context_blocks.append(text[:800])
            
            context_text = "\n\n".join(context_blocks)
            
            # 히스토리 가져오기
            prior = self.get_chat_history(user_id)
            history_text = "\n".join([f"사용자: {p['user']}\nAI: {p['assistant']}" for p in prior[-5:]])
            
            # 프롬프트 구성
            prompt = (
                ("다음은 참고할 수 있는 문서 발췌입니다:\n" + context_text + "\n\n" if context_text else "")
                + ("이전 대화:\n" + history_text + "\n\n" if history_text else "")
                + f"사용자 질문: {question}\nAI 답변:"
            )
            
            # 모델 호출
            if self.model_service and self.model_service.is_loaded():
                response = self.model_service.ask_question(prompt)
            else:
                response = "죄송합니다. 로컬 LLM이 준비되지 않았습니다."
            
            # 히스토리 저장
            self._save_to_history(user_id, question, response)
            
            return {
                "response": response,
                "sources": [s[:200] + "..." for s in context_blocks] if context_blocks else [],
                "has_rag": bool(context_blocks)
            }
            
        except Exception as e:
            logger.error(f"로컬 모드 응답 생성 중 오류: {str(e)}")
            return {
                "response": f"로컬 모델 오류: {str(e)}",
                "sources": [],
                "has_rag": False
            }
    
    def _save_to_history(self, user_id: str, question: str, response: str):
        """대화 히스토리를 저장합니다."""
        try:
            hist = self.user_histories.get(user_id, [])
            hist.append({"user": question, "assistant": response})
            self.user_histories[user_id] = hist
        except Exception as e:
            logger.error(f"히스토리 저장 중 오류: {str(e)}")
    
    def get_chat_history(self, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """채팅 히스토리를 반환합니다."""
        try:
            uid = user_id or "anonymous"
            return self.user_histories.get(uid, [])
        except Exception as e:
            logger.error(f"채팅 히스토리 조회 중 오류 발생: {str(e)}")
            return []
    
    def clear_history(self, user_id: Optional[str] = None) -> bool:
        """채팅 히스토리를 초기화합니다."""
        try:
            uid = user_id or "anonymous"
            if uid in self.user_histories:
                del self.user_histories[uid]
            return True
        except Exception as e:
            logger.error(f"히스토리 초기화 중 오류 발생: {str(e)}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태를 반환합니다."""
        return {
            "remote_mode": self.remote_mode,
            "model_ready": self.model_service.is_loaded() if self.model_service else False,
            "rag_ready": self.rag_service.is_ready() if self.rag_service else False,
            "fastapi_url": self.fastapi_url if self.remote_mode else None
        }
