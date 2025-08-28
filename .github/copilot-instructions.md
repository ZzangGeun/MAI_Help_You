# 코파일럿 지침 (MAI 프로젝트)

## 목적
메이플스토리 AI 챗봇 - Django + LlamaIndex(RAG) + PostgreSQL(pgvector) 기반 프로젝트에서 AI 코딩 에이전트의 생산적 협업 지원

## 핵심 아키텍처
**HTTP 요청 → `chatbot/views.py` → `ChatbotService` (`chatbot/services.py`) → `RagEngine` (`chatbot/rag_engine.py`) → PostgreSQL 벡터DB → LLM**

### 프로젝트 구조 (실제)
```
MAI/                     # Django 메인 프로젝트
├── chatbot/             # 챗봇 앱 (RAG + LLM 통합)
├── character_info/      # 넥슨 API 캐릭터 정보
├── main_page/          # 메인 페이지 
apps/                   # 추가 앱들
├── character/, chatbot/, main/
fastapi_model/          # 선택적 FastAPI 마이크로서비스
config/                 # 환경 설정 모듈
├── env.py              # PostgreSQL/RAG/LLM 설정
```

## 핵심 패턴

### 1. 모듈 설계 (중요)
- **`config/env.py`**: 모든 환경 설정을 중앙화 (`get_pg_config()`, `get_rag_config()`, `get_llm_config()`)
- **`chatbot/services.py`**: 모듈 import 시 `chatbot_service = ChatbotService()` 싱글톤 초기화
- **`chatbot/rag_engine.py`**: LlamaIndex + pgvector 래퍼, PostgreSQL 테이블 자동 생성

### 2. 환경 변수 패턴 (.env 필수)
```bash
# 필수
HUGGINGFACE_TOKEN=...
SECRET_KEY=...

# PostgreSQL (pgvector)
PG_HOST=localhost / PGHOST=localhost
PG_DB=postgres / PGDATABASE=postgres
PG_USER=postgres / PGUSER=postgres
PG_PASSWORD=... / PGPASSWORD=...

# 선택적
LOCAL_MODEL_PATH=fine_tuned_model/merged_qwen
HF_BASE_MODEL=deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
```

### 3. LLM 모델 로딩 우선순위 (`CustomLLM`)
1. 로컬 파인튜닝 모델 (`fine_tuned_model/merged_qwen/`)
2. HuggingFace 공개 모델 (`deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`)
3. **중요**: tokenizer에 `pad_token = eos_token` 자동 설정

### 4. RAG 동작 패턴
- **임베딩**: `sentence-transformers/all-MiniLM-L6-v2` (384차원, CPU)
- **초기화**: 첫 실행 시 RAG 데이터 → pgvector 인덱싱 → 이후 DB 로드
- **검색**: `top_k=3` 유사 문서 반환

## 주요 API 엔드포인트
- `POST /chatbot/ask/`: 챗봇 질문 처리 (JSON: `{"question": "...", "user_id": "..."}`)
- `GET /chatbot/history/`: 대화 히스토리 조회
- `POST /chatbot/clear-history/`: 히스토리 초기화
- FastAPI 대안: `POST /api/chat` (포트 8001)

## 개발 워크플로우 (Windows)

### 필수 설정
```cmd
# 가상환경 활성화
conda activate mai_env

# PostgreSQL pgvector 확장 활성화 (DB에서)
CREATE EXTENSION IF NOT EXISTS vector;

# Django 서버 시작
python manage.py runserver

# FastAPI 서버 (선택적)
cd fastapi_model && uvicorn main:app --reload --port 8001
```

### FastAPI Import 패턴 (중요)
`fastapi_model/main.py`에서 **상대 import 사용**: `from .routes import router`
- Python 패키지 충돌 방지 (시스템 `routes` vs 프로젝트 `routes.py`)

## 핵심 주의사항

### ✅ 반드시 지킬 것
1. **싱글톤 패턴**: `chatbot_service` 재사용 (요청마다 모델 재로딩 금지)
2. **환경 변수**: 모든 설정은 `.env`에서 관리 (하드코딩 금지)
3. **PostgreSQL 일관성**: pgvector 테이블명/스키마 변경 시 전체 동기화

### ❌ 피해야 할 것
- 로컬 모델 경로 하드코딩 (폴백 로직 필수)
- 요청 시마다 RAG 인덱스 재생성
- FastAPI import에서 절대 경로 사용

### 디버깅 체크리스트
1. **환경 변수**: `HUGGINGFACE_TOKEN` 설정 확인
2. **PostgreSQL**: pgvector 확장 설치/활성화 확인
3. **모델 로딩**: 로컬 → HuggingFace 폴백 로그 확인
4. **RAG**: 첫 실행 시 인덱싱 완료 대기

## 확장 가이드
- **새 챗봇 기능**: `chatbot/views.py` → `chatbot_service.get_response()` 호출
- **모델 교체**: `config/env.py` 설정 변경 + `chatbot/services.py` 수정
- **RAG 데이터 추가**: PostgreSQL 벡터 인덱스 재생성 필요
