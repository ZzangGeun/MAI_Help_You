from langchain_community.chat_models import ChatOllama
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



 # RAG 기법 사용 위해 사용자 메세지를 벡터 변환
embeddings = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-large-instruct",model_kwargs={"device": "cuda"})

def get_embedding(texts):
    try:
        embedding = embeddings.embed_documents(texts)
        return embedding
    except Exception as e:
        return None


chat = ChatOllama(model="llama3")

chat_prompt = ChatPromptTemplate([
    ("system","당신은 메이플스토리의 npc 돌의 정령 입니다."),
    ("user","{user_input}")

])

chain = chat_prompt | chat



def ask_question(question: str) -> str:
    response = chat.invoke(question)
    return response.content
