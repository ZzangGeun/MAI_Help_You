from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def signup_view(request):
    """회원가입 페이지 뷰"""
    return render(request, "signup.html")

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """
    회원가입 API (기본 Django 뷰)
    POST /api/signup/
    """
    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        user_id = data.get('user_id')
        email = data.get('email')
        password = data.get('password')
        nickname = data.get('nickname')
        
        if not all([user_id, email, password]):
            return JsonResponse({
                'error': '사용자ID, 이메일, 비밀번호를 모두 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # TODO: 사용자 생성, 이메일 중복 체크, 비밀번호 해싱 등
        
        return JsonResponse({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'id': f'user_{user_id}',
                'user_id': user_id,
                'email': email,
                'nickname': nickname
            },
            'status': 'success'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '잘못된 JSON 형식입니다.',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        return JsonResponse({
            'error': f'회원가입 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)
