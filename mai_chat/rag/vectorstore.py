# -*- coding: utf-8 -*-
"""
ChromaDB 기반 벡터 저장소

ChromaDB를 사용하여 문서 임베딩을 저장하고 유사도 검색을 수행합니다.
"""

import logging
from typing import List, Tuple, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings

from .models import DocumentChunk
from .embeddings import generate_embedding, get_embedding_model

logger = logging.getLogger(__name__)

# ChromaDB 저장 경로
CHROMA_DB_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_db"
CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

# ChromaDB 클라이언트 (전역 싱글톤)
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    ChromaDB 클라이언트를 싱글톤 패턴으로 반환합니다.
    
    Returns:
        chromadb.PersistentClient: ChromaDB 클라이언트
    """
    global _chroma_client
    
    if _chroma_client is None:
        logger.info(f"ChromaDB 클라이언트 초기화 중 (경로: {CHROMA_DB_PATH})")
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.info("ChromaDB 클라이언트 초기화 완료")
    
    return _chroma_client


def get_collection(collection_name: str = "mai_documents"):
    """
    ChromaDB 컬렉션을 가져오거나 생성합니다.
    
    Args:
        collection_name: 컬렉션 이름
        
    Returns:
        Collection: ChromaDB 컬렉션
    """
    global _collection
    if _collection is None:
        client = get_chroma_client()
        
        try:
            _collection = client.get_collection(name=collection_name)
            logger.info(f"기존 컬렉션 '{collection_name}' 로드 완료")
        except Exception:
            # 컬렉션 생성 시 거리 측정 방식을 'cosine'으로 설정
            _collection = client.create_collection(
                name=collection_name,
                metadata={
                    "description": "메이플스토리 RAG 문서",
                    "hnsw:space": "cosine"
                }
            )
            logger.info(f"새 컬렉션 '{collection_name}' (Cosine Space) 생성 완료")
    
    return _collection


class VectorStore:
    """
    ChromaDB 기반 벡터 저장소
    
    임베딩 벡터를 저장하고 코사인 유사도 기반 검색을 수행합니다.
    """
    
    def __init__(self, collection_name: str = "mai_documents"):
        """
        VectorStore 초기화
        
        Args:
            collection_name: ChromaDB 컬렉션 이름
        """
        self.collection_name = collection_name
        self.collection = get_collection(collection_name)
    
    def save_embedding(
        self,
        chunk: DocumentChunk,
        vector: List[float],
        model_name: str = "jhgan/ko-sroberta-multitask"
    ) -> bool:
        """
        청크의 임베딩 벡터를 ChromaDB에 저장합니다.
        
        Args:
            chunk: 문서 청크 객체
            vector: 임베딩 벡터 (768차원 리스트)
            model_name: 사용한 임베딩 모델명
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # ChromaDB에 저장
            self.collection.add(
                ids=[str(chunk.id)],
                embeddings=[vector],
                documents=[chunk.content],
                metadatas=[{
                    "document_id": str(chunk.document.id),
                    "document_title": chunk.document.title,
                    "content_type": chunk.document.content_type,
                    "chunk_index": chunk.chunk_index,
                    "source": chunk.document.source or "",
                    "model_name": model_name
                }]
            )
            
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
        """
        쿼리 텍스트와 유사한 문서 청크를 검색합니다.
        
        Args:
            query_text: 검색할 질문 또는 텍스트
            top_k: 반환할 최대 결과 개수
            content_type: 문서 타입 필터 (선택, 예: 'guide', 'notice')
            distance_threshold: 최대 허용 거리 (ChromaDB는 작을수록 유사)
            
        Returns:
            List[Tuple[DocumentChunk, float]]: (청크, 유사도 점수) 튜플 리스트
            유사도 점수는 0~1 사이 (1에 가까울수록 유사)
        """
        try:
            # 쿼리 텍스트를 임베딩으로 변환
            query_embedding = generate_embedding(query_text)
            
            # 메타데이터 필터 구성
            where_filter = None
            if content_type:
                where_filter = {"content_type": content_type}
            
            # ChromaDB 검색 (거리 기반)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            print(f"DEBUG: ChromaDB raw results: {results['ids']}")
            print(f"DEBUG: ChromaDB raw distances: {results['distances']}")
            
            if not results or not results['ids'] or not results['ids'][0]:
                logger.info(f"검색 결과 없음: '{query_text[:50]}...'")
                print(f"DEBUG: ChromaDB에서 아무것도 찾지 못했습니다.")
                return []
            
            # 결과 파싱
            chunk_ids = results['ids'][0]
            distances = results['distances'][0]
            
            # 코사인 거리를 코사인 유사도로 변환
            # Cosine Distance = 1 - Cosine Similarity
            # 따라서 Similarity = 1 - Distance
            similarities = [1.0 - dist for dist in distances]
            
            # DocumentChunk 객체 가져오기
            chunks = DocumentChunk.objects.filter(
                id__in=chunk_ids
            ).select_related('document')
            
            print(f"DEBUG: Django DB chunks found: {len(chunks)} / {len(chunk_ids)}")
            
            chunk_dict = {str(chunk.id): chunk for chunk in chunks}
            
            # 결과 리스트 생성 (거리 임계값 적용)
            result_list = []
            for chunk_id, similarity, distance in zip(chunk_ids, similarities, distances):
                if distance <= distance_threshold:
                    if chunk_id in chunk_dict:
                        result_list.append((chunk_dict[chunk_id], similarity))
                    else:
                        print(f"DEBUG: Chunk ID {chunk_id} not found in Django database!")
            
            logger.info(f"검색 완료: '{query_text[:30]}...' -> {len(result_list)}개 결과")
            
            return result_list
            
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
        
        ChromaDB는 동기 API만 제공하므로 sync_to_async로 래핑합니다.
        """
        from asgiref.sync import sync_to_async
        
        return await sync_to_async(
            self.search_similar_chunks,
            thread_sensitive=True
        )(query_text, top_k, content_type, distance_threshold)
    
    def get_stats(self) -> dict:
        """
        ChromaDB 컬렉션 통계를 반환합니다.
        
        Returns:
            dict: 통계 정보
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "db_path": str(CHROMA_DB_PATH)
            }
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}", exc_info=True)
            return {}
    
    def reset_collection(self) -> bool:
        """
        컬렉션의 모든 데이터를 삭제합니다.
        
        주의: 이 작업은 되돌릴 수 없습니다!
        
        Returns:
            bool: 성공 여부
        """
        try:
            client = get_chroma_client()
            client.delete_collection(name=self.collection_name)
            
            # 컬렉션 재생성
            global _collection
            _collection = None
            self.collection = get_collection(self.collection_name)
            
            logger.warning(f"컬렉션 '{self.collection_name}' 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"컬렉션 초기화 실패: {e}", exc_info=True)
            return False
