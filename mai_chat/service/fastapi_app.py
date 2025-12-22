# -*- coding: utf-8 -*-
"""FastAPI AI 서비스 애플리케이션

이 모듈은 FastAPI를 사용하여 AI 모델 추론을 위한 REST API를 제공합니다.
Django 백엔드 또는 다른 클라이언트에서 비동기적으로 AI 응답을 요청할 수 있습니다.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

from .ai_service import get_ai_response_async

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MAI Chat AI Service")

class AIRequest(BaseModel):
    prompt: str

class AIResponse(BaseModel):
    response: str

@app.post("/ai/respond", response_model=AIResponse)
async def respond_to_prompt(request: AIRequest):
    """
    AI 모델에게 프롬프트를 보내고 응답을 반환합니다.
    """
    try:
        response_text = await get_ai_response_async(request.prompt)
        return AIResponse(response=response_text)
    except Exception as e:
        logger.error(f"AI 응답 생성 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI Service Error")

def run():
    """FastAPI 서버를 실행합니다."""
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    run()
