# 메이플스토리 AI 챗봇 프로젝트

## 프로젝트 개요
메이플스토리 게임 정보를 제공하는 AI 챗봇입니다. LangChain을 활용하여 RAG(Retrieval-Augmented Generation) 기반의 정확한 정보 제공과 대화 히스토리 관리 기능을 제공합니다.

## 주요 기능

### 🤖 AI 챗봇
- 파인튜닝된 메이플스토리 전용 AI 모델
- LangChain 기반 대화 관리
- RAG를 통한 정확한 정보 제공
- 실시간 대화 히스토리 유지

### 🔍 RAG 시스템
- FAISS 벡터 데이터베이스 활용
- 메이플스토리 관련 문서 검색
- 소스 문서 참조 기능
- 정확한 정보 제공

### 💬 대화 관리
- 세션별 대화 히스토리 저장
- 대화 초기화 기능
- 연속적인 대화 지원

## 기술 스택

### Backend
- **Django 5.1.7**: 웹 프레임워크
- **LangChain**: AI 체인 및 메모리 관리
- **FAISS**: 벡터 데이터베이스
- **Transformers**: AI 모델 관리
- **PEFT**: 파인튜닝 모델 로딩

### Frontend
- **HTML/CSS/JavaScript**: 사용자 인터페이스
- **Font Awesome**: 아이콘
- **반응형 디자인**: 모바일 지원

### AI/ML
- **DeepSeek-R1-0528-Qwen3-8B**: 베이스 모델
- **LoRA**: 파인튜닝 어댑터
- **Sentence Transformers**: 임베딩 모델

## 설치 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

### 3. 벡터 데이터베이스 생성 (선택사항)
```bash
python manage.py shell
```
```python
from chatbot.services import chatbot_service
# 벡터 스토어가 자동으로 생성됩니다
```

### 4. 서버 실행
```bash
# Django 서버
python manage.py runserver

# FastAPI 서버 (기존 모델 사용 시)
cd fastapi_model
uvicorn main:app --reload --port 8001
```

## 사용 방법

### 1. 챗봇 접속
브라우저에서 `http://localhost:8000/chatbot/` 접속

### 2. 질문하기
- 메이플스토리 관련 질문을 자유롭게 입력
- RAG 시스템이 관련 정보를 검색하여 정확한 답변 제공
- 소스 문서 참조 정보도 함께 표시

### 3. 대화 관리
- 대화 히스토리가 자동으로 저장됨
- "대화 초기화" 버튼으로 히스토리 삭제 가능

## 프로젝트 구조

```
nexon_2/
├── chatbot/                 # 챗봇 앱
│   ├── services.py         # LangChain 서비스
│   ├── views.py           # Django 뷰
│   ├── urls.py            # URL 패턴
│   └── templates/         # HTML 템플릿
├── fastapi_model/         # 기존 FastAPI 모델
├── fine_tuned_model/      # 파인튜닝된 모델
├── MAI_db/               # 데이터베이스 및 인덱스
│   ├── json_data/        # 메이플스토리 데이터
│   └── indexex/          # FAISS 인덱스
└── static/               # 정적 파일
    └── css/              # 스타일시트
```

## LangChain 적용 사항

### 1. CustomLLM 클래스
- 파인튜닝된 모델을 LangChain과 연동
- 기존 모델 로딩 로직 재사용

### 2. ChatbotService 클래스
- 대화 메모리 관리 (ConversationBufferMemory)
- RAG 체인 구성 (ConversationalRetrievalChain)
- 벡터 스토어 관리 (FAISS)

### 3. RAG 시스템
- 문서 로딩 및 분할
- 임베딩 생성 및 벡터 저장
- 유사도 기반 검색

### 4. API 엔드포인트
- `/chatbot/ask/`: 질문 처리
- `/chatbot/history/`: 대화 히스토리 조회
- `/chatbot/clear-history/`: 히스토리 초기화

## 성능 최적화

### 1. 모델 로딩
- 전역 변수로 모델 캐싱
- GPU 가속 지원
- 메모리 효율적 관리

### 2. 벡터 검색
- FAISS 인덱스 캐싱
- 효율적인 유사도 검색
- 검색 결과 제한 (k=3)

### 3. 대화 관리
- 세션별 메모리 관리
- 히스토리 크기 제한
- 효율적인 메시지 처리

## 문제 해결

### 1. 모델 로딩 오류
```bash
# CUDA 메모리 부족 시
export CUDA_VISIBLE_DEVICES=""
```

### 2. 벡터 스토어 생성 오류
```python
# 수동으로 벡터 스토어 생성
from chatbot.services import ChatbotService
service = ChatbotService()
```

### 3. 메모리 부족
- 모델을 CPU에서 실행
- 배치 크기 줄이기
- 벡터 스토어 크기 조정

## 향후 개선 사항

### 1. 고급 기능
- [ ] 사용자 인증 시스템
- [ ] 개인화된 대화 히스토리
- [ ] 실시간 채팅 기능

### 2. RAG 개선
- [ ] 더 정확한 문서 검색
- [ ] 다중 소스 통합
- [ ] 동적 문서 업데이트

### 3. 성능 최적화
- [ ] 모델 양자화
- [ ] 캐싱 시스템
- [ ] 로드 밸런싱

## 라이선스
이 프로젝트는 교육 목적으로 제작되었습니다.

## 기여하기
버그 리포트나 기능 제안은 이슈를 통해 제출해주세요. 