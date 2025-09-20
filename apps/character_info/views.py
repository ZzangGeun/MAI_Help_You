from django.shortcuts import render, redirect
import json
import os
from .get_character_info import get_character_info
from .extract import *
from django.core.cache import cache
import logging
logger = logging.getLogger(__name__)


async def character_info_view(request):
    character_name = request.GET.get('character_name', None)
    logger.info(f"Attempting to fetch info for character: {character_name}")

    if not character_name:
        return render(request, 'character_info/character_info.html', {'message': '검색할 캐릭터 이름을 입력해주세요.'})

    character_info = await get_character_info(character_name)
    if not character_info:
        error_message = f"'{character_name}' 캐릭터 정보를 가져오는 데 실패했습니다. 캐릭터 이름을 확인해주세요."
        return render(request, 'character_info/character_info.html', {'error': error_message})

    context = {'character_info': character_info}
    return render(request, 'character_info/character_info.html', context)
