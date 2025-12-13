# -*- coding: utf-8 -*-
"""
MAI Chat Django Views

Django 뷰에서 LangChain을 사용하여 채팅 기능을 제공합니다.
"""

import json
import uuid
import logging
import time
from datetime import datetime
from typing import Dict, Any

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

from .models import ChatSession, ChatMessage
from .langchain_service import chat_with_memory, clear_session_memory

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def get_sessions_view(request: HttpRequest) -> JsonResponse:
    """
    사용자의 채팅 세션 목록을 조회합니다.
    GET /api/chat/sessions/
    """
    try:
        if request.user.is_authenticated:
            # UserProfile이 존재하는지 확인 (related_name='profile')
            if hasattr(request.user, 'profile'):
                sessions = ChatSession.objects.filter(user=request.user.profile)
            else:
                # 인증은 되었으나 프로필이 없는 경우
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
                'last_message': last_message.user_message if last_message else None,
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
    GET /api/chat/sessions/<session_id>/messages/
    """
    try:
        # session_id는 이미 UUID 객체입니다 (urls.py에서 <uuid:session_id> 사용)
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all().order_by('created_at')
        message_list = []
        for msg in messages:
            if msg.user_message:
                message_list.append({
                    'is_user': True,
                    'content': msg.user_message,
                    'created_at': msg.created_at.isoformat()
                })
            if msg.ai_response:
                message_list.append({
                    'is_user': False,
                    'content': msg.ai_response,
                    'created_at': msg.created_at.isoformat()
                })
        return JsonResponse({'data': message_list})
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def send_message_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    세션에 메시지를 전송하고 AI 응답을 받습니다.
    POST /api/chat/sessions/<session_id>/send/
    """
    try:
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        # session_id는 이미 UUID 객체입니다 (urls.py에서 <uuid:session_id> 사용)
        session = ChatSession.objects.get(session_id=session_id)

        start_time = time.time()
        # session_id는 UUID 객체이므로 문자열로 변환하여 전달
        ai_response = chat_with_memory(str(session_id), content)
        response_time = int((time.time() - start_time) * 1000)

        ChatMessage.objects.create(
            session=session,
            user_message=content,
            ai_response=ai_response,
            response_time=response_time
        )

        return JsonResponse({
            'data': {
                'user_message': {
                    'is_user': True,
                    'content': content,
                    'created_at': datetime.now().isoformat()
                },
                'ai_message': {
                    'is_user': False,
                    'content': ai_response,
                    'created_at': datetime.now().isoformat()
                }
            }
        })
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"메시지 전송 중 오류 발생: {e}")
        return JsonResponse({'error': '메시지 전송 중 오류가 발생했습니다.'}, status=500)
        
        
        
 

 
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_session_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    채팅 세션 및 메모리를 삭제합니다.
    DELETE /api/chat/session/<session_id>/
    """
    try:
        # session_id는 이미 UUID 객체입니다 (urls.py에서 <uuid:session_id> 사용)
        session = ChatSession.objects.get(session_id=session_id)
        session.delete()
        # LangChain 서비스에는 문자열로 전달
        clear_session_memory(str(session_id))
        return JsonResponse({'status': 'deleted', 'session_id': str(session_id)})
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"세션 삭제 중 오류 발생: {e}")
        return JsonResponse({'error': '세션 삭제 중 오류가 발생했습니다.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat_view(request: HttpRequest) -> JsonResponse:
    """레거시: POST /api/chat/ 엔드포인트"""
    return JsonResponse({"error": "Not implemented"}, status=501)


@require_http_methods(["GET"])
def chat_history_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """레거시: GET /api/chat/history/<session_id>/ 엔드포인트"""
#        return JsonResponse({"error": "Invalid JSON"}, status=400)
#
# 5. LangChain 통합의 핵심:
#    ai_response = chat_with_memory(session_id, user_input)
#    → 이 한 줄이 대화 메모리를 자동으로 관리합니다!
#
# ============================================================================
