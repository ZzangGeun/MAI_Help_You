# API 문서화 가이드

## 구조 개요
```
docs/
├── README.md                    # 이 파일 - API 문서 사용 가이드
├── api/                        # OpenAPI 명세서들
│   ├── auth.yaml              # 인증/로그인 관련 API
│   ├── chatbot.yaml           # 챗봇 관련 API
│   ├── character.yaml         # 캐릭터 정보 관련 API
│   ├── main.yaml              # 메인 페이지 관련 API
│   └── fastapi.yaml           # FastAPI 서비스 API
├── schemas/                    # 공통 스키마 정의
│   ├── common.yaml            # 공통 응답 모델
│   └── models.yaml            # 데이터 모델 정의
└── postman/                   # Postman 컬렉션 (선택)
    └── MAI_Chatbot.postman_collection.json
```

## 협업 규칙

### 1. API 명세서 수정 시
- 해당 기능 담당자가 관련 .yaml 파일 수정
- PR 전에 `docs/api/` 폴더의 해당 파일 업데이트 필수
- 새로운 엔드포인트 추가 시 반드시 문서화

### 2. 스키마 참조
- 공통 응답 형식은 `schemas/common.yaml` 참조
- 데이터 모델은 `schemas/models.yaml`에 정의 후 참조

### 3. 문서 통합
- 전체 API 문서 확인: `npm run docs:serve` (Swagger UI)
- 개발 서버에서 자동 문서화: `/docs/` 경로

## 빠른 시작
1. 새로운 API 개발 시 해당 .yaml 파일 먼저 작성
2. 팀원과 리뷰 후 구현 시작
3. 구현 완료 후 실제 응답과 문서 일치 확인
