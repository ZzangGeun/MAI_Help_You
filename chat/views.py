# chat/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# 동일 경로에 있는 chatbot.py 파일에서 함수/클래스 import
from .chatbot import get_chatbot, clear_chatbot
from .models import ChatSession 

@csrf_exempt # API 테스트를 위해 임시로 exempt (프로덕션에서는 CSRF 토큰 사용 권장)
@require_http_methods(["POST"])
def chat_api(request):
    """
    챗봇 대화 요청을 처리하고 응답을 반환하는 API
    비로그인 사용자도 접근 가능 (DB 저장 안됨)
    """
    # 1. 사용자 식별: 로그인 시 user.id, 비로그인 시 session key
    if request.user.is_authenticated:
        session_id = f"user_{request.user.id}"
        user_id = request.user.id
    else:
        # 비로그인 사용자는 Django 세션 키 사용
        if not request.session.session_key:
            request.session.create()
        session_id = f"guest_{request.session.session_key}"
        user_id = None
    
    try:
        data = json.loads(request.body)
        user_input = data.get('message', '').strip()

        if not user_input:
            return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)
        
        # 2. 세션별 챗봇 인스턴스 로드 또는 생성
        chatbot = get_chatbot(
            session_id=session_id,
            user_id=user_id
        )
        
        # 3. 챗봇 응답 생성
        result = chatbot.generate_response(user_input)
        
        # 4. DB에 대화 기록 저장 (로그인 사용자만)
        if user_id and result.get('response') and not result.get('error'):
            chatbot.save_message_to_db(user_input, result['response'])

        # 5. 결과 반환
        return JsonResponse({
            'response': result.get('response'),
            'thinking_content': result.get('thinking_content'),
            'timestamp': result.get('timestamp'),
            'status': 'success'
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'챗봇 처리 오류: {e}'}, status=500)


@login_required
def chat_sessions(request):
    """사용자의 채팅 세션 목록 조회 (로그인 필수)"""
    try:
        sessions = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')
        
        sessions_data = [
            {
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': session.messages.count()
            }
            for session in sessions
        ]
        
        return JsonResponse({'sessions': sessions_data}, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'세션 조회 오류: {e}'}, status=500)