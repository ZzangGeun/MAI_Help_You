# -*- coding: utf-8 -*-
"""
문서 검색 서비스

벡터 저장소를 활용하여 사용자 질문과 관련된 문서를 검색합니다.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .vectorstore import VectorStore
from .models import DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """
    검색된 문서 정보를 담는 데이터 클래스
    """
    content: str
    title: str
    source: Optional[str]
    content_type: str
    similarity_score: float
    chunk_index: int
    metadata: Dict[str, Any]
    
    def to_context_string(self) -> str:
        """
        LLM 프롬프트에 포함할 컨텍스트 문자열을 생성합니다.
        
        Returns:
            str: 포맷팅된 컨텍스트 문자열
        """
        source_info = f" (출처: {self.source})" if self.source else ""
        return f"[{self.title}{source_info}]\n{self.content}"


class DocumentRetriever:
    """
    문서 검색 클래스
    
    사용자 질문에 대해 관련 문서를 검색하고 결과를 구조화합니다.
    """
    
    def __init__(
        self,
        top_k: int = 3,
        similarity_threshold: float = 0.5,
        content_type_filter: Optional[str] = None
    ):
        """
        DocumentRetriever 초기화
        
        Args:
            top_k: 반환할 최대 문서 개수
            similarity_threshold: 최소 유사도 점수 (0~1, 높을수록 엄격)
            content_type_filter: 문서 타입 필터 (예: 'guide', 'notice')
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.content_type_filter = content_type_filter
        self.vector_store = VectorStore()
    
    def retrieve(self, query: str) -> List[RetrievedDocument]:
        """
        쿼리에 대한 관련 문서를 검색합니다.
        
        Args:
            query: 사용자 질문 또는 검색어
            
        Returns:
            List[RetrievedDocument]: 검색된 문서 리스트 (유사도 순)
        """
        if not query or not query.strip():
            logger.warning("빈 쿼리로 검색 시도")
            return []
        
        # 벡터 저장소에서 유사 청크 검색
        # distance_threshold는 코사인 거리이므로 (1 - similarity_threshold)로 변환
        distance_threshold = 1.0 - self.similarity_threshold
        
        try:
            results = self.vector_store.search_similar_chunks(
                query_text=query,
                top_k=self.top_k,
                content_type=self.content_type_filter,
                distance_threshold=distance_threshold
            )
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}", exc_info=True)
            return []
        
        if not results:
            logger.info(f"검색 결과 없음: '{query[:50]}...'")
            return []
        
        # RetrievedDocument 객체로 변환
        retrieved_docs = []
        for chunk, similarity_score in results:
            doc = RetrievedDocument(
                content=chunk.content,
                title=chunk.document.title,
                source=chunk.document.source,
                content_type=chunk.document.content_type,
                similarity_score=similarity_score,
                chunk_index=chunk.chunk_index,
                metadata=chunk.metadata
            )
            retrieved_docs.append(doc)
        
        logger.info(f"검색 완료: {len(retrieved_docs)}개 문서 반환 (쿼리: '{query[:30]}...')")
        
        return retrieved_docs
    
    async def retrieve_async(self, query: str) -> List[RetrievedDocument]:
        """
        비동기 버전의 문서 검색
        
        Args:
            query: 사용자 질문 또는 검색어
            
        Returns:
            List[RetrievedDocument]: 검색된 문서 리스트 (유사도 순)
        """
        if not query or not query.strip():
            logger.warning("빈 쿼리로 검색 시도")
            return []
        
        distance_threshold = 1.0 - self.similarity_threshold
        
        try:
            results = await self.vector_store.search_similar_chunks_async(
                query_text=query,
                top_k=self.top_k,
                content_type=self.content_type_filter,
                distance_threshold=distance_threshold
            )
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}", exc_info=True)
            return []
        
        if not results:
            logger.info(f"검색 결과 없음: '{query[:50]}...'")
            return []
        
        # RetrievedDocument 객체로 변환
        retrieved_docs = []
        for chunk, similarity_score in results:
            doc = RetrievedDocument(
                content=chunk.content,
                title=chunk.document.title,
                source=chunk.document.source,
                content_type=chunk.document.content_type,
                similarity_score=similarity_score,
                chunk_index=chunk.chunk_index,
                metadata=chunk.metadata
            )
            retrieved_docs.append(doc)
        
        logger.info(f"검색 완료: {len(retrieved_docs)}개 문서 반환 (쿼리: '{query[:30]}...')")
        
        return retrieved_docs
    
    def format_context_for_llm(self, documents: List[RetrievedDocument]) -> str:
        """
        검색된 문서들을 LLM 프롬프트에 포함할 컨텍스트 문자열로 포맷팅합니다.
        
        Args:
            documents: 검색된 문서 리스트
            
        Returns:
            str: LLM에 전달할 컨텍스트 문자열
        """
        if not documents:
            return ""
        
        context_parts = ["다음은 관련 참고 자료입니다:\n"]
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n--- 참고자료 {i} (유사도: {doc.similarity_score:.2f}) ---")
            context_parts.append(doc.to_context_string())
        
        context_parts.append("\n--- 참고자료 끝 ---\n")
        
        return "\n".join(context_parts)


def search_documents(query: str, top_k: int = 3) -> List[RetrievedDocument]:
    """
    편의 함수: 기본 설정으로 문서를 검색합니다.
    
    Args:
        query: 검색 쿼리
        top_k: 반환할 최대 문서 개수
        
    Returns:
        List[RetrievedDocument]: 검색된 문서 리스트
    """
    retriever = DocumentRetriever(top_k=top_k)
    return retriever.retrieve(query)
