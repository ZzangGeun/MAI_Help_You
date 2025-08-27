# MAI 프로젝트 브랜치 전략

## 🌿 브랜치 구조

### 메인 브랜치
- **`master`**: 프로덕션 안정 버전 (배포 가능한 상태)
- **`develop`**: 개발 통합 브랜치 (다음 릴리즈 준비)

### 기능 브랜치 (`feature/`)

#### `feature/rag-enhancement`
**목적**: RAG(검색 증강 생성) 시스템 개선
- **주요 작업**:
  - PostgreSQL pgvector 성능 최적화
  - 임베딩 모델 교체/개선
  - 검색 정확도 향상 (top_k 조정, 유사도 임계값)
  - 문서 청킹 전략 개선
- **관련 파일**: `chatbot/rag_engine.py`, `config/env.py`

#### `feature/model-optimization`
**목적**: LLM 모델 성능 및 추론 속도 최적화
- **주요 작업**:
  - 모델 양자화 (8-bit, 4-bit)
  - GPU 메모리 사용량 최적화
  - 배치 처리 개선
  - 캐싱 전략 구현
- **관련 파일**: `chatbot/services.py`, `fastapi_model/model.py`

#### `feature/ui-enhancement`
**목적**: 사용자 인터페이스 개선
- **주요 작업**:
  - 반응형 디자인 개선
  - 실시간 채팅 UI (WebSocket)
  - 대화 히스토리 관리 UI
  - 로딩 상태 표시 개선
- **관련 파일**: `templates/`, `static/`, `chatbot/views.py`

#### `feature/nexon-api-integration`
**목적**: 넥슨 API 연동 기능 확장
- **주요 작업**:
  - 캐릭터 정보 실시간 조회
  - 랭킹 시스템 연동
  - API 응답 캐싱
  - 에러 핸들링 개선
- **관련 파일**: `character_info/`, `main_page/get_nexon_api.py`

### 지원 브랜치

#### `hotfix/`
- 프로덕션 긴급 수정
- `master`에서 분기 → 수정 → `master`, `develop` 양쪽 병합

#### `release/`
- 릴리즈 준비 (버전 태그, 문서 정리)
- `develop`에서 분기 → 준비 완료 → `master` 병합

## 🔄 워크플로우

### 새 기능 개발
```bash
# 1. develop에서 feature 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 개발 및 커밋
git add .
git commit -m "feat: 새 기능 구현"

# 3. 원격 푸시
git push origin feature/new-feature

# 4. Pull Request 생성 (feature → develop)
```

### 릴리즈 준비
```bash
# 1. release 브랜치 생성
git checkout develop
git checkout -b release/v1.1.0

# 2. 버전 정보 업데이트, 테스트
git commit -m "release: v1.1.0 준비"

# 3. master 병합 및 태그
git checkout master
git merge release/v1.1.0
git tag v1.1.0
git push origin master --tags
```

### 긴급 수정
```bash
# 1. master에서 hotfix 브랜치 생성
git checkout master
git checkout -b hotfix/critical-bug

# 2. 수정 및 테스트
git commit -m "fix: 치명적 버그 수정"

# 3. master, develop 양쪽 병합
git checkout master
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
```

## 📋 커밋 메시지 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 스타일 변경 (포매팅, 세미콜론 추가 등)
refactor: 코드 리팩토링
test: 테스트 추가 또는 수정
chore: 빌드 프로세스 또는 보조 도구 변경
```

### 예시
```bash
git commit -m "feat(rag): 임베딩 모델을 sentence-transformers/all-MiniLM-L6-v2로 변경"
git commit -m "fix(api): nexon API 타임아웃 에러 처리 개선"
git commit -m "docs: README.md 설치 가이드 업데이트"
```

## 🛡️ 보호 규칙

### `master` 브랜치
- 직접 푸시 금지
- Pull Request 필수
- 최소 1명 리뷰 필요
- CI/CD 테스트 통과 필수

### `develop` 브랜치  
- Pull Request 권장
- 자동 테스트 통과 필요

## 🎯 현재 권장 작업 브랜치

### 즉시 작업 가능
1. **`feature/model-optimization`**: attention_mask 경고 완전 해결
2. **`feature/rag-enhancement`**: PostgreSQL 연결 안정성 개선
3. **`feature/ui-enhancement`**: 채팅 UI 실시간 업데이트

### 우선순위 높음
- FastAPI와 Django 통합 테스트
- 로컬 모델 메모리 사용량 최적화
- 에러 핸들링 개선
