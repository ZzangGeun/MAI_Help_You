# 📱 메인 페이지 API 명세서

메이플스토리 AI 챗봇 - 메인 페이지의 API 문서입니다.

## 📋 기본 정보
- **서비스명**: MAI 챗봇 - 메인 페이지
- **Base URL**: `http://localhost:8000`
- **버전**: v1.0.1
- **최종 업데이트**: 2025-09-02

---

## 🌐 페이지 엔드포인트

### 메인 페이지 렌더링
- **URL**: `/`
- **Method**: `GET`
- **설명**: 메이플스토리 공지사항과 이벤트 정보가 포함된 메인 페이지
- **응답**: HTML 템플릿 렌더링

**성공 응답 (200 OK)**:
- 메인 페이지 HTML이 렌더링됨
- 로그인 기능 추가
- 챗봇 페이지 이동 기능 추가
- 캐릭터 검색 기능 추가

---

## 로그인 기능

**📝 기본 정보**
- **설명**: 페이지의 기본적인 로그인 기능 구현
- **인증**: 사용자 ID와 비밀번호를 입력하여 로그인

**📤 정상 응답 (200 OK)**
```json
{
  "status": "success",
  "components": {
    "login": {
      "status": "success",
      "message": "로그인 성공",
      "user_id": "user123",
      "nick_name": "무당햄스터",
    },
    "session": {
      "status": "success",
      "message": "세션 생성 성공",
      "session_id": "session123"
    },
    "database": {
      "status": "success",
      "message": "데이터베이스 연결 성공",
      "database_status": "connected"
    }
  },
  "uptime": "2d 15h 30m",
  "status": "success",
  "message": "로그인 성공",
  "version": "1.0.0",
  "timestamp": "2025-08-31T10:40:00Z"
}
```

## 로그아웃 기능

**📝 기본 정보**
- **설명**: 페이지의 기본적인 로그아웃 기능 구현
- **인증**: 로그인 상태에서 로그아웃 버튼을 누르면 로그아웃

**📤 정상 응답 (200 OK)**
```json
{
  "status": "success",
  "components": {
    "logout": {
      "status": "success",
      "message": "로그아웃 성공",
      "user_id": "null",
      "nick_name": "null",
    },
    "session": {
      "status": "success",
      "message": "세션 삭제 성공",
      "session_id": "session123"
    },
    "database": {
      "status": "success",
      "message": "데이터베이스 연결 해제 성공",
      "database_status": "disconnected"
    }
  },
  "uptime": "2d 15h 30m",
  "status": "success",
  "message": "로그아웃 성공",
  "version": "1.0.0",
  "timestamp": "2025-08-31T10:40:00Z"
}
```

## 챗봇 페이지 이동 기능

**📝 기본 정보**
- **설명**: 페이지의 기본적인 챗봇 페이지 이동 기능 구현
- **기능**: 챗봇 페이지 버튼을 누르면 챗봇 페이지로 이동
- **인증**: 로그인 상태에서 챗봇 페이지 버튼을 누르면 채팅 세션이 저장된 챗봇 페이지로 이동


**📤 정상 응답 (200 OK)**
- 비회원으로 챗봇 페이지 이동
```json
{
  "status": "success",
  "components": {
    "chatbot": {
      "status": "success",
      "message": "챗봇 페이지 이동 성공",
      "user_id": "null",
      "nick_name": "null",
    },
  },
}
```
- 회원으로 챗봇 페이지 이동
```json
{
  "status": "success",
  "components": {
    "chatbot": {
      "status": "success",
      "message": "챗봇 페이지 이동 성공",
      "user_id": "user123",
      "nick_name": "무당햄스터",
    },
    "session": {
      "status": "success",
      "message": "세션 유지 성공",
      "session_id": "session123"
    },
    "database": {
      "status": "success",
      "message": "데이터베이스 연결 유지 성공",
      "database_status": "connected"
    }   
  },
}
```
