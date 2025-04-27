# -*- coding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.agents import initialize_agent, load_tools, AgentType
from peft import LoraConfig, PeftModel


# FastAPI 앱 생성
app = FastAPI()

# 파인튜닝된 모델 디렉토리 경로
MODEL_DIR = "c:/Users/ccg/Desktop/mai_project/넥슨/character_info/notebook/output"

# 모델과 토크나이저 로드
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, device_map="auto", load_in_8bit=True, torch_dtype="auto")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

# 요청 데이터 형식 정의
class TextRequest(BaseModel):
    text: str

# 텍스트 생성 엔드포인트
@app.post("/generate")
async def generate_text(request: TextRequest):
    try:
        # 입력 텍스트를 토큰화
        inputs = tokenizer.encode(request.text, return_tensors="pt")

        # 모델로 텍스트 생성
        outputs = model.generate(
            inputs,
            max_length=256,  # 생성할 최대 토큰 길이
            temperature=0.7,  # 생성 다양성을 조절
            top_p=0.9,       # nucleus sampling
            top_k=50         # top-k sampling
        )

        # 생성된 텍스트 디코딩
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"generated_text": response}
    except Exception as e:
        return {"error": str(e)}
    
    
    
