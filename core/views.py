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
import json
from .get_carousel_data import transform_to_carousel_format



logger = logging.getLogger(__name__)


# HTML 페이지 뷰들
def main_page(request):
    notice = get_notice_list()
    ranking = get_ranking_list()
    carousel_notice = transform_to_carousel_format(notice)
    notice_event_data = notice.get('notice_event') or {}
    notice_update_data = notice.get('notice_update') or {}
    notice_cashshop_data = notice.get('notice_cashshop') or {}
    
    # Ranking 데이터 추출
    ranking_data = ranking.get('overall_ranking') or {}
    
    # overall_ranking은 {'ranking': [...]} 구조이므로 ranking 배열 추출
    if isinstance(ranking_data, dict) and 'ranking' in ranking_data:
        ranking_list = ranking_data['ranking']
    elif isinstance(ranking_data, list):
        ranking_list = ranking_data
    else:
        ranking_list = []
    
    # 5개씩 묶음으로 그룹화 (1-5위, 6-10위, 11-15위, ...)
    grouped_rankings = []
    for i in range(0, len(ranking_list), 5):
        group = ranking_list[i:i+5]  # 5개씩 그룹
        grouped_rankings.append(group)

    # Extract lists from possible API response shapes
    def extract_list(data):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for k in ('event_notice', 'update_notice', 'cashshop_notice', 'notices', 'data', 'results'):
                if k in data and isinstance(data[k], list):
                    return data[k]
        return []

    notice_events = extract_list(notice_event_data)
    notice_updates = extract_list(notice_update_data)
    notice_cashshops = extract_list(notice_cashshop_data)

    # JSON으로 변환하여 전달 (JavaScript에서 안전하게 사용 가능)
    context = {
        'events': json.dumps(carousel_notice.get('events', []), ensure_ascii=False),
        'cashItems': json.dumps(carousel_notice.get('cashItems', []), ensure_ascii=False),
        'noticeEvents': json.dumps(notice_events or [], ensure_ascii=False),
        'noticeUpdates': json.dumps(notice_updates or [], ensure_ascii=False),
        'noticeCashshops': json.dumps(notice_cashshops or [], ensure_ascii=False),
        'ranking': json.dumps(grouped_rankings or [], ensure_ascii=False),
        'timestamp': int(time.time())  # 캐시 방지용 타임스탐프
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


# ============================================================================
# JSON 데이터 API
# ============================================================================

@require_http_methods(["GET"])
def notice_json_api(request):
    """
    JSON 파일에서 공지사항 데이터를 로드하여 반환하는 API
    
    Returns:
        JSON: {
            "notice_event": [...],
            "notice_update": [...],
            "notice_cashshop": [...]
        }
    """
    try:
        from .services import load_notice_data_from_json
        notice_data = load_notice_data_from_json()
        
        return JsonResponse({
            'data': notice_data,
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"공지사항 JSON 데이터 조회 오류: {e}")
        return JsonResponse({
            'error': f'공지사항 JSON 데이터 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def ranking_json_api(request):
    """
    JSON 파일에서 랭킹 데이터를 로드하여 반환하는 API
    
    Returns:
        JSON: {
            "overall_ranking": [...]
        }
    """
    try:
        from .services import load_ranking_data_from_json
        ranking_data = load_ranking_data_from_json()
        
        return JsonResponse({
            'data': ranking_data,
            'status': 'success'
        }, status=200)
        
    except Exception as e:
        logger.error(f"랭킹 JSON 데이터 조회 오류: {e}")
        return JsonResponse({
            'error': f'랭킹 JSON 데이터 조회 중 오류가 발생했습니다: {str(e)}',
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

