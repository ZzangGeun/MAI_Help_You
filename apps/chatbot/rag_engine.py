import os
import logging
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, text
<<<<<<< Updated upstream

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQuery
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from core.legacy_config.env import get_pg_config, get_rag_config
=======
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
>>>>>>> Stashed changes


logger = logging.getLogger(__name__)


class RagEngine:
    """LlamaIndex + pgvector 기반 간단 RAG 엔진.

    - 임베딩: sentence-transformers/all-MiniLM-L6-v2 (384차원)
    - Vector Store: PostgreSQL pgvector (테이블 자동 생성)
    - 최초 실행 시 json_data를 인덱싱 후 PostgreSQL에 저장
    - 질의 시 top_k 유사 문서의 텍스트를 반환
    """

    def __init__(self) -> None:
<<<<<<< Updated upstream
        pg = get_pg_config()
        rag = get_rag_config()
        self.table_name = pg["table"]
        self.top_k = rag["top_k"]

        # Postgres 접속 정보
        self.host = pg["host"]
        self.port = pg["port"]
        self.db = pg["db"]
        self.user = pg["user"]
        self.password = pg["password"]

        # 임베딩 모델 (CPU)
        self.embed_model = HuggingFaceEmbedding(model_name=rag["embed_model"]) 
        self.embed_dim = rag["embed_dim"]
=======
        # LangChain에서는 collection_name 사용
        self.collection_name = os.getenv("PG_COLLECTION_NAME", "maple_docs")
        self.top_k = int(os.getenv("RAG_TOP_K", 3))

        # Postgres 접속 정보
        self.host = os.getenv("PGHOST", "localhost")
        self.port = os.getenv("PGPORT", "5432")
        self.db = os.getenv("PGDATABASE", "mai")
        self.user = os.getenv("PGUSER", "mai")
        self.password = os.getenv("PGPASSWORD")
        
        # PostgreSQL 연결 URL 생성
        self.connection_string = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

        # 임베딩 모델 (LangChain 방식)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            model_kwargs={'device': 'cpu'}
        )
        
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
>>>>>>> Stashed changes

        # Vector Store 초기화
        self.vector_store = PGVectorStore.from_params(
            database=self.db,
            host=self.host,
            password=self.password,
            port=self.port,
            user=self.user,
            table_name=self.table_name,
            embed_dim=self.embed_dim,
        )

        # 선택: 확장 설치 시도 (권한 없을 수 있어 예외 무시)
        self._ensure_vector_extension()

        # 데이터 유무 확인 후 없으면 인덱싱
        try:
            if self._count_rows() == 0:
                self._ingest_from_dir()
        except Exception as e:
            logger.warning("pgvector 카운트/인덱싱 중 경고: %s", e)

    # --- 내부 유틸 ---
    def _sqlalchemy_url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def _ensure_vector_extension(self) -> None:
        try:
            engine = create_engine(self._sqlalchemy_url())
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            logger.info("vector 확장 확인/생성 생략(%s)", e)

    def _count_rows(self) -> int:
        try:
            engine = create_engine(self._sqlalchemy_url())
            with engine.connect() as conn:
<<<<<<< Updated upstream
                result = conn.execute(text(f"SELECT COUNT(*) FROM {self.table_name}"))
                row = result.fetchone()
                return int(row[0]) if row else 0
        except Exception as e:
            logger.info("행 수 확인 실패(처음 생성일 수 있음): %s", e)
            return 0

    def _ingest_from_dir(self) -> None:
        data_path = get_rag_config()["data_path"]
=======
                # langchain-postgres는 langchain_pg_collection, langchain_pg_embedding 테이블을 사용합니다.
                # 컬렉션 이름으로 필터링하여 문서 수를 확인합니다.
                query = text("""
                    SELECT count(*)
                    FROM langchain_pg_embedding e
                    JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                    WHERE c.name = :collection_name
                """)
                result = conn.execute(query, {"collection_name": self.collection_name})
                count = result.scalar_one_or_none()
                return count or 0
        except Exception as e:
            # 테이블이 아직 존재하지 않을 경우 OperationalError 등이 발생할 수 있습니다.
            # 이 경우 0을 반환하여 인덱싱을 진행하도록 합니다.
            logger.info("행 수 확인 실패(테이블이 없을 수 있음): %s", e)
            return 0

    def _ingest_from_dir(self) -> None:
        """디렉토리에서 JSON 파일들을 로드하여 벡터 스토어에 인덱싱"""
        data_path = os.getenv("RAG_DATA_PATH", "MAI_db/json_data")
>>>>>>> Stashed changes
        if not os.path.exists(data_path):
            logger.warning("RAG 데이터 경로를 찾을 수 없습니다: %s", data_path)
            return

        # 단순: JSON 파일을 텍스트로 취급해 문서화
        documents: List[Document] = []
        for root, _, files in os.walk(data_path):
            for fn in files:
                if fn.lower().endswith(".json"):
                    fp = os.path.join(root, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            text = f.read()
                        documents.append(Document(text=text, metadata={"file": fn}))
                    except Exception as e:
                        logger.warning("파일 로드 실패 %s: %s", fp, e)

        if not documents:
            logger.info("인덱싱할 문서가 없습니다.")
            return

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        try:
            VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True,
                embed_model=self.embed_model,
            )
            logger.info("pgvector에 %d개 문서 인덱싱 완료", len(documents))
        except Exception as e:
            logger.warning("문서 인덱싱 중 오류(나중에 재시도 가능): %s", e)

    # --- 공개 API ---
    def retrieve_texts(self, query: str, top_k: Optional[int] = None) -> List[Tuple[str, dict]]:
        """유사 텍스트와 메타데이터를 반환.

        Returns: List of (text, metadata)
        """
        k = top_k or self.top_k
        try:
            q_embed = self.embed_model.get_query_embedding(query)
            res = self.vector_store.query(
                VectorStoreQuery(query_embedding=q_embed, similarity_top_k=k)
            )
            results: List[Tuple[str, dict]] = []
            if res and res.nodes:
                for node in res.nodes:
                    results.append((node.get_content(), node.metadata or {}))
            return results
        except Exception as e:
            logger.error("RAG 검색 실패: %s", e)
            return []
