# MAI 챗봇 API 문서 📋

메이플스토리 AI 챗봇 프로젝트의 API 문서입니다.

## 🌐 서버 정보
- **Base URL**: `http://localhost:8000`
- **개발 서버**: Django Development Server

---

## 📄 페이지 엔드포인트

### 메인 페이지
- **URL**: `/`
- **Method**: `GET`
- **설명**: 메이플스토리 공지사항과 이벤트가 포함된 메인 페이지
- **응답**: HTML 페이지

### 캐릭터 정보 페이지
- **URL**: `/character_info/`
- **Method**: `GET`
- **설명**: 캐릭터 정보 조회 페이지
- **응답**: HTML 페이지

---

## 🔌 API 엔드포인트

### 1. 공지사항 목록 조회

```
GET /nexon_api/notice/
```

**설명**: 넥슨 메이플스토리 API로부터 공지사항 목록을 조회

**파라미터**:
- `page` (선택사항): 페이지 번호 (기본값: 1)

**성공 응답 (200 OK)**:
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
  }
}
```

**에러 응답 (503 Service Unavailable)**:
```json
{
  "success": false,
  "error": "넥슨 API 서비스에 연결할 수 없습니다"
}
```

### 2. 이벤트 목록 조회

```
GET /nexon_api/notice-event/
```

**설명**: 넥슨 메이플스토리 API로부터 이벤트 목록을 조회

**성공 응답 (200 OK)**:
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
  }
}
```

### 3. 특정 공지사항 상세 조회

```
GET /api/notice/{notice_id}/
```

**설명**: 특정 ID의 공지사항 상세 내용을 조회

**URL 파라미터**:
- `notice_id`: 공지사항 ID (정수, 예: 147581)

**예시 요청**:
```
GET /api/notice/147581/
```

**성공 응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "title": "넥슨에서 토스페이가 처음이라면 결제 시 10% 토스포인트 즉시 적립",
    "url": "https://maplestory.nexon.com/News/Notice/Notice/147581",
    "notice_id": 147581,
    "date": "2025-08-29T16:00+09:00",
    "content": "공지사항 상세 내용..."
  }
}
```

**에러 응답 (404 Not Found)**:
```json
{
  "success": false,
  "error": "공지사항을 찾을 수 없습니다"
}
```

---

## 🧪 테스트 방법

### 1. 브라우저에서 테스트
```
http://localhost:8000/nexon_api/notice/
```

### 2. curl 명령어로 테스트
```bash
# 공지사항 목록 조회
curl -X GET "http://localhost:8000/nexon_api/notice/"

# 이벤트 목록 조회
curl -X GET "http://localhost:8000/nexon_api/notice-event/"

# 특정 공지사항 조회
curl -X GET "http://localhost:8000/api/notice/147581/"
```

### 3. 자동화된 테스트
```bash
# 전체 API 테스트 실행
python tests/api/test_nexon_api.py
```

---

## 📊 에러 코드

| 상태 코드 | 설명 |
|---------|------|
| 200 | 성공 |
| 404 | 요청한 리소스를 찾을 수 없음 |
| 503 | 넥슨 API 서비스 이용 불가 |

---

## 🔗 관련 링크

- [넥슨 오픈 API](https://openapi.nexon.com/)
- [프로젝트 테스트 가이드](../tests/README.md)

---

**마지막 업데이트**: 2025-08-31
