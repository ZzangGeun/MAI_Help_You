from django.shortcuts import render, redirect
from .get_nexon_api import get_notice_list, get_api_data
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
import asyncio
import aiohttp
import time
import logging
import psutil

logger = logging.getLogger(__name__)


# HTML 페이지 뷰들
def main_page(request):
    notice = get_notice_list()
    context = {
        **notice,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
<<<<<<< HEAD
    return render(request, 'main_page/main_page.html', context)
=======
    
    return render(request, 'main_page.html', context)
>>>>>>> feature/Design


def character_info_view(request):
    return render(request, "character_info/character_info.html")


# JSON API 뷰들
@require_http_methods(["GET"])
def notice_list_api(request):
    """공지사항 목록 조회 API"""
    try:
        # 쿼리 파라미터 처리
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        category = request.GET.get('category')
        important_only = request.GET.get('important_only', 'false').lower() == 'true'
        
        # 넥슨 API에서 공지사항 데이터 가져오기
        notice_data = get_api_data("/notice")
        
        if not notice_data:
            return JsonResponse({
                "success": False,
                "message": "공지사항을 불러올 수 없습니다.",
                "error_code": "API_ERROR"
            }, status=503)
        
        # 공지사항 리스트 추출
        notices = notice_data.get('notice', [])
        
        # 카테고리 필터링 (넥슨 API의 notice_type 기준)
        if category:
            notices = [n for n in notices if category.lower() in n.get('notice_type', '').lower()]
        
        # 페이지네이션 처리
        total_count = len(notices)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_notices = notices[start_idx:end_idx]
        
        # 응답 데이터 구성
        response_data = {
            "success": True,
            "data": {
                "notices": paginated_notices,
                "pagination": {
                    "current_page": page,
                    "per_page": limit,
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"공지사항 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "서버 내부 오류가 발생했습니다.",
            "error_code": "INTERNAL_ERROR"
        }, status=500)


@require_http_methods(["GET"])
def notice_detail_api(request, notice_id):
    """공지사항 상세 조회 API"""
    try:
        # 전체 공지사항 목록에서 해당 ID 찾기
        notice_data = get_api_data("/notice")
        
        if not notice_data:
            return JsonResponse({
                "success": False,
                "message": "공지사항을 불러올 수 없습니다."
            }, status=503)
        
        notices = notice_data.get('notice', [])
        notice = next((n for n in notices if n.get('notice_id') == notice_id), None)
        
        if not notice:
            return JsonResponse({
                "success": False,
                "message": "해당 공지사항을 찾을 수 없습니다."
            }, status=404)
        
        return JsonResponse({
            "success": True,
            "data": notice
        })
        
    except Exception as e:
        logger.error(f"공지사항 상세 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "서버 내부 오류가 발생했습니다."
        }, status=500)


@require_http_methods(["GET"])
def event_list_api(request):
    """이벤트 목록 조회 API"""
    try:
        event_status = request.GET.get('status', 'ongoing')
        
        # 넥슨 API에서 이벤트 데이터 가져오기
        event_data = get_api_data("/notice-event")
        
        if not event_data:
            return JsonResponse({
                "success": False,
                "message": "이벤트 정보를 불러올 수 없습니다."
            }, status=503)
        
        events = event_data.get('event_notice', [])
        
        return JsonResponse({
            "success": True,
            "data": {
                "events": events
            }
        })
        
    except Exception as e:
        logger.error(f"이벤트 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "서버 내부 오류가 발생했습니다."
        }, status=500)


@require_http_methods(["GET"])
def health_check_api(request):
    """서비스 상태 확인 API"""
    try:
        # 데이터베이스 연결 상태 확인
        try:
            connection.ensure_connection()
            db_status = "connected"
        except Exception:
            db_status = "error"
        
        # 넥슨 API 상태 확인
        try:
            test_response = get_api_data("/notice")
            external_api_status = "available" if test_response else "limited"
        except Exception:
            external_api_status = "unavailable"
        
        # 챗봇 서비스 상태 (추후 구현)
        chatbot_status = "ready"
        
        # 전체 서비스 상태 결정
        if db_status == "connected" and external_api_status == "available":
            overall_status = "healthy"
        elif db_status == "error" or external_api_status == "unavailable":
            overall_status = "down"
        else:
            overall_status = "degraded"
        
        # 시스템 정보
        try:
            uptime = time.time() - psutil.boot_time()
        except Exception:
            uptime = 0
        
        response_data = {
            "success": True,
            "data": {
                "status": overall_status,
                "services": {
                    "database": db_status,
                    "chatbot": chatbot_status,
                    "external_api": external_api_status
                },
                "uptime": uptime,
                "version": "1.0.0"
            }
        }
        
        if overall_status == "down":
            return JsonResponse(response_data, status=503)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"헬스체크 중 오류 발생: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "헬스체크 실패",
            "error_code": "HEALTH_CHECK_ERROR"
        }, status=500)
