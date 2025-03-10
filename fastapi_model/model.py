from langchain_openai import ChatOpenAI
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



chat = ChatOpenAI(model="ft:gpt-4o-2024-08-06:personal::ASKX7WaZ")
chat_prompt = ChatPromptTemplate([
    ("system","당신은 메이플스토리의 npc 돌의 정령 입니다.")
    ("user","{user_input}")

])

chain = chat_prompt | chat



def ask_question(question: str) -> str:
    response = chat.invoke(question)
    return response.content