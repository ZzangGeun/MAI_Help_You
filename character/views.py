from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings
from .get_character_info import *
from .extract import *
from django.core.cache import cache
import logging
import asyncio

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
async def character_info_view(request):
    """
    캐릭터 정보 조회 API
    GET /character/?character_name={캐릭터명}
    """
    try:
        character_name = request.GET.get('character_name', None)
        
        # 입력 검증
        if not character_name or not character_name.strip():
            return JsonResponse({
                'error': '캐릭터 이름을 입력해주세요.',
                'status': 'error'
            }, status=400)
        
        logger.info(f"캐릭터 정보 조회 요청: {character_name}")
        
        # 캐릭터 정보 조회
        character_info = await get_character_data(character_name.strip())
        
        if not character_info:
            return JsonResponse({
                'error': '캐릭터 정보를 가져오는 데 실패했습니다.',
                'status': 'error'
            }, status=404)
        
        logger.info(f"캐릭터 정보 조회 성공: {character_name}")
        
        return JsonResponse({
            'message': '캐릭터 정보 조회 성공',
            'data': character_info,
            'status': 'success'
        }, status=200)
    
    except Exception as e:
        logger.error(f"캐릭터 정보 조회 오류: {str(e)}")
        return JsonResponse({
            'error': '서버 오류가 발생했습니다.',
            'status': 'error'
        }, status=500)
    

