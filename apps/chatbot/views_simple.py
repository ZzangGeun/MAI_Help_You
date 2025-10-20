# 임시 간단한 views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .models import ChatSession, ChatMessage
from services.ai_models.fastapi_model.model import ask_question
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def chat_api(request):
    """API 엔드포인트: 채팅 메시지 처리 (간단한 버전)"""
    try:
        # JSON 데이터 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        # 입력 검증
        if not message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        if len(message) > 1000:  # 메시지 길이 제한
            return JsonResponse({'error': 'Message too long (max 1000 characters)'}, status=400)
        
        # 세션 처리 (간단한 버전)
        user = request.user if request.user.is_authenticated else None
        
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                # 존재하지 않는 세션이면 새로 생성
                session = ChatSession.objects.create(user=user)
        else:
            # 새 세션 생성
            session = ChatSession.objects.create(user=user)
        
        # 사용자 메시지 저장
        ChatMessage.objects.create(
            session=session,
            content=message,
            is_user=True
        )
        
        # 간단한 응답 생성 (일단 echo)
        try:
            # AI 모델 호출 시도
            ai_response = ask_question(message)
            if not ai_response or ai_response.strip() == "":
                ai_response = f"안녕하세요! 메시지를 받았습니다: '{message}'"
        except Exception as e:
            logger.error(f"AI model error: {str(e)}")
            ai_response = f"안녕하세요! 메시지를 받았습니다: '{message}' (AI 모델 오류로 간단 응답)"
        
        # AI 응답 저장
        ChatMessage.objects.create(
            session=session,
            content=ai_response,
            is_user=False
        )
        
        logger.info(f"Chat API request processed successfully for session {session.id}")
        
        return JsonResponse({
            'response': ai_response,
            'session_id': session.id,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in chat_api: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'success': False
        }, status=500)

@login_required
def chat_sessions(request):
    """사용자의 모든 채팅 세션 목록 조회"""
    sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    data = [{
        'id': session.id,
        'created_at': session.created_at,
        'updated_at': session.updated_at,
        'message_count': session.messages.count()
    } for session in sessions]
    
    return JsonResponse({'sessions': data})