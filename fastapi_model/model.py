# -*- coding: utf-8 -*-

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 모델과 토크나이저를 전역 변수로 선언
model = None
tokenizer = None
def load_model():
    """모델과 토크나이저를 로드합니다."""
    global model, tokenizer

    try:
        # 현재 스크립트의 디렉토리를 기준으로 상대 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_local = os.path.join(os.path.dirname(current_dir), "fine_tuned_model", "merged_qwen")
        model_dir = os.getenv("LOCAL_MODEL_PATH", default_local)

        logger.info("로컬 모델을 로딩 중입니다...")

        # 로컬 모델 디렉토리가 존재하는지 확인
        if not os.path.exists(model_dir):
            logger.error(f"로컬 모델 디렉토리를 찾을 수 없습니다: {model_dir}")
            model = None
            tokenizer = None
            return False

        # 로컬 모델에서 직접 토크나이저와 모델 로드
        logger.info(f"로컬 모델 경로: {model_dir}")
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        
        # 토크나이저 설정 개선
        if getattr(tokenizer, "pad_token", None) is None:
            tokenizer.pad_token = tokenizer.eos_token
        if getattr(tokenizer, "pad_token_id", None) is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        # 로컬 모델 로드
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=dtype,
            trust_remote_code=True,
        )
        model = model.to(device)

        logger.info("로컬 모델 로딩이 완료되었습니다.")
        return True

    except Exception as e:
        logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
        model = None
        tokenizer = None
        return False

def ask_question(question: str) -> str:
    """질문에 대한 답변을 생성합니다."""
    global model, tokenizer
    
    # 모델이 로드되지 않았으면 로드 시도
    if model is None or tokenizer is None:
        if not load_model():
            return "모델을 로드할 수 없습니다. 관리자에게 문의하세요."
    
    # 모델이 여전히 None이면 오류 반환
    if model is None or tokenizer is None:
        return "모델을 로드할 수 없습니다. 관리자에게 문의하세요."
    
    try:
        # 입력 텍스트를 토큰화 (attention_mask 포함)
        inputs = tokenizer(question, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # GPU로 이동 (가능한 경우)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        # 모델로 텍스트 생성
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=1024,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # 생성된 텍스트 디코딩
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 입력 질문 제거하고 답변만 반환
        if question in response:
            response = response.replace(question, "").strip()
        
        return response if response else "죄송합니다. 답변을 생성할 수 없습니다."
        
    except Exception as e:
        logger.error(f"질문 처리 중 오류 발생: {str(e)}")
        return f"오류가 발생했습니다: {str(e)}"

# 모델 초기 로딩
if __name__ == "__main__":
    load_model()
    
    
    
