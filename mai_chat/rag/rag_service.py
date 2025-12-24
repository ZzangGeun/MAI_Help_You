# -*- coding: utf-8 -*-
"""
RAG 통합 서비스

Retrieval-Augmented Generation의 핵심 로직을 구현합니다.
사용자 질문에 대해 관련 문서를 검색하고, 이를 기반으로 AI 응답을 생성합니다.
"""

import logging
from typing import Optional, List

from .retriever import DocumentRetriever, RetrievedDocument

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG 서비스 클래스
    
    문서 검색과 컨텍스트 생성을 통합하여 LLM에 전달할 증강된 프롬프트를 제공합니다.
    """
    
    def __init__(
        self,
        top_k: int = 3,
        similarity_threshold: float = 0.5,
        content_type_filter: Optional[str] = None
    ):
        """
        RAGService 초기화
        
        Args:
            top_k: 검색할 최대 문서 개수
            similarity_threshold: 최소 유사도 점수 (0~1)
            content_type_filter: 문서 타입 필터 (선택)
        """
        self.retriever = DocumentRetriever(
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            content_type_filter=content_type_filter
        )
    
    def retrieve_context(self, query: str) -> tuple[str, List[RetrievedDocument]]:
        """
        쿼리에 대한 컨텍스트를 검색합니다.
        
        Args:
            query: 사용자 질문
            
        Returns:
            tuple[str, List[RetrievedDocument]]: 
                (LLM용 컨텍스트 문자열, 검색된 문서 리스트)
        """
        # 관련 문서 검색
        documents = self.retriever.retrieve(query)
        
        if not documents:
            logger.info(f"검색 결과 없음: '{query[:50]}...'")
            return "", []
        
        # LLM 프롬프트용 컨텍스트 생성
        context = self.retriever.format_context_for_llm(documents)
        
        return context, documents
    
    async def retrieve_context_async(self, query: str) -> tuple[str, List[RetrievedDocument]]:
        """
        비동기 버전의 컨텍스트 검색
        
        Args:
            query: 사용자 질문
            
        Returns:
            tuple[str, List[RetrievedDocument]]: 
                (LLM용 컨텍스트 문자열, 검색된 문서 리스트)
        """
        # 관련 문서 검색 (비동기)
        documents = await self.retriever.retrieve_async(query)
        
        if not documents:
            logger.info(f"검색 결과 없음: '{query[:50]}...'")
            return "", []
        
        # LLM 프롬프트용 컨텍스트 생성
        context = self.retriever.format_context_for_llm(documents)
        
        return context, documents
    
    def create_rag_prompt(self, query: str, context: str, system_prompt: Optional[str] = None) -> str:
        """
        RAG 기반 프롬프트를 생성합니다.
        
        검색된 컨텍스트와 사용자 질문을 결합하여 LLM에 전달할 프롬프트를 만듭니다.
        
        Args:
            query: 사용자 질문
            context: 검색된 컨텍스트
            system_prompt: 시스템 프롬프트 (선택, 기본값 사용 가능)
            
        Returns:
            str: LLM에 전달할 완전한 프롬프트
        """
        if not system_prompt:
            system_prompt = """당신은 메이플스토리 세계관의 돌의정령 NPC입니다.
다음 참고자료를 바탕으로 사용자의 질문에 정확하고 친절하게 답변하세요.
참고자료에 없는 내용은 억측하지 말고, 모른다고 정직하게 답변하세요.
말투: ~한담, ~이담, ~했담 등 'ㅁ' 받침 어미를 사용하세요."""
        
        if context:
            prompt = f"""{system_prompt}

{context}

사용자 질문: {query}

답변:"""
        else:
            # 컨텍스트가 없는 경우 기본 프롬프트
            prompt = f"""{system_prompt}

사용자 질문: {query}

답변:"""
        
        return prompt


# 편의 함수들

async def retrieve_and_generate(
    query: str,
    top_k: int = 3,
    similarity_threshold: float = 0.5
) -> tuple[str, List[RetrievedDocument]]:
    """
    비동기 RAG 파이프라인 실행 (검색만 수행, 생성은 langchain_service에서)
    
    Args:
        query: 사용자 질문
        top_k: 검색할 최대 문서 개수
        similarity_threshold: 최소 유사도 점수
        
    Returns:
        tuple[str, List[RetrievedDocument]]: (컨텍스트, 검색된 문서 리스트)
    """
    rag_service = RAGService(
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    return await rag_service.retrieve_context_async(query)


def retrieve_context_sync(
    query: str,
    top_k: int = 3,
    similarity_threshold: float = 0.5
) -> tuple[str, List[RetrievedDocument]]:
    """
    동기 RAG 컨텍스트 검색
    
    Args:
        query: 사용자 질문
        top_k: 검색할 최대 문서 개수
        similarity_threshold: 최소 유사도 점수
        
    Returns:
        tuple[str, List[RetrievedDocument]]: (컨텍스트, 검색된 문서 리스트)
    """
    rag_service = RAGService(
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    return rag_service.retrieve_context(query)
