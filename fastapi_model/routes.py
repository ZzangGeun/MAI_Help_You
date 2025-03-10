from fastapi import APIRouter
from model import ask_question

router = APIRouter()

@router.get("/api/fastapi/ask")
async def fastapi_ask(question: str):

    try:
        response = ask_question(question)
        return {"question":question , "response" : response}
    
    except Exception as e:
        return {"error": str(e)}
    
