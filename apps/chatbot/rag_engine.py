import os
import logging
import json
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import create_engine, text
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.legacy_config.env import get_pg_config, get_rag_config


logger = logging.getLogger(__name__)


class RagEngine:
    """LangChain + pgvector 기반 간단 RAG 엔진.

    - 임베딩: sentence-transformers/all-MiniLM-L6-v2 (384차원)
    - Vector Store: PostgreSQL pgvector (LangChain PGVector)
    - 최초 실행 시 json_data를 인덱싱 후 PostgreSQL에 저장
    - 질의 시 top_k 유사 문서의 텍스트를 반환
    """

    def __init__(self) -> None:
        pg = get_pg_config()
        rag = get_rag_config()
        self.collection_name = pg["table"]  # LangChain에서는 collection_name 사용
        self.top_k = rag["top_k"]

        # Postgres 접속 정보
        self.host = pg["host"]
        self.port = pg["port"]
        self.db = pg["db"]
        self.user = pg["user"]
        self.password = pg["password"]
        
        # PostgreSQL 연결 URL 생성
        self.connection_string = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

        # 임베딩 모델 (LangChain 방식)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=rag["embed_model"],
            model_kwargs={'device': 'cpu'}
        )
        
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Vector Store 초기화 (처음에는 None으로 두고 필요시 생성)
        self.vector_store = None

        # 선택: 확장 설치 시도 (권한 없을 수 있어 예외 무시)
        self._ensure_vector_extension()

        # 벡터 스토어 초기화 및 데이터 확인
        try:
            self._initialize_vector_store()
            if self._count_rows() == 0:
                self._ingest_from_dir()
        except Exception as e:
            logger.warning("pgvector 초기화/인덱싱 중 경고: %s", e)

    # --- 내부 유틸 ---
    def _ensure_vector_extension(self) -> None:
        """PostgreSQL에 pgvector 확장 설치"""
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            logger.info("vector 확장 확인/생성 생략(%s)", e)

    def _initialize_vector_store(self) -> None:
        """LangChain PGVector 벡터 스토어 초기화"""
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

    def _ingest_from_dir(self) -> None:
        """디렉토리에서 JSON 파일들을 로드하여 벡터 스토어에 인덱싱"""
        data_path = get_rag_config()["data_path"]
        if not os.path.exists(data_path):
            logger.warning("RAG 데이터 경로를 찾을 수 없습니다: %s", data_path)
            return

        if not self.vector_store:
            logger.warning("벡터 스토어가 초기화되지 않았습니다.")
            return

        # JSON 파일을 LangChain Document로 변환
        documents: List[Document] = []
        for root, _, files in os.walk(data_path):
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

    # --- 공개 API ---
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
