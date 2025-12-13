# -*- coding: utf-8 -*-
"""
MAI Chat Django Views - 학습용 템플릿

Django 뷰에서 LangChain을 사용하는 방법 학습

학습 목표:
1. Django 뷰에서 LangChain chat_with_memory() 호출
2. RESTful API 응답 형식 설계
3. Django ORM과 LangChain 통합
4. 세션 및 메시지 관리
"""

import json
import uuid
import logging
from typing import Dict, Any

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

from .models import ChatSession, ChatMessage
from .langchain_service import chat_with_memory, clear_session_memory

# 로깅 설정
logger = logging.getLogger(__name__)


# ============================================================================
# TODO 1: 세션 목록 조회 뷰
# ============================================================================
# 목표: 사용자의 모든 채팅 세션 목록을 조회하는 API
#
# 엔드포인트: GET /mai_chat/api/chat/sessions/
#
# 구현해야 할 내용:
# 1. 사용자별 세션 필터링
#    - request.user.is_authenticated 확인
#    - 인증된 경우: ChatSession.objects.filter(user=request.user)
#    - 비인증 사용자: ChatSession.objects.none()
# 2. 최신 순으로 정렬 (.order_by('-created_at'))
# 3. 각 세션에 대해 다음 정보 수집:
#    - id: str(session.session_id)
#    - created_at: session.created_at.isoformat()
#    - last_message: 마지막 메시지의 user_message (없으면 None)
#    - message_count: session.messages.count()
# 4. JsonResponse로 반환: {"data": [세션 리스트]}
# 5. 에러 처리 및 로깅
#
# 힌트:
# - session.messages.order_by('-created_at').first()로 마지막 메시지 조회
# - try-except로 전체 블록 감싸기
# ============================================================================

@require_http_methods(["GET"])
def get_sessions_view(request: HttpRequest) -> JsonResponse:
    """
    사용자의 모든 채팅 세션 목록을 조회합니다.
    
    GET /api/chat/sessions/
    
    Response:
        {
            "data": [
                {
                    "id": "UUID",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_message": "마지막 메시지",
                    "message_count": 5
                },
                ...
            ]
        }
    """
    # TODO: 구현하세요
    try:
        if request.user.is_authenticated:
            sessions = ChatSession.objects.filter(user=request.user)
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


# ============================================================================
# TODO 2: 세션 생성 뷰
# ============================================================================
# 목표: 새로운 채팅 세션을 생성하는 API
#
# 엔드포인트: POST /mai_chat/api/chat/sessions/create/
#
# 구현해야 할 내용:
# 1. ChatSession.objects.create() 호출
#    - user: request.user (인증된 경우) 또는 None
# 2. 생성된 세션 정보 반환
#    - id, created_at, last_message=None, message_count=0
# 3. JsonResponse로 반환: {"data": {세션 정보}}
# 4. status=201 (Created)
# 5. 에러 처리 및 로깅
#
# 힌트:
# - @csrf_exempt 데코레이터 필요
# - logger.info()로 세션 생성 로깅
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_session_view(request: HttpRequest) -> JsonResponse:
    """
    새로운 채팅 세션을 생성합니다.
    
    POST /api/chat/sessions/create/
    
    Response:
        {
            "data": {
                "id": "UUID",
                "created_at": "2024-01-01T00:00:00Z",
                "last_message": null,
                "message_count": 0
            }
        }
    """
    # TODO: 구현하세요
    try:
        session = ChatSession.objects.create(user=request.user)
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


# ============================================================================
# TODO 3: 세션 메시지 조회 뷰
# ============================================================================
# 목표: 특정 세션의 모든 메시지를 조회하는 API
#
# 엔드포인트: GET /mai_chat/api/chat/sessions/<session_id>/messages/
#
# 구현해야 할 내용:
# 1. session_id를 UUID로 변환 (uuid.UUID())
#    - 실패 시 400 에러 반환
# 2. ChatSession.objects.get(session_id=session_uuid)
#    - 없으면 404 에러 반환
# 3. session.messages.all().order_by('created_at')로 메시지 조회
# 4. 각 메시지를 사용자 메시지와 AI 응답으로 분리:
#    - {"is_user": True, "content": msg.user_message, "created_at": ...}
#    - {"is_user": False, "content": msg.ai_response, "created_at": ...}
# 5. JsonResponse로 반환: {"data": [메시지 리스트]}
#
# 힌트:
# - 메시지 하나당 두 개의 딕셔너리 생성 (user + ai)
# - isoformat()로 날짜 변환
# ============================================================================

@require_http_methods(["GET"])
def get_messages_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    세션의 모든 메시지를 조회합니다.
    
    GET /api/chat/sessions/<session_id>/messages/
    
    Response:
        {
            "data": [
                {
                    "is_user": true,
                    "content": "사용자 메시지",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "is_user": false,
                    "content": "AI 응답",
                    "created_at": "2024-01-01T00:00:01Z"
                },
                ...
            ]
        }
    """
    # TODO: 구현하세요
    try:
        session_uuid = uuid.UUID(session_id)
        session = ChatSession.objects.get(session_id=session_uuid)
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


# ============================================================================
# TODO 4: 메시지 전송 뷰 (핵심!)
# ============================================================================
# 목표: 메시지를 전송하고 LangChain으로 AI 응답을 생성하는 API
#
# 엔드포인트: POST /mai_chat/api/chat/sessions/<session_id>/send/
#
# 구현해야 할 내용:
# 1. JSON 파싱 (json.loads(request.body))
#    - 실패 시 400 에러
# 2. content 필드 검증
#    - 비어있으면 400 에러
# 3. session_id로 세션 조회
#    - 없으면 404 에러
# 4. LangChain 호출: ai_response = chat_with_memory(session_id, content)
#    - 이 부분이 핵심! LangChain이 메모리를 관리합니다
#    - 시간 측정 (time.time())
# 5. DB에 저장: ChatMessage.objects.create()
#    - session, user_message, ai_response, response_time
# 6. JsonResponse 반환:
#    - user_message: {"is_user": True, "content": ..., "created_at": ...}
#    - ai_message: {"is_user": False, "content": ..., "created_at": ...}
# 7. 에러 처리 및 로깅
#
# 힌트:
# - import time 필요
# - response_time = int((time.time() - start_time) * 1000)
# - chat_with_memory()가 예외를 발생시킬 수 있으니 try-except
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_message_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    세션에 메시지를 전송하고 AI 응답을 받습니다.
    
    POST /api/chat/sessions/<session_id>/send/
    Request Body:
        {
            "content": "사용자 메시지"
        }
    
    Response:
        {
            "data": {
                "user_message": {
                    "is_user": true,
                    "content": "사용자 메시지",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "ai_message": {
                    "is_user": false,
                    "content": "AI 응답",
                    "created_at": "2024-01-01T00:00:01Z"
                }
            }
        }
    """
    # TODO: 구현하세요
    # 1. JSON 파싱
    # 2. 입력 검증
    # 3. 세션 조회
    # 4. 시간 측정 시작
    # 5. chat_with_memory() 호출 ← 핵심!
    # 6. DB 저장
    # 7. 응답 반환
    
    try:
        session_uuid = uuid.UUID(session_id)
        session = ChatSession.objects.get(session_id=session_uuid)

        start_time = time.time()
        ai_response = chat_with_memory(session_id, content)
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
        
        
        


# ============================================================================
# TODO 5: 세션 삭제 뷰
# ============================================================================
# 목표: 채팅 세션 및 메모리를 삭제하는 API
#
# 엔드포인트: DELETE /mai_chat/api/chat/sessions/<session_id>/delete/
#
# 구현해야 할 내용:
# 1. session_id로 세션 조회
# 2. session.delete() - DB에서 삭제 (CASCADE로 메시지도 삭제됨)
# 3. clear_session_memory(session_id) - LangChain 메모리 캐시 삭제
# 4. JsonResponse 반환: {"status": "deleted", "session_id": ...}
#
# 힌트:
# - 메모리와 DB 모두 정리해야 합니다
# - @csrf_exempt 필요
# ============================================================================

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_session_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    채팅 세션 및 메모리를 삭제합니다.
    
    DELETE /api/chat/session/<session_id>/
    
    Response:
        {
            "status": "deleted",
            "session_id": "UUID"
        }
    """
    # TODO: 구현하세요
    try:
        session_uuid = uuid.UUID(session_id)
        session = ChatSession.objects.get(session_id=session_uuid)
        session.delete()
        clear_session_memory(session_id)
        return JsonResponse({'status': 'deleted', 'session_id': session_id})
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"세션 삭제 중 오류 발생: {e}")
        return JsonResponse({'error': '세션 삭제 중 오류가 발생했습니다.'}, status=500)


# ============================================================================
# 레거시 엔드포인트 (참고용 - 기존 코드 유지)
# ============================================================================
# 아래 함수들은 기존 엔드포인트와의 호환성을 위해 유지합니다.
# 위의 RESTful 뷰를 먼저 구현하는 것을 권장합니다.
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_view(request: HttpRequest) -> JsonResponse:
    """레거시: POST /api/chat/ 엔드포인트"""
    # 기존 코드 유지 - 참고용
    return JsonResponse({"error": "Not implemented"}, status=501)


@require_http_methods(["GET"])
def chat_history_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """레거시: GET /api/chat/history/<session_id>/ 엔드포인트"""
    # 기존 코드 유지 - 참고용
    return JsonResponse({"error": "Not implemented"}, status=501)
    

# ============================================================================
# 학습 힌트
# ============================================================================
#
# 1. Django ORM 패턴:
#    - .objects.filter(user=request.user)
#    - .objects.get(id=some_id)  # DoesNotExist 예외 처리
#    - .objects.create(field=value)
#
# 2. JsonResponse 사용:
#    return JsonResponse({"key": "value"}, status=200)
#
# 3. UUID 처리:
#    try:
#        uuid_obj = uuid.UUID(string_id)
#    except (ValueError, ValidationError):
#        return JsonResponse({"error": "Invalid UUID"}, status=400)
#
# 4. JSON 파싱:
#    try:
#        data = json.loads(request.body)
#    except json.JSONDecodeError:
#        return JsonResponse({"error": "Invalid JSON"}, status=400)
#
# 5. LangChain 통합의 핵심:
#    ai_response = chat_with_memory(session_id, user_input)
#    → 이 한 줄이 대화 메모리를 자동으로 관리합니다!
#
# ============================================================================
