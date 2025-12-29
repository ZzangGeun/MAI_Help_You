# -*- coding: utf-8 -*-
import json
import uuid
import logging
import time
import requests 
from datetime import datetime
from typing import Dict, Any

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

# 기존 모델은 그대로 사용합니다
from .models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

# FastAPI AI 서버 주소
AI_SERVER_URL = "http://127.0.0.1:8001/generate"


# 1. 화면 렌더링 (HTML)
def chat_page(request: HttpRequest):
    """
    채팅봇 페이지를 렌더링합니다.
    """
    # 템플릿 경로가 mai_chat/chat.html 인지 확인하세요
    return render(request, 'mai_chat/chat.html')


# 2. 세션 관리 API (기존 코드 유지)
@require_http_methods(["GET"])
def get_sessions_view(request: HttpRequest) -> JsonResponse:
    """
    사용자의 채팅 세션 목록을 조회합니다.
    GET /api/chat/sessions/
    """
    try:
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                sessions = ChatSession.objects.filter(user=request.user.profile)
            else:
                sessions = ChatSession.objects.none()
        else:
            sessions = ChatSession.objects.none()

        sessions = sessions.order_by('-created_at')
        session_list = []
        for session in sessions:
            last_message = session.messages.order_by('-created_at').first()
            session_list.append({
                'id': str(session.session_id),
                'created_at': session.created_at.isoformat(),
                'last_message': last_message.user_message if last_message else "대화 없음",
                'message_count': session.messages.count()
            })

        return JsonResponse({'data': session_list})
    except Exception as e:
        logger.error(f"세션 조회 중 오류 발생: {e}")
        return JsonResponse({'error': '세션 조회 중 오류가 발생했습니다.'}, status=500)
            

@csrf_exempt
@require_http_methods(["POST"])
def create_session_view(request: HttpRequest) -> JsonResponse:
    """
    새로운 채팅 세션을 생성합니다.
    POST /api/chat/sessions/create/
    """
    try:
        user_profile = None
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_profile = request.user.profile
            
        session = ChatSession.objects.create(user=user_profile)
        logger.info(f"새로운 세션 생성: {session.session_id}")
        
        return JsonResponse({
            'data': {
                'id': str(session.session_id),
                'created_at': session.created_at.isoformat(),
                'last_message': None,
                'message_count': 0
            }
        }, status=201)
    except Exception as e:
        logger.error(f"세션 생성 중 오류 발생: {e}")
        return JsonResponse({'error': '세션 생성 중 오류가 발생했습니다.'}, status=500)


@require_http_methods(["GET"])
def get_messages_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    특정 세션의 메시지 목록을 조회합니다.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all().order_by('created_at')
        
        message_list = []
        for msg in messages:
            # 사용자 메시지
            if msg.user_message:
                message_list.append({
                    'role': 'user',
                    'content': msg.user_message,
                    'created_at': msg.created_at.isoformat()
                })
            # AI 응답
            if msg.ai_response:
                message_list.append({
                    'role': 'assistant',
                    'content': msg.ai_response,
                    'created_at': msg.created_at.isoformat(),
                    # DB에 thinking 필드가 없다면 빈값, 있다면 추가
                    'thinking': getattr(msg, 'thinking', "") 
                })
                
        return JsonResponse({'data': message_list})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# 3. 메시지 전송 (여기가 핵심 변경!)
# ==========================================
@csrf_exempt
@require_http_methods(["POST"])
def send_message_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    세션에 메시지를 전송하고 AI 서버(FastAPI)로부터 응답을 받습니다.
    POST /api/chat/sessions/<session_id>/send/
    """
    try:
        # 1. 요청 데이터 파싱
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        # 2. 세션 가져오기
        try:
            if isinstance(session_id, str):
                s_uuid = uuid.UUID(session_id)
            else:
                s_uuid = session_id
            session = ChatSession.objects.get(session_id=s_uuid)
        except (ValueError, ChatSession.DoesNotExist):
             return JsonResponse({'error': 'Invalid session ID or Session not found'}, status=404)

        start_time = time.time()
        
        # ==================================================================
        # 3. [핵심 수정] AI 서버(FastAPI)로 요청 보내기
        # LangGraph가 기억을 하려면 'session_id'가 반드시 필요합니다!
        # ==================================================================
        try:
            payload = {
                "session_id": str(session.session_id),  # ★ UUID를 문자열로 변환해서 추가
                "message": content
            }
            
            # timeout을 넉넉히 줍니다 (로컬 LLM 고려)
            response = requests.post(AI_SERVER_URL, json=payload, timeout=1200)
            
            if response.status_code == 200:
                ai_data = response.json()
                ai_text = ai_data.get("response", "")
                ai_thinking = ai_data.get("thinking", "")
            else:
                # 422 에러 등이 나면 여기서 잡힙니다.
                raise Exception(f"AI Server Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"AI 서버 연결 실패: {e}")
            return JsonResponse({'error': 'AI 서버에 연결할 수 없습니다.'}, status=503)

        response_time = int((time.time() - start_time) * 1000)

        # 4. DB에 저장 (동기 방식)
        # models.py에 thinking 필드를 추가하셨다면 여기서 같이 저장해야 합니다.
        chat_msg = ChatMessage.objects.create(
            session_id=session,
            user_message=content,
            ai_response=ai_text,
            thinking=ai_thinking,  # ★ 사고 과정(Thinking)도 DB에 저장!
            response_time=response_time
        )

        # 5. 응답 반환
        return JsonResponse({
            'data': {
                'user_message': {
                    'role': 'user',
                    'content': content,
                    'created_at': datetime.now().isoformat()
                },
                'ai_message': {
                    'role': 'assistant',
                    'content': ai_text,
                    'thinking': ai_thinking,
                    'created_at': datetime.now().isoformat()
                }
            }
        })

    except Exception as e:
        logger.error(f"메시지 전송 중 오류 발생: {e}")
        return JsonResponse({'error': f'서버 오류: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_session_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    채팅 세션을 삭제합니다.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        session.delete()
        # 메모리 삭제 로직은 이제 AI 서버 쪽 관할이거나, DB 삭제로 충분하므로 생략 가능
        return JsonResponse({'status': 'deleted', 'session_id': str(session_id)})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"세션 삭제 중 오류 발생: {e}")
        return JsonResponse({'error': '세션 삭제 중 오류가 발생했습니다.'}, status=500)