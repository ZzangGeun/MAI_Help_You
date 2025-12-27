# -*- coding: utf-8 -*-
"""
문서 로더 및 전처리

외부 파일이나 데이터베이스에서 문서를 로드하고 청크로 분할하여 저장합니다.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from django.db import transaction

from .models import Document, DocumentChunk
from .embeddings import generate_embeddings_batch
from .vectorstore import VectorStore

logger = logging.getLogger(__name__)


class CharacterTextSplitter:
    """
    텍스트를 문자 수 기준으로 분할하는 클래스
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        splits = text.split(self.separator)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_len = len(split)
            if current_length + split_len > self.chunk_size and current_chunk:
                chunks.append(self.separator.join(current_chunk))
                # 겹침(overlap) 처리는 여기서는 단순화하여 다음 청크로 넘어감
                current_chunk = []
                current_length = 0
            
            current_chunk.append(split)
            current_length += split_len + len(self.separator)
            
        if current_chunk:
            chunks.append(self.separator.join(current_chunk))
            
        return [c.strip() for c in chunks if c.strip()]


def load_document_from_text(
    title: str,
    content: str,
    content_type: str = 'other',
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500
) -> Document:
    """
    텍스트로부터 문서를 생성하고 청크로 분할하여 임베딩까지 저장합니다.
    
    Args:
        title: 문서 제목
        content: 문서 내용
        content_type: 문서 타입 (guide, notice, item, quest, skill, other)
        source: 출처 URL 또는 파일명
        metadata: 추가 메타데이터
        chunk_size: 청크당 최대 문자 수
        
    Returns:
        Document: 생성된 문서 객체
        
    Raises:
        ValueError: 제목이나 내용이 비어있는 경우
    """
    if not title or not content:
        raise ValueError("제목과 내용은 필수입니다")
    
    with transaction.atomic():
        # 1. 문서 생성
        document = Document.objects.create(
            title=title,
            source=source,
            content_type=content_type,
            metadata=metadata or {}
        )
        
        logger.info(f"문서 생성: {title} (ID: {document.id})")
        
        # 2. 텍스트 분할
        splitter = CharacterTextSplitter(chunk_size=chunk_size)
        chunks_text = splitter.split_text(content)
        
        if not chunks_text:
            logger.warning(f"문서 '{title}'에서 청크를 생성하지 못했습니다")
            return document
        
        # 3. 청크 객체 생성 및 임베딩 할당
        embeddings = generate_embeddings_batch(chunks_text)
        
        for idx, (chunk_content, embedding) in enumerate(zip(chunks_text, embeddings)):
            DocumentChunk.objects.create(
                document=document,
                content=chunk_content,
                chunk_index=idx,
                embedding=embedding,
                metadata={}
            )
        
        logger.info(f"청크 및 임베딩 저장 완료: {len(chunks_text)}개")
    
    return document


def load_document_from_json_file(file_path: str) -> List[Document]:
    """
    JSON 파일로부터 여러 문서를 로드합니다.
    
    JSON 형식 예시:
    [
        {
            "title": "초보자 가이드",
            "content": "메이플스토리 초보자를 위한...",
            "content_type": "guide",
            "source": "https://maplestory.nexon.com/guide",
            "metadata": {"author": "GM"}
        },
        ...
    ]
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        List[Document]: 로드된 문서 리스트
        
    Raises:
        FileNotFoundError: 파일이 존재하지 않는 경우
        json.JSONDecodeError: JSON 파싱 실패
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        data = [data]
    
    documents = []
    for item in data:
        try:
            if 'title' not in item or 'content' not in item:
                # 필수 필드가 없으면 RAG 문서로 간주하지 않고 조용히 넘김 (메타데이터 파일 등)
                continue

            doc = load_document_from_text(
                title=item['title'],
                content=item['content'],
                content_type=item.get('content_type', 'other'),
                source=item.get('source'),
                metadata=item.get('metadata', {})
            )
            documents.append(doc)
        except Exception as e:
            logger.error(f"문서 로드 실패: {item.get('title', 'Unknown')} - {e}")
            continue
    
    logger.info(f"JSON 파일로부터 {len(documents)}개 문서 로드 완료")
    
    return documents


def load_sample_documents() -> List[Document]:
    """
    테스트용 샘플 문서를 로드합니다.
    
    메이플스토리 관련 기본 정보를 포함한 샘플 문서들을 생성합니다.
    
    Returns:
        List[Document]: 생성된 샘플 문서 리스트
    """
    sample_data = [
        {
            "title": "메이플스토리 초보자 가이드",
            "content": """
메이플스토리는 2D 횡스크롤 MMORPG입니다. 게임을 처음 시작하면 캐릭터를 생성하고 직업을 선택해야 합니다.

초보자를 위한 기본 팁:
1. 레벨 10까지는 튜토리얼을 진행하며 게임의 기본을 익히세요.
2. 직업 선택 시 자신의 플레이 스타일을 고려하세요. 전사는 체력이 높고, 마법사는 마법 공격이 강력합니다.
3. 퀘스트를 적극적으로 수행하여 경험치와 보상을 획득하세요.
4. 장비를 주기적으로 업그레이드하여 효율적으로 사냥하세요.
5. 길드에 가입하여 다른 플레이어들과 협력하세요.

레벨업이 빠른 초반 사냥터:
- 레벨 10-30: 헤네시스 사냥터, 돼지 해변
- 레벨 30-60: 페리온 사냥터, 커닝 스퀘어
- 레벨 60-100: 커닝 스퀘어, 루디브리엄
            """,
            "content_type": "guide",
            "source": "내부 가이드",
            "metadata": {"author": "GM", "difficulty": "beginner"}
        },
        {
            "title": "메이플스토리 직업 소개",
            "content": """
메이플스토리에는 다양한 직업군이 있습니다:

1. 전사: 높은 체력과 방어력, 근접 물리 공격
   - 히어로, 팔라딘, 다크나이트

2. 마법사: 강력한 마법 공격, 원거리 전투
   - 아크메이지(불,독), 아크메이지(썬,콜), 비숍

3. 궁수: 빠른 공격 속도, 원거리 물리 공격
   - 보우마스터, 신궁, 패스파인더

4. 도적: 빠른 이동 속도, 높은 회피율
   - 나이트로드, 섀도어, 듀얼블레이드

5. 해적: 근거리/원거리 공격 가능, 높은 기동성
   - 바이퍼, 캡틴, 캐논슈터

각 직업은 고유한 스킬과 플레이 스타일을 가지고 있으므로, 자신에게 맞는 직업을 선택하세요.
            """,
            "content_type": "guide",
            "source": "내부 가이드",
            "metadata": {"author": "GM", "category": "job"}
        },
        {
            "title": "메이플스토리 장비 강화 가이드",
            "content": """
장비 강화는 캐릭터의 전투력을 높이는 중요한 요소입니다.

주요 강화 방법:

1. 주문서 사용
   - 장비에 주문서를 사용하여 능력치를 향상시킬 수 있습니다.
   - 주문서에는 성공률이 있으며, 실패 시 장비가 파괴될 수 있습니다.
   - 프로텍트 실드를 사용하면 파괴를 방지할 수 있습니다.

2. 스타포스 강화
   - 메소를 사용하여 장비를 강화합니다.
   - 강화 단계가 높을수록 비용과 실패 확률이 증가합니다.
   - 스타포스 이벤트 기간에는 강화 비용이 할인됩니다.

3. 잠재능력
   - 잠재능력 큐브를 사용하여 추가 옵션을 부여합니다.
   - 등급: 레어 < 에픽 < 유니크 < 레전드리

4. 에디셔널 잠재능력
   - 잠재능력과 별도로 추가 옵션을 얻을 수 있습니다.

강화 팁:
- 중요한 장비는 이벤트 기간에 강화하세요.
- 메소를 충분히 모은 후 한 번에 강화하세요.
- 파괴 방지 아이템을 준비하세요.
            """,
            "content_type": "guide",
            "source": "내부 가이드",
            "metadata": {"author": "GM", "category": "equipment"}
        }
    ]
    
    documents = []
    for data in sample_data:
        try:
            doc = load_document_from_text(**data)
            documents.append(doc)
        except Exception as e:
            logger.error(f"샘플 문서 생성 실패: {data['title']} - {e}")
    
    logger.info(f"샘플 문서 {len(documents)}개 생성 완료")
    
    return documents


def load_documents(file_path: Optional[str] = None, load_samples: bool = False) -> List[Document]:
    """
    문서를 로드하는 통합 함수
    
    Args:
        file_path: JSON 파일 경로 (선택)
        load_samples: 샘플 문서 로드 여부
        
    Returns:
        List[Document]: 로드된 문서 리스트
    """
    documents = []
    
    if file_path:
        try:
            documents.extend(load_document_from_json_file(file_path))
        except Exception as e:
            logger.error(f"파일 로드 실패: {e}")
    
    if load_samples:
        documents.extend(load_sample_documents())
    
    return documents
