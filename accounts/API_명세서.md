# Accounts API 명세서

## 1. 회원가입 (Signup)

**Endpoint:** `POST /accounts/api/signup/`

**설명:**  
새로운 사용자를 등록합니다. `nexon_api_key`를 입력하면 해당 키로 계정의 **가장 레벨이 높은 캐릭터**를 자동으로 찾아 연동합니다. API 키를 입력하지 않으면 캐릭터 연동 없이 회원가입만 진행됩니다.

### Request Body
```json
{
  "user_id": "testuser123",
  "password": "SecurePassword123!",
  "nexon_api_key": "your_nexon_api_key_here"  // 선택 사항
}
```

### Request Body 필드
- `user_id` (string, 필수): 사용자 아이디
  - 4~20자
  - 영문자와 숫자만 사용 가능
- `password` (string, 필수): 비밀번호
  - 최소 8자
  - 영문자, 숫자, 특수문자를 모두 포함해야 함
- `nexon_api_key` (string, 선택): 넥슨 오픈 API 키
  - **입력 시**: 자동으로 계정의 가장 레벨이 높은 캐릭터를 찾아 연동 (캐릭터명, OCID 저장)
  - **미입력 시**: 캐릭터 연동 없이 회원가입만 진행

### Response (성공 - API 키 포함)
**Status Code:** `201 Created`

```json
{
  "message": "회원가입이 완료되었습니다. (캐릭터 연동: 육즙기육카리)",
  "user": {
    "user_id": "testuser123",
    "linked_character": "육즙기육카리",
    "character_ocid": "caaa920c7065db6e87752c3a0c94e67e"
  },
  "status": "success"
}
```

### Response (성공 - API 키 없음)
**Status Code:** `201 Created`

```json
{
  "message": "회원가입이 완료되었습니다.",
  "user": {
    "user_id": "testuser123",
    "linked_character": null,
    "character_ocid": null
  },
  "status": "success"
}
```

### Response 필드
- `message` (string): 성공 메시지 (캐릭터 연동 시 캐릭터명 포함)
- `user` (object): 생성된 사용자 정보
  - `user_id` (string): 사용자 아이디
  - `linked_character` (string | null): 연동된 캐릭터명 (연동 안 한 경우 `null`)
  - `character_ocid` (string | null): 연동된 캐릭터 OCID (연동 안 한 경우 `null`)
- `status` (string): 응답 상태 (`"success"`)

### Response (실패)
**Status Code:** `400 Bad Request` 또는 `500 Internal Server Error`

```json
{
  "error": "이미 존재하는 아이디입니다.",
  "status": "error"
}
```

### 가능한 에러 메시지
- `"필수 필드(아이디, 비밀번호)를 채워주세요."` - 필수 필드 누락
- `"아이디는 4~20자의 영문자와 숫자만 사용 가능합니다."` - 아이디 형식 오류
- `"비밀번호는 최소 8자이며 영문자, 숫자, 특수문자를 모두 포함해야 합니다."` - 비밀번호 형식 오류
- `"이미 존재하는 아이디입니다."` - 중복 아이디
- `"유효하지 않은 API Key이거나 계정에 캐릭터가 없습니다."` - API 키 오류 또는 캐릭터 없음
- `"캐릭터 정보를 가져오는 중 오류가 발생했습니다."` - 캐릭터 정보 조회 실패

### 참고 사항
- 캐릭터 자동 연동 시 넥슨 API `/character/list` 엔드포인트를 사용하여 계정의 모든 캐릭터를 조회합니다
- 조회된 캐릭터 중 `character_level`이 가장 높은 캐릭터를 자동으로 선택합니다
- 선택된 캐릭터의 상세 정보는 JSON 파일로 `character_data/` 디렉토리에 저장됩니다
- 캐릭터 정보는 캐시(1시간)에 저장되어 중복 API 호출을 방지합니다

---

## 2. 로그인 (Login)

**Endpoint:** `POST /accounts/api/login/`

**설명:**  
등록된 사용자로 로그인합니다.

### Request Body
```json
{
  "user_id": "testuser123",
  "password": "SecurePassword123!"
}
```

### Request Body 필드
- `user_id` (string, 필수): 사용자 아이디
- `password` (string, 필수): 비밀번호

### Response (성공)
**Status Code:** `200 OK`

```json
{
  "message": "로그인에 성공했습니다.",
  "status": "success"
}
```

### Response (실패)
**Status Code:** `401 Unauthorized`

```json
{
  "error": "아이디 또는 비밀번호가 올바르지 않습니다.",
  "status": "error"
}
```

### 참고 사항
- 로그인 성공 시 세션이 생성됩니다
- 세션 쿠키를 통해 인증 상태가 유지됩니다

---

## 3. 로그아웃 (Logout)

**Endpoint:** `POST /accounts/api/logout/`

**설명:**  
현재 로그인된 사용자를 로그아웃합니다.

### Request Body
없음

### Response (성공)
**Status Code:** `200 OK`

```json
{
  "message": "로그아웃되었습니다.",
  "status": "success"
}
```

### Response (실패 - 인증 필요)
**Status Code:** `401 Unauthorized`

```json
{
  "error": "로그인이 필요합니다.",
  "status": "error"
}
```

### 참고 사항
- 로그인된 상태에서만 호출 가능합니다
- 로그아웃 시 세션이 삭제됩니다
