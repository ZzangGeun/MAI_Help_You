from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from model import ask_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    user_id: str = None

class ChatResponse(BaseModel):
    question: str
    response: str
    user_id: str = None

@router.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        response = ask_question(request.question)
        return ChatResponse(
            question=request.question,
            response=response,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 모델 오류: {str(e)}")

@router.get("/api/chat")
async def fastapi_ask(question: str, user_id: str = None):
    try:
        response = ask_question(question)
        return {
            "question": question,
            "response": response,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 모델 오류: {str(e)}")
    
