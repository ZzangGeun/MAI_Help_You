# -*- coding: utf-8 -*-
"""
문서 검색 서비스

벡터 저장소를 활용하여 사용자 질문과 관련된 문서를 검색합니다.
"""

import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_postgres import PGVector

from .vectorstore import get_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, k=3):
        """
        검색기 초기화
        """
        self.k = k
        self.vectorstore = get_vectorstore()
        print(self.vectorstore)

        # as_retriever : 벡터 저장소를 검색 가능한 객체 변환
        self.retriever = self.vectorstore.as_retriever(
            search_type = "similarity",
            search_kwargs = {"k": self.k}
            )
    
    def retrieve(self, query: str) -> List[Document]:
        """
        사용자 질문에 대한 관련 문서 검색
        """
        logger.info(f"문서 검색: {query}")
        try:
            # 실제 검색 수행
            docs = self.retriever.invoke(query)
            logger.info(f"검색 결과: {len(docs)} 문서")
            return docs
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}")
            return []
    



# --- 테스트 실행 코드 (이 파일을 직접 실행할 때만 작동) ---
if __name__ == "__main__":
    # 테스트하고 싶은 질문을 여기에 적으세요
    # 예: 데이터에 있는 보스 이름이나 스킬 이름을 넣어보세요
    test_query = "크리스마스 이벤트는 언제까지?" 
    
    retriever_instance = Retriever()
    results = retriever_instance.retrieve(test_query)
    
    print("\n" + "="*50)
    print(f"질문: {test_query}")
    print("="*50)
    
    for i, doc in enumerate(results):
        print(f"\n[문서 {i+1}]")
        # 메타데이터에 우리가 저장한 title이나 category가 있으면 출력
        title = doc.metadata.get('title', '제목 없음')
        category = doc.metadata.get('category', '카테고리 없음')
        print(f"출처: {category} > {title}")
        print("-" * 30)
        print(doc.page_content[:300]) # 내용이 너무 길면 300자까지만 출력
        if len(doc.page_content) > 300:
            print("... (생략)")


