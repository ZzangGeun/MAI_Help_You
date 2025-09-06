# LlamaIndex → LangChain 마이그레이션 가이드

## 🚀 개요

MAI 프로젝트의 RAG 시스템을 LlamaIndex에서 LangChain으로 완전히 전환했습니다. 기존 기능은 그대로 유지하면서 LangChain의 강력한 기능들을 활용할 수 있게 되었습니다.

## 🔄 주요 변경사항

### **1. 패키지 변경**
```bash
# 이전 (LlamaIndex)
llama-index>=0.10.0
llama-index-vector-stores-postgres>=0.2.0
llama-index-embeddings-huggingface>=0.2.0

# 현재 (LangChain)
langchain>=0.1.0
langchain-community>=0.0.10
langchain-postgres>=0.0.6
sentence-transformers>=2.2.2
```

### **2. 코드 구조 변경**

#### **임베딩 모델**
```python
# 이전 (LlamaIndex)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 현재 (LangChain)
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
```

#### **벡터 스토어**
```python
# 이전 (LlamaIndex)
from llama_index.vector_stores.postgres import PGVectorStore
vector_store = PGVectorStore.from_params(
    database=db, host=host, password=password,
    port=port, user=user, table_name=table_name,
    embed_dim=embed_dim
)

# 현재 (LangChain)
from langchain_postgres.vectorstores import PGVector
vector_store = PGVector(
    collection_name=collection_name,
    connection_string=connection_string,
    embedding_function=embeddings
)
```

#### **문서 처리**
```python
# 이전 (LlamaIndex)
from llama_index.core import Document
documents = [Document(text=text, metadata={"file": fn})]

# 현재 (LangChain)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
)
doc = Document(page_content=text, metadata={"source": fn})
split_docs = text_splitter.split_documents([doc])
```

## 🆕 새로운 기능들

### **1. 개선된 문서 청킹**
```python
# 자동 문서 분할로 더 정확한 검색
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 청크 크기
    chunk_overlap=200,      # 겹치는 부분
    length_function=len,    # 길이 계산 함수
)
```

### **2. 유사도 점수 제공**
```python
# 검색 결과에 유사도 점수 포함
docs_with_scores = vector_store.similarity_search_with_score(query, k=3)
for doc, score in docs_with_scores:
    print(f"유사도: {score}, 내용: {doc.page_content}")
```

### **3. JSON 데이터 지능형 파싱**
```python
def _json_to_text(self, json_obj: Dict[str, Any]) -> str:
    """JSON을 읽기 쉬운 텍스트로 변환"""
    text_parts = []
    for key, value in json_obj.items():
        if isinstance(value, (dict, list)):
            text_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False, indent=2)}")
        else:
            text_parts.append(f"{key}: {value}")
    return "\n".join(text_parts)
```

### **4. 유연한 문서 관리**
```python
# 새로운 문서 추가
rag_engine.add_documents([document1, document2])

# 모든 문서 삭제 (주의!)
rag_engine.clear_documents()
```

## 🔧 마이그레이션 절차

### **1. 패키지 업데이트**
```bash
pip install -r requirements.txt
```

### **2. 기존 데이터 정리 (선택사항)**
```sql
-- 기존 LlamaIndex 테이블 삭제 (선택사항)
DROP TABLE IF EXISTS your_old_table;
```

### **3. 서버 재시작**
```bash
python manage.py runserver
```

### **4. 자동 재인덱싱**
- 첫 실행 시 자동으로 새로운 LangChain 형식으로 재인덱싱 됩니다
- PostgreSQL에 새로운 테이블 생성: `langchain_pg_embedding_[collection_name]`

## 📊 성능 비교

| 항목 | LlamaIndex | LangChain | 개선점 |
|------|------------|-----------|--------|
| 문서 청킹 | 단순 분할 | 지능형 분할 | 더 의미있는 청크 |
| 검색 정확도 | 기본 | 유사도 점수 | 결과 신뢰성 향상 |
| JSON 처리 | 원본 텍스트 | 구조화 파싱 | 더 나은 이해도 |
| 확장성 | 제한적 | 높음 | 다양한 체인 활용 |

## 🚨 주의사항

### **1. 데이터베이스 변경**
- LangChain은 다른 테이블 구조를 사용합니다
- 기존 데이터는 자동으로 재인덱싱됩니다

### **2. API 호환성**
- `retrieve_texts()` 메서드 시그니처는 동일하게 유지
- 응답에 `similarity_score` 추가됨

### **3. 메타데이터 변경**
```python
# 이전
{"file": "filename.json"}

# 현재  
{
    "source": "filename.json",
    "file_path": "/full/path/filename.json",
    "file_type": "json",
    "similarity_score": 0.85
}
```

## 🔍 문제 해결

### **문제 1: "langchain_postgres 모듈이 없습니다"**
```bash
pip install langchain-postgres>=0.0.6
```

### **문제 2: 기존 데이터가 검색되지 않음**
- 첫 실행 시 재인덱싱이 완료될 때까지 기다려주세요
- 로그에서 "인덱싱 완료" 메시지 확인

### **문제 3: PostgreSQL 연결 오류**
```python
# 연결 문자열 형식 확인
connection_string = "postgresql+psycopg2://user:pass@host:port/db"
```

## ✅ 검증 방법

### **1. RAG 엔진 테스트**
```python
# Django shell에서
from apps.chatbot.rag_engine import RagEngine

rag = RagEngine()
results = rag.retrieve_texts("메이플스토리 레벨업")
print(f"검색 결과: {len(results)}개")
for text, metadata in results:
    print(f"점수: {metadata.get('similarity_score', 'N/A')}")
```

### **2. API 테스트**
```bash
# DRF API 테스트
curl -X POST http://localhost:8000/api/v1/chatbot/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "메이플스토리 질문"}'
```

### **3. 문서 개수 확인**
```sql
-- 새로운 테이블에서 문서 개수 확인
SELECT COUNT(*) FROM langchain_pg_embedding_[your_collection_name];
```

## 🎯 다음 단계

### **1. LangChain 고급 기능 활용**
- **체인 구성**: 다단계 추론 체인
- **에이전트**: 동적 도구 사용
- **메모리**: 대화 컨텍스트 관리

### **2. 성능 최적화**
```python
# 캐싱 활용
from langchain.cache import InMemoryCache
llm.cache = InMemoryCache()

# 배치 처리
vector_store.add_documents(documents, batch_size=100)
```

### **3. 모니터링**
```python
# 성능 로깅
import time
start_time = time.time()
results = rag.retrieve_texts(query)
logger.info(f"검색 시간: {time.time() - start_time:.3f}초")
```

## 📚 참고 자료

- **LangChain 공식 문서**: https://docs.langchain.com/
- **PGVector 설정**: https://github.com/pgvector/pgvector
- **임베딩 모델**: https://huggingface.co/sentence-transformers

---

LlamaIndex에서 LangChain으로의 전환이 완료되었습니다! 🎉  
더 강력하고 유연한 RAG 시스템을 활용해보세요.
