<<<<<<< HEAD
# 메이플스토리 AI 챗봇 (Django + LangChain + PostgreSQL/pgvector)

## 개요
메이플스토리 게임 정보를 제공하는 AI 챗봇입니다. LangChain 기반 RAG(Retrieval-Augmented Generation)와 PostgreSQL(pgvector),  대화 히스토리를 유지하면서, 관련 문서를 근거로 한 답변을 반환합니다.

## 주요 기능

### 🤖 AI 챗봇
- 파인튜닝/허깅페이스 모델 기반 응답 생성
- LangChain 기반 RAG 시스템 연동
- 근거 문서(소스) 표시 및 유사도 점수
- 대화 히스토리 유지 및 초기화

### 🔍 RAG 시스템
- 임베딩: `Qwen3-Embedding` (CPU)
- 벡터 DB: PostgreSQL + pgvector
- 최초 실행 시 `MAI_db/json_data/**` 인덱싱 → 이후에는 DB에서 로드
- Retriever Top-K: 3

### 💬 대화 관리
- 세션(또는 user_id)별 히스토리 저장/조회/초기화
- 대화 기반 문맥 유지

## 기술 스택

### Backend
- **Django 5.1.7** + **Django REST Framework**
- **LangChain**: RAG 시스템 및 문서 처리
- **PostgreSQL + pgvector**: 벡터 스토어 (LangChain PGVector)
- **Transformers**: 모델 로딩/추론
- (선택) **FastAPI 마이크로서비스**: 별도 모델 엔드포인트

### Frontend
- HTML/CSS/JS
- 반응형 UI (메인/챗봇 페이지)

### AI/ML
- 기본 모델: `Qwen3-4B-Thinking-2507` 또는 로컬 파인튜닝 모델
- 임베딩: `Qwen3-Embedding-0.6B`

## 설치 & 실행

### 1) 의존성 설치 (Windows CMD)
```cmd
pip install -r requirements.txt
```

### 2) 환경 변수(.env)
```
SECRET_KEY=...
HUGGINGFACE_TOKEN=...
NEXON_API_KEY=...

# PostgreSQL 접속 정보 (예시)
PGHOST=localhost
PGPORT=5432
PGDATABASE=mai
PGUSER=mai
PGPASSWORD=your_password
```

### 3) PostgreSQL + pgvector 준비
1. PostgreSQL 설치 및 DB/유저 생성
2. pgvector 확장 설치 후 DB에서 활성화
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

### 4) 마이그레이션
```cmd
python manage.py migrate
```

### 5) 서버 실행
```cmd
python manage.py runserver
```

선택) FastAPI 서버
```cmd
cd fastapi_model
uvicorn main:app --reload --port 8001
```

## 사용법

1) 메인/챗봇 접속
- 메인: `http://localhost:8000/`
- 챗봇: `http://localhost:8000/chatbot/`

2) 질문하기
- 질문을 입력하면 LangChain이 관련 문서를 검색하고 근거와 함께 답변을 생성

3) 대화 관리
- 히스토리 자동 저장, “대화 초기화” 버튼으로 클리어 가능

## 프로젝트 구조(요약)

```
MAI/
├── chatbot/                 # 챗봇 앱 (서비스/뷰/템플릿)
├── fastapi_model/           # 선택: FastAPI 모델 엔드포인트
├── MAI_db/json_data/        # RAG 원천 데이터(JSON)
├── static/                  # 정적 파일(CSS/JS/이미지)
└── templates/               # 공통 레이아웃 및 include
```

## RAG 동작 (LangChain + pgvector)
- 최초 실행 시 JSON 데이터를 인덱싱하여 PostgreSQL(pgvector)에 저장
- LangChain PGVector로 벡터 스토어 관리 및 유사도 검색
- 문서 청킹과 임베딩을 통해 의미 기반 검색 수행
- Top-K=3으로 근거 문서를 선별하여 답변에 반영

## API 엔드포인트

### 기존 Django API
- `POST /chatbot/ask/` 질문 처리
- `GET /chatbot/history/` 히스토리 조회
- `POST /chatbot/clear-history/` 히스토리 초기화
- `GET /chatbot/health/` 헬스 체크


## 광고(선택)
- 전역 인클루드 `includes/_ad_slot.html`로 어디서든 광고 슬롯 배치 가능
- .env로 `ADS_ENABLED`, `ADS_PROVIDER=adsense`, `ADSENSE_CLIENT`, 슬롯 ID를 설정

## 최신 버전 변경점
- **LlamaIndex → LangChain** (인덱스 중심에서 체인/에이전트 중심으로 전환)
- **개선된 문서 처리** (JSON 파싱 및 청킹 최적화)
- **유사도 점수 제공** (검색 결과에 점수 포함)
- **API 문서화** (Swagger UI 자동 생성)

## 문제 해결
- pgvector 미설치: DB에서 `CREATE EXTENSION vector;` 실행 필요
- 임베딩/허깅페이스 인증: `HUGGINGFACE_TOKEN` 확인
- 첫 인덱싱 지연: 최초 1회 생성 후엔 DB 로드로 빠르게 동작
=======
# 메이플스토리 AI 챗봇 (Django + LangChain + PostgreSQL/pgvector)

## 개요
메이플스토리 게임 정보를 제공하는 AI 챗봇입니다. LangChain 기반 RAG(Retrieval-Augmented Generation)와 PostgreSQL(pgvector), Django REST Framework를 활용해 안정적인 검색/추론 및 RESTful API를 제공합니다. 대화 히스토리를 유지하면서, 관련 문서를 근거로 한 답변을 반환합니다.

## 주요 기능

### 🤖 AI 챗봇
- 파인튜닝/허깅페이스 모델 기반 응답 생성
- LangChain 기반 RAG 시스템 연동
- 근거 문서(소스) 표시 및 유사도 점수
- 대화 히스토리 유지 및 초기화

### 🔍 RAG 시스템
- 임베딩: `Qwen3-Embedding` (CPU)
- 벡터 DB: PostgreSQL + pgvector
- 최초 실행 시 `MAI_db/json_data/**` 인덱싱 → 이후에는 DB에서 로드
- Retriever Top-K: 3

### 💬 대화 관리
- 세션(또는 user_id)별 히스토리 저장/조회/초기화
- 대화 기반 문맥 유지

## 기술 스택

### Backend
- **Django 5.1.7** + **Django REST Framework**
- **LangChain**: RAG 시스템 및 문서 처리
- **PostgreSQL + pgvector**: 벡터 스토어 (LangChain PGVector)
- **Transformers**: 모델 로딩/추론
- (선택) **FastAPI 마이크로서비스**: 별도 모델 엔드포인트

### Frontend
- HTML/CSS/JS
- 반응형 UI (메인/챗봇 페이지)

### AI/ML
- 기본 모델: `Qwen3-4B-Thinking-2507` 또는 로컬 파인튜닝 모델
- 임베딩: `Qwen3-Embedding-0.6B`

## 설치 & 실행

### 1) 의존성 설치 (Windows CMD)
```cmd
pip install -r requirements.txt
```

### 2) 환경 변수(.env)
```
SECRET_KEY=...
HUGGINGFACE_TOKEN=...
NEXON_API_KEY=...

# PostgreSQL 접속 정보 (예시)
PGHOST=localhost
PGPORT=5432
PGDATABASE=mai
PGUSER=mai
PGPASSWORD=your_password
```

### 3) PostgreSQL + pgvector 준비
1. PostgreSQL 설치 및 DB/유저 생성
2. pgvector 확장 설치 후 DB에서 활성화
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

### 4) 마이그레이션
```cmd
python manage.py migrate
```

### 5) 서버 실행
```cmd
python manage.py runserver
```

선택) FastAPI 서버
```cmd
cd fastapi_model
uvicorn main:app --reload --port 8001
```

## 사용법

1) 메인/챗봇 접속
- 메인: `http://localhost:8000/`
- 챗봇: `http://localhost:8000/chatbot/`

2) 질문하기
- 질문을 입력하면 LangChain이 관련 문서를 검색하고 근거와 함께 답변을 생성

3) 대화 관리
- 히스토리 자동 저장, “대화 초기화” 버튼으로 클리어 가능

## 프로젝트 구조(요약)

```
MAI/
├── chatbot/                 # 챗봇 앱 (서비스/뷰/템플릿)
├── fastapi_model/           # 선택: FastAPI 모델 엔드포인트
├── MAI_db/json_data/        # RAG 원천 데이터(JSON)
├── static/                  # 정적 파일(CSS/JS/이미지)
└── templates/               # 공통 레이아웃 및 include
```

## RAG 동작 (LangChain + pgvector)
- 최초 실행 시 JSON 데이터를 인덱싱하여 PostgreSQL(pgvector)에 저장
- LangChain PGVector로 벡터 스토어 관리 및 유사도 검색
- 문서 청킹과 임베딩을 통해 의미 기반 검색 수행
- Top-K=3으로 근거 문서를 선별하여 답변에 반영

## API 엔드포인트

### 기존 Django API
- `POST /chatbot/ask/` 질문 처리
- `GET /chatbot/history/` 히스토리 조회
- `POST /chatbot/clear-history/` 히스토리 초기화
- `GET /chatbot/health/` 헬스 체크


## 광고(선택)
- 전역 인클루드 `includes/_ad_slot.html`로 어디서든 광고 슬롯 배치 가능
- .env로 `ADS_ENABLED`, `ADS_PROVIDER=adsense`, `ADSENSE_CLIENT`, 슬롯 ID를 설정

## 최신 버전 변경점
- **LlamaIndex → LangChain** (인덱스 중심에서 체인/에이전트 중심으로 전환)
- **개선된 문서 처리** (JSON 파싱 및 청킹 최적화)
- **유사도 점수 제공** (검색 결과에 점수 포함)
- **API 문서화** (Swagger UI 자동 생성)

## 문제 해결
- pgvector 미설치: DB에서 `CREATE EXTENSION vector;` 실행 필요
- 임베딩/허깅페이스 인증: `HUGGINGFACE_TOKEN` 확인
- 첫 인덱싱 지연: 최초 1회 생성 후엔 DB 로드로 빠르게 동작
>>>>>>> feature/chatbot
