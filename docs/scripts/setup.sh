#!/bin/bash
# MAI Chatbot API 문서 설정 스크립트

echo "🚀 MAI Chatbot API 문서 환경 설정을 시작합니다..."

# Node.js 설치 확인
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되어 있지 않습니다."
    echo "   Node.js를 설치하고 다시 시도해주세요: https://nodejs.org"
    exit 1
fi

# npm 설치 확인
if ! command -v npm &> /dev/null; then
    echo "❌ npm이 설치되어 있지 않습니다."
    exit 1
fi

echo "✅ Node.js $(node --version) 및 npm $(npm --version) 감지됨"

# docs 디렉토리로 이동
cd "$(dirname "$0")/.." || exit 1

# 필요한 도구 글로벌 설치
echo "📦 API 문서 도구 설치 중..."
npm install -g @redocly/cli swagger-ui-dist openapi-to-postmanv2

# 로컬 패키지 설치
if [ -f "package.json" ]; then
    echo "📦 로컬 패키지 설치 중..."
    npm install
fi

# 빌드 디렉토리 생성
mkdir -p build
mkdir -p postman

# API 문서 유효성 검사
echo "🔍 API 문서 유효성 검사 중..."
if redocly lint api/openapi.yaml; then
    echo "✅ API 문서 유효성 검사 통과"
else
    echo "⚠️  API 문서에 경고가 있습니다. 확인해주세요."
fi

# 문서 빌드 테스트
echo "🏗️  문서 빌드 테스트 중..."
if redocly build-docs api/openapi.yaml --output ./build/test.html; then
    echo "✅ 문서 빌드 성공"
    rm -f ./build/test.html
else
    echo "❌ 문서 빌드 실패. YAML 파일을 확인해주세요."
    exit 1
fi

echo ""
echo "🎉 설정 완료!"
echo ""
echo "📖 사용 가능한 명령어:"
echo "   npm run docs:serve    - 문서 서버 실행 (http://localhost:3001)"
echo "   npm run docs:build    - 정적 문서 빌드"
echo "   npm run docs:validate - 문서 유효성 검사"
echo "   npm run postman:convert - Postman 컬렉션 생성"
echo ""
echo "🚀 시작하려면: cd docs && npm run docs:serve"
