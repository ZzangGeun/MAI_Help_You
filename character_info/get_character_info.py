from django.conf import settings
import asyncio
import requests
import json
import asyncio
from datetime import datetime, timedelta
import logging
import os
import numpy as np
import aiohttp


logger =logging
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = settings.NEXON_API_KEY

async def get_api_data(endpoint, params=None):
    headers = {'x-nxopen-api-key': NEXON_API_KEY}
    url = f'{BASE_URL}{endpoint}'

    try: 
        response = requests.get(url, headers = headers , params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    except requests.RequestException as e:
        return None
    

async def get_character_data(character_name, date=None):
    async with aiohttp.ClientSession() as session:
        ocid_data = await get_api_data('/id',{'character_name' : character_name})  # 닉네임 입력 후 ocid 가져오기
        
        ocid = ocid_data['ocid']
        params ={"ocid" : ocid}

        #필요한 정보 가져오기

        basic_info = await get_api_data("/character/basic", params)
        stat_info = await get_api_data("/character/stat", params)
        hyper_stat_info = await get_api_data("/character/hyper-stat", params)
        ability_info = await get_api_data("/character/ability", params)
        item_equipment_info = await get_api_data("/character/item-equipment", params)
        symbol_info = await get_api_data("/character/symbol-equipment", params)
        set_effect_info = await get_api_data("/character/set-effect", params)
        link_skill_info = await get_api_data("/character/link-skill", params)
        vmatrix_info = await get_api_data("/character/vmatrix", params)
        hexamatrix_info = await get_api_data("/character/hexamatrix", params)


        return {
            "basic_info": basic_info,
            "stat_info": stat_info,
            "hyper_stat_info":hyper_stat_info,
            "item_equipment_info": item_equipment_info,
            "ability_info": ability_info,
            "set_effect_info": set_effect_info,
            "link_skill_info": link_skill_info,
            "hexamatrix_info": hexamatrix_info,
            "symbol_info": symbol_info,
            "vmatrix_info": vmatrix_info,
        }






    


