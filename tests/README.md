# MAI 프로젝트 테스트 가이드

이 폴더에는 MAI (메이플스토리 AI 챗봇) 프로젝트의 모든 테스트 파일들이 체계적으로 정리되어 있습니다.

## 📁 폴더 구조

```
tests/
├── README.md                    # 이 파일 (테스트 가이드)
├── __init__.py                  # 패키지 초기화
├── api/                         # API 관련 테스트
│   ├── __init__.py
│   ├── test_nexon_api.py       # 독립 실행 API 테스트
│   └── test_django_integration.py # Django 통합 테스트
├── data/                        # 테스트 데이터 저장소
│   └── __init__.py
└── utils/                       # 테스트 유틸리티
    ├── __init__.py
    └── test_helpers.py         # 공통 테스트 함수들
```

## 🚀 테스트 실행 방법

### 1. 독립 API 테스트 (권장)

Django 설정 없이도 바로 실행 가능한 테스트입니다.

```bash
# 프로젝트 루트에서 실행
python tests/api/test_nexon_api.py
```

**특징:**
- ✅ 즉시 실행 가능
- ✅ 상세한 결과 출력
- ✅ JSON 파일로 결과 저장 옵션
- ✅ 환경 검증 포함

### 2. Django 통합 테스트

Django 환경에서 실행하는 테스트입니다.

```bash
# Django 셸에서 실행
python manage.py shell

>>> from tests.api.test_django_integration import quick_test
>>> quick_test()

# 또는 단일 API 테스트
>>> from tests.api.test_django_integration import test_single_api
>>> test_single_api()
```

**특징:**
- ✅ Django 설정과 완전 통합
- ✅ 실제 앱의 함수들 직접 테스트
- ✅ 대화형 테스트 가능

### 3. 테스트 유틸리티 사용

```python
from tests.utils.test_helpers import validate_api_response, check_environment

# 환경 확인
env_info = check_environment()
print(env_info)

# API 응답 검증
result = validate_api_response(api_data, expected_keys=['notice', 'event'])
```

## 📊 테스트 결과 해석

### 성공적인 API 호출 예시:
```
🌐 API 호출: https://open.api.nexon.com/maplestory/v1/notice
🔑 API 키 설정됨: ✅
📡 HTTP 상태 코드: 200
✅ 성공!
📊 데이터 타입: <class 'dict'>
🗝️  키 목록: ['notice']
📝 notice: 리스트 (항목 20개)
```

### 실패한 API 호출 예시:
```
🌐 API 호출: https://open.api.nexon.com/maplestory/v1/notice
🔑 API 키 설정됨: ❌
⚠️  NEXON_API_KEY가 설정되지 않았습니다!
❌ 데이터 가져오기 실패
```

## 🔧 문제 해결

### API 키 설정 오류
```bash
# .env 파일에 API 키가 설정되어 있는지 확인
NEXON_API_KEY=your_api_key_here
```

### Django 설정 오류
```bash
# 가상환경 활성화 확인
conda activate mai_env

# Django 셸 실행
python manage.py shell
```

### 패키지 import 오류
```python
# 프로젝트 루트 경로가 Python path에 추가되었는지 확인
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
```

## 📈 고급 사용법

### 1. 정기적인 API 상태 모니터링
```python
# 스케줄러와 함께 사용하여 정기적으로 API 상태 확인
from tests.api.test_nexon_api import NexonAPITester

tester = NexonAPITester()
tester.run_all_tests()
# 결과를 로그 파일이나 데이터베이스에 저장
```

### 2. API 응답 변화 감지
```python
from tests.utils.test_helpers import compare_api_responses, load_test_data

old_data = load_test_data("previous_api_response.json")
new_data = get_current_api_data()
diff = compare_api_responses(old_data, new_data)
```

### 3. 커스텀 테스트 작성
```python
from tests.utils.test_helpers import validate_api_response, format_test_output

def my_custom_test():
    # 여기에 테스트 로직 작성
    data = get_api_data("/my-endpoint")
    validation = validate_api_response(data, expected_keys=['my_key'])
    
    return validation['valid']
```

## 📝 테스트 데이터

`tests/data/` 폴더에는 테스트 실행 시 생성되는 JSON 파일들이 저장됩니다:

- `nexon_api_notice_data.json` - 공지사항 API 응답
- `nexon_api_notice-event_data.json` - 이벤트 API 응답
- 기타 timestamp가 포함된 테스트 결과 파일들

이 파일들을 통해 API 응답의 구조를 자세히 분석하고, 시간에 따른 변화를 추적할 수 있습니다.

## 🎯 추천 워크플로우

1. **개발 시작**: 독립 API 테스트로 API 연결 확인
2. **기능 개발**: Django 통합 테스트로 앱 내 함수들 검증
3. **디버깅**: 테스트 데이터 파일을 통해 상세 분석
4. **배포 전**: 모든 테스트 실행하여 최종 검증

---

💡 **팁**: 테스트를 자주 실행하여 API 상태를 모니터링하고, 문제를 조기에 발견하세요!
