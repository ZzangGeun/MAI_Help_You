from fastapi import FastAPI
from routes import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def root():
    return {"message":'FastAPI 서버 실행 중'}