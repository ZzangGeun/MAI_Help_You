# -*- coding: utf-8 -*-
"""
pgvector 기반 벡터 저장소

pgvector를 사용하여 문서 임베딩을 저장하고 유사도 검색을 수행합니다.
"""

import logging
from typing import List, Tuple, Optional
from django.db.models import F
from pgvector.django import CosineDistance

from .models import DocumentChunk
from .embeddings import generate_embedding

logger = logging.getLogger(__name__)




class VectorStore:
    """
    pgvector 기반 벡터 저장소

    임베딩 벡터를 저장하고 코사인 유사도 기반 검색을 수행합니다.
    """

    def __init__(self):
        """
        VectorStore 초기화 (pgvector 사용)
        """
        logger.info("VectorStore 초기화 (pgvector 모드)")

    def save_embedding(
        self,
        chunk: DocumentChunk,
        vector: List[float],
        model_name: str = "jhgan/ko-sroberta-multitask"
    ) -> bool:
        """DocumentChunk 모델에 임베딩을 저장합니다.

        Args:
            chunk: 저장할 청크 객체
            vector: 768 차원 임베딩 벡터
            model_name: 사용 모델명 (현재는 메타데이터에 저장되지 않음)
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # pgvector 필드에 직접 저장
            chunk.embedding = vector
            chunk.save(update_fields=["embedding"])
            logger.info(f"임베딩 저장: {chunk.document.title} - Chunk {chunk.chunk_index}")
            return True
        except Exception as e:
            logger.error(f"임베딩 저장 실패: {e}", exc_info=True)
            return False

    def search_similar_chunks(
        self,
        query_text: str,
        top_k: int = 5,
        content_type: Optional[str] = None,
        distance_threshold: float = 1.0
    ) -> List[Tuple[DocumentChunk, float]]:
        """pgvector를 이용해 유사 청크를 검색합니다.

        Args:
            query_text: 검색할 텍스트
            top_k: 반환할 청크 수
            content_type: 필터링할 문서 타입 (옵션)
            distance_threshold: 코사인 거리 임계값 (0~2, 0에 가까울수록 유사)
        Returns:
            (DocumentChunk, similarity) 리스트
        """
        try:
            query_vector = generate_embedding(query_text)
            qs = DocumentChunk.objects.filter(embedding__isnull=False)
            if content_type:
                qs = qs.filter(document__content_type=content_type)
            # annotate cosine distance (pgvector function returns distance)
            qs = qs.annotate(distance=CosineDistance('embedding', query_vector))
            qs = qs.order_by('distance')[:top_k]
            results: List[Tuple[DocumentChunk, float]] = []
            for chunk in qs:
                similarity = 1.0 - chunk.distance  # convert distance to similarity
                if chunk.distance <= distance_threshold:
                    results.append((chunk, similarity))
            logger.info(f"검색 완료: '{query_text[:30]}...' -> {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"검색 실패: {e}", exc_info=True)
            return []

    async def search_similar_chunks_async(
        self,
        query_text: str,
        top_k: int = 5,
        content_type: Optional[str] = None,
        distance_threshold: float = 1.0
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        비동기 버전의 유사 청크 검색
        
        동기 검색 메서드를 sync_to_async로 래핑합니다.
        """
        from asgiref.sync import sync_to_async
        
        return await sync_to_async(
            self.search_similar_chunks,
            thread_sensitive=True
        )(query_text, top_k, content_type, distance_threshold)
    
    def get_stats(self) -> dict:
        """
        벡터 DB 통계를 반환합니다.
        
        Returns:
            dict: 통계 정보
        """
        try:
            total_chunks = DocumentChunk.objects.count()
            chunks_with_embedding = DocumentChunk.objects.filter(embedding__isnull=False).count()
            return {
                "total_chunks": total_chunks,
                "chunks_with_embedding": chunks_with_embedding,
                "vectorstore_type": "pgvector"
            }
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}", exc_info=True)
            return {}
    
    def reset_collection(self) -> bool:
        """
        모든 청크의 임베딩을 삭제합니다.
        
        주의: 이 작업은 되돌릴 수 없습니다!
        
        Returns:
            bool: 성공 여부
        """
        try:
            updated_count = DocumentChunk.objects.filter(embedding__isnull=False).update(embedding=None)
            logger.warning(f"임베딩 초기화 완료: {updated_count}개 청크")
            return True
        except Exception as e:
            logger.error(f"임베딩 초기화 실패: {e}", exc_info=True)
            return False
