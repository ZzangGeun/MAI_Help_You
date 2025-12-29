# -*- coding: utf-8 -*-
"""
pgvector 기반 벡터 저장소

pgvector를 사용하여 문서 임베딩을 저장하고 유사도 검색을 수행합니다.
"""

import logging
from langchain_postgres import PGVector
from langchain_core.documents import Document
from typing import List

import os
import dotenv
dotenv.load_dotenv()

#기존 모듈
from .embeddings import QwenEmbeddings
from .document_loader import DocumentLoader

logger = logging.getLogger(__name__)

DB_CONNECTION = os.getenv("DB_CONNECTION")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


def get_vectorstore():
    """
    pgvector 저장소 객체를 가져오는 함수
    """
    embedding_model = QwenEmbeddings()

    vectorstore = PGVector(
        embeddings=embedding_model,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )
    return vectorstore

def build_database():
    """
    JSON 파일을 읽고 pgvector에 저장하는 함수
    """
    # 문서 로드
    document_loader = DocumentLoader()
    docs = document_loader.load_json_file()
    
    if not docs:
        raise ValueError("로드된 문서 없음")
    
    # 벡터 저장소 생성
    vectorstore = get_vectorstore()
    
    # 문서를 벡터로 변환하고 저장
    vectorstore.add_documents(docs)
    
    logger.info("데이터베이스 구축 완료")

def get_retriever(k = 3):
    """
    pgvector retriever를 가져오는 함수
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever({"k": k})
    return retriever

if __name__ == "__main__":
    build_database()
