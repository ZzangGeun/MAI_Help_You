from langchain_openai import ChatOpenAI
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



 # RAG 기법 사용 위해 사용자 메세지를 벡터 변환
embeddings = HuggingFaceEmbeddings(model_name = "Upstage/solar-embedding-1-large",model_kwargs={"device": "cuda"})

def get_embedding(texts):
    vector = embeddings.embed_documents(texts)
    return


chat = ChatOpenAI(model="ft:gpt-4o-2024-08-06:personal::ASKX7WaZ")
chat_prompt = ChatPromptTemplate([
    ("system","당신은 메이플스토리의 npc 돌의 정령 입니다.")
    ("user","{user_input}")

])

chain = chat_prompt | chat



def ask_question(question: str) -> str:
    response = chat.invoke(question)
    return response.content