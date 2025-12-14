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




# character 앱에서 정보 추출 함수 가져오기
from services.nexon_service import process_signup_with_key
import asyncio

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """
    회원가입 API
    POST /accounts/api/signup/
    Request Body: {
        "user_id": "...",
        "password": "...",
        "nexon_api_key": "..."    # 선택 (입력 시 자동 캐릭터 연동)
    }
    """
    try:
        # 데이터 파싱
        data = json.loads(request.body)
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '').strip()
        # character_name은 입력받지 않아도 됨 (API Key로 자동 탐색)
        nexon_api_key = data.get('nexon_api_key', '').strip()

        # 유효성 검사
        if not all([user_id, password]):
            return JsonResponse({'error': '필수 필드(아이디, 비밀번호)를 채워주세요.', 'status': 'error'}, status=400)

        # user_id: 4-20자, 영문+숫자만
        if not re.match(r'^[A-Za-z0-9]{4,20}$', user_id):
            return JsonResponse({'error': '아이디는 4~20자의 영문자와 숫자만 사용 가능합니다.', 'status': 'error'}, status=400)

        # password: 최소 8자, 영문 + 숫자 + 특수문자 포함
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
            return JsonResponse({'error': '비밀번호는 최소 8자이며 영문자, 숫자, 특수문자를 모두 포함해야 합니다.', 'status': 'error'}, status=400)
            
        # 중복 검사 (아이디만)
        if User.objects.filter(username=user_id).exists():
            return JsonResponse({'error': '이미 존재하는 아이디입니다.', 'status': 'error'}, status=400)

        detected_character_name = None
        
        # API Key가 있는 경우 캐릭터 자동 연동 시도
        if nexon_api_key:
            try:
                detected_character_name, detected_character_ocid = asyncio.run(process_signup_with_key(nexon_api_key))
                
                if not detected_character_name:
                    logger.warning(f"API Key({nexon_api_key})로 캐릭터를 찾을 수 없습니다. (연동 실패)")
                    return JsonResponse({'error': f'유효하지 않은 API Key이거나 계정에 캐릭터가 없습니다. (Key: {nexon_api_key[:5]}...)', 'status': 'error'}, status=400)
                    
            except Exception as e:
                logger.error(f"캐릭터 자동 연동 중 오류: {e}")
                return JsonResponse({'error': '캐릭터 정보를 가져오는 중 오류가 발생했습니다.', 'status': 'error'}, status=400)

        # 사용자 생성   
        user = User.objects.create_user(
            username=user_id, 
            password=password, 
        )
        
        # UserProfile 생성
        UserProfile.objects.create(
            user=user,
            nexon_api_key=nexon_api_key if nexon_api_key else None,
            maple_nickname=detected_character_name if detected_character_name else None,
            character_ocid=detected_character_ocid if detected_character_ocid else None
        )
        
        message = '회원가입이 완료되었습니다.'
        if detected_character_name:
            message += f" (캐릭터 연동: {detected_character_name})"
            logger.info(f"새 사용자 생성: {user_id} (자동 연동: {detected_character_name})")
        else:
            logger.info(f"새 사용자 생성: {user_id} (캐릭터 연동 없음)")

        return JsonResponse({
            'message': message,
            'user': {
                'user_id': user.username,
                'linked_character': detected_character_name,
                'character_ocid': detected_character_ocid
            },
            'status': 'success'
        }, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다.', 'status': 'error'}, status=400)
    
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'회원가입 중 서버 오류가 발생했습니다: {str(e)}', 'status': 'error'}, status=500)
    
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
        username = data.get('username', '').strip()
        # 호환성을 위해 user_id도 체크 (혹시 모를 구버전 클라이언트 대비)
        if not username:
            username = data.get('user_id', '').strip()
            
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({'error': '아이디와 비밀번호를 모두 입력해주세요.', 'status': 'error'}, status=400)

        # 2. 사용자 인증 (Authenticate)
        # DB에 저장된 암호화된 비밀번호와 입력된 비밀번호를 비교하여 User 객체를 반환하거나 None 반환
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 3. 인증 성공: 세션 생성 및 유지 (Login)
            # request 객체에 사용자 정보를 담아 세션을 시작합니다.
            login(request, user)
            logger.info(f"로그인 성공: {username}")

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


@require_http_methods(["GET"])
def user_info_api(request):
    """
    현재 로그인한 사용자 정보 조회 API
    GET /accounts/api/user/
    AuthContext에서 로그인 상태 확인용으로 사용
    """
    if request.user.is_authenticated:
        try:
            # UserProfile 정보 가져오기 (related_name='profile')
            profile = getattr(request.user, 'profile', None)
            
            user_data = {
                'user_id': request.user.username,
                'maple_nickname': profile.maple_nickname if profile else None,
                'character_ocid': profile.character_ocid if profile else None,
            }
            
            return JsonResponse({'data': user_data, 'status': 'success'})
            
        except Exception as e:
            logger.error(f"사용자 정보 조회 오류: {e}")
            return JsonResponse({'error': '사용자 정보를 불러오는 중 오류가 발생했습니다.'}, status=500)
    else:
        return JsonResponse({'error': '로그인 상태가 아닙니다.', 'status': 'error'}, status=401)
