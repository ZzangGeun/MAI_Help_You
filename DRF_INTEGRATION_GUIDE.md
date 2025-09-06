# Django REST Framework + LangChain 통합 가이드

## 🚀 개요

기존 Django 프로젝트에 DRF를 점진적으로 도입하고, LangChain 기반 RAG 시스템으로 전환하여 기존 구조를 해치지 않으면서 RESTful API와 고급 AI 기능을 제공합니다.

## 📁 새로운 프로젝트 구조

```
MAI_Help_You/
├── apps/
│   ├── api/                    # 🆕 DRF API 전용 앱
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── urls.py             # API v1 통합 URL
│   │   ├── chatbot_urls.py     # 챗봇 API URL
│   │   ├── chatbot_views.py    # 챗봇 API 뷰 (DRF)
│   │   ├── chatbot_serializers.py  # 챗봇 시리얼라이저
│   │   ├── character_urls.py   # 캐릭터 API (향후 확장)
│   │   └── auth_urls.py        # 인증 API (향후 확장)
│   ├── chatbot/               # 기존 챗봇 앱 (그대로 유지)
│   ├── character_info/        # 기존 캐릭터 앱 (그대로 유지)
│   └── ...
└── requirements.txt           # DRF 패키지 추가됨
```

## 🔧 설치 및 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 마이그레이션 (필요한 경우)
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🌐 API 엔드포인트

### 기존 vs 새로운 API

| 기능 | 기존 Django | 새로운 DRF | 설명 |
|------|-------------|------------|------|
| 챗봇 질문 | `POST /chatbot/ask/` | `POST /api/v1/chatbot/ask/` | 동일한 기능, DRF 버전 |
| 채팅 히스토리 | `GET /chatbot/history/` | `GET /api/v1/chatbot/history/` | 동일한 기능, DRF 버전 |
| 히스토리 삭제 | `POST /chatbot/clear-history/` | `POST /api/v1/chatbot/clear-history/` | 동일한 기능, DRF 버전 |
| 헬스체크 | `GET /chatbot/health/` | `GET /api/v1/chatbot/health/` | 동일한 기능, DRF 버전 |

### API 문서화
- **Swagger UI**: http://localhost:8000/api/docs/ (개발 환경에서만)
- **스키마**: http://localhost:8000/api/schema/

## 📝 사용 예시

### 챗봇 API 사용법

#### 1. 질문하기
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/ask/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "메이플스토리 레벨업 방법 알려줘",
    "user_id": "user123"
  }'
```

**응답:**
```json
{
  "response": "레벨업 방법에 대한 AI 응답...",
  "sources": ["가이드1", "가이드2"],
  "has_rag": true,
  "status": "success",
  "user_id": "user123"
}
```

#### 2. 히스토리 조회
```bash
curl -X GET "http://localhost:8000/api/v1/chatbot/history/?user_id=user123"
```

#### 3. JavaScript에서 사용
```javascript
// DRF API 사용
const response = await fetch('/api/v1/chatbot/ask/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: '질문 내용',
    user_id: 'user123'
  })
});

const data = await response.json();
console.log(data.response);
```

## 🔄 점진적 마이그레이션 전략

### Phase 1: 병행 운영 (현재 상태)
- ✅ **기존 Django API**: `/chatbot/ask/` 등 계속 동작
- ✅ **새로운 DRF API**: `/api/v1/chatbot/ask/` 추가 제공
- 두 API가 동시에 작동하여 호환성 유지

### Phase 2: 점진적 전환 (추천)
```python
# 기존 코드 (chatbot/views.py)
def chatbot_ask(request):
    # 기존 로직...
    pass

# 새로운 코드 (apps/api/chatbot_views.py)
class ChatbotAskAPIView(APIView):
    # DRF 로직...
    pass
```

### Phase 3: 완전 전환 (선택사항)
- 기존 API에서 새로운 API로 리다이렉트
- 또는 기존 API를 deprecated로 표시

## 🆕 새로운 기능 추가 가이드

### 1. 새로운 API 엔드포인트 추가

#### 캐릭터 정보 API 예시:
```python
# apps/api/character_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.character_info.get_character_info import get_character_data

class CharacterInfoAPIView(APIView):
    permission_classes = [AllowAny]
    
    async def get(self, request, character_name):
        try:
            character_info = await get_character_data(character_name)
            return Response({
                'character': character_info,
                'status': 'success'
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'status': 'error'
            }, status=500)
```

#### URL 연결:
```python
# apps/api/character_urls.py
from . import character_views

urlpatterns = [
    path('info/<str:character_name>/', 
         character_views.CharacterInfoAPIView.as_view(), 
         name='character-info'),
]
```

### 2. 시리얼라이저 추가
```python
# apps/api/character_serializers.py
class CharacterInfoResponseSerializer(serializers.Serializer):
    character_name = serializers.CharField()
    level = serializers.IntegerField()
    world_name = serializers.CharField()
    # ... 기타 필드들
```

## 🔍 개발 도구

### API 테스트
1. **Swagger UI**: http://localhost:8000/api/docs/
2. **Postman**: API 컬렉션 import 가능
3. **Django Shell**: `python manage.py shell`에서 직접 테스트

### 로깅 및 디버깅
```python
# settings/development.py에 추가
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.api': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🔐 보안 고려사항

### 개발 환경
- ✅ `AllowAny` 권한으로 테스트 용이
- ✅ CORS 전체 허용으로 프론트엔드 개발 편의

### 프로덕션 환경 준비
```python
# core/settings/production.py에서 설정 필요:

REST_FRAMEWORK.update({
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 인증 필요
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
})

# CORS를 특정 도메인으로 제한
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

## 📊 다음 단계

### 우선순위 1: 핵심 API 완성
- [ ] 캐릭터 정보 조회 API
- [ ] 사용자 인증 API  
- [ ] 넥슨 API 통합

### 우선순위 2: 고급 기능  
- [ ] API 버전 관리 (`v2` 등)
- [ ] 실시간 기능 (WebSocket)
- [ ] 캐싱 시스템
- [ ] LangChain RAG 성능 최적화

### 우선순위 3: 모니터링
- [ ] API 사용량 추적
- [ ] 에러 모니터링
- [ ] 성능 최적화

## 💡 팁

1. **기존 코드 재사용**: `apps.chatbot.services`의 `chatbot_service` 같은 비즈니스 로직은 그대로 활용
2. **단계별 적용**: 한 번에 모든 API를 변환하지 말고 하나씩 차근차근
3. **테스트 작성**: 새로운 API에 대한 유닛 테스트 추가 권장
4. **문서화**: API 스펙 변경 시 Swagger 문서 자동 업데이트

---

이 가이드를 통해 프로젝트 구조를 해치지 않으면서 DRF의 장점을 활용할 수 있습니다! 🚀
