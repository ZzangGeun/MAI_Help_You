
# ai_server/gemini_bot_graph.py

import logging
from typing import Annotated, List, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langgraph.checkpoint.memory import MemorySaver

from llm.factory import LLMFactory
from rag.retriever import Retriever
# Prompts
from prompt import (
    GEMINI_ROUTE_SYSTEM,
    GEMINI_REWRITE_SYSTEM,
    GEMINI_RAG_SYSTEM,
    GEMINI_CHAT_SYSTEM
)

logger = logging.getLogger("GeminiGraph")

class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context : str
    query : str

retriever_instance = Retriever()

def get_llm():
    return LLMFactory.get_llm()

def route_question(state: GraphState):
    llm = get_llm()
    messages = state["messages"] # Gemini는 전체 대맥을 봐도 됨, 혹은 마지막 질문만
    question = messages[-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", GEMINI_ROUTE_SYSTEM),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({"question": question}).strip().lower()
    
    logger.info(f"Dimini Route Decision: {decision} (Question: {question})")
    
    if "search" in decision:
        return "rewrite"
    else:
        return "generate_chat"

def rewrite_query(state: GraphState):
    llm = get_llm()
    messages = state["messages"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", GEMINI_REWRITE_SYSTEM),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    new_query = chain.invoke({"messages": messages}).strip()
    logger.info(f"Gemini Rewritten Query: {new_query}")
    return {"query": new_query}

def retrieve_node(state: GraphState):
    query = state["query"]
    docs = retriever_instance.retriever.invoke(query)
    
    # 문서 내용 + 메타데이터를 포함한 구조화된 컨텍스트 생성
    context_parts = []
    for i, doc in enumerate(docs, 1):
        metadata = doc.metadata
        title = metadata.get('title', '제목 없음')
        source = metadata.get('source', '출처 정보 없음')
        category = metadata.get('category', '기타')
        
        # URL 추출 (notice_url 또는 thumbnail_url 등)
        url = metadata.get('notice_url') or metadata.get('thumbnail_url') or metadata.get('url', '')
        
        context_part = f"""## [문서 {i}] {title}
- **카테고리**: {category}
- **출처**: {source}
{f"- **참고 링크**: {url}" if url else ""}

**내용**:
{doc.page_content}

---
"""
        context_parts.append(context_part)
    
    context_text = "\n".join(context_parts)
    
    logger.info(f"Gemini Retrieval: Found {len(docs)} docs for query '{query}'")
    if docs:
        logger.info(f"First doc preview: {docs[0].page_content[:100]}...")
        
    return {"context": context_text}
    
def generate_node(state: GraphState):
    llm = get_llm()
    context = state["context"]
    
    logger.info("Generating RAG response with Gemini...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", GEMINI_RAG_SYSTEM), # Context가 System Message 안에 format 됨
        MessagesPlaceholder(variable_name="messages"),
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "context" : context,
        "messages" : state["messages"]
    })
    
    return {"messages": [AIMessage(content=response)]}

def generate_chat_node(state: GraphState):
    llm = get_llm()
    logger.info("Generating simple chat response with Gemini...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", GEMINI_CHAT_SYSTEM),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"messages": state["messages"]})
    
    return {"messages": [AIMessage(content=response)]}


workflow = StateGraph(GraphState)

workflow.add_node("rewrite", rewrite_query)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate_node", generate_node)
workflow.add_node("generate_chat", generate_chat_node)

workflow.add_conditional_edges(
    START,
    route_question,
    {
        "rewrite" : "rewrite",
        "generate_chat" : "generate_chat"
    }
)

workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("retrieve", "generate_node")
workflow.add_edge("generate_node", END)
workflow.add_edge("generate_chat", END)

memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)
