from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings
from django.urls import reverse
from .get_character_info import *
from .extract import *
from django.core.cache import cache
import logging
import asyncio

logger = logging.getLogger(__name__)


async def character_info_page(request):
    """캐릭터 정보 페이지 렌더링"""
    character_name = request.GET.get('character_name', '').strip()
    
    context = {}
    
    if character_name:
        try:
            logger.info(f"캐릭터 정보 조회 요청: {character_name}")
            
            # 캐릭터 정보 조회
            character_data = await get_character_data(character_name)
            
            if character_data:
                # basic_info에서 기본 정보 추출
                basic_info = character_data.get('basic_info', {})
                
                # item_info에서 item_equipment를 리스트로 변환
                item_info_dict = character_data.get('item_info', {})
                item_equipment = item_info_dict.get('item_equipment', {})
                item_list = []
                
                # 딕셔너리를 리스트로 변환
                for slot, item_data in item_equipment.items():
                    if item_data and item_data.get('name') != 'none':
                        item_list.append({
                            'item_name': item_data.get('name', '알 수 없음'),
                            'item_icon': item_data.get('icon', ''),
                            'item_part': item_data.get('part', '알 수 없음'),
                            'slot': slot,
                            'starforce': item_data.get('starforce', '0'),
                            'potential_grade': item_data.get('potential_option_grade', 'none')
                        })
                
                # 캐릭터 정보 구성
                context['character_info'] = {
                    'name': basic_info.get('character_name', character_name),
                    'level': basic_info.get('character_level', 'N/A'),
                    'job': basic_info.get('character_class', 'N/A'),
                    'server': basic_info.get('world_name', 'N/A'),
                    'image_url': basic_info.get('character_image', ''),
                    'fame': basic_info.get('character_popularity', 'N/A'),
                    'stat_info': character_data.get('stat_info', {}),
                    'item_info': item_list,  # 리스트로 변환된 장비 정보
                    'ability_info': character_data.get('ability_info', {}),
                    'link_skill_info': character_data.get('link_skill_info', {}),
                    'vmatrix_info': character_data.get('vmatrix_info', {}),
                    'symbol_info': character_data.get('symbol_info', {}),
                    'hyper_stat_info': character_data.get('hyper_stat_info', {}),
                    'pet_equipment_info': character_data.get('pet_equipment_info', {}),
                    'hexamatrix_info': character_data.get('hexamatrix_info', {}),
                    'hexamatrix_stat_info': character_data.get('hexamatrix_stat_info', {}),
                    'other_stat_info': character_data.get('other_stat_info', {})
                }
                logger.info(f"캐릭터 정보 조회 성공: {character_name}")
            else:
                context['error'] = f'"{character_name}" 캐릭터를 찾을 수 없습니다.'
                logger.warning(f"캐릭터 정보를 찾을 수 없음: {character_name}")
                
        except Exception as e:
            context['error'] = f'캐릭터 정보를 가져오는 중 오류가 발생했습니다: {str(e)}'
            logger.error(f"캐릭터 정보 조회 오류: {str(e)}")
    else:
        context['message'] = '캐릭터 닉네임을 입력해주세요.'
    
    return render(request, 'character_info.html', context)

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
    

