from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from .services import get_notice_list, get_api_data, get_ranking_list
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
from .get_carousel_data import transform_to_carousel_format



logger = logging.getLogger(__name__)


# HTML 페이지 뷰들
def main_page(request):
    notice = get_notice_list()
    carousel_notice = transform_to_carousel_format(notice)
    ranking = get_ranking_list()

    # JSON으로 변환하여 전달 (JavaScript에서 안전하게 사용 가능)
    context = {
        'events': json.dumps(carousel_notice.get('events', []), ensure_ascii=False),
        'cashItems': json.dumps(carousel_notice.get('cashItems', []), ensure_ascii=False),
        **ranking,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
    

    return render(request, 'core/main_page.html', context)


# ============================================================================
# API Views
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_request_api(request):
    """
    챗봇 요청 API (POST만 사용)
    
    레거시 API - 새로운 chat 앱의 API로 리다이렉트
    새 API: /chat/api/chat/
    """
    try:
        data = json.loads(request.body)
        question = data.get('question')
        
        # 새로운 chat 앱의 chat_api로 요청 전달
        from chat.views import chat_api
        
        # 요청 데이터 형식 변환 (question → message)
        new_body = json.dumps({'message': question})
        request._body = new_body.encode('utf-8')
        
        # 새 API 호출
        response = chat_api(request)
        
        # 응답 형식 변환 (호환성 유지)
        response_data = json.loads(response.content)
        return JsonResponse({
            'response': response_data.get('response', ''),
            'status': 'success' if not response_data.get('error') else 'error'
        }, status=response.status_code)
        
    except Exception as e:
        logger.error(f"챗봇 요청 오류: {e}")
        return JsonResponse({
            'error': f'챗봇 요청 중 오류가 발생했습니다: {str(e)}',
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
        from .services import get_api_data
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
        from .services import get_api_data
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
        from .services import get_api_data
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
def ranking_api(request):
    """
    통합 랭킹 API
    GET /api/rankings/?type=general  - 종합 랭킹
    GET /api/rankings/?type=power    - 전투력 랭킹
    """
    try:
        ranking_type = request.GET.get('type', 'general')
        ranking_data = get_ranking_list()
        
        if ranking_type == 'power':
            # 전투력 랭킹 (가정: union_level 사용)
            data = ranking_data.get('overall_ranking', [])
        else:
            # 종합 랭킹 (기본값)
            data = ranking_data.get('overall_ranking', [])
        
        return JsonResponse({
            'success': True,
            'data': data,
            'type': ranking_type,
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"랭킹 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': f'랭킹 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def ranking_overall_api(request):
    """전체 랭킹 API (기본 Django 뷰) - 레거시 지원"""
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


@csrf_exempt
@require_http_methods(["GET"])
def character_search_api(request):
    """캐릭터 검색 API"""
    try:
        character_name = request.GET.get('name')
        
        if not character_name:
            return JsonResponse({
                'error': '캐릭터 이름을 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        # Nexon API를 통한 캐릭터 정보 조회
        character_data = get_api_data("/character/basic", {"character_name": character_name})
        
        if not character_data:
            return JsonResponse({
                'error': '캐릭터를 찾을 수 없습니다.',
                'status': 'error'
            }, status=404)
        
        return JsonResponse({
            'character': character_data,
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"캐릭터 검색 오류: {e}")
        return JsonResponse({
            'error': f'캐릭터 검색 중 오류가 발생했습니다: {str(e)}',
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
