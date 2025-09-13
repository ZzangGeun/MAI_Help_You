from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from .main_page_nexon_api_get import get_notice_list, get_api_data
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import asyncio
import aiohttp
import time
import logging
import psutil
import json

logger = logging.getLogger(__name__)


# HTML 페이지 뷰들
def main_page(request):
    notice = get_notice_list()
    context = {
        **notice,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
    
    return render(request, 'main_page.html', context)


# 캐릭터 정보 페이지 뷰
def character_info_view(request):
    return render(request, "character_info.html")

# 회원가입 페이지 뷰
def signup_view(request):
    return render(request, "signup.html")

# 로그인 페이지 뷰
def login_view(request):
    return render(request, "login.html")

# =============================================================================
# DRF APIView 예제들 (하이브리드 방식)
# =============================================================================



@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """
    로그인 API (기본 Django 뷰)
    POST /api/login/
    """
    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': '사용자명과 비밀번호를 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # 실제 로그인 로직 (예제)
        # TODO: 사용자 인증, JWT 토큰 생성 등
        
        return JsonResponse({
            'message': '로그인 성공',
            'token': f'jwt_token_for_{username}',
            'user': {
                'id': f'user_{username}',
                'username': username,
                'nickname': f'{username}_닉네임'
            },
            'status': 'success'
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '잘못된 JSON 형식입니다.',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return JsonResponse({
            'error': f'로그인 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def character_info_api(request):
    """
    캐릭터 정보 조회 API (기본 Django 뷰)
    GET /api/character-info/
    """
    try:
        # 쿼리 파라미터에서 캐릭터 이름 가져오기
        character_name = request.GET.get('character_name')
        world_name = request.GET.get('world_name', '스카니아')
        
        if not character_name:
            return JsonResponse({
                'error': '캐릭터 이름이 필요합니다.',
                'status': 'error'
            }, status=400)
        
        # 실제 캐릭터 정보 조회 로직 (예제)
        # TODO: Nexon API 호출, 데이터베이스 조회 등
        
        character_data = {
            'name': character_name,
            'level': 200,
            'class': '아크메이지',
            'world': world_name,
            'guild': '테스트길드',
            'last_updated': time.time()
        }
        
        return JsonResponse({
            'character': character_data,
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"캐릭터 정보 조회 오류: {e}")
        return JsonResponse({
            'error': f'캐릭터 정보 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


# =============================================================================
# DRF Function-based View 예제들 (@api_view 데코레이터 사용)
# =============================================================================

@require_http_methods(["GET"])
def notice_list_api(request):
    """
    공지사항 목록 조회 API (기본 Django 뷰)
    GET /api/notice/
    """
    try:
        # 기존 함수 재사용
        notice_data = get_notice_list()
        
        return JsonResponse({
            'notices': notice_data.get('notices', []),
            'total_count': len(notice_data.get('notices', [])),
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"공지사항 조회 오류: {e}")
        return JsonResponse({
            'error': f'공지사항 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validate_api_key_api(request):
    """
    API 키 검증 API (기본 Django 뷰)
    POST /api/validate-api-key/
    """
    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        api_key = data.get('api_key')
        
        if not api_key:
            return JsonResponse({
                'error': 'API 키가 필요합니다.',
                'status': 'error'
            }, status=400)
        
        # 실제 API 키 검증 로직 (예제)
        is_valid = len(api_key) >= 10  # 간단한 검증 예제
        
        if is_valid:
            return JsonResponse({
                'valid': True,
                'message': '유효한 API 키입니다.',
                'status': 'success'
            }, status=200)
        else:
            return JsonResponse({
                'valid': False,
                'message': '유효하지 않은 API 키입니다.',
                'status': 'error'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '잘못된 JSON 형식입니다.',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"API 키 검증 오류: {e}")
        return JsonResponse({
            'error': f'API 키 검증 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


# 추가 API 함수들
@require_http_methods(["GET"])
def notice_cashshop_api(request):
    """캐시샵 공지사항 API (기본 Django 뷰)"""
    try:
        from .main_page_nexon_api_get import get_api_data
        notice_data = get_api_data("/notice-cashshop")
        
        return JsonResponse({
            'notices': notice_data or [],
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"캐시샵 공지사항 조회 오류: {e}")
        return JsonResponse({
            'error': f'캐시샵 공지사항 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def notice_update_api(request):
    """업데이트 공지사항 API (기본 Django 뷰)"""
    try:
        from .main_page_nexon_api_get import get_api_data
        notice_data = get_api_data("/notice-update")
        
        return JsonResponse({
            'notices': notice_data or [],
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"업데이트 공지사항 조회 오류: {e}")
        return JsonResponse({
            'error': f'업데이트 공지사항 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def notice_event_api(request):
    """이벤트 공지사항 API (기본 Django 뷰)"""
    try:
        from .main_page_nexon_api_get import get_api_data
        notice_data = get_api_data("/notice-event")
        
        return JsonResponse({
            'notices': notice_data or [],
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"이벤트 공지사항 조회 오류: {e}")
        return JsonResponse({
            'error': f'이벤트 공지사항 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def health_check_api(request):
    """헬스 체크 API (기본 Django 뷰)"""
    try:
        import psutil
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': time.time(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }, status=200)
        
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }, status=500)


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
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return JsonResponse({
                'error': '사용자명, 이메일, 비밀번호를 모두 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # 실제 회원가입 로직 (예제)
        # TODO: 사용자 생성, 이메일 중복 체크, 비밀번호 해싱 등
        
        return JsonResponse({
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'id': f'user_{username}',
                'username': username,
                'email': email
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


