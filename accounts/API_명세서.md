## 회원가입 API 명세

### Endpoint
`POST /signup/api/signup/`

### Request Body
```json
{
    "user_id": "testuser123",
    "email": "test@example.com",
    "password": "password123",
    "nickname": "테스터"
}
```

### Response (성공)
```json
{
    "message": "회원가입이 완료되었습니다.",
    "user": {
        "user_id": "testuser123",
        "nickname": "테스터",
        "email": "test@example.com"
    },
    "status": "success"
}
```

### Response (실패)
```json
{
    "error": "이미 존재하는 아이디입니다.",
    "status": "error"
}
```

### 유효성 검사 규칙
- user_id: 4-20자, 영문+숫자만
- password: 최소 8자
- email: 유효한 이메일 형식
- nickname: 필수 입력