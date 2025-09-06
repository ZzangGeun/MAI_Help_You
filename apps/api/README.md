# MAI Project DRF API

Django REST Framework + LangChain을 활용한 MAI 프로젝트 RESTful API입니다.

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

### 향후 확장 예정
- `GET /api/v1/character/info/<name>/` - 캐릭터 정보
- `POST /api/v1/auth/login/` - 로그인
- `GET /api/v1/auth/profile/` - 사용자 프로필

## 🔧 개발 가이드

새로운 API 추가 시:
1. `serializers.py` - 데이터 검증/직렬화
2. `views.py` - 비즈니스 로직
3. `urls.py` - URL 매핑
4. 테스트 코드 작성

자세한 내용은 `DRF_INTEGRATION_GUIDE.md`를 참고하세요.
