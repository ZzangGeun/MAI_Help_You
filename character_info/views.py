from django.shortcuts import render, redirect
import json
import os
from django.conf import settings
from django.urls import reverse
from character_info.get_character_info import *
from character_info.extract import *

# async def character_info_view(request):
#     return render(request, 'character_info/character_info.html')



async def character_info_view(request):

    character_name = request.GET.get('character_name', None)
    print(f"Character Name: {character_name}")  # 디버깅을 위한 출력


    character_info = await get_character_data(character_name)

    if character_info:

        basic_info = await character_info.get('basic_info', {})
        stat_info = await extract_stat(character_info.get('stat_info',{}))
        item_info = await extract_item_equipment(character_info.get('item_equipment_info',{}))
        ability_info = await extract_ability(character_info.get('ability_info', {}))
        link_skill_info = await extract_link_skills(character_info.get('link_skill_info',{}))
        vmatrix_info = await extract_vmatrix(character_info.get('vmatrix_info',{}))
        symbol_info = await extract_symbols(character_info.get('symbol_info', {}))
        hyper_stat_info = await character_info.get('hyper_stat_info', {})
        set_effect_info = await character_info.get('set_effect_info', {})
        hexamatrix_info = await character_info.get('hexamatrix_info', {})

        context = {
            'character_name': character_name,
            'stat_info': stat_info,
            'hyper_stat_info': hyper_stat_info,
            'item_info': item_info,
            'ability_info': ability_info,
            'set_effect_info': set_effect_info,
            'link_skill_info': link_skill_info,
            'hexamatrix_info': hexamatrix_info,
            'symbol_info': symbol_info,
            'preset_range': range(1, 4),
            'vmatrix_info': vmatrix_info,
            'basic_info': basic_info
        }

        return render(request, 'character_info/character_info.html', context)
    
    else:
        return render(request, 'error.html', {'error': '캐릭터 정보를 찾을 수 없습니다.'})


