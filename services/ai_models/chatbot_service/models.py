# -*- coding: utf-8 -*-

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import logging
from huggingface_hub import login
from typing import Optional, Any

logger = logging.getLogger(__name__)

class ChatbotModelService:
    """통합 챗봇 모델 서비스 - 로컬/원격 모드 지원"""
    
    def __init__(self):
        self.model: Any = None
        self.tokenizer: Any = None
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self._setup_huggingface()
        self._load_model()
    
    def _setup_huggingface(self):
        """HuggingFace Hub 로그인"""
        if self.huggingface_token:
            try:
                login(self.huggingface_token)
            except Exception as e:
                logger.warning("Hugging Face Hub 로그인 실패: %s", str(e))
    
    def _load_model(self):
        """모델과 토크나이저를 로드합니다."""
        try:
            # 로컬 모델 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            default_local = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 
                "fine_tuned_model", "merged_qwen"
            )
            model_dir = os.getenv("LOCAL_MODEL_PATH", default_local)
            
            logger.info("모델을 로딩 중입니다...")
            
            base_model_name = os.getenv("HF_BASE_MODEL", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B")
            
            # 로컬 병합 모델이 존재하는지 확인
            if os.path.exists(model_dir):
                logger.info(f"로컬 병합 모델을 로드합니다: {model_dir}")
                
                # 로컬 모델에서 토크나이저 로드
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_dir, 
                    trust_remote_code=True
                )
                if getattr(self.tokenizer, "pad_token", None) is None:
                    self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
                
                # 로컬 병합 모델 로드
                device = "cuda" if torch.cuda.is_available() else "cpu"
                dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_dir,
                    torch_dtype=dtype,
                    trust_remote_code=True,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                if not torch.cuda.is_available():
                    self.model = self.model.to(device)
                
                logger.info("로컬 병합 모델이 성공적으로 로드되었습니다.")
                
            else:
                logger.warning(f"로컬 모델 디렉토리를 찾을 수 없습니다: {model_dir}")
                logger.info("HuggingFace 베이스 모델을 로드합니다.")
                
                # HuggingFace 베이스 모델 로드
                self.tokenizer = AutoTokenizer.from_pretrained(
                    base_model_name, 
                    auth_token=self.huggingface_token, 
                    trust_remote_code=True
                )
                if getattr(self.tokenizer, "pad_token", None) is None:
                    self.tokenizer.pad_token = getattr(self.tokenizer, "eos_token", None)
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                self.model = AutoModelForCausalLM.from_pretrained(
                    base_model_name,
                    torch_dtype=dtype,
                    auth_token=self.huggingface_token,
                    trust_remote_code=True,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                if not torch.cuda.is_available():
                    self.model = self.model.to(device)
                
                logger.info("HuggingFace 베이스 모델이 로드되었습니다.")
            
            logger.info("모델 로딩이 완료되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
            self.model = None
            self.tokenizer = None
            return False
    
    def ask_question(self, question: str) -> str:
        """질문에 대한 답변을 생성합니다."""
        if self.model is None or self.tokenizer is None:
            return "모델을 로드할 수 없습니다. 관리자에게 문의하세요."
        
        try:
            # 채팅 템플릿이 있는지 확인
            if hasattr(self.tokenizer, 'apply_chat_template') and self.tokenizer.chat_template:
                # 채팅 템플릿 사용
                messages = [{"role": "user", "content": question}]
                formatted_input = self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
                inputs = self.tokenizer.encode(formatted_input, return_tensors="pt")
            else:
                # 기본 텍스트 인코딩
                inputs = self.tokenizer.encode(question, return_tensors="pt")
            
            # GPU로 이동 (가능한 경우)
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)
            
            # 모델로 텍스트 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=512,  # max_length 대신 max_new_tokens 사용
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # 생성된 텍스트 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 입력 질문 제거하고 답변만 반환
            if formatted_input in response:
                response = response.replace(formatted_input, "").strip()
            elif question in response:
                response = response.replace(question, "").strip()
            
            # 불필요한 공백 및 특수 문자 정리
            response = response.strip()
            
            return response if response else "죄송합니다. 답변을 생성할 수 없습니다."
            
        except Exception as e:
            logger.error(f"질문 처리 중 오류 발생: {str(e)}")
            return f"오류가 발생했습니다: {str(e)}"
    
    def is_loaded(self) -> bool:
        """모델이 로드되었는지 확인"""
        return self.model is not None and self.tokenizer is not None
