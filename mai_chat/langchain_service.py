# -*- coding: utf-8 -*-
"""
LangChain Service Module (Refactored for LangGraph & Django)

LangGraph의 StateGraph를 활용하여 대화 흐름과 상태를 관리합니다.
Django ORM 기반의 커스텀 비동기 체크포인터를 통해 데이터 영속성을 보장하며,
BaseChatModel을 상속받은 커스텀 모델로 구조화된 메시지 처리를 수행합니다.
"""

import logging
import uuid
from typing import Optional, List, Any, Dict

import httpx
from asgiref.sync import sync_to_async

# LangChain & LangGraph Imports
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, 
    get_buffer_string
)
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.base import (
    BaseCheckpointSaver, 
    Checkpoint, 
    CheckpointMetadata, 
    CheckpointTuple,
    ChannelVersions
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from typing_extensions import TypedDict, Annotated

# Models Import (실제 환경에 맞게 경로 수정 필요)
# from.models import LangGraphCheckpoint 
# 레거시 ChatSession 모델을 대체하거나 병행 사용할 새로운 모델이 필요함.
from .models import LangGraphCheckpoint 

logger = logging.getLogger(__name__)

# --- 1. Custom Chat Model ---
class MapleStoryChatModel(BaseChatModel):
    api_url: str = "http://localhost:8001/ai/respond"
    timeout: float = 180.0

    @property
    def _llm_type(self) -> str:
        return "maplestory_ai_client"

    def _format_messages(self, messages: List) -> str:
        # 시스템 메시지 처리: 맨 앞에 있는 경우 캐릭터 설정으로 인식 가능
        # 여기서는 get_buffer_string을 사용하여 텍스트로 변환
        return get_buffer_string(messages, human_prefix="User", ai_prefix="Dol-ui-jeongnyeong")

    async def _agenerate(
        self, messages: List, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> ChatResult:
        prompt_str = self._format_messages(messages)
        headers = {"Content-Type": "application/json"}
        payload = {"prompt": prompt_str}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=self.timeout
                )
                response.raise_for_status()
                content = response.json().get("response", "")
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
        except Exception as e:
            logger.error(f"Async AI Call Error: {e}", exc_info=True)
            raise

    def _generate(self, messages: List, stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        raise NotImplementedError("Sync invoke is not supported in this async-first implementation.")

# --- 2. Django Async Checkpointer ---
class DjangoAsyncCheckpointSaver(BaseCheckpointSaver):
    def __init__(self):
        super().__init__(serde=JsonPlusSerializer())

    async def aget_tuple(self, config: RunnableConfig) -> Optional:
        thread_id = config["configurable"]["thread_id"]
        
        def _get_latest():
            # LangGraphCheckpoint 모델이 존재한다고 가정
            return LangGraphCheckpoint.objects.filter(thread_id=thread_id).order_by("-created_at").first()

        record = await sync_to_async(_get_latest, thread_sensitive=True)()
        if not record: 
            return None
            
        return CheckpointTuple(
            config,
            self.serde.loads(record.checkpoint_data),
            self.serde.loads(record.metadata),
            (record.parent_checkpoint_id,) if record.parent_checkpoint_id else None
        )

    async def aput(self, config, checkpoint, metadata, new_versions):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        parent_id = config["configurable"].get("checkpoint_id")
        
        blob = self.serde.dumps(checkpoint)
        meta_blob = self.serde.dumps(metadata)
        
        def _save():
            LangGraphCheckpoint.objects.create(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                parent_checkpoint_id=parent_id,
                checkpoint_data=blob,
                metadata=meta_blob
            )
            
        await sync_to_async(_save, thread_sensitive=True)()
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}

    async def alist(self, config, **kwargs): return # 간소화
    async def aput_writes(self, config, writes, task_id, task_path=""): pass # 간소화

# --- 3. Graph Construction ---
class AgentState(TypedDict):
    messages: [Annotated, add_messages]

maplestory_model = MapleStoryChatModel()

async def npc_node(state: AgentState):
    return {"messages": [await maplestory_model.ainvoke(state["messages"])]}

builder = StateGraph(AgentState)
builder.add_node("npc", npc_node)
builder.add_edge(START, "npc")
builder.add_edge("npc", END)

# 체크포인터 인스턴스 (전역 혹은 DI)
_checkpointer = DjangoAsyncCheckpointSaver()
graph_app = builder.compile(checkpointer=_checkpointer)

# --- 4. Public API ---
async def chat_with_memory_async(session_id: str, user_input: str) -> str:
    """
    LangGraph 기반의 비동기 채팅 처리 함수.
    """
    if not user_input.strip():
        raise ValueError("Input cannot be empty")

    config = {"configurable": {"thread_id": session_id}}
    
    # 1. 현재 상태 조회
    current_state = await graph_app.aget_state(config)
    
    # 2. 새로운 메시지 목록 준비
    new_messages = []
    
    # 3. 상태가 비어있다면(첫 대화), 시스템 메시지 추가
    # current_state.values가 비어있으면 초기 상태
    if not current_state.values:
        logger.info(f"Initializing new session: {session_id}")
        system_prompt = (
            "당신은 메이플스토리 세계관의 돌의정령 NPC입니다.\n"
            "캐릭터 설정:\n"
            "- 메이플스토리의 모든 정보를 알고 있는 지식이 풍부한 정령\n"
            "- 사용자의 질문에 친절하고 정확하게 답변\n"
            "- 말투: ~한담, ~이담, ~했담 등 'ㅁ' 받침 어미 사용"
        )
        new_messages.append(SystemMessage(content=system_prompt))
    
    # 4. 사용자 메시지 추가
    new_messages.append(HumanMessage(content=user_input.strip()))

    # 5. 그래프 실행 (새로운 메시지만 전달)
    # LangGraph는 add_messages 리듀서를 통해 기존 히스토리에 자동 병합함
    final_state = await graph_app.ainvoke({"messages": new_messages}, config=config)
    
    # 6. 마지막 AI 메시지 추출
    last_msg = final_state["messages"][-1]
    return last_msg.content if isinstance(last_msg, AIMessage) else ""

def clear_session_memory(session_id: str) -> None:
    """
    세션 메모리 삭제 (Django DB 레코드 삭제)
    """
    # 동기 컨텍스트에서 호출되므로 바로 ORM 사용 가능 (또는 sync_to_async 고려)
    try:
        LangGraphCheckpoint.objects.filter(thread_id=session_id).delete()
        logger.info(f"Cleared checkpoints for session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")