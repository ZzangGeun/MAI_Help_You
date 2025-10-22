from django.shortcuts import render
from django.http import JsonResponse
import json
import os
from django.conf import settings
from django.urls import reverse
from .get_character_info import get_character_data
from .extract import *
from django.core.cache import cache

async def character_info_view(request):
    character_name = request.GET.get('character_name', None)

    if not character_name:
        return JsonResponse({'success': False, 'message': '캐릭터 이름을 입력해주세요.'}, status=400)

    character_info = await get_character_data(character_name)

    if character_info:
        return JsonResponse({'success': True, 'data': character_info})
    else:
        return JsonResponse({'success': False, 'message': '캐릭터 정보를 찾을 수 없습니다.'}, status=404)
