# 코파일럿 지침 (MAI 프로젝트)

## 목적
- Django + LlamaIndex (RAG) 프로젝트에서 AI 코딩 에이전트가 생산적으로 협업할 수 있도록 지원.
- 선택적으로 FastAPI 마이크로서비스도 제공.

---

## 전체 구조
- Django 프로젝트 `MAI`  
  - 앱: `chatbot`, `character_info`, `main_page`
- 채팅 플로우:  
  **HTTP 요청 → `chatbot/views.py` → `ChatbotService` (`chatbot/services.py`) → LlamaIndex QueryEngine → PostgreSQL 벡터DB → LLM**
- RAG 데이터: `MAI_db/json_data/**`  
  - 최초 실행 시 인덱스를 생성해 PostgreSQL에 저장  
  - 이후에는 지속적으로 PostgreSQL에서 로드
- 선택적 모드: `fastapi_model/`에서 별도의 API 제공 (유사한 HuggingFace 모델 로직 활용)

---

## 주요 파일/디렉토리
- `MAI/settings.py`:  
  - `.env` 로드 (`dotenv` 사용)  
  - 기본 DB: SQLite  
  - 환경 변수: `SECRET_KEY`, `NEXON_API_KEY`, `OPENAI_API_KEY`, `HUGGINGFACE_TOKEN`
- `chatbot/services.py`:  
  - RAG + LLM 코어 로직  
  - 엔트리포인트:  
    - `ChatbotService.get_response()`  
    - `get_chat_history()`  
    - `clear_history()`
- `chatbot/views.py` + `chatbot/urls.py`:  
  - `/chatbot/ask/`  
  - `/chatbot/history/`  
  - `/chatbot/clear-history/`  
  - `/chatbot/health/`
- `fastapi_model/{main.py, routes.py, model.py}`  
  - FastAPI 별도 실행 진입점 (`uvicorn main:app`)
- `MAI_db/json_data/`: RAG 원천 데이터
- PostgreSQL DB: 벡터 저장소 (pgvector 확장 사용)

---

## LLM / RAG 동작
- `chatbot/services.py`에서 `chatbot_service = ChatbotService()`를 모듈 import 시점에 초기화 → 모델 및 메모리는 싱글톤처럼 동작
- `CustomLLM`:  
  - 로컬 파인튜닝 모델 (`fine_tuned_model/fine_tuned_model`)을 우선 시도  
  - 없으면 `Qwen/Qwen3-8B`로 폴백
- 임베딩: `sentence-transformers/all-MiniLM-L6-v2` (CPU)  
- Retriever: `top_k=3`
- 최초 실행 시:  
  - `MAI_db/json_data/**` → LlamaIndex 인덱싱 → PostgreSQL에 저장  
- Hugging Face Hub 로그인 필요 (`HUGGINGFACE_TOKEN`)

---

## 개발 워크플로우 (Windows CMD)
- 설치:  
  ```bash
  pip install -r requirements.txt


# 코파일럿 지침 (MAI 프로젝트)

## 목적
- Django + LlamaIndex (RAG) 프로젝트에서 AI 코딩 에이전트가 생산적으로 협업할 수 있도록 지원.
- 선택적으로 FastAPI 마이크로서비스도 제공.

---

## 전체 구조
- Django 프로젝트 `MAI`  
  - 앱: `chatbot`, `character_info`, `main_page`
- 채팅 플로우:  
  **HTTP 요청 → `chatbot/views.py` → `ChatbotService` (`chatbot/services.py`) → LlamaIndex QueryEngine → PostgreSQL 벡터DB → LLM**
- RAG 데이터: `MAI_db/json_data/**`  
  - 최초 실행 시 인덱스를 생성해 PostgreSQL에 저장  
  - 이후에는 지속적으로 PostgreSQL에서 로드
- 선택적 모드: `fastapi_model/`에서 별도의 API 제공 (유사한 HuggingFace 모델 로직 활용)

---

## 주요 파일/디렉토리
- `MAI/settings.py`:  
  - `.env` 로드 (`dotenv` 사용)  
  - 기본 DB: SQLite  
  - 환경 변수: `SECRET_KEY`, `NEXON_API_KEY`, `OPENAI_API_KEY`, `HUGGINGFACE_TOKEN`
- `chatbot/services.py`:  
  - RAG + LLM 코어 로직  
  - 엔트리포인트:  
    - `ChatbotService.get_response()`  
    - `get_chat_history()`  
    - `clear_history()`
- `chatbot/views.py` + `chatbot/urls.py`:  
  - `/chatbot/ask/`  
  - `/chatbot/history/`  
  - `/chatbot/clear-history/`  
  - `/chatbot/health/`
- `fastapi_model/{main.py, routes.py, model.py}`  
  - FastAPI 별도 실행 진입점 (`uvicorn main:app`)
- `MAI_db/json_data/`: RAG 원천 데이터
- PostgreSQL DB: 벡터 저장소 (pgvector 확장 사용)

---

## LLM / RAG 동작
- `chatbot/services.py`에서 `chatbot_service = ChatbotService()`를 모듈 import 시점에 초기화 → 모델 및 메모리는 싱글톤처럼 동작
- `CustomLLM`:  
  - 로컬 파인튜닝 모델 (`fine_tuned_model/fine_tuned_model`)을 우선 시도  
  - 없으면 `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`로 폴백
- 임베딩: `sentence-transformers/all-MiniLM-L6-v2` (CPU)  
- Retriever: `top_k=3`
- 최초 실행 시:  
  - `MAI_db/json_data/**` → LlamaIndex 인덱싱 → PostgreSQL에 저장  
- Hugging Face Hub 로그인 필요 (`HUGGINGFACE_TOKEN`)

---

## 개발 워크플로우 (Windows CMD)
- 설치:  
  ```bash
  pip install -r requirements.txt

cd fastapi_model
uvicorn main:app --reload --port 8001

SECRET_KEY=...
HUGGINGFACE_TOKEN=...
NEXON_API_KEY=...
OPENAI_API_KEY=...

RAG 데이터 갱신:

MAI_db/json_data/에 JSON 추가

PostgreSQL 벡터 인덱스 재생성

규칙 및 주의사항

요청마다 모델 재초기화 금지 → chatbot_service 재사용

PostgreSQL 벡터 인덱스 경로/스키마 일관성 유지

Windows 전용 경로 (CustomLLM.model_path)는 .env로 관리하도록 개선 권장

Tokenizer는 pad_token = eos_token 설정 필요 (이미 코드 반영됨)

FastAPI CORS 허용: http://localhost:8000, http://127.0.0.1:8000

기본 DB는 SQLite (마이그레이션은 Django 표준 사용)

확장 방법

새로운 챗봇 엔드포인트 추가:

chatbot/views.py에 뷰 작성

chatbot/urls.py에 라우트 등록

내부에서 chatbot_service.get_response() 호출

임베딩/모델 교체:

chatbot/services.py 수정

FastAPI 경로(fastapi_model/model.py)도 함께 변경

RAG 데이터 경로 변경:

json_data 경로 및 PostgreSQL 저장 위치 일관되게 수정

외부 연동

넥슨 API: NEXON_API_KEY (참고: main_page/get_nexon_api.py)

Hugging Face Hub: HUGGINGFACE_TOKEN

Do / Don’t

✅ 할 것

환경 변수는 반드시 .env에 설정 (하드코딩 금지)

모델 초기화는 단일 인스턴스 유지 (요청마다 새로 로드 X)

❌ 하지 말 것

PostgreSQL 벡터 인덱스 스키마/위치 변경 (일관성 깨짐)

로컬 파인튜닝 모델 경로 존재를 가정하지 말 것 (폴백 처리 필요)

스모크 테스트

Django 실행

/chatbot/ 접속

/chatbot/ask/에 POST 요청:
{ "question": "테스트" }

JSON 응답 확인:

정상 응답

PostgreSQL에 벡터 인덱스가 존재하면 
has_rag = true
