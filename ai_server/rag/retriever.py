# -*- coding: utf-8 -*-
"""
문서 검색 서비스

Vector Store(의미 검색)와 BM25(키워드 검색)를 결합한 Hybrid Search를 구현합니다.
"""

import logging
import sys
import os
from typing import List, Optional

# --- LangChain 모듈 임포트 ---
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    # 내부 모듈 임포트
    from ai_server.rag.vectorstore import get_vectorstore
    from ai_server.rag.document_loader import DocumentLoader
except ImportError:
    try:
        from vectorstore import get_vectorstore
        from document_loader import DocumentLoader
    except ImportError as e:
        raise ImportError(f"필요한 모듈을 찾을 수 없습니다: {e}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, k: int = 5):
        """
        하이브리드 검색기 초기화 (Vector + BM25)
        """
        self.k = k
        self.vectorstore = get_vectorstore()
        self.retriever: Optional[BaseRetriever] = None

        self._initialize_hybrid_retriever()

    def _initialize_hybrid_retriever(self):
        """BM25 Retriever 초기화"""
        try:
            # BM25 Retriever 설정 (Keyword Search)
            self.retriever = self._create_bm25_retriever()

            if self.retriever:
                logger.info("✅ BM25 검색기 초기화 완료")
            else:
                # BM25 생성 실패 시 Vector Search를 Fallback으로 사용
                logger.warning("⚠️ BM25 초기화 실패로 Vector Search를 Fallback으로 사용합니다.")
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": self.k}
                )

        except Exception as e:
            logger.error(f"❌ 검색기 초기화 중 오류 발생: {e}")
            # 최악의 경우 Vector만이라도 동작하도록 시도
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.k})

    def _create_bm25_retriever(self) -> Optional[BM25Retriever]:
        """PostgreSQL에서 문서를 로드하여 BM25 인덱스 생성"""
        try:
            # PostgreSQL(pgvector)에서 모든 문서 가져오기
            docs = self._load_documents_from_vectorstore()

            if not docs:
                logger.warning("BM25 생성을 위한 문서 데이터가 없습니다.")
                return None

            # 공식 문서에 따른 BM25 초기화 방식
            bm25 = BM25Retriever.from_documents(docs)
            bm25.k = self.k  # 검색 개수 설정
            logger.info(f"✅ BM25 Retriever 초기화 완료 (문서 수: {len(docs)})")
            return bm25
        
        except ImportError:
            logger.error("❌ 'rank_bm25' 패키지가 설치되지 않았습니다. 'pip install rank_bm25'를 실행하세요.")
            return None
        except Exception as e:
            logger.error(f"BM25 생성 중 오류: {e}")
            return None
    
    def _load_documents_from_vectorstore(self) -> List[Document]:
        """
        PostgreSQL의 pgvector에서 모든 문서를 로드
        
        Returns:
            List[Document]: pgvector에 저장된 모든 문서 리스트
        """
        try:
            # pgvector에서 전체 문서 가져오기 (similarity_search with empty query)
            # 또는 get() 메서드로 전체 문서 가져오기
            # PGVector는 get() 메서드를 지원하지 않으므로, 
            # 임의의 쿼리로 충분히 많은 문서를 가져옴
            docs = self.vectorstore.similarity_search(
                query="",  # 빈 쿼리
                k=10000    # 충분히 큰 수로 모든 문서 가져오기
            )
            
            if docs:
                logger.info(f"PostgreSQL에서 {len(docs)}개 문서 로드 완료")
            
            return docs
        except Exception as e:
            logger.error(f"PostgreSQL에서 문서 로드 실패: {e}")
            # 대안: DocumentLoader로 JSON 파일에서 로드 시도 (Fallback)
            try:
                logger.info("Fallback: JSON 파일에서 문서 로드 시도")
                loader = DocumentLoader()
                return loader.load_json_file()
            except Exception as fallback_error:
                logger.error(f"Fallback 로드도 실패: {fallback_error}")
                return []

    def retrieve(self, query: str) -> List[Document]:
        """문서 검색 실행"""
        if not self.retriever:
            logger.error("검색기가 초기화되지 않았습니다.")
            return []

        logger.info(f"🔍 검색 요청 (Hybrid): {query}")
        try:
            # invoke() 메서드 사용
            docs = self.retriever.invoke(query)
            
            # 결과 로깅
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'unknown')
                title = doc.metadata.get('title', 'No Title')
                logger.info(f"  [Doc {i+1}] {source} | {title}")

            if not docs:
                logger.warning("검색 결과 없음")

            return docs

        except Exception as e:
            logger.error(f"검색 실행 오류: {e}")
            return []

# --- 테스트 실행 코드 ---
if __name__ == "__main__":
    test_query = "메이플스토리 크리스마스 이벤트"
    print(f"\n🚀 테스트 시작: {test_query}")
    
    try:
        retriever = Retriever(k=3)
        results = retriever.retrieve(test_query)

        print("\n📊 검색 결과:")
        for i, doc in enumerate(results):
            print(f"[{i+1}] {doc.metadata.get('title', '제목없음')} : {doc.page_content[:100]}...")
            
    except Exception as e:
        print(f"오류 발생: {e}")