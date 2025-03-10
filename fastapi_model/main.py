from fastapi import FastAPI

app = FastAPI()

@app.get("/api/fastapi")
async def fastapi_test():
    return {"message": "Hello from FastAPI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
