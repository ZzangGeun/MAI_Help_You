#!/usr/bin/env python3
"""
MAI Chatbot API 문서 서버 - Python 버전
Node.js가 없는 환경에서 API 문서를 간단히 확인할 수 있습니다.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import json
from pathlib import Path

# 현재 스크립트 위치 기준으로 docs 디렉토리 찾기
script_dir = Path(__file__).parent
docs_dir = script_dir.parent
api_dir = docs_dir / "api"

def create_simple_html():
    """간단한 HTML 문서 생성"""
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAI Chatbot API 문서</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .api-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .api-title {{ color: #2c3e50; margin-bottom: 10px; }}
        .endpoint {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .method {{ padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }}
        .get {{ background: #28a745; }}
        .post {{ background: #007bff; }}
        .put {{ background: #ffc107; color: #212529; }}
        .delete {{ background: #dc3545; }}
        .description {{ margin-top: 10px; color: #666; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍁 MAI Chatbot API 문서</h1>
            <p>메이플스토리 AI 챗봇 프로젝트 API 명세서</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ 간단 버전 문서</strong><br>
            이 페이지는 Python 서버로 제공되는 간단 버전입니다.<br>
            완전한 API 문서를 보려면 <code>npm run docs:serve</code>를 사용하세요.
        </div>

        <div class="api-section">
            <h2 class="api-title">🔐 인증 API</h2>
            <div class="endpoint">
                <span class="method post">POST</span>/auth/login/
                <div class="description">SNS 로그인 (Google, Kakao, Naver)</div>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>/auth/logout/
                <div class="description">로그아웃 및 토큰 무효화</div>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>/auth/refresh/
                <div class="description">JWT 토큰 갱신</div>
            </div>
        </div>

        <div class="api-section">
            <h2 class="api-title">🤖 챗봇 API</h2>
            <div class="endpoint">
                <span class="method post">POST</span>/chatbot/ask/
                <div class="description">AI 챗봇에게 메이플스토리 관련 질문</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/chatbot/history/
                <div class="description">사용자 대화 기록 조회</div>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>/chatbot/clear-history/
                <div class="description">대화 기록 초기화</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/chatbot/health/
                <div class="description">챗봇 서비스 상태 확인</div>
            </div>
        </div>

        <div class="api-section">
            <h2 class="api-title">👤 캐릭터 API</h2>
            <div class="endpoint">
                <span class="method get">GET</span>/character_info/{{character_id}}/
                <div class="description">특정 캐릭터 상세 정보 조회</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/character_info/search/
                <div class="description">캐릭터 검색 (이름, 직업, 레벨 등)</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/character_info/{{character_id}}/stats/
                <div class="description">캐릭터 능력치 정보 조회</div>
            </div>
        </div>

        <div class="api-section">
            <h2 class="api-title">📰 메인 페이지 API</h2>
            <div class="endpoint">
                <span class="method get">GET</span>/api/notice/
                <div class="description">공지사항 목록 조회</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/api/notice/{{notice_id}}/
                <div class="description">공지사항 상세 조회</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/api/events/
                <div class="description">진행 중인 이벤트 조회</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/health/
                <div class="description">전체 서비스 상태 확인</div>
            </div>
        </div>

        <div class="api-section">
            <h2 class="api-title">🧠 AI 모델 API (FastAPI:8001)</h2>
            <div class="endpoint">
                <span class="method post">POST</span>/api/chat
                <div class="description">AI 모델 직접 호출 (Django 우회)</div>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>/api/model/status
                <div class="description">AI 모델 상태 및 정보 조회</div>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>/api/model/reload
                <div class="description">AI 모델 재로드 (관리자 전용)</div>
            </div>
        </div>

        <div class="api-section">
            <h2 class="api-title">📁 API 파일 구조</h2>
            <ul>
                <li><strong>docs/api/openapi.yaml</strong> - 통합 명세서</li>
                <li><strong>docs/api/auth.yaml</strong> - 인증 관련</li>
                <li><strong>docs/api/chatbot.yaml</strong> - 챗봇 관련</li>
                <li><strong>docs/api/character.yaml</strong> - 캐릭터 관련</li>
                <li><strong>docs/api/main.yaml</strong> - 메인 페이지 관련</li>
                <li><strong>docs/api/fastapi.yaml</strong> - FastAPI 서비스</li>
                <li><strong>docs/schemas/common.yaml</strong> - 공통 스키마</li>
                <li><strong>docs/schemas/models.yaml</strong> - 데이터 모델</li>
            </ul>
        </div>

        <div class="api-section">
            <h2 class="api-title">🛠️ 개발 도구</h2>
            <p>완전한 API 문서 및 테스트 도구 사용법:</p>
            <pre>
cd docs
npm install -g @redocly/cli
npm run docs:serve          # Swagger UI 서버 시작
npm run docs:validate       # 문서 유효성 검사
npm run postman:convert     # Postman 컬렉션 생성
            </pre>
        </div>

        <footer style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
            <p>📧 문의: mai-chatbot@example.com | 🐙 GitHub: MAI_Help_You</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # build 디렉토리에 HTML 파일 생성
    build_dir = docs_dir / "build"
    build_dir.mkdir(exist_ok=True)
    
    html_file = build_dir / "simple.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_file

def main():
    port = 3001
    
    # 간단한 HTML 페이지 생성
    html_file = create_simple_html()
    print(f"📝 간단 문서 페이지 생성: {html_file}")
    
    # docs 디렉토리로 이동
    os.chdir(docs_dir)
    
    # HTTP 서버 시작
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 API 문서 서버가 시작되었습니다!")
            print(f"📖 브라우저에서 확인: http://localhost:{port}/build/simple.html")
            print(f"📁 파일 탐색: http://localhost:{port}")
            print(f"🛑 서버 종료: Ctrl+C")
            print()
            
            # 자동으로 브라우저 열기 (선택사항)
            try:
                webbrowser.open(f"http://localhost:{port}/build/simple.html")
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 포트 {port}이 이미 사용 중입니다.")
            print(f"   다른 포트를 사용하거나 기존 서비스를 종료하세요.")
        else:
            print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
