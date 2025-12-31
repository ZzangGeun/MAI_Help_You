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

# 모델 경로

# 리눅스
# BASE_DIR = "/home/ccg700/바탕화면/programming/MAI_Help_You/fine_tuned_model/merged_qwen"
# 윈도우
BASE_DIR = "C:/Users/ccg70/OneDrive/desktop/programming/MAI_Help_You/fine_tuned_model/merged_qwen"

def load_model():
    global model, tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_DIR, trust_remote_code=True, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(BASE_DIR,
                                                torch_dtype="auto",
                                                device_map="auto" if torch.cuda.is_available() else None, 
                                                trust_remote_code=True, 
                                                local_files_only=True)
    return model is not None and tokenizer is not None

def ask_question(question):
    """질문에 대한 답변을 생성합니다."""
    global model, tokenizer
    
    if model is None or tokenizer is None:
        return print("모델 로딩 실패")
    
    try:
        inputs = tokenizer(question, return_tensors="pt", padding=True, truncation=True, max_length=512)

        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                input_ids = inputs["input_ids"],
                attention_mask = inputs["attention_mask"],
                max_length = 1024,
                temperature = 1,
                top_p = 0.9,
                top_k = 50,
                do_sample = True,
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if question in response:
            response = response.replace(question, "").strip()

        return response
    
    except Exception as e:
        return f"오류 발생: {str(e)}"



# 모델 초기 로딩
if __name__ == "__main__":
    load_model()
    
    
    
