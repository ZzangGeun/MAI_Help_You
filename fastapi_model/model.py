# -*- coding: utf-8 -*-

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import logging
from huggingface_hub import login

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
login(HUGGINGFACE_TOKEN)

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
        MODEL_DIR = "C:/Users/ccg70/OneDrive/desktop/programming/MAPLE/nexon_2/fine_tuned_model/merged_qwen"

        if not os.path.exists(MODEL_DIR):
            logger.warning(f"모델 디렉토리를 찾을 수 없습니다: {MODEL_DIR}")
            return False
            
        logger.info("모델을 로딩 중입니다...")
        

        base_model_name = " Qwen/Qwen3-8B"  
        
        # 토크나이저 로드
        tokenizer = AutoTokenizer.from_pretrained(base_model_name, auth_token=HUGGINGFACE_TOKEN)
        tokenizer.pad_token = tokenizer.eos_token
        
        # 베이스 모델 로드
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            auth_token=HUGGINGFACE_TOKEN
        )
        
        # LoRA 어댑터 적용 (어댑터가 호환되지 않을 경우 베이스 모델만 사용)
        try:
            model = PeftModel.from_pretrained(base_model, MODEL_DIR)
            logger.info("LoRA 어댑터가 성공적으로 로드되었습니다.")
        except Exception as e:
            logger.warning(f"LoRA 어댑터 로딩 실패, 베이스 모델만 사용: {str(e)}")
            model = base_model
        
        logger.info("모델 로딩이 완료되었습니다.")
        return True
        
    except Exception as e:
        logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
        return False

def ask_question(question: str) -> str:
    """질문에 대한 답변을 생성합니다."""
    global model, tokenizer
    
    if model is None or tokenizer is None:
        if not load_model():
            return "모델을 로드할 수 없습니다. 관리자에게 문의하세요."
    
    try:
        # 입력 텍스트를 토큰화
        inputs = tokenizer.encode(question, return_tensors="pt")
        
        # GPU로 이동 (가능한 경우)
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # 모델로 텍스트 생성
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=1024,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
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
    
    
    
