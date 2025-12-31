# -*- coding: utf-8 -*-
"""
MAI Chat Django Views

DRF 없이 Django의 JsonResponse를 사용한 API 뷰 구현
LangChain을 활용한 대화 메모리 관리 포함
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


@csrf_exempt
@require_http_methods(["POST"])
def chat_view(request: HttpRequest) -> JsonResponse:
    """
    채팅 메시지를 처리하고 AI 응답을 반환합니다.
    
    POST /api/chat/
    Request Body:
        {
            "question": "질문 내용",
            "session_id": "선택적 세션 ID (UUID)"
        }
    
    Response:
        {
            "response": "AI 응답",
            "session_id": "세션 ID",
            "response_time": 123  # 밀리초
        }
    """
    try:
        # JSON 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "잘못된 JSON 형식입니다."},
                status=400
            )
        
        # 필수 필드 검증
        question = data.get("question", "").strip()
        if not question:
            return JsonResponse(
                {"error": "질문이 비어있습니다."},
                status=400
            )
        
        # 세션 ID 가져오기 또는 생성
        session_id = data.get("session_id")
        if session_id:
            # 기존 세션 사용
            try:
                session_uuid = uuid.UUID(session_id)
                session, created = ChatSession.objects.get_or_create(
                    session_id=session_uuid,
                    defaults={"user": request.user if request.user.is_authenticated else None}
                )
            except (ValueError, ValidationError):
                return JsonResponse(
                    {"error": "잘못된 세션 ID 형식입니다."},
                    status=400
                )
        else:
            # 새 세션 생성
            session = ChatSession.objects.create(
                user=request.user if request.user.is_authenticated else None
            )
        
        # LangChain을 사용하여 AI 응답 생성 (메모리 포함)
        import time
        start_time = time.time()
        
        try:
            ai_response = chat_with_memory(
                session_id=str(session.session_id),
                user_input=question
            )
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {str(e)}", exc_info=True)
            return JsonResponse(
                {"error": f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}"},
                status=500
            )
        
        response_time = int((time.time() - start_time) * 1000)  # 밀리초
        
        # DB에 저장
        ChatMessage.objects.create(
            session=session,
            user_message=question,
            ai_response=ai_response,
            response_time=response_time
        )
        
        logger.info(f"채팅 응답 생성 완료 (session={session.session_id}, time={response_time}ms)")
        
        return JsonResponse({
            "response": ai_response,
            "session_id": str(session.session_id),
            "response_time": response_time
        })
    
    except Exception as e:
        logger.error(f"채팅 처리 중 예상치 못한 오류: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": "서버 오류가 발생했습니다."},
            status=500
        )


@require_http_methods(["GET"])
def chat_history_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """
    세션별 채팅 히스토리를 조회합니다.
    
    GET /api/chat/history/<session_id>/
    
    Response:
        {
            "session_id": "세션 ID",
            "messages": [
                {
                    "user_message": "질문",
                    "ai_response": "응답",
                    "created_at": "2024-01-01T00:00:00Z",
                    "response_time": 123
                },
                ...
            ]
        }
    """
    try:
        # 세션 조회
        try:
            session_uuid = uuid.UUID(session_id)
            session = ChatSession.objects.get(session_id=session_uuid)
        except (ValueError, ValidationError):
            return JsonResponse(
                {"error": "잘못된 세션 ID 형식입니다."},
                status=400
            )
        except ChatSession.DoesNotExist:
            return JsonResponse(
                {"error": "세션을 찾을 수 없습니다."},
                status=404
            )
        
        # 메시지 조회
        messages = session.messages.all().order_by('created_at')
        
        messages_data = [
            {
                "user_message": msg.user_message,
                "ai_response": msg.ai_response,
                "created_at": msg.created_at.isoformat(),
                "response_time": msg.response_time
            }
            for msg in messages
        ]
        
        return JsonResponse({
            "session_id": str(session.session_id),
            "message_count": len(messages_data),
            "messages": messages_data
        })
    
    except Exception as e:
        logger.error(f"히스토리 조회 중 오류: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": "서버 오류가 발생했습니다."},
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def create_session_view(request: HttpRequest) -> JsonResponse:
    """
    새로운 채팅 세션을 생성합니다.
    
    POST /api/chat/session/
    
    Response:
        {
            "session_id": "UUID",
            "created_at": "2024-01-01T00:00:00Z"
        }
    """
    try:
        session = ChatSession.objects.create(
            user=request.user if request.user.is_authenticated else None
        )
        
        logger.info(f"새 세션 생성: {session.session_id}")
        
        return JsonResponse({
            "session_id": str(session.session_id),
            "created_at": session.created_at.isoformat()
        }, status=201)
    
    except Exception as e:
        logger.error(f"세션 생성 중 오류: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": "서버 오류가 발생했습니다."},
            status=500
        )


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
    try:
        # 세션 조회 및 삭제
        try:
            session_uuid = uuid.UUID(session_id)
            session = ChatSession.objects.get(session_id=session_uuid)
        except (ValueError, ValidationError):
            return JsonResponse(
                {"error": "잘못된 세션 ID 형식입니다."},
                status=400
            )
        except ChatSession.DoesNotExist:
            return JsonResponse(
                {"error": "세션을 찾을 수 없습니다."},
                status=404
            )
        
        # DB에서 삭제 (관련 메시지도 CASCADE로 자동 삭제)
        session.delete()
        
        # LangChain 메모리 캐시에서도 삭제
        clear_session_memory(session_id)
        
        logger.info(f"세션 삭제 완료: {session_id}")
        
        return JsonResponse({
            "status": "deleted",
            "session_id": session_id
        })
    
    except Exception as e:
        logger.error(f"세션 삭제 중 오류: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": "서버 오류가 발생했습니다."},
            status=500
        )
