from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from .main_page_nexon_api_get import get_notice_list, get_api_data, get_ranking_list
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
    ranking = get_ranking_list()
    context = {
        **notice,
        **ranking,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
    
    return render(request, 'main_page.html', context)


# 캐릭터 정보 페이지 뷰
def character_info_view(request):
    return render(request, "character_info.html")


# 로그인 페이지 뷰
def login_view(request):
    return render(request, "login.html")




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
        user_id = data.get('user_id')
        password = data.get('password')
        email = data.get('email')
        nickname = data.get('nickname')
        
        if not user_id or not password:
            return JsonResponse({
                'error': '사용자ID와 비밀번호를 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # TODO: 사용자 인증, JWT 토큰 생성 등
        
        return JsonResponse({
            'message': '로그인 성공',
            'token': f'jwt_token_for_{user_id}',
            'user': {
                'user_id': user_id,
                'nickname': nickname,
                'email': email,
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
def logout_api(request):
    """
    로그아웃 API (기본 Django 뷰)
    GET /api/logout/
    """
    return JsonResponse({'message': '로그아웃이 완료되었습니다.', 'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_request_api(request):
    """챗봇 요청 API (POST만 사용)"""
    try:
        data = json.loads(request.body)
        question = data.get('question')
        user_id = data.get('user_id')
        nickname = data.get('nickname')
        
        if not question:
            return JsonResponse({
                'error': '질문을 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # 로그인 상태 확인
        if user_id or nickname:
            # 로그인 챗봇 기능
            result = get_api_data("/chatbot", {
                "question": question, 
                "user_id": user_id, 
                "nickname": nickname
            })
        else:
            # 비로그인 챗봇 기능
            result = get_api_data("/chatbot", {"question": question})
        
        return JsonResponse({
            'response': result.get('response'),
            'status': 'success'
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '잘못된 JSON 형식입니다.',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"챗봇 요청 오류: {e}")
        return JsonResponse({
            'error': f'챗봇 요청 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def character_search_api(request):
    """캐릭터 검색 API - character_info 페이지로 리다이렉트"""
    try:
        data = json.loads(request.body)
        character_name = data.get('character_name')
        
        if not character_name:
            return JsonResponse({
                'error': '캐릭터 닉네임을 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # character_info 페이지로 리다이렉트
        from django.shortcuts import redirect
        from urllib.parse import quote
        encoded_character_name = quote(character_name)
        return redirect(f'/character-info/?character_name={encoded_character_name}')
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '잘못된 JSON 형식입니다.',
            'status': 'error'
        }, status=400)
    except Exception as e:
        logger.error(f"캐릭터 검색 오류: {e}")
        return JsonResponse({
            'error': f'캐릭터 검색 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)
    



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

@csrf_exempt
@require_http_methods(["GET"])
def ranking_overall_api(request):
    """전체 랭킹 API (기본 Django 뷰)"""
    try:
        ranking_data = get_ranking_list()
        
        return JsonResponse({
            'ranking': ranking_data.get('overall_ranking', []),
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"전체 랭킹 조회 오류: {e}")
        return JsonResponse({
            'error': f'전체 랭킹 조회 중 오류가 발생했습니다: {str(e)}',
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


