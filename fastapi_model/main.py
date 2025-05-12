from fastapi import FastAPI
from routes import router

app = FastAPI()

app.include_router(router)

@app.get("/api/fastapi/ask")
async def ask_question(question: str):
    return {"response": f"{question}에 대한 답변입니다."}