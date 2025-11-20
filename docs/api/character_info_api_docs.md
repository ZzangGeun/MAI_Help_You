# 👤 캐릭터 정보 API 명세서

메이플스토리 AI 챗봇 - 캐릭터 정보 조회 페이지의 API 문서입니다.

## 📋 기본 정보
- **서비스명**: MAI 챗봇 - 캐릭터 정보
- **Base URL**: `http://localhost:8000`
- **버전**: v1.0.0
- **최종 업데이트**: 2025-08-31

---

## 🌐 페이지 엔드포인트

### 캐릭터 정보 페이지 렌더링
- **URL**: `/character_info/`
- **Method**: `GET`
- **설명**: 캐릭터 정보를 조회하고 표시하는 페이지
- **응답**: HTML 템플릿 렌더링

**성공 응답 (200 OK)**:
- 캐릭터 검색 폼과 정보 표시 페이지가 렌더링됨

---

## 🔌 캐릭터 정보 API 엔드포인트

### 1. 캐릭터 기본 정보 조회

```
GET /api/character/{character_name}/basic/
```

**📝 기본 정보**
- **설명**: 넥슨 API를 통해 캐릭터의 기본 정보를 조회
- **외부 API**: `https://open.api.nexon.com/maplestory/v1/character/basic`
- **캐시**: 30분

**📥 URL 파라미터**
| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `character_name` | string | 필수 | 캐릭터명 (URL 인코딩 필요) | `홍길동` |

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "character_name": "홍길동",
    "world_name": "스카니아",
    "character_gender": "남",
    "character_class": "히어로",
    "character_class_level": "4차",
    "character_level": 275,
    "character_exp": 123456789,
    "character_exp_rate": "15.5%",
    "character_guild_name": "길드명",
    "character_image": "https://avatar.maplestory.nexon.com/...",
    "character_date_create": "2020-01-15T00:00:00Z",
    "access_flag": "true"
  }
}
```

**❌ 에러 응답**
```json
// 404 Not Found
{
  "success": false,
  "error": "캐릭터를 찾을 수 없습니다",
  "error_code": "CHARACTER_NOT_FOUND"
}

// 400 Bad Request
{
  "success": false,
  "error": "캐릭터명이 올바르지 않습니다",
  "error_code": "INVALID_CHARACTER_NAME"
}
```

---

### 2. 캐릭터 스탯 정보 조회

```
GET /api/character/{character_name}/stat/
```

**📝 기본 정보**
- **설명**: 캐릭터의 상세 스탯 정보를 조회
- **외부 API**: `https://open.api.nexon.com/maplestory/v1/character/stat`
- **캐시**: 30분

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "character_name": "홍길동",
    "character_stat": [
      {
        "stat_name": "STR",
        "stat_value": "1250"
      },
      {
        "stat_name": "DEX", 
        "stat_value": "850"
      },
      {
        "stat_name": "INT",
        "stat_value": "450"
      },
      {
        "stat_name": "LUK",
        "stat_value": "450"
      },
      {
        "stat_name": "HP",
        "stat_value": "125000"
      },
      {
        "stat_name": "MP",
        "stat_value": "45000"
      }
    ],
    "damage": "2,500,000 ~ 3,200,000",
    "boss_damage": "350%",
    "ignore_defense": "92%"
  }
}
```

---

### 3. 캐릭터 장비 정보 조회

```
GET /api/character/{character_name}/item-equipment/
```

**📝 기본 정보**
- **설명**: 캐릭터가 착용 중인 장비 정보를 조회
- **외부 API**: `https://open.api.nexon.com/maplestory/v1/character/item-equipment`
- **캐시**: 30분

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "character_name": "홍길동",
    "character_gender": "남",
    "character_class": "히어로",
    "item_equipment": [
      {
        "item_equipment_part": "모자",
        "equipment_slot": "01",
        "item_name": "아케인셰이드 헬름",
        "item_icon": "https://avatar.maplestory.nexon.com/...",
        "item_description": "아케인 리버의 힘이 깃든 투구",
        "item_shape_name": "아케인셰이드 헬름",
        "item_shape_icon": "https://avatar.maplestory.nexon.com/...",
        "item_gender": "남",
        "item_total_option": {
          "str": "45",
          "dex": "45",
          "int": "45",
          "luk": "45",
          "max_hp": "855",
          "max_mp": "855",
          "attack_power": "12",
          "boss_damage": "30%"
        },
        "potential_option_grade": "레어",
        "additional_potential_option_grade": "에픽",
        "potential_option_1": "STR +12%",
        "potential_option_2": "데미지 +9%",
        "potential_option_3": "",
        "additional_potential_option_1": "STR +7%",
        "additional_potential_option_2": "크리티컬 확률 +6%",
        "additional_potential_option_3": "",
        "equipment_level_increase": 5,
        "item_exceptional_option": {
          "str": "35",
          "dex": "21",
          "attack_power": "7"
        },
        "item_add_option": {
          "str": "7",
          "dex": "7",
          "int": "7",
          "luk": "7",
          "max_hp": "120",
          "max_mp": "120",
          "attack_power": "1"
        }
      }
    ]
  }
}
```

---

### 4. 캐릭터 스킬 정보 조회 (예정)

```
GET /api/character/{character_name}/skill/
```

**📝 기본 정보**
- **설명**: 캐릭터의 스킬 정보를 조회
- **개발 상태**: 🚧 개발 예정

---

### 5. 길드 정보 조회 (예정)

```
GET /api/guild/{guild_name}/basic/
```

**📝 기본 정보**
- **설명**: 길드의 기본 정보를 조회
- **개발 상태**: 🚧 개발 예정

---

### 6. 캐릭터 검색

```
POST /api/character/search/
```

**📝 기본 정보**
- **설명**: 캐릭터명으로 검색하여 존재 여부 확인 및 기본 정보 조회
- **Content-Type**: `application/json`

**📥 요청 데이터**
```json
{
  "character_name": "홍길동",
  "world_name": "스카니아"  // 선택적
}
```

**📤 성공 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "exists": true,
    "character_name": "홍길동",
    "world_name": "스카니아",
    "character_level": 275,
    "character_class": "히어로",
    "character_image": "https://avatar.maplestory.nexon.com/...",
    "last_updated": "2025-08-31T10:30:00Z"
  }
}
```

**❌ 캐릭터 없음 응답 (200 OK)**
```json
{
  "success": true,
  "data": {
    "exists": false,
    "message": "해당 캐릭터를 찾을 수 없습니다"
  }
}
```

---

## 🧪 테스트 방법

### 1. 브라우저에서 테스트
```bash
# 캐릭터 정보 페이지
http://localhost:8000/character_info/

# API 직접 호출 (캐릭터명은 URL 인코딩 필요)
http://localhost:8000/api/character/홍길동/basic/
```

### 2. cURL로 테스트
```bash
# 캐릭터 기본 정보 조회
curl -X GET "http://localhost:8000/api/character/%ED%99%8D%EA%B8%B8%EB%8F%99/basic/"

# 캐릭터 검색
curl -X POST "http://localhost:8000/api/character/search/" \
  -H "Content-Type: application/json" \
  -d '{"character_name": "홍길동"}'

# 캐릭터 스탯 조회
curl -X GET "http://localhost:8000/api/character/%ED%99%8D%EA%B8%B8%EB%8F%99/stat/"
```

### 3. JavaScript로 테스트
```javascript
// 캐릭터 검색
async function searchCharacter(characterName) {
    const response = await fetch('/api/character/search/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            character_name: characterName
        })
    });
    
    const data = await response.json();
    return data;
}

// 캐릭터 정보 조회
async function getCharacterInfo(characterName) {
    const encodedName = encodeURIComponent(characterName);
    const response = await fetch(`/api/character/${encodedName}/basic/`);
    const data = await response.json();
    return data;
}
```

---

## 📊 에러 코드 정리

| HTTP 상태 | 에러 코드 | 설명 | 해결 방법 |
|----------|-----------|------|----------|
| 200 | - | 성공 | - |
| 400 | `INVALID_CHARACTER_NAME` | 잘못된 캐릭터명 | 올바른 캐릭터명 입력 |
| 404 | `CHARACTER_NOT_FOUND` | 캐릭터를 찾을 수 없음 | 캐릭터명과 서버 확인 |
| 503 | `NEXON_API_UNAVAILABLE` | 넥슨 API 서비스 불가 | 잠시 후 재시도 |
| 429 | `RATE_LIMIT_EXCEEDED` | API 호출 한도 초과 | 잠시 대기 후 재시도 |

---

## ⚙️ 설정 및 환경변수

### 필요한 환경변수
```bash
# .env 파일
NEXON_API_KEY=your_nexon_api_key_here
```

### 캐시 설정
```python
# 캐릭터 정보는 자주 변경되지 않으므로 30분 캐시
CHARACTER_CACHE_DURATION = timedelta(minutes=30)
```

### URL 인코딩 주의사항
- 한글 캐릭터명은 반드시 URL 인코딩 필요
- JavaScript: `encodeURIComponent()`
- Python: `urllib.parse.quote()`

---

## 🔗 관련 링크

- [넥슨 오픈 API - 캐릭터 정보](https://openapi.nexon.com/game/maplestory/?id=1)
- [메인 페이지 API](./main_page_api_docs.md)
- [챗봇 API](./chatbot_page_api_docs.md)

---

## 📝 개발 노트

### TODO
- [ ] 캐릭터 스킬 정보 API 구현
- [ ] 길드 정보 API 구현
- [ ] 유니온 정보 API 구현
- [ ] 캐릭터 큐브 히스토리 API 구현
- [ ] 실시간 캐릭터 정보 업데이트
- [ ] 캐릭터 비교 기능

### 개발 우선순위
1. **우선 구현**: 캐릭터 기본 정보, 스탯, 장비
2. **차순 구현**: 스킬 정보, 길드 정보
3. **향후 구현**: 유니온, 큐브 히스토리

### 변경 이력
- **v1.0.0** (2025-08-31): 초기 버전 - API 명세서 뼈대 생성

---

**📅 마지막 업데이트**: 2025-08-31
