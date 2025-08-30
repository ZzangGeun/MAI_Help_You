from django.shortcuts import render
import requests
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import chatbot_service
from django.utils.crypto import get_random_string

# Create your views here.

FASTAPI_URL = "http://localhost:8000/api/fastapi/ask"

def chatbot_view(request):
    """챗봇 메인 페이지 뷰"""
    return render(request, "chatbot/chatbot.html")

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_ask(request):
    """LangChain 기반 챗봇 질문 처리 뷰 (로그인 불필요)."""
    # JSON 파싱
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.', 'status': 'error'}, status=400)

    question = data.get('question', '').strip()
    user_id = data.get('user_id')

    # 세션 기반 임시 user_id 생성
    if not user_id:
        if not request.session.session_key:
            request.session.save()
        user_id = request.session.session_key or get_random_string(12)

    if not question:
        return JsonResponse({'error': '질문이 없습니다.', 'status': 'error', 'user_id': user_id}, status=400)

    try:
        result = chatbot_service.get_response(question, user_id)
    except Exception as e:
        return JsonResponse({'error': f'답변 생성 오류: {e}', 'status': 'error', 'user_id': user_id}, status=500)

    return JsonResponse({
        'response': result.get('response'),
        'sources': result.get('sources', []),
        'has_rag': result.get('has_rag', False),
        'status': 'success',
        'user_id': user_id
    })

@csrf_exempt
@require_http_methods(["GET"])
def chatbot_history(request):
    """채팅 히스토리 조회"""
    try:
        user_id = request.GET.get("user_id")
        if not user_id:
            if not request.session.session_key:
                request.session.save()
            user_id = request.session.session_key
        history = chatbot_service.get_chat_history(user_id)
        
        return JsonResponse({
            'history': history,
            'status': 'success',
            'user_id': user_id
        })
    except Exception as e:
        return JsonResponse({
            'error': f"히스토리 조회 중 오류: {str(e)}",
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_clear_history(request):
    """채팅 히스토리 초기화"""
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        if not user_id:
            if not request.session.session_key:
                request.session.save()
            user_id = request.session.session_key
        
        success = chatbot_service.clear_history(user_id)
        
        if success:
            return JsonResponse({
                'message': "채팅 히스토리가 초기화되었습니다.",
                'status': 'success',
                'user_id': user_id
            })
        else:
            return JsonResponse({
                'error': "히스토리 초기화에 실패했습니다.",
                'status': 'error'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': "잘못된 JSON 형식입니다.",
            'status': 'error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f"히스토리 초기화 중 오류: {str(e)}",
            'status': 'error'
        }, status=500)

def chatbot_health_check(request):
    """챗봇 서버 상태 확인"""
    try:
        # LangChain 서비스 상태 확인
        test_response = chatbot_service.get_response("테스트", "test_user")
        
        if test_response['response']:
            return JsonResponse({'status': 'healthy'})
        else:
            return JsonResponse({'status': 'unhealthy'}, status=503)
    except:
        return JsonResponse({'status': 'unhealthy'}, status=503)
