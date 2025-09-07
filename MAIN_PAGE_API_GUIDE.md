# Main Page API 사용 가이드

## 🚀 개요

Main Page API는 메이플스토리 공지사항, 이벤트, 사용자 인증, 시스템 헬스체크 등의 기능을 제공하는 RESTful API입니다.

## 📋 API 엔드포인트 목록

### 📢 공지사항 & 이벤트
- `GET /api/v1/main/notices/` - 공지사항 목록 조회
- `GET /api/v1/main/events/` - 이벤트 목록 조회

### 🔐 사용자 인증
- `POST /api/v1/main/auth/register/` - 회원가입
- `POST /api/v1/main/auth/login/` - 로그인

### 🔧 시스템 & 검증
- `GET /api/v1/main/health/` - 헬스체크
- `POST /api/v1/main/validate-api-key/` - 넥슨 API 키 검증

## 📝 사용 예시

### 1. 공지사항 목록 조회

#### **요청**
```bash
curl -X GET http://localhost:8000/api/v1/main/notices/ \
  -H "Content-Type: application/json"
```

#### **응답**
```json
{
  "notices": [
    {
      "notice_id": 1,
      "title": "[공지] 메이플스토리 업데이트 안내",
      "url": "https://maplestory.nexon.com/notice/1",
      "date": "2024-01-15",
      "notice_type": "업데이트"
    },
    {
      "notice_id": 2,
      "title": "[이벤트] 신년 이벤트 진행",
      "url": "https://maplestory.nexon.com/notice/2",
      "date": "2024-01-10",
      "notice_type": "이벤트"
    }
  ],
  "total_count": 2,
  "last_updated": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

### 2. 이벤트 목록 조회

#### **요청**
```bash
curl -X GET http://localhost:8000/api/v1/main/events/ \
  -H "Content-Type: application/json"
```

#### **응답**
```json
{
  "events": [
    {
      "event_id": 1,
      "title": "신년 맞이 경험치 2배 이벤트",
      "url": "https://maplestory.nexon.com/events/1",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "event_type": "경험치",
      "thumbnail_url": "https://example.com/thumbnail.jpg"
    }
  ],
  "total_count": 1,
  "last_updated": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

### 3. 사용자 회원가입

#### **요청**
```bash
curl -X POST http://localhost:8000/api/v1/main/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maple_user",
    "password": "secure_password123",
    "email": "user@example.com",
    "nickname": "메이플유저",
    "nexon_api_key": "your_nexon_api_key_here"
  }'
```

#### **응답**
```json
{
  "user": {
    "id": "maple_user",
    "username": "maple_user",
    "email": "user@example.com",
    "nickname": "메이플유저",
    "has_nexon_api": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "회원가입이 완료되었습니다.",
  "status": "success"
}
```

### 4. 사용자 로그인

#### **요청**
```bash
curl -X POST http://localhost:8000/api/v1/main/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maple_user",
    "password": "secure_password123"
  }'
```

#### **응답**
```json
{
  "user": {
    "id": "maple_user",
    "username": "maple_user",
    "email": "user@example.com",
    "nickname": "메이플유저",
    "has_nexon_api": true
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "로그인이 완료되었습니다.",
  "status": "success"
}
```

### 5. 시스템 헬스체크

#### **요청**
```bash
curl -X GET http://localhost:8000/api/v1/main/health/ \
  -H "Content-Type: application/json"
```

#### **응답**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": {
      "healthy": true,
      "message": "Database connection OK"
    },
    "nexon_api": {
      "healthy": true,
      "message": "Nexon API OK"
    },
    "system": {
      "healthy": true,
      "cpu_percent": 45.2,
      "memory_percent": 62.1,
      "disk_percent": 35.8,
      "message": "System resources OK"
    }
  },
  "version": "1.0.0"
}
```

### 6. 넥슨 API 키 검증

#### **요청**
```bash
curl -X POST http://localhost:8000/api/v1/main/validate-api-key/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_nexon_api_key_here"
  }'
```

#### **응답 (유효한 키)**
```json
{
  "is_valid": true,
  "api_info": {
    "key_type": "game_api",
    "expires_at": "2025-12-31",
    "permissions": ["character_info", "rankings"]
  },
  "status": "success"
}
```

#### **응답 (무효한 키)**
```json
{
  "is_valid": false,
  "error_message": "API 키가 유효하지 않습니다.",
  "status": "error"
}
```

## 🔧 JavaScript 사용 예시

### Fetch API를 사용한 공지사항 조회
```javascript
async function getNotices() {
  try {
    const response = await fetch('/api/v1/main/notices/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log('공지사항 목록:', data.notices);
      return data.notices;
    } else {
      console.error('공지사항 조회 실패:', data.error);
    }
  } catch (error) {
    console.error('네트워크 오류:', error);
  }
}

// 사용법
getNotices().then(notices => {
  notices.forEach(notice => {
    console.log(`${notice.title} - ${notice.date}`);
  });
});
```

### 회원가입 예시
```javascript
async function registerUser(userData) {
  try {
    const response = await fetch('/api/v1/main/auth/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (response.status === 201) {
      console.log('회원가입 성공:', data.user);
      localStorage.setItem('auth_token', data.token);
      return data.user;
    } else {
      console.error('회원가입 실패:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('회원가입 중 오류:', error);
    throw error;
  }
}

// 사용법
const newUser = {
  username: 'maple_user',
  password: 'secure_password123',
  email: 'user@example.com',
  nickname: '메이플유저',
  nexon_api_key: 'optional_api_key'
};

registerUser(newUser)
  .then(user => console.log('가입된 사용자:', user))
  .catch(error => console.error('가입 실패:', error));
```

## ⚡ 성능 최적화 팁

### 1. 캐싱 활용
```javascript
// 공지사항 캐싱 (5분간 유효)
const CACHE_DURATION = 5 * 60 * 1000; // 5분
let noticeCache = {
  data: null,
  timestamp: null
};

async function getCachedNotices() {
  const now = Date.now();
  
  if (noticeCache.data && 
      noticeCache.timestamp && 
      (now - noticeCache.timestamp) < CACHE_DURATION) {
    return noticeCache.data;
  }
  
  const notices = await getNotices();
  noticeCache = {
    data: notices,
    timestamp: now
  };
  
  return notices;
}
```

### 2. 에러 처리 및 재시도
```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.ok) {
        return response;
      } else if (response.status >= 500 && i < maxRetries - 1) {
        // 서버 에러 시 재시도
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        continue;
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

## 🔒 보안 고려사항

### 1. 인증 토큰 관리
```javascript
// 안전한 토큰 저장
function setAuthToken(token) {
  // HttpOnly 쿠키 사용 권장 (XSS 방지)
  document.cookie = `auth_token=${token}; HttpOnly; Secure; SameSite=Strict`;
}

// API 요청 시 토큰 자동 포함
async function authenticatedFetch(url, options = {}) {
  const token = getAuthToken(); // 쿠키에서 토큰 가져오기
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
}
```

### 2. API 키 보호
```javascript
// 클라이언트에서 API 키를 직접 노출하지 않음
// 대신 서버를 통해 검증
async function validateApiKeyOnServer(encryptedKey) {
  return fetch('/api/v1/main/validate-api-key/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      api_key: encryptedKey // 암호화된 키 전송
    })
  });
}
```

## 🧪 테스트

### 자동 테스트 실행
```bash
# 모든 API 테스트
python manage.py test_api

# 특정 API만 테스트 (예: main page)
curl -X GET http://localhost:8000/api/v1/main/health/
```

### API 문서 확인
- **Swagger UI**: http://localhost:8000/api/docs/
- **스키마**: http://localhost:8000/api/schema/

## 🎯 향후 계획

### 추가 예정 기능
- [ ] 실시간 공지사항 알림 (WebSocket)
- [ ] 사용자별 관심 이벤트 구독
- [ ] API 사용량 제한 (Rate Limiting)
- [ ] 캐시 무효화 API
- [ ] 관리자 전용 API

---

이제 Main Page도 완전한 DRF API로 사용할 수 있습니다! 🎉
