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
        confirm_password = data.get('confirm_password', '').strip()
        maple_nickname = data.get('maple_nickname', '').strip()  # 필수
        nexon_api_key = data.get('nexon_api_key', '').strip()  # 선택사항

        # 유효성 검사
        if not all ([user_id, password, confirm_password, maple_nickname]):
            return JsonResponse({'error': '필수 필드를 모두 채워주세요.'}, status=400)
        
        if not re.match(r'^[a-zA-Z0-9_]{6,20}$', user_id):
            return JsonResponse({'error': '아이디는 6~20자의 영문자, 숫자, 밑줄(_)만 사용할 수 있습니다.'}, status=400)
        
        if len(password) < 8:
            return JsonResponse({'error': '비밀번호는 최소 8자 이상이어야 합니다.'}, status=400)
        
        if password != confirm_password:
            return JsonResponse({'error': '비밀번호와 비밀번호 확인이 일치하지 않습니다.'}, status=400)
        
        # 중복 검사
        if User.objects.filter(username=user_id).exists():
            return JsonResponse({'error': '이미 존재하는 아이디입니다.'}, status=400)
        
        if UserProfile.objects.filter(maple_nickname=maple_nickname).exists():
            return JsonResponse({'error': '이미 사용 중인 메이플 닉네임입니다.'}, status=400)
        

        # 사용자 생성
        user = User.objects.create_user(
            username=user_id, 
            password=password, 
        )
        
        # 5. UserProfile 생성 및 연결
        UserProfile.objects.create(
            user=user,
            maple_nickname=maple_nickname,
            nexon_api_key=nexon_api_key if nexon_api_key else None
        )

        logger.info(f"새 사용자 생성: {user_id}")

        return JsonResponse({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'user_id': user.username,
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
            return JsonResponse({'error': '아이디와 비밀번호를 모두 입력해주세요.'}, status=400)

        # 2. 사용자 인증 (Authenticate)
        # DB에 저장된 암호화된 비밀번호와 입력된 비밀번호를 비교하여 User 객체를 반환하거나 None 반환
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            # 3. 인증 성공: 세션 생성 및 유지 (Login)
            # request 객체에 사용자 정보를 담아 세션을 시작합니다.
            login(request, user)
            
            # 4. UserProfile에서 메이플 닉네임 가져오기
            try:
                profile = get_object_or_404(UserProfile, user=user)
                maple_nickname = profile.maple_nickname
            except:
                # UserProfile이 없을 경우 (예외 처리)
                maple_nickname = None 

            logger.info(f"로그인 성공: {user_id}")

            return JsonResponse({
                'message': f'{user_id}님, 환영합니다!',
                'user': {
                    'user_id': user.username,
                    'email': user.email,
                    'maple_nickname': maple_nickname,
                },
                'status': 'success'
            }, status=200)
            
        else:
            # 5. 인증 실패
            return JsonResponse({'error': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return JsonResponse({'error': '로그인 중 서버 오류가 발생했습니다.'}, status=500)

    

@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    """
    로그아웃 API
    POST /accounts/api/logout/
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': '로그인 상태가 아닙니다.'}, status=401)
        
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
        return JsonResponse({'error': '로그아웃 중 서버 오류가 발생했습니다.'}, status=500)