# MAI 프로젝트 URL 구조 가이드

## 📋 URL 패턴 규칙

### 1. 기본 구조
```
/{app_name}/              # 페이지 (HTML 렌더링)
/{app_name}/api/          # API 엔드포인트 (JSON 응답)
```

### 2. 네이밍 규칙

#### URL path (소문자, 하이픈 사용)
```python
# ✅ 권장
path('character-info/', ...)
path('api/user-profile/', ...)

# ❌ 비권장
path('characterInfo/', ...)  # camelCase
path('api/user_profile/', ...)  # snake_case in URL
```

#### URL name (snake_case 사용)
```python
# ✅ 권장
path('...', views.view_func, name='user_profile')
path('...', views.view_func, name='article_list')

# ❌ 비권장
name='userProfile'  # camelCase
name='article-list'  # kebab-case
```

### 3. 각 앱별 URL 패턴

#### **core/** (메인 페이지 및 공통 API)
```
/                              → main_page (홈)
/api/notices/                  → notice_list_api
/api/notices/cashshop/         → notice_cashshop_api
/api/notices/update/           → notice_update_api
/api/notices/event/            → notice_event_api
/api/rankings/overall/         → ranking_overall_api
/api/health/                   → health_check_api
```

#### **accounts/** (인증 관련)
```
/accounts/api/signup/          → signup_api
/accounts/api/login/           → login_api
/accounts/api/logout/          → logout_api
/accounts/api/profile/         → profile_api
```

#### **character/** (캐릭터 조회)
```
/character/                    → character_page (캐릭터 검색 페이지)
/character/api/search/         → character_search_api
/character/api/detail/<ocid>/  → character_detail_api
```

#### **chat/** (챗봇)
```
/chat/                         → chatbot_page (챗봇 페이지)
/chat/api/message/             → chat_message_api
/chat/api/sessions/            → chat_sessions_api
/chat/api/sessions/<id>/       → chat_session_detail_api
```

### 4. URL 역참조 (Reverse URL)

#### 템플릿에서
```django
{# 같은 앱 내 #}
<a href="{% url 'core:main_page' %}">홈</a>

{# 다른 앱 #}
<a href="{% url 'accounts:signup_api' %}">회원가입</a>
<a href="{% url 'chat:chatbot' %}">챗봇</a>
```

#### Python 코드에서
```python
from django.urls import reverse

# 절대 URL 생성
url = reverse('core:main_page')
url = reverse('character:character_page')
url = reverse('accounts:login_api')
```

### 5. RESTful API 규칙

#### Resource 기반 URL 설계
```python
# Collection (목록)
GET    /api/articles/           # 목록 조회
POST   /api/articles/           # 생성

# Item (개별 리소스)
GET    /api/articles/<id>/      # 상세 조회
PUT    /api/articles/<id>/      # 전체 수정
PATCH  /api/articles/<id>/      # 부분 수정
DELETE /api/articles/<id>/      # 삭제
```

#### Sub-resource 처리
```python
# 중첩 리소스
GET /api/users/<id>/posts/           # 특정 사용자의 포스트 목록
GET /api/users/<id>/posts/<post_id>/ # 특정 사용자의 특정 포스트
```

### 6. 파라미터 처리

#### URL Path Parameter (필수 값)
```python
path('articles/<int:id>/', views.detail, name='article_detail')
path('users/<str:username>/', views.profile, name='user_profile')
```

#### Query Parameter (선택적 필터)
```python
# URL: /api/articles/?category=tech&page=2
path('api/articles/', views.article_list, name='article_list_api')

# View에서
def article_list(request):
    category = request.GET.get('category')
    page = request.GET.get('page', 1)
```

### 7. 버전 관리 (선택사항)

API 버전이 필요한 경우:
```python
# 옵션 1: URL prefix
path('api/v1/', include('myapp.urls.v1'))
path('api/v2/', include('myapp.urls.v2'))

# 옵션 2: Accept header (권장)
# API 버전을 HTTP 헤더로 관리
```

### 8. 주의사항

#### ❌ 피해야 할 패턴
```python
# 동사 사용 (RESTful 위반)
path('api/get-user/', ...)      # ❌
path('api/users/', ...)         # ✅

# 불명확한 이름
path('data/', ...)              # ❌
path('character-data/', ...)    # ✅

# 일관성 없는 복수형
path('api/user/', ...)          # ❌
path('api/users/', ...)         # ✅

# trailing slash 불일치
path('api/users/', ...)         # ✅
path('api/posts', ...)          # ❌ (slash 누락)
```

#### ✅ 권장 패턴
```python
# 명확한 리소스 이름
path('api/users/', views.user_list, name='user_list_api')

# 계층 구조 표현
path('api/users/<int:user_id>/posts/', ...)

# 일관된 trailing slash
모든 URL에 trailing slash 사용
```

### 9. 실제 적용 예시

```python
# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages
    path('', views.main_page, name='main_page'),
    
    # API - Notices
    path('api/notices/', views.notice_list_api, name='notice_list_api'),
    path('api/notices/cashshop/', views.notice_cashshop_api, name='notice_cashshop_api'),
    path('api/notices/update/', views.notice_update_api, name='notice_update_api'),
    path('api/notices/event/', views.notice_event_api, name='notice_event_api'),
    
    # API - Rankings
    path('api/rankings/overall/', views.ranking_overall_api, name='ranking_overall_api'),
    
    # API - Health
    path('api/health/', views.health_check_api, name='health_check_api'),
]
```

## 🔍 참고 자료

- [Django URL dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [RESTful API 설계 가이드](https://restfulapi.net/)
- [Django REST Framework](https://www.django-rest-framework.org/)
