
# ai_server/local_bot_graph.py

import logging
from typing import Annotated, List, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langgraph.checkpoint.memory import MemorySaver

# Factory & Modules
from llm.factory import LLMFactory
from rag.retriever import Retriever
# Prompts
from prompt import (
    LOCAL_ROUTE_SYSTEM, LOCAL_ROUTE_HUMAN,
    LOCAL_REWRITE_SYSTEM, LOCAL_REWRITE_HUMAN,
    LOCAL_RAG_SYSTEM, LOCAL_RAG_HUMAN,
    LOCAL_CHAT_SYSTEM, LOCAL_CHAT_HUMAN
)

logger = logging.getLogger("LocalGraph")

# 상태 정의
class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context : str
    query : str

# LocalLoader 강제 사용 권장하지만, Factory가 설정을 따르므로 여기선 Factory 사용
# (단, 사용자가 LLM_PROVIDER=local로 설정했다고 가정)
retriever_instance = Retriever()

def get_llm():
    return LLMFactory.get_llm()

def route_question(state: GraphState):
    llm = get_llm()
    # 마지막 사용자 질문만 추출
    question = state["messages"][-1].content
    
    # Qwen-specific ChatML Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", LOCAL_ROUTE_SYSTEM),
        ("human", LOCAL_ROUTE_HUMAN)  # user input is injected here via .format if needed, but here we construct raw string?
        # LangChain Template handles {question} replacement
    ])

    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({"question": question}).strip().lower()

    if "search" in decision:
        return "rewrite"
    else:
        return "generate_chat"

def rewrite_query(state: GraphState):
    llm = get_llm()
    messages = state["messages"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", LOCAL_REWRITE_SYSTEM),
        MessagesPlaceholder(variable_name="messages"),
        ("human", LOCAL_REWRITE_HUMAN)
    ])
    
    chain = prompt | llm | StrOutputParser()
    # Qwen이 <think>를 내뱉을 수도 있지만, Rewrite Prompt는 비교적 단순해서 바로 답이 올 것
    # 만약 <think>가 포함되면 main.py의 파서가 거르거나 여기서 strip 해야 함.
    # 여기서는 결과만 사용.
    new_query = chain.invoke({"messages": messages}).strip()
    
    return {"query": new_query}

def retrieve_node(state: GraphState):
    query = state["query"]
    docs = retriever_instance.retriever.invoke(query)
    context_text = "\n\n".join([doc.page_content for doc in docs])
    return {"context": context_text}
    
def generate_node(state: GraphState):
    llm = get_llm()
    context = state["context"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", LOCAL_RAG_SYSTEM),
        MessagesPlaceholder(variable_name="messages"),
        ("human", LOCAL_RAG_HUMAN)
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "context" : context,
        "messages" : state["messages"]
    })
    
    return {"messages": [AIMessage(content=response)]}


def generate_chat_node(state: GraphState):
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", LOCAL_CHAT_SYSTEM),
        MessagesPlaceholder(variable_name="messages"),
        ("human", LOCAL_CHAT_HUMAN)
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"messages": state["messages"]})
    
    return {"messages": [AIMessage(content=response)]}


# Workflow Definition
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