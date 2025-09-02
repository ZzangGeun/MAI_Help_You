# 📚 MAI 챗봇 API 문서 모음

메이플스토리 AI 챗봇 프로젝트의 모든 API 문서를 한눈에 볼 수 있는 가이드입니다.

## 🎯 프로젝트 개요
**MAI (Maplestory AI) 챗봇**은 Django + LlamaIndex RAG + PostgreSQL pgvector + Fine-tuned LLM을 활용한 메이플스토리 전문 AI 챗봇 서비스입니다.

## 📋 API 문서 목록

### 1. 📱 [메인 페이지 API](./main_page_api_docs.md)
- **서비스**: 넥슨 공식 API 연동
- **주요 기능**:
  - 메이플스토리 공지사항 목록 조회
  - 이벤트 정보 조회
  - 메인 페이지 렌더링

**핵심 엔드포인트**:
```
GET /                           # 메인 페이지
GET /nexon_api/notice/          # 공지사항 목록
GET /nexon_api/notice-event/    # 이벤트 목록
```

---

### 2. 👤 [캐릭터 정보 API](./character_info_api_docs.md)
- **서비스**: 캐릭터 정보 조회 시스템
- **주요 기능**:
  - 캐릭터 기본 정보 조회
  - 캐릭터 스탯 정보 조회  
  - 캐릭터 장비 정보 조회
  - 캐릭터 검색 기능

**핵심 엔드포인트**:
```
GET /character_info/                           # 캐릭터 정보 페이지
GET /api/character/{name}/basic/               # 캐릭터 기본 정보
GET /api/character/{name}/stat/                # 캐릭터 스탯
GET /api/character/{name}/item-equipment/      # 캐릭터 장비
POST /api/character/search/                    # 캐릭터 검색
```

---

### 3. 🤖 [챗봇 페이지 API](./chatbot_page_api_docs.md) ⭐
- **서비스**: AI 챗봇 대화 시스템 (핵심 기능)
- **기술 스택**: LlamaIndex RAG + Fine-tuned LLM + pgvector
- **주요 기능**:
  - AI 질문 답변 처리
  - 채팅 히스토리 관리
  - RAG 기반 정보 검색
  - 실시간 대화 인터페이스

**핵심 엔드포인트**:
```
GET /chatbot/                    # 챗봇 페이지
POST /chatbot/ask/               # AI 질문 처리 (핵심!)
GET /chatbot/history/            # 채팅 히스토리 조회  
POST /chatbot/clear-history/     # 히스토리 초기화
GET /chatbot/health/             # 챗봇 시스템 상태
```

---

## 🚀 빠른 시작 가이드

### 1. 환경 설정
```bash
# 가상환경 활성화
conda activate mai_env

# 환경변수 설정 (.env 파일)
NEXON_API_KEY=your_nexon_api_key
HUGGINGFACE_TOKEN=your_hf_token
PG_HOST=localhost
PG_USER=postgres
PG_PASSWORD=your_password
```

### 2. 서버 시작
```bash
# Django 서버 시작
python manage.py runserver

# PostgreSQL pgvector 확장 활성화 (DB에서 실행)
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. API 테스트
```bash
# 자동화된 전체 테스트
python tests/api/test_nexon_api.py

# Django 통합 테스트
python manage.py shell
>>> from tests.api.test_django_integration import quick_test
>>> quick_test()
```

---

## 🧪 API 테스트 방법

### 브라우저에서 테스트
```bash
# 각 페이지 확인
http://localhost:8000/                    # 메인 페이지
http://localhost:8000/character_info/     # 캐릭터 정보
http://localhost:8000/chatbot/            # 챗봇 페이지

# API 직접 호출
http://localhost:8000/nexon_api/notice/          # 공지사항
http://localhost:8000/chatbot/health/            # 챗봇 상태
```

### cURL로 API 테스트
```bash
# 공지사항 조회
curl -X GET "http://localhost:8000/nexon_api/notice/"

# 챗봇 질문 (CSRF 토큰 필요)
curl -X POST "http://localhost:8000/chatbot/ask/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"question": "메르세데스 스킬 알려줘"}'

# 캐릭터 검색
curl -X POST "http://localhost:8000/api/character/search/" \
  -H "Content-Type: application/json" \
  -d '{"character_name": "홍길동"}'
```

### JavaScript로 테스트
```javascript
// 챗봇 질문
async function askChatbot(question) {
    const response = await fetch('/chatbot/ask/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({question})
    });
    return await response.json();
}

// 공지사항 조회
async function getNotices() {
    const response = await fetch('/nexon_api/notice/');
    return await response.json();
}
```

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   사용자 요청    │───▶│ Django Views │───▶│ Service 계층 │
└─────────────────┘    └──────────────┘    └─────────────┘
                                                  │
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   AI 응답       │◀───│ LLM 모델     │◀───│ RAG Engine  │
└─────────────────┘    └──────────────┘    └─────────────┘
                                                  │
                       ┌──────────────┐    ┌─────────────┐
                       │ 넥슨 API     │    │PostgreSQL   │
                       │             │    │+ pgvector   │
                       └──────────────┘    └─────────────┘
```

**주요 구성 요소**:
- **Django**: 웹 프레임워크 및 API 서버
- **LlamaIndex**: RAG(검색증강생성) 엔진
- **PostgreSQL + pgvector**: 벡터 데이터베이스
- **Fine-tuned LLM**: 메이플스토리 특화 언어모델
- **Nexon OpenAPI**: 공식 게임 데이터

---

## 📊 에러 코드 공통 규칙

| HTTP 상태 | 의미 | 공통 해결책 |
|----------|------|-------------|
| **200** | 성공 | - |
| **400** | 잘못된 요청 | 요청 형식 및 파라미터 확인 |
| **401** | 인증 오류 | CSRF 토큰 또는 세션 확인 |
| **404** | 리소스 없음 | URL 경로 및 리소스 ID 확인 |
| **429** | 요청 한도 초과 | 잠시 대기 후 재시도 |
| **500** | 서버 내부 오류 | 로그 확인 후 관리자 문의 |
| **503** | 서비스 불가 | 외부 API 또는 DB 연결 확인 |

---

## 🔗 관련 링크

### 외부 문서
- [넥슨 오픈 API](https://openapi.nexon.com/)
- [LlamaIndex 문서](https://docs.llamaindex.ai/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)

### 프로젝트 내부 문서
- [테스트 가이드](../../tests/README.md)
- [프로젝트 설정 가이드](../../README.md)

### 개발 도구
- [API 자동 문서 생성](./auto_generate_docs.py)
- [API 테스트 스크립트](../../tests/api/)

---

## 📝 개발 현황

### ✅ 완료된 기능
- [x] 넥슨 API 연동 (공지사항, 이벤트)
- [x] AI 챗봇 기본 대화 시스템
- [x] RAG 기반 정보 검색
- [x] 채팅 히스토리 관리
- [x] 캐릭터 기본 정보 조회 (설계 완료)

### 🚧 개발 중인 기능
- [ ] 캐릭터 상세 정보 API 구현
- [ ] 실시간 WebSocket 채팅
- [ ] 챗봇 응답 품질 향상

### 🔮 향후 계획
- [ ] 다중 언어 지원
- [ ] 모바일 앱 API
- [ ] 음성 인식/합성 기능

---

## 🎯 API 사용 우선순위

### 🥇 **1순위 - 핵심 기능**
- `POST /chatbot/ask/` - AI 챗봇 질문 처리
- `GET /chatbot/health/` - 시스템 상태 확인

### 🥈 **2순위 - 주요 기능**  
- `GET /nexon_api/notice/` - 공지사항 조회
- `GET /chatbot/history/` - 채팅 히스토리

### 🥉 **3순위 - 부가 기능**
- `GET /api/character/*/basic/` - 캐릭터 정보
- `POST /chatbot/clear-history/` - 히스토리 초기화

---

**📅 마지막 업데이트**: 2025-08-31  
**📧 문의**: 프로젝트 관리자에게 연락  
**🐛 버그 리포트**: GitHub Issues 활용
