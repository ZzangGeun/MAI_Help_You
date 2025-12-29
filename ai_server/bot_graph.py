# ai_server/bot_graph.py

import logging
from typing import Annotated, List, Dict
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langgraph.checkpoint.memory import MemorySaver

# 만든 로더들 가져오기
from llm.llm_loader import LocalLLMLoader
from rag.retriever import Retriever

logger = logging.getLogger("Graph")

# 상태 정의
class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context : str
    query : str

llm_loader =LocalLLMLoader()
retriever_instance = Retriever()


def route_question(state: GraphState) -> Literal["rewrite", "generate_chat"]:
    """
    사용자의 질문을 보고 'search'(검색 필요)인지 'chat'(일상 대화)인지 결정
    """
    llm = llm_loader.get_llm()
    question = state["messages"][-1].content

    prompt = ChatPromptTemplate.from_messages([
        ("system", """<|im_start|>system
당신은 질문 분류기입니다. 
사용자의 질문이 '메이플스토리 게임 정보(아이템, 몬스터, 공략 등)'와 관련되어 있으면 'search'를,
단순한 인사나 일상 대화라면 'chat'을 단어만 출력하세요.
<|im_end|>"""),
        ("human", "<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant")
    ])

    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({"question": question}).strip().lower()

    if "search" in decision:

        return "rewrite" # 검색 전 질문 다듬기로 이동
    else:
        return "generate_chat" # 바로 답변 생성으로 이동

def rewrite_query(state: GraphState):
    llm = llm_loader.get_llm()
    messages = state["messages"]
    original_query = messages[-1].content
    
    # Qwen용 프롬프트: 대화 내역을 보고 모호한 질문을 명확하게 바꿈
    prompt = ChatPromptTemplate.from_messages([
        ("system", """<|im_start|>system
당신은 질문 재구성 도우미입니다. 
주어진 대화 내역을 참고하여, 사용자의 마지막 질문이 무엇을 의미하는지 명확한 문장으로 다시 쓰세요.
답변이나 설명 없이 오직 재구성된 질문 하나만 출력하세요.
<|im_end|>"""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", """<|im_start|>assistant
명확한 질문: """)
    ])
    
    chain = prompt | llm | StrOutputParser()
    new_query = chain.invoke({"messages": messages}).strip()
    
    return {"query": new_query} # state['query']에 저장


def retrieve_node(state: GraphState):
    """
    사용자의 질문을 보고 관련된 문서를 찾아서 context를 만듭니다. 
    """
    
    # 대화 내역 중 마지막 메세지를 꺼낸다.
    query = state["query"]

    docs = retriever_instance.retriever.invoke(query)

    # 하나로 합치기
    context_text = "\n\n".join([doc.page_content for doc in docs])

    return {"context": context_text}
    
def generate_node(state: GraphState):
    """
    context + history -> 답변 생성
    """
    llm = llm_loader.get_llm()
    context = state["context"]

        # Qwen Thinking 모델용 프롬프트
    prompt = ChatPromptTemplate.from_messages([
            ("system", """<|im_start|>system
    당신은 메이플스토리 세계관의 돌의정령 NPC입니다. 말투: ~한담, ~이담, ~했담 등 'ㅁ' 받침 어미 사용
    다음 [Context]를 깊이 있게 분석하여 논리적으로 답변하세요.
    대화의 흐름을 기억하고 이전 질문과 이어지는 답변을 하세요.
    주의사항:
    1. [Context]에 없는 내용은 절대 지어내지 마세요.
    2. 정보가 없으면 "지금은 알 수 없는 내용이담."이라고 솔직하게 말하세요.

    [Context]:
    {context}<|im_end|>"""),
            MessagesPlaceholder(variable_name="messages"), # 여기에 대화 내역이 자동으로 들어감
            ("human", """<|im_start|>assistant
    <think>
    """)
        ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "context" : context,
        "messages" : state["messages"]
    })

    return {"messages": [AIMessage(content=response)]}


def generate_chat_node(state: GraphState):
    llm = llm_loader.get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """<|im_start|>system
당신은 메이플스토리의 귀여운 마스코트 '돌의 정령'입니다. 
사용자의 일상적인 대화에 재치 있게 '~담' 말투로 반응하세요.
게임 공략을 지어내지 마세요.
<|im_end|>"""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", """<|im_start|>assistant
<think>
""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"messages": state["messages"]})
    
    return {"messages": [AIMessage(content=response)]}




workflow = StateGraph(GraphState)

workflow.add_node("rewrite", rewrite_query)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate_rag", generate_rag_node)
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
workflow.add_edge("retrieve", "generate_rag")
workflow.add_edge("generate_rag", END)

# Chat 파이프라인 연결
workflow.add_edge("generate_chat", END)

memory = MemorySaver()

app_graph = workflow.compile(checkpointer=memory)