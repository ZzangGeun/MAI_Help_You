from django.shortcuts import render, redirect
from .get_nexon_api import get_notice_list, get_ranking_info, get_character_full_info
import requests
from django.http import JsonResponse
import asyncio
import aiohttp
import time
import json


def main_page(request):

    notice = get_notice_list()

    # event_info가 None일 경우 빈 딕셔너리로 처리하여 안전하게 접근
    event_info_data = notice.get('event_info') or {}
    context = {
        **notice,
        'event_list_json': json.dumps(event_info_data.get('event_notice', []))
    }
    
    return render(request, 'main_page.html', context)

def character_info_view(request):
    return render(request, "character_info/character_info.html")

def chatbot_page(request):
    return render(request, 'chatbot_page.html')

def ranking_api_view(request):
    """
    랭킹 정보를 JSON으로 반환하는 API 뷰
    """
    ranking_type = request.GET.get('type', 'overall') # 'overall' 또는 'union'
    
    # 프론트엔드에서 사용하는 'power'를 'union'으로 매핑
    if ranking_type == 'power':
        ranking_type = 'union'

    try:
        ranking_data = get_ranking_info(ranking_type=ranking_type)
        return JsonResponse({'success': True, 'data': ranking_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def character_search_api_view(request):
    """
    캐릭터 이름으로 정보를 검색하여 JSON으로 반환하는 API 뷰
    """
    character_name = request.GET.get('name', None)
    if not character_name:
        return JsonResponse({'success': False, 'error': '캐릭터 이름이 필요합니다.'}, status=400)

    character_data = get_character_full_info(character_name)
    if character_data:
        return JsonResponse({'success': True, 'data': character_data})
    else:
        return JsonResponse({'success': False, 'error': '캐릭터를 찾을 수 없습니다.'}, status=404)
