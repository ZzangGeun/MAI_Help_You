## 회원가입 API 명세

### Endpoint
`POST /accounts/api/signup/`

### Request Body
```json
{
    "user_id": "testuser123",
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
- password: 최소 8자 영문 + 숫자 + 특수 문자 조합
- nickname: 2-10자, 한글/영문/숫자 가능

## 로그인 API 명세
### Endpoint
`POST /accounts/api/login/`

### Request Body
```json
{
    "user_id": "testuser123",
    "password": "password123"
}
```
### Response (성공)
```json
{
    "message": "로그인에 성공했습니다.",
}
```
### Response (실패)
```json
{
    "error": "아이디 또는 비밀번호가 올바르지 않습니다.",
    "status": "error"
}
```
