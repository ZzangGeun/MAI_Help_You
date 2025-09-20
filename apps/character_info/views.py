from django.shortcuts import render, redirect
import json
import os
from django.conf import settings
from django.urls import reverse
from .get_character_info import *
from .extract import *
from django.core.cache import cache


async def character_info_view(request):

    character_name = request.GET.get('character_name', None)
    print(f"Character Name: {character_name}")  # 디버깅을 위한 출력


    character_info = await get_character_data(character_name)
    if not character_info:
        return render(request, 'character_info/character_info.html', {'error': '캐릭터 정보를 가져오는 데 실패했습니다.'})

    

