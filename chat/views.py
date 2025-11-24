from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
# from .chat_session import ChatSessionManager
# from .models import ChatSession, ChatMessage

def chatbot_page(request):
    """채팅 페이지 렌더링"""
    return render(request, 'chatbot_page.html')

@csrf_exempt
@require_POST
def chat_api(request):
    """API 엔드포인트: 채팅 메시지 처리"""
    import logging
    logger = logging.getLogger(__name__)
    
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
        
        # 세션 관리자 초기화
        user = request.user if request.user.is_authenticated else None
        session_manager = ChatSessionManager(session_id=session_id, user=user)
        
        try:
            session_id = session_manager.initialize_session()
        except Exception as session_error:
            logger.error(f"Session initialization failed: {str(session_error)}")
            return JsonResponse({'error': 'Failed to initialize session'}, status=500)
        
        # 메시지 처리
        try:
            response = session_manager.process_message(message)
        except Exception as process_error:
            logger.error(f"Message processing failed: {str(process_error)}")
            response = "죄송합니다. 메시지 처리 중 오류가 발생했습니다."
        
        logger.info(f"Chat API request processed successfully for session {session_id}")
        
        return JsonResponse({
            'response': response,
            'session_id': session_id,
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