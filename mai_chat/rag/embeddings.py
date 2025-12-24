# -*- coding: utf-8 -*-
"""
임베딩 생성 서비스

한국어 텍스트를 벡터 임베딩으로 변환하는 서비스입니다.
sentence-transformers의 ko-sroberta-multitask 모델을 사용합니다.
"""

import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# 전역 싱글톤 임베딩 모델 (메모리 효율성을 위해)
_embedding_model: SentenceTransformer | None = None
_model_name: str = "jhgan/ko-sroberta-multitask"


def get_embedding_model() -> SentenceTransformer:
    """
    임베딩 모델을 싱글톤 패턴으로 로드합니다.
    
    첫 호출 시 모델을 다운로드하고 로드하며, 이후 호출에서는 캐시된 모델을 반환합니다.
    
    Returns:
        SentenceTransformer: 한국어 임베딩 모델
    """
    global _embedding_model
    
    if _embedding_model is None:
        logger.info(f"임베딩 모델 '{_model_name}' 로딩 중...")
        try:
            _embedding_model = SentenceTransformer(_model_name)
            logger.info(f"임베딩 모델 '{_model_name}' 로딩 완료")
        except Exception as e:
            logger.error(f"임베딩 모델 로딩 실패: {e}", exc_info=True)
            raise
    
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    단일 텍스트에 대한 임베딩 벡터를 생성합니다.
    
    Args:
        text: 임베딩할 텍스트 (한국어 또는 영어)
        
    Returns:
        List[float]: 768차원의 임베딩 벡터
        
    Raises:
        ValueError: 빈 텍스트가 입력된 경우
    """
    if not text or not text.strip():
        raise ValueError("텍스트가 비어있습니다")
    
    model = get_embedding_model()
    
    try:
        # 정규화(normalize_embeddings)를 적용하여 모든 벡터를 단위 벡터로 만듭니다.
        # 이를 통해 L2 거리가 코사인 유사도와 직접적으로 연관됩니다.
        embedding = model.encode(text.strip(), convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {e}", exc_info=True)
        raise


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    여러 텍스트에 대한 임베딩 벡터를 배치로 생성합니다.
    
    대량의 텍스트를 처리할 때 개별 호출보다 효율적입니다.
    
    Args:
        texts: 임베딩할 텍스트 리스트
        
    Returns:
        List[List[float]]: 각 텍스트의 768차원 임베딩 벡터 리스트
        
    Raises:
        ValueError: 빈 리스트가 입력된 경우
    """
    if not texts:
        raise ValueError("텍스트 리스트가 비어있습니다")
    
    # 빈 문자열 필터링
    valid_texts = [text.strip() for text in texts if text and text.strip()]
    
    if not valid_texts:
        raise ValueError("유효한 텍스트가 없습니다")
    
    model = get_embedding_model()
    
    try:
        # 배치 인코딩 (정규화 포함)
        embeddings = model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(valid_texts) > 10
        )
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"배치 임베딩 생성 실패: {e}", exc_info=True)
        raise


def get_embedding_dimension() -> int:
    """
    현재 사용 중인 임베딩 모델의 차원을 반환합니다.
    
    Returns:
        int: 임베딩 벡터의 차원 (ko-sroberta-multitask는 768)
    """
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()
