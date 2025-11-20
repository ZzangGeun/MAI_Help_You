# 🤖 챗봇 페이지 API 명세서

메이플스토리 AI 챗봇 - 핵심 대화형 AI 서비스의 API 문서입니다.

## 📋 기본 정보
- **서비스명**: MAI 챗봇 (Maplestory AI Chatbot)
- **Base URL**: `http://localhost:8000`
- **버전**: v1.0.0
- **AI 엔진**: LangChain RAG + Fine-tuned LLM
- **벡터 DB**: PostgreSQL with pgvector
- **최종 업데이트**: 2025-08-31

## 🧠 AI 시스템 구조
```
사용자 질문 → Django Views → ChatbotService → LangChain RAG → 
PostgreSQL Vector DB → LLM 모델 → 답변 생성 → 사용자
```

---

## 🌐 페이지 엔드포인트

### 챗봇 페이지 렌더링
- **URL**: `/chatbot/`
- **Method**: `GET`
- **설명**: 메이플스토리 AI 챗봇과 대화할 수 있는 인터페이스 페이지
- **응답**: HTML 템플릿 렌더링

**기능**:
- 실시간 채팅 인터페이스
- 채팅 히스토리 표시
- RAG 소스 정보 표시
- 세션 기반 대화 관리

---

## 🔌 챗봇 API 엔드포인트

### 1. 챗봇 질문 처리 (핵심 기능)

```
POST /chatbot/ask/
```

**📝 기본 정보**
- **설명**: 메이플스토리 관련 질문을 AI에게 전달하고 답변을 받는 핵심 API
- **AI 모델**: Fine-tuned LLM (deepseek-ai/DeepSeek-R1-0528-Qwen3-8B 또는 로컬 모델)
- **RAG 엔진**: sentence-transformers/all-MiniLM-L6-v2 (384차원 임베딩)
- **벡터 검색**: PostgreSQL pgvector (top_k=3)
- **세션 관리**: Django 세션 기반

**📥 요청 데이터**
```json
{
  "question": "메르세데스 스킬 트리 알려줘",
  "user_id": "optional_user_identifier",
}
```

**📤 성공 응답 (200 OK)**
```json
{
  "response": "🏹 **메르세데스 스킬 정보**\n\n메르세데스는 궁수 계열의 히어로 직업으로, 우아하고 화려한 스킬을 가지고 있습니다.\n\n**주요 스킬:**\n- 엘리시온: 강력한 원거리 공격 스킬\n- 래피드 파이어: 연속 화살 발사\n- 유니콘 스파이크: 유니콘 소환 공격\n\n더 자세한 정보가 필요하시면 언제든 물어보세요! 😊",
  "sources": [
    {
      "title": "메르세데스 스킬 가이드",
      "content": "메르세데스는 엘프 왕국의 여왕으로, 활과 마법을 동시에 다루는 특별한 직업입니다...",
      "score": 0.95,
      "source_type": "guide"
    },
    {
      "title": "히어로 직업군 소개",
      "content": "메르세데스를 포함한 5명의 히어로들은...",
      "score": 0.87,
      "source_type": "general_info"
    }
  ],
  "has_rag": true,
  "processing_time": "2.3s",
  "status": "success",
  "user_id": "session_abc123def456",
  "timestamp": "2025-08-31T10:30:45Z"
}
```

**❌ 에러 응답**
```json
// 400 Bad Request - 질문 없음
{
  "error": "질문이 입력되지 않았습니다.",
  "status": "error",
  "error_code": "MISSING_QUESTION",
  "user_id": "session_abc123def456"
}

// 500 Internal Server Error - AI 모델 오류
{
  "error": "AI 모델에서 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
  "status": "error", 
  "error_code": "AI_MODEL_ERROR",
  "user_id": "session_abc123def456"
}

// 503 Service Unavailable - RAG 시스템 오류
{
  "error": "검색 시스템이 일시적으로 사용할 수 없습니다.",
  "status": "error",
  "error_code": "RAG_SYSTEM_ERROR",
  "user_id": "session_abc123def456"
}
```

---

### 2. 채팅 히스토리 조회

```
GET /chatbot/history/
```

**📝 기본 정보**
- **설명**: 사용자의 채팅 히스토리를 페이지네이션으로 조회
- **세션**: 세션 기반으로 사용자별 히스토리 관리
- **정렬**: 최신 순 (최대 50개 표시)

**📥 쿼리 파라미터**
| 파라미터 | 타입 | 필수 | 설명 | 기본값 | 예시 |
|---------|------|------|------|-------|------|
| `user_id` | string | 선택 | 사용자 ID (없으면 세션 ID 사용) | 세션 ID | `test_user` |
| `limit` | integer | 선택 | 조회할 대화 수 | 50 | `20` |
| `offset` | integer | 선택 | 건너뛸 대화 수 | 0 | `10` |

**📤 성공 응답 (200 OK)**
```json
{
  "history": [
    {
      "id": 1234,
      "question": "메르세데스 스킬 알려줘",
      "response": "🏹 메르세데스는 궁수 계열의 히어로 직업으로...",
      "timestamp": "2025-08-31T10:30:45Z",
      "has_rag": true,
      "processing_time": "2.3s",
      "sources_count": 2
    },
    {
      "id": 1233,
      "question": "아란은 어떤 직업이야?",
      "response": "⚔️ 아란은 전사 계열의 히어로 직업입니다...",
      "timestamp": "2025-08-31T10:28:12Z",
      "has_rag": true,
      "processing_time": "1.8s",
      "sources_count": 3
    }
  ],
  "total_count": 25,
  "has_more": false,
  "status": "success",
  "user_id": "session_abc123def456"
}
```

**❌ 에러 응답**
```json
// 404 Not Found - 히스토리 없음
{
  "history": [],
  "total_count": 0,
  "message": "채팅 히스토리가 없습니다.",
  "status": "success",
  "user_id": "session_abc123def456"
}
```

---

### 3. 채팅 히스토리 초기화

```
POST /chatbot/clear-history/
```

**📝 기본 정보**
- **설명**: 사용자의 모든 채팅 히스토리를 삭제
- **Content-Type**: `application/json`
- **주의**: 삭제된 히스토리는 복구할 수 없음

**📥 요청 데이터**
```json
{
  "user_id": "optional_user_id",
  "confirm": true
}
```

**📤 성공 응답 (200 OK)**
```json
{
  "message": "채팅 히스토리가 성공적으로 초기화되었습니다.",
  "deleted_count": 25,
  "status": "success",
  "user_id": "session_abc123def456",
  "timestamp": "2025-08-31T10:35:00Z"
}
```

**❌ 에러 응답**
```json
// 400 Bad Request - 확인 없음
{
  "error": "히스토리 삭제를 확인해주세요. (confirm: true 필요)",
  "status": "error",
  "error_code": "CONFIRMATION_REQUIRED"
}
```

---

### 4. 챗봇 상태 확인

```
GET /chatbot/health/
```

**📝 기본 정보**
- **설명**: AI 챗봇 시스템의 상태를 확인
- **모니터링**: AI 모델, RAG 엔진, 벡터 DB 상태 체크
- **인증**: 불필요 (public endpoint)

**📤 정상 응답 (200 OK)**
```json
{
  "status": "healthy",
  "components": {
    "ai_model": {
      "status": "healthy",
      "model_name": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
      "model_type": "local_finetuned",
      "last_response_time": "1.2s"
    },
    "rag_engine": {
      "status": "healthy",
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "vector_db": "postgresql_pgvector",
      "indexed_documents": 1250
    },
    "database": {
      "status": "healthy",
      "connection": "active",
      "vector_extension": "enabled"
    }
  },
  "uptime": "2d 15h 30m",
  "version": "1.0.0",
  "timestamp": "2025-08-31T10:40:00Z"
}
```

**❌ 오류 응답 (503 Service Unavailable)**
```json
{
  "status": "unhealthy",
  "components": {
    "ai_model": {
      "status": "error",
      "error": "모델 로딩 실패"
    },
    "rag_engine": {
      "status": "healthy"
    },
    "database": {
      "status": "error", 
      "error": "벡터 DB 연결 실패"
    }
  },
  "timestamp": "2025-08-31T10:40:00Z"
}
```

---

### 5. 실시간 채팅 (WebSocket) - 예정

```
WS /chatbot/ws/{session_id}/
```

**📝 기본 정보**
- **설명**: 실시간 양방향 채팅을 위한 WebSocket 연결
- **개발 상태**: 🚧 개발 예정
- **프로토콜**: WebSocket

**예상 메시지 형식**
```json
// 클라이언트 → 서버
{
  "type": "question",
  "content": "메르세데스에 대해 알려줘",
  "timestamp": "2025-08-31T10:45:00Z"
}

// 서버 → 클라이언트
{
  "type": "response",
  "content": "메르세데스는...",
  "sources": [...],
  "timestamp": "2025-08-31T10:45:03Z"
}

// 서버 → 클라이언트 (실시간 타이핑)
{
  "type": "typing",
  "status": "generating",
  "progress": "50%"
}
```

---

## 🧪 테스트 방법

### 1. 브라우저에서 테스트
```bash
# 챗봇 페이지
http://localhost:8000/chatbot/

# 시스템 상태 확인
http://localhost:8000/chatbot/health/
```

### 2. cURL로 테스트
```bash
# 챗봇에 질문하기
curl -X POST "http://localhost:8000/chatbot/ask/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"question": "메르세데스 스킬 알려줘", "user_id": "test_user"}'

# 채팅 히스토리 조회
curl -X GET "http://localhost:8000/chatbot/history/?user_id=test_user&limit=10"

# 히스토리 초기화
curl -X POST "http://localhost:8000/chatbot/clear-history/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"user_id": "test_user", "confirm": true}'

# 상태 확인
curl -X GET "http://localhost:8000/chatbot/health/"
```

### 3. JavaScript로 테스트
```javascript
// 챗봇 질문 함수
async function askChatbot(question, userId = null) {
    const response = await fetch('/chatbot/ask/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            question: question,
            user_id: userId
        })
    });
    
    return await response.json();
}

// 히스토리 조회 함수
async function getChatHistory(userId = null, limit = 20) {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (limit) params.append('limit', limit);
    
    const response = await fetch(`/chatbot/history/?${params}`);
    return await response.json();
}

// 실제 사용 예시
const result = await askChatbot("메르세데스 어떤 스킬이 좋아?");
console.log("챗봇 응답:", result.response);
console.log("RAG 소스:", result.sources);
```

### 4. Python으로 테스트
```python
import requests

# 챗봇 API 테스트
def test_chatbot_api():
    # 질문하기
    response = requests.post("http://localhost:8000/chatbot/ask/", json={
        "question": "메르세데스 스킬 트리 알려줘",
        "user_id": "test_user"
    })
    data = response.json()
    
    print(f"챗봇 응답: {data.get('response')}")
    print(f"RAG 사용: {data.get('has_rag')}")
    print(f"소스 개수: {len(data.get('sources', []))}")
    
    # 히스토리 조회
    history_response = requests.get("http://localhost:8000/chatbot/history/?user_id=test_user")
    history_data = history_response.json()
    print(f"대화 기록 수: {len(history_data.get('history', []))}")

# 실행
test_chatbot_api()
```

---

## 📊 에러 코드 정리

| HTTP 상태 | 에러 코드 | 설명 | 해결 방법 |
|----------|-----------|------|----------|
| 200 | - | 성공 | - |
| 400 | `MISSING_QUESTION` | 질문 누락 | 질문 내용 입력 필요 |
| 400 | `INVALID_REQUEST` | 잘못된 요청 형식 | JSON 형식 확인 |
| 400 | `CONFIRMATION_REQUIRED` | 삭제 확인 필요 | confirm: true 추가 |
| 401 | `CSRF_TOKEN_MISSING` | CSRF 토큰 누락 | CSRF 토큰 헤더 추가 |
| 429 | `RATE_LIMIT_EXCEEDED` | 요청 한도 초과 | 잠시 대기 후 재시도 |
| 500 | `AI_MODEL_ERROR` | AI 모델 오류 | 잠시 후 재시도 |
| 503 | `RAG_SYSTEM_ERROR` | RAG 시스템 오류 | 시스템 관리자 문의 |
| 503 | `DATABASE_ERROR` | 데이터베이스 오류 | 시스템 관리자 문의 |

---

## ⚙️ 설정 및 환경변수

### 필요한 환경변수
```bash
# .env 파일
HUGGINGFACE_TOKEN=your_huggingface_token
SECRET_KEY=your_django_secret_key

# PostgreSQL (pgvector)
PG_HOST=localhost
PG_DB=postgres  
PG_USER=postgres
PG_PASSWORD=your_password

# 선택적 - 로컬 파인튜닝 모델
LOCAL_MODEL_PATH=fine_tuned_model/merged_qwen
HF_BASE_MODEL=deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
```

### AI 모델 설정
```python
# config/env.py
def get_llm_config():
    return {
        'model_path': os.getenv('LOCAL_MODEL_PATH', 'fine_tuned_model/merged_qwen'),
        'hf_model': os.getenv('HF_BASE_MODEL', 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'),
        'max_new_tokens': 1000,
        'temperature': 0.7
    }

def get_rag_config():
    return {
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
        'chunk_size': 1000,
        'chunk_overlap': 200,
        'top_k': 3
    }
```

### 성능 최적화 설정
```python
# 챗봇 서비스 싱글톤 패턴 사용
# chatbot/services.py에서 모델을 한 번만 로드
chatbot_service = ChatbotService()  # 전역 인스턴스

# PostgreSQL 벡터 인덱스 최적화
# CREATE EXTENSION IF NOT EXISTS vector;
# CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 🔗 관련 링크

- [LangChain 공식 문서](https://python.langchain.com/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [메인 페이지 API](./main_page_api_docs.md)
- [캐릭터 정보 API](./character_info_api_docs.md)

---

## 📝 개발 노트

### AI 시스템 특징
- **RAG (검색증강생성)**: 정확한 메이플스토리 정보 제공
- **Fine-tuned Model**: 메이플스토리 특화 학습된 모델
- **Vector Search**: 의미론적 유사도 기반 정보 검색
- **Context Awareness**: 대화 맥락을 고려한 답변 생성

### TODO
- [ ] 실시간 WebSocket 채팅 구현
- [ ] 챗봇 응답 품질 평가 시스템
- [ ] 다중 언어 지원 (영어/일본어)
- [ ] 음성 인식/합성 기능 추가
- [ ] 채팅 테마 및 개인화 설정
- [ ] API 응답 캐싱 최적화

### 성능 지표
- **평균 응답 시간**: < 3초 목표
- **RAG 정확도**: 90%+ 목표  
- **사용자 만족도**: 4.0/5.0+ 목표
- **동시 접속자**: 100명+ 지원

### 변경 이력
- **v1.0.0** (2025-08-31): 초기 버전 - 기본 채팅 및 RAG 시스템

---

**📅 마지막 업데이트**: 2025-08-31
