# ai_server/main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import logging
import re
import json
from langchain_core.messages import HumanMessage

# [핵심] 우리가 만든 그래프 가져오기
from bot_graph import app_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_Server")

app = FastAPI(title="MapleStory AI Server (LangGraph)")

# 요청 데이터 모델 (session_id 추가됨!)
class QueryRequest(BaseModel):
    session_id: str
    message: str

def parse_thinking_response(text: str):
    """
    Qwen Thinking 모델의 출력에서 <think>...</think> 부분을 발라냅니다.
    """
    # 1. <think> 태그가 있는 경우 (정석적인 경우)
    if "<think>" in text and "</think>" in text:
        think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
        thinking_process = think_match.group(1).strip() if think_match else ""
        final_answer = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return thinking_process, final_answer
    
    # 2. 모델이 실수로 태그를 안 닫은 경우 (흔한 오류)
    elif "<think>" in text:
        parts = text.split("<think>")
        return "태그 파싱 에러", text.replace("<think>", "").strip()

    # 3. 태그가 아예 없는 경우 (생각 없이 바로 답함)
    else:
        return "", text.strip()

@app.post("/generate")
async def generate_response(request: QueryRequest):
    try:
        logger.info(f"요청 수신 (Session: {request.session_id}): {request.message}")
        
        # 1. LangGraph 설정 (thread_id = session_id)
        config = {"configurable": {"thread_id": request.session_id}}
        
        # 2. 그래프 실행
        # 사용자의 질문을 HumanMessage 형태로 주입
        input_message = HumanMessage(content=request.message)
        
        # ainvoke를 사용하면 비동기로 실행 가능
        # state의 "messages" 중 가장 마지막 것(AI 답변)을 가져옴
        output = await app_graph.ainvoke(
            {"messages": [input_message]}, 
            config=config
        )
        
        # 3. 결과 파싱
        ai_full_response = output["messages"][-1].content
        thinking, answer = parse_thinking_response(ai_full_response)
        
        return {
            "response": answer,
            "thinking": thinking
        }
        
    except Exception as e:
        logger.error(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_response(request: QueryRequest):
    """
    스트리밍 답변 생성 엔드포인트
    SSE(Server-Sent Events) 형식으로 데이터를 전송합니다.
    """
    try:
        logger.info(f"스트리밍 요청 수신 (Session: {request.session_id}): {request.message}")
        
        config = {"configurable": {"thread_id": request.session_id}}
        input_message = HumanMessage(content=request.message)

        async def event_generator():
            try:
                # astream_events를 사용하여 생성 과정을 실시간으로 스트리밍
                # version="v2"는 LangChain 최신 표준 (권장)
                async for event in app_graph.astream_events(
                    {"messages": [input_message]}, 
                    config=config,
                    version="v2" 
                ):
                    event_type = event["event"]
                    
                    # LLM이 텍스트를 생성하는 이벤트 (on_chat_model_stream)
                    if event_type == "on_chat_model_stream":
                        # 메타데이터에서 현재 실행 중인 노드 이름을 확인
                        node_name = event.get("metadata", {}).get("langgraph_node", "")
                        
                        # "generate_node" 또는 "generate_chat" 노드에서 나온 출력만 전송
                        # (route_question, rewrite_query 등의 중간 과정 토큰은 숨김)
                        if node_name in ["generate_node", "generate_chat", "generate_chat_node"]:
                            chunk = event["data"]["chunk"]
                            if chunk.content:
                                # SSE 포맷: data: JSON\n\n
                                payload = {"type": "token", "content": chunk.content}
                                yield f"data: {json.dumps(payload)}\n\n"
                            
            except Exception as e:
                logger.error(f"스트리밍 중 에러: {e}")
                payload = {"type": "error", "content": str(e)}
                yield f"data: {json.dumps(payload)}\n\n"
            
            # 종료 신호
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"스트리밍 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)