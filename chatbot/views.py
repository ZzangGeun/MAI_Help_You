from django.shortcuts import render
import requests
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import chatbot_service

# Create your views here.

FASTAPI_URL = "http://localhost:8000/api/fastapi/ask"

def chatbot_view(request):
    """챗봇 메인 페이지 뷰"""
    return render(request, "chatbot/chatbot.html")

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_ask(request):
    """LangChain 기반 챗봇 질문 처리 뷰"""
    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        question = data.get("question", "")
        user_id = data.get("user_id", None)
        
        if not question:
            return JsonResponse({
                'error': "질문이 없습니다.",
                'status': 'error'
            }, status=400)
        
        # LangChain 서비스를 사용하여 답변 생성
        result = chatbot_service.get_response(question, user_id)
        
        return JsonResponse({
            'response': result['response'],
            'sources': result.get('sources', []),
            'has_rag': result.get('has_rag', False),
            'status': 'success'
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': "잘못된 JSON 형식입니다.",
            'status': 'error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f"예상치 못한 오류: {str(e)}",
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def chatbot_history(request):
    """채팅 히스토리 조회"""
    try:
        user_id = request.GET.get("user_id", None)
        history = chatbot_service.get_chat_history(user_id)
        
        return JsonResponse({
            'history': history,
            'status': 'success'
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
        user_id = data.get("user_id", None)
        
        success = chatbot_service.clear_history(user_id)
        
        if success:
            return JsonResponse({
                'message': "채팅 히스토리가 초기화되었습니다.",
                'status': 'success'
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
