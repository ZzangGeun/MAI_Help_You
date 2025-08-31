# MAI 챗봇 API 자동 생성 문서 🤖

> 이 문서는 실제 API 응답 데이터를 기반으로 자동 생성되었습니다.
> 
> **생성 시간**: 2025-08-31 16:33:23

## 📊 데이터 분석 결과

### NOTICE 엔드포인트

- **데이터 타입**: `dict`
- **최상위 키**: `['notice']`

#### notice 필드

- **타입**: 배열 (항목 20개)
- **배열 항목 구조**:
  - `title`: str (예시: "넥슨에서 토스페이가 처음이라면 결제 시 10% 토스포인트 즉시 적립")
  - `url`: str (예시: "https://maplestory.nexon.com/News/Notice/Notice/147581")
  - `notice_id`: int
  - `date`: str (예시: "2025-08-29T16:00+09:00")

#### 실제 응답 예시

```json
{
  "notice": [
    {
      "title": "넥슨에서 토스페이가 처음이라면 결제 시 10% 토스포인트 즉시 적립",
      "url": "https://maplestory.nexon.com/News/Notice/Notice/147581",
      "notice_id": 147581,
      "date": "2025-08-29T16:00+09:00"
    },
    {
      "title": "[패치완료] 8/28(목) ver1.2.406 마이너 버전 (9) 패치 (14:50 적용)",
      "url": "https://maplestory.nexon.com/News/Notice/Notice/147574",
      "notice_id": 147574,
      "date": "2025-08-28T14:50+09:00"
    },
    {
      "...more_items": "..."
    }
  ]
}
```

---

### EVENT 엔드포인트

- **데이터 타입**: `dict`
- **최상위 키**: `['event_notice']`

#### event_notice 필드

- **타입**: 배열 (항목 19개)
- **배열 항목 구조**:
  - `title`: str (예시: "썬데이 메이플")
  - `url`: str (예시: "https://maplestory.nexon.com/News/Event/1187")
  - `notice_id`: int
  - `date`: str (예시: "2025-08-29T10:00+09:00")
  - `date_event_start`: str (예시: "2025-08-31T00:00+09:00")
  - `date_event_end`: str (예시: "2025-08-31T23:59+09:00")

#### 실제 응답 예시

```json
{
  "event_notice": [
    {
      "title": "썬데이 메이플",
      "url": "https://maplestory.nexon.com/News/Event/1187",
      "notice_id": 1187,
      "date": "2025-08-29T10:00+09:00",
      "date_event_start": "2025-08-31T00:00+09:00",
      "date_event_end": "2025-08-31T23:59+09:00"
    },
    {
      "title": "(수정) 프론티어 패스",
      "url": "https://maplestory.nexon.com/News/Event/1185",
      "notice_id": 1185,
      "date": "2025-08-21T08:38+09:00",
      "date_event_start": "2025-08-21T10:00+09:00",
      "date_event_end": "2025-11-19T23:59+09:00"
    },
    {
      "...more_items": "..."
    }
  ]
}
```

---

## 🚀 API 사용법

### cURL로 테스트
```bash
# 공지사항 조회
curl -X GET "http://localhost:8000/nexon_api/notice/"

# 이벤트 조회  
curl -X GET "http://localhost:8000/nexon_api/notice-event/"
```

### Python으로 테스트
```python
import requests

# 공지사항 조회
response = requests.get("http://localhost:8000/nexon_api/notice/")
data = response.json()
print(data)
```

### 자동 테스트 실행
```bash
python tests/api/test_nexon_api.py
```

---

**📅 마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

> 💡 **팁**: 이 문서는 `python docs/api/auto_generate_docs.py` 명령어로 언제든 재생성할 수 있습니다!
