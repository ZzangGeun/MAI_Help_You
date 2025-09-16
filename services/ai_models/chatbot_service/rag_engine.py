# -*- coding: utf-8 -*-

import os
import logging
import json
from typing import List, Tuple, Any, Optional, Dict
from sqlalchemy import create_engine, text
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class ChatbotRAGService:
    """RAG 엔진 서비스 - LangChain + PostgreSQL pgvector 기반"""
    
    def __init__(self):
        self.vector_store: Optional[PGVector] = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.text_splitter: Optional[RecursiveCharacterTextSplitter] = None
        self.connection_string: str = ""
        self.collection_name: str = "rag_documents"
        self.top_k: int = 3
        self._setup_rag()
    
    def _get_pg_config(self) -> dict:
        """PostgreSQL 설정을 가져옵니다."""
        return {
            'host': os.getenv('PG_HOST', os.getenv('PGHOST', 'localhost')),
            'port': os.getenv('PG_PORT', os.getenv('PGPORT', '5432')),
            'user': os.getenv('PG_USER', os.getenv('PGUSER', 'postgres')),
            'password': os.getenv('PG_PASSWORD', os.getenv('PGPASSWORD', '')),
            'dbname': os.getenv('PG_DB', os.getenv('PGDATABASE', 'postgres')),
        }
    
    def _setup_rag(self):
        """RAG 엔진을 설정합니다."""
        try:
            # PostgreSQL 연결 설정
            pg_config = self._get_pg_config()
            
            # PostgreSQL 연결 URL 생성
            self.connection_string = f"postgresql+psycopg2://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['dbname']}"
            
            # pgvector 확장 확인 및 생성
            self._ensure_pgvector_extension()
            
            # 임베딩 모델 설정 (LangChain 방식)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # 텍스트 분할기 설정
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # 벡터 스토어 초기화
            self._initialize_vector_store()
            
            # 데이터 확인 및 초기 인덱싱
            if self._count_rows() == 0:
                self._ingest_from_dir()
                
        except Exception as e:
            logger.error(f"RAG 엔진 설정 중 오류 발생: {str(e)}")
            self.vector_store = None
            self.embeddings = None
    
    def _ensure_pgvector_extension(self):
        """PostgreSQL에 pgvector 확장이 설치되어 있는지 확인합니다."""
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            logger.info("pgvector 확장이 확인되었습니다.")
        except Exception as e:
            logger.error(f"pgvector 확장 확인 중 오류: {str(e)}")
            raise
    
    def _initialize_vector_store(self):
        """LangChain PGVector 벡터 스토어를 초기화합니다."""
        try:
            self.vector_store = PGVector(
                collection_name=self.collection_name,
                connection_string=self.connection_string,
                embedding_function=self.embeddings,
            )
            logger.info("LangChain PGVector 벡터 스토어 초기화 완료")
        except Exception as e:
            logger.warning("벡터 스토어 초기화 실패: %s", e)
            self.vector_store = None
    
    def _count_rows(self) -> int:
        """벡터 스토어의 문서 개수 확인"""
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                # LangChain PGVector의 기본 테이블명 형식
                table_name = f"langchain_pg_embedding_{self.collection_name}"
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row = result.fetchone()
                return int(row[0]) if row else 0
        except Exception as e:
            logger.info("행 수 확인 실패(테이블이 없을 수 있음): %s", e)
            return 0
    
    def _ingest_from_dir(self):
        """디렉토리에서 JSON 파일들을 로드하여 벡터 스토어에 인덱싱"""
        # RAG 데이터 디렉토리 확인
        rag_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "rag_data"
        )
        
        if not os.path.exists(rag_data_dir):
            logger.warning("RAG 데이터 경로를 찾을 수 없습니다: %s", rag_data_dir)
            return

        if not self.vector_store:
            logger.warning("벡터 스토어가 초기화되지 않았습니다.")
            return

        # JSON 파일을 LangChain Document로 변환
        documents: List[Document] = []
        for root, _, files in os.walk(rag_data_dir):
            for fn in files:
                if fn.lower().endswith(".json"):
                    fp = os.path.join(root, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # JSON 파일 내용을 파싱해서 더 의미있는 텍스트로 변환
                        try:
                            json_data = json.loads(content)
                            # JSON 구조를 텍스트로 변환
                            if isinstance(json_data, dict):
                                text_content = self._json_to_text(json_data)
                            elif isinstance(json_data, list):
                                text_content = "\n\n".join([
                                    self._json_to_text(item) if isinstance(item, dict) else str(item) 
                                    for item in json_data
                                ])
                            else:
                                text_content = str(json_data)
                        except json.JSONDecodeError:
                            # JSON 파싱 실패 시 원본 텍스트 사용
                            text_content = content
                        
                        # LangChain Document 생성
                        doc = Document(
                            page_content=text_content,
                            metadata={
                                "source": fn,
                                "file_path": fp,
                                "file_type": "json"
                            }
                        )
                        documents.append(doc)
                        
                    except Exception as e:
                        logger.warning("파일 로드 실패 %s: %s", fp, e)

        if not documents:
            logger.info("인덱싱할 문서가 없습니다.")
            return

        try:
            # 문서들을 청크로 분할
            split_docs = self.text_splitter.split_documents(documents)
            
            # LangChain PGVector에 문서 추가
            self.vector_store.add_documents(split_docs)
            
            logger.info("pgvector에 %d개 문서 (%d개 청크) 인덱싱 완료", 
                       len(documents), len(split_docs))
        except Exception as e:
            logger.warning("문서 인덱싱 중 오류(나중에 재시도 가능): %s", e)
    
    def _json_to_text(self, json_obj: Dict[str, Any]) -> str:
        """JSON 객체를 읽기 쉬운 텍스트로 변환"""
        text_parts = []
        for key, value in json_obj.items():
            if isinstance(value, (dict, list)):
                text_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else:
                text_parts.append(f"{key}: {value}")
        return "\n".join(text_parts)
    
    def retrieve_texts(self, query: str, top_k: Optional[int] = None) -> List[Tuple[str, dict]]:
        """유사 텍스트와 메타데이터를 반환 (LangChain 방식).

        Returns: List of (text, metadata)
        """
        k = top_k or self.top_k
        
        if not self.vector_store:
            logger.warning("벡터 스토어가 초기화되지 않았습니다.")
            return []
        
        try:
            # LangChain의 similarity_search_with_score 사용
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query, k=k
            )
            
            results: List[Tuple[str, dict]] = []
            for doc, score in docs_with_scores:
                # 메타데이터에 점수 추가
                metadata = doc.metadata.copy()
                metadata['similarity_score'] = float(score)
                
                results.append((doc.page_content, metadata))
            
            logger.debug(f"RAG 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error("RAG 검색 실패: %s", e)
            return []
    
    def add_documents(self, documents: List[Document]) -> bool:
        """새로운 문서들을 벡터 스토어에 추가"""
        if not self.vector_store:
            logger.warning("벡터 스토어가 초기화되지 않았습니다.")
            return False
        
        try:
            # 문서들을 청크로 분할
            split_docs = self.text_splitter.split_documents(documents)
            
            # 벡터 스토어에 추가
            self.vector_store.add_documents(split_docs)
            
            logger.info(f"{len(documents)}개 문서 ({len(split_docs)}개 청크) 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"문서 추가 실패: {e}")
            return False
    
    def clear_documents(self) -> bool:
        """벡터 스토어의 모든 문서 삭제 (주의: 복구 불가능)"""
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                table_name = f"langchain_pg_embedding_{self.collection_name}"
                conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()
            
            logger.info("모든 문서가 삭제되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"문서 삭제 실패: {e}")
            return False
    
    def is_ready(self) -> bool:
        """RAG 엔진이 준비되었는지 확인"""
        return self.vector_store is not None and self.embeddings is not None
