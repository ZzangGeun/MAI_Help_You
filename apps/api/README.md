# MAI Project DRF API (집계 라우터)

Django REST Framework + LangChain을 활용한 MAI 프로젝트 RESTful API 집계 라우터입니다.

## 🏗️ 새로운 구조 (도메인별 분리)

API 구현이 각 도메인 앱 내부의 `api/` 패키지로 이동되었습니다:

```
apps/
├── main_page/api/       # 메인 페이지 API
├── chatbot/api/         # 챗봇 API  
├── character_info/api/  # 캐릭터 정보 API
├── signup/api/          # 회원가입/인증 API
└── api/                 # 집계 라우터 (이 파일)
    ├── urls.py          # 도메인별 라우팅
    └── management/      # 관리 명령어
```

## 🚀 빠른 시작

### 1. 서버 실행
```bash
python manage.py runserver
```

### 2. API 테스트
```bash
# 자동 테스트 실행
python manage.py test_api

# 수동 테스트
curl -X POST http://localhost:8000/api/v1/chatbot/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "안녕하세요", "user_id": "test"}'
```

### 3. API 문서 확인
- **Swagger UI**: http://localhost:8000/api/docs/
- **스키마**: http://localhost:8000/api/schema/

## 📋 현재 구현된 API

### 챗봇 API (`/api/v1/chatbot/`)
- `POST /ask/` - 질문하기
- `GET /history/` - 히스토리 조회  
- `POST /clear-history/` - 히스토리 삭제
- `GET /health/` - 서비스 상태 확인

### 메인 페이지 API (`/api/v1/main/`)
- `GET /notices/` - 공지사항 목록 조회
- `GET /events/` - 이벤트 목록 조회
- `GET /health/` - 시스템 헬스체크
- `POST /validate-api-key/` - 넥슨 API 키 검증

### 인증 API (`/api/v1/auth/`)
- `POST /register/` - 회원가입
- `POST /login/` - 로그인

### 향후 확장 예정
- `GET /api/v1/character/info/<name>/` - 캐릭터 정보
- `GET /api/v1/auth/profile/` - 사용자 프로필
- `POST /api/v1/main/events/<id>/subscribe/` - 이벤트 구독

## 🔧 개발 가이드

새로운 API 추가 시:
1. 해당 도메인 앱의 `api/` 패키지에 구현
2. `serializers.py` - 데이터 검증/직렬화
3. `views.py` - 비즈니스 로직
4. `urls.py` - URL 매핑
5. `apps/api/urls.py`에 라우팅 추가
6. 테스트 코드 작성

자세한 내용은 `DRF_INTEGRATION_GUIDE.md`를 참고하세요.