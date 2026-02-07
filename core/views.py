from django.http.request import HttpRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import os
from django.conf import settings
from .services import get_api_data
from pathlib import Path


logger = logging.getLogger(__name__)


def serve_react(request):
    index_path = Path(settings.BASE_DIR) / 'static' / 'dist' / 'index.html'
    try:
        with index_path.open('rb') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html; charset=utf-8')
    except FileNotFoundError:
        return HttpResponse("React build not found. Please run 'npm run build' in frontend directory.", status=501)

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
        # from .services import get_api_data
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
        # from .services import get_api_data
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
        # from .services import get_api_data
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

