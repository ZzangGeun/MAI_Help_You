# 📱 메인 페이지 API 명세서

메이플스토리 AI 챗봇 - 메인 페이지의 API 문서입니다.

## 📋 기본 정보
- **서비스명**: MAI 챗봇 - 메인 페이지
- **Base URL**: `http://localhost:8000`
- **버전**: v1.0.0
- **최종 업데이트**: 2025-08-31

---

## 🌐 페이지 엔드포인트

### 메인 페이지 렌더링
- **URL**: `/`
- **Method**: `GET`
- **설명**: 메이플스토리 공지사항과 이벤트 정보가 포함된 메인 페이지
- **응답**: HTML 템플릿 렌더링

**성공 응답 (200 OK)**:
- 메인 페이지 HTML이 렌더링됨
- 공지사항과 이벤트 리스트가 포함된 페이지

---

## 🔌 넥슨 API 연동 엔드포인트

### 1. 공지사항 목록 조회

```
GET /nexon_api/notice/
```

**📝 기본 정보**
- **설명**: 넥슨 메이플스토리 공식 API에서 공지사항 목록을 가져옴
- **외부 API**: `https://open.api.nexon.com/maplestory/v1/notice`
- **캐시**: 1시간 (CACHE_DURATION)

**📥 요청 파라미터**
| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `page` | integer | 선택 | 페이지 번호 (기본값: 1) | `1` |

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "notice": [
      {
        "title": "넥슨에서 토스페이가 처음이라면 결제 시 10% 토스포인트 즉시 적립",
        "url": "https://maplestory.nexon.com/News/Notice/Notice/147581",
        "notice_id": 147581,
        "date": "2025-08-29T16:00+09:00"
      }
    ]
  },
  "total_count": 20,
  "page": 1
}
```

**❌ 에러 응답**
```json
// 503 Service Unavailable
{
  "success": false,
  "error": "넥슨 API 서비스에 연결할 수 없습니다",
  "error_code": "NEXON_API_UNAVAILABLE"
}

// 400 Bad Request  
{
  "success": false,
  "error": "잘못된 페이지 번호입니다",
  "error_code": "INVALID_PAGE_NUMBER"
}
```

---

### 2. 이벤트 목록 조회

```
GET /nexon_api/notice-event/
```

**📝 기본 정보**
- **설명**: 넥슨 메이플스토리 공식 API에서 진행 중인 이벤트 목록을 가져옴
- **외부 API**: `https://open.api.nexon.com/maplestory/v1/notice-event`
- **캐시**: 1시간 (CACHE_DURATION)

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "event_notice": [
      {
        "title": "썬데이 메이플",
        "url": "https://maplestory.nexon.com/News/Event/1187",
        "notice_id": 1187,
        "date": "2025-08-29T10:00+09:00",
        "date_event_start": "2025-08-31T00:00+09:00",
        "date_event_end": "2025-08-31T23:59+09:00"
      }
    ]
  },
  "total_count": 19
}
```

**❌ 에러 응답**
```json
// 503 Service Unavailable
{
  "success": false,
  "error": "넥슨 API 서비스에 연결할 수 없습니다",
  "error_code": "NEXON_API_UNAVAILABLE"
}
```

---

### 3. 특정 공지사항 상세 조회 (예정)

```
GET /api/notice/{notice_id}/
```

**📝 기본 정보**
- **설명**: 특정 공지사항의 상세 내용을 조회
- **개발 상태**: 🚧 개발 예정

**📥 URL 파라미터**
| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `notice_id` | integer | 필수 | 공지사항 ID | `147581` |

**📤 예상 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "title": "공지사항 제목",
    "url": "https://maplestory.nexon.com/News/Notice/Notice/147581",
    "notice_id": 147581,
    "date": "2025-08-29T16:00+09:00",
    "content": "공지사항 상세 내용...",
    "category": "일반",
    "importance": "normal"
  }
}
```

---

## 🧪 테스트 방법

### 1. 브라우저에서 테스트
```bash
# 메인 페이지
http://localhost:8000/

# 공지사항 API
http://localhost:8000/nexon_api/notice/

# 이벤트 API  
http://localhost:8000/nexon_api/notice-event/
```

### 2. cURL로 테스트
```bash
# 공지사항 목록 조회
curl -X GET "http://localhost:8000/nexon_api/notice/"

# 이벤트 목록 조회
curl -X GET "http://localhost:8000/nexon_api/notice-event/"

# 페이지네이션 테스트
curl -X GET "http://localhost:8000/nexon_api/notice/?page=2"
```

### 3. 자동 테스트
```bash
# 전체 API 테스트
python tests/api/test_nexon_api.py

# Django 통합 테스트
python manage.py shell
>>> from tests.api.test_django_integration import quick_test
>>> quick_test()
```

---

## 📊 에러 코드 정리

| HTTP 상태 | 에러 코드 | 설명 | 해결 방법 |
|----------|-----------|------|----------|
| 200 | - | 성공 | - |
| 400 | `INVALID_PAGE_NUMBER` | 잘못된 페이지 번호 | 1 이상의 정수 입력 |
| 503 | `NEXON_API_UNAVAILABLE` | 넥슨 API 서비스 불가 | 잠시 후 재시도 |
| 500 | `INTERNAL_SERVER_ERROR` | 서버 내부 오류 | 개발팀 문의 |

---

## ⚙️ 설정 및 환경변수

### 필요한 환경변수
```bash
# .env 파일
NEXON_API_KEY=your_nexon_api_key_here
```

### 캐시 설정
```python
# settings.py 또는 config/env.py
CACHE_DURATION = timedelta(hours=1)  # 1시간 캐시
```

---

## 🔗 관련 링크

- [넥슨 오픈 API 공식 문서](https://openapi.nexon.com/)
- [프로젝트 테스트 가이드](../../tests/README.md)
- [캐릭터 정보 API](./character_info_api_docs.md)
- [챗봇 API](./chatbot_page_api_docs.md)

---

## 📝 개발 노트

### TODO
- [ ] 특정 공지사항 상세 조회 API 구현
- [ ] 페이지네이션 개선
- [ ] 캐시 전략 최적화
- [ ] API 응답 시간 모니터링

### 변경 이력
- **v1.0.0** (2025-08-31): 초기 버전 - 공지사항/이벤트 목록 조회 API

---

**📅 마지막 업데이트**: 2025-08-31