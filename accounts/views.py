from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from core.models import User as UserModel
import json
import logging
import re

logger = logging.getLogger(__name__)

def signup_page(request):
    """회원가입 페이지 뷰"""
    return render(request, 'signup.html')

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """
    회원가입 API
    POST /signup/api/signup/
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id','').strip()
        email = data.get('email','').strip()
        password = data.get('password','').strip()  # ⚠️ 중복 제거
        nickname = data.get('nickname','').strip()

        # 전체 필수 입력 검증
        if not all([user_id, password, email, nickname]):
            return JsonResponse({
                'error': '모든 필드를 채워주세요.',
                'status': 'error'
                 }, status=400)

        # 아이디 형식 검증
        if not re.match(r'^[a-zA-Z0-9]{4,20}$', user_id):
            return JsonResponse({
                'error': '아이디는 4~20자의 영문 대소문자와 숫자만 사용할 수 있습니다.',
                'status': 'error'
                 }, status=400)

        # 이메일 형식 검증
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return JsonResponse({
                'error': '유효한 이메일 주소를 입력해주세요.',
                'status': 'error'
                 }, status=400)
        
        # 비밀번호 길이 검증
        if len(password) < 8:
            return JsonResponse({
                'error': '비밀번호는 최소 8자 이상이어야 합니다.',
                'status': 'error'
                 }, status=400)
        
        # 중복 확인 - ⚠️ 필드명 수정
        if UserModel.objects.filter(user_id=user_id).exists():  # id → user_id
            return JsonResponse({
                'error': '이미 존재하는 아이디입니다.',
                'status': 'error'
                 }, status=400)
        
        if UserModel.objects.filter(email=email).exists():
            return JsonResponse({
                'error': '이미 사용 중인 이메일입니다.',
                'status': 'error'
            }, status=400)
        
        # 사용자 비밀번호 해싱
        hashed_password = make_password(password)

        # 사용자 생성 - ⚠️ 필드명 수정
        user = UserModel.objects.create(
            user_id=user_id,
            password=hashed_password,
            email=email,
            nick_name=nickname,  # nickname → nick_name
            nexon_api_key='',
        )

        logger.info(f"새 사용자 생성: {user_id}")

        return JsonResponse({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'user_id': user.user_id,
                'nickname': user.nick_name,
                'email': user.email
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
            'error': '회원가입 중 오류가 발생했습니다.',
            'status': 'error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """
    로그인 API
    POST /accounts/api/login/
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        password = data.get('password')

        if not user_id or not password:
            return JsonResponse({
                'error': '사용자 ID와 비밀번호를 입력해주세요.',
                'status': 'error'
            }, status=400)

        # 사용자 찾기
        try:
            user = UserModel.objects.get(user_id=user_id)
        except UserModel.DoesNotExist:
            return JsonResponse({
                'error': '존재하지 않는 아이디입니다.',
                'status': 'error'
            }, status=404)

        # 비밀번호 확인
        if not check_password(password, user.password):
            return JsonResponse({
                'error': '비밀번호가 일치하지 않습니다.',
                'status': 'error'
            }, status=400)

        # TODO: JWT 토큰 생성 및 세션 처리
        
        logger.info(f"사용자 로그인 성공: {user_id}")

        return JsonResponse({
            'message': '로그인 성공',
            'token': f'jwt_token_for_{user_id}',  # 임시 토큰
            'user': {
                'user_id': user.user_id,
                'nickname': user.nick_name,
                'email': user.email,
            },
            'status': 'success'
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.', 'status': 'error'}, status=400)
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return JsonResponse({'error': f'로그인 중 오류가 발생했습니다: {str(e)}', 'status': 'error'}, status=500)