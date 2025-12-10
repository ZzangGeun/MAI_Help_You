import json
import re


# Django 내장 사용자 모델을 가져옵니다.
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from .models import UserProfile

import logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """
    회원가입 API (Django 표준 User & UserProfile 사용)
    POST /accounts/api/signup/
    """
    try:
        # 데이터 파싱, 정리
        data = json.loads(request.body)
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '').strip()
        nickname = data.get('nickname', '').strip()  # 필수
        # 기존 UserProfile 필드와 호환을 위해 내부적으로는 maple_nickname에 저장합니다
        nexon_api_key = data.get('nexon_api_key', '').strip()  # 선택사항 (옵션)

        # 유효성 검사
        # 필수 필드 체크
        if not all([user_id, password, nickname]):
            return JsonResponse({'error': '필수 필드를 모두 채워주세요.', 'status': 'error'}, status=400)

        # user_id: 4-20자, 영문+숫자만
        if not re.match(r'^[A-Za-z0-9]{4,20}$', user_id):
            return JsonResponse({'error': '아이디는 4~20자의 영문자와 숫자만 사용 가능합니다.', 'status': 'error'}, status=400)

        # password: 최소 8자, 영문 + 숫자 + 특수문자 포함
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
            return JsonResponse({'error': '비밀번호는 최소 8자이며 영문자, 숫자, 특수문자를 모두 포함해야 합니다.', 'status': 'error'}, status=400)

        # nickname: 2-10자, 한글/영문/숫자
        if not re.match(r'^[\uAC00-\uD7A3A-Za-z0-9]{2,10}$', nickname):
            return JsonResponse({'error': '닉네임은 2~10자의 한글/영문/숫자만 가능합니다.', 'status': 'error'}, status=400)
        
        # 중복 검사
        if User.objects.filter(username=user_id).exists():
            return JsonResponse({'error': '이미 존재하는 아이디입니다.', 'status': 'error'}, status=400)

        if UserProfile.objects.filter(maple_nickname=nickname).exists():
            return JsonResponse({'error': '이미 사용 중인 닉네임입니다.', 'status': 'error'}, status=400)
        

        # 사용자 생성
        user = User.objects.create_user(
            username=user_id, 
            password=password, 
        )
        
        # 5. UserProfile 생성 및 연결
        UserProfile.objects.create(
            user=user,
            maple_nickname=nickname,
            nexon_api_key=nexon_api_key if nexon_api_key else None
        )

        logger.info(f"새 사용자 생성: {user_id}")

        return JsonResponse({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'user_id': user.username,
                'nickname': nickname,
            },
            'status': 'success'
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.', 'status': 'error'}, status=400)
    
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        return JsonResponse({'error': '회원가입 중 서버 오류가 발생했습니다.', 'status': 'error'}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """
    로그인 API (Django 표준 User 사용)
    POST /accounts/api/login/
    """
    try:
        # 1. 요청 데이터 파싱 (JSON 형식으로 변경해야 함)
        # 회원가입과 마찬가지로, 프론트엔드는 JSON을 보낼 가능성이 높습니다.
        data = json.loads(request.body)
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '').strip()

        if not user_id or not password:
            return JsonResponse({'error': '아이디와 비밀번호를 모두 입력해주세요.', 'status': 'error'}, status=400)

        # 2. 사용자 인증 (Authenticate)
        # DB에 저장된 암호화된 비밀번호와 입력된 비밀번호를 비교하여 User 객체를 반환하거나 None 반환
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            # 3. 인증 성공: 세션 생성 및 유지 (Login)
            # request 객체에 사용자 정보를 담아 세션을 시작합니다.
            login(request, user)
            logger.info(f"로그인 성공: {user_id}")

            return JsonResponse({
                'message': '로그인에 성공했습니다.',
                'status': 'success'
            }, status=200)
            
        else:
            # 5. 인증 실패
            return JsonResponse({'error': '아이디 또는 비밀번호가 올바르지 않습니다.', 'status': 'error'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return JsonResponse({'error': '로그인 중 서버 오류가 발생했습니다.', 'status': 'error'}, status=500)

    

@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    """
    로그아웃 API
    POST /accounts/api/logout/
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': '로그인 상태가 아닙니다.', 'status': 'error'}, status=401)
        
        user_id = request.user.username
        
        # 세션 삭제 및 로그아웃 처리
        logout(request)
        
        logger.info(f"로그아웃 성공: {user_id}")
        
        return JsonResponse({
            'message': '로그아웃되었습니다.',
            'status': 'success'
        }, status=200)
    
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return JsonResponse({'error': '로그아웃 중 서버 오류가 발생했습니다.', 'status': 'error'}, status=500)