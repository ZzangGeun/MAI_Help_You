from django.conf import settings
import asyncio
import requests
import json
import asyncio
from datetime import datetime, timedelta
import logging
import os
import aiohttp
from .extract import *


logger =logging
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = settings.NEXON_API_KEY

# API 엔드 포인트 리스트
API_ENDPOINTS = {
    "get_character_id": "/id",
    "get_character_basic_info": "/character/basic",
    "get_character_stat_info": "/character/stat",
    "get_character_hyper_stat_info": "/character/hyper-stat",
    "get_character_ability_info": "/character/ability",
    "get_character_item_equipment_info": "/character/item-equipment",
    "get_character_symbol_info": "/character/symbol-equipment",
    "get_character_set_effect_info": "/character/set-effect",
    "get_character_link_skill_info": "/character/link-skill",
    "get_character_vmatrix_info": "/character/vmatrix",
    "get_character_hexamatrix_info": "/character/hexamatrix",
}

def get_api_url(endpoint, **params):
    """
    API 엔드 포인트에 맞는 URL을 생성합니다.
    """
    url = f"{BASE_URL}{API_ENDPOINTS[endpoint]}"
    if params:
        url += "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return url

def all_info_extract(character_info):
    """
    캐릭터 정보에서 모든 정보를 추출합니다.
    """
    stat_info = extract_stat(character_info.get('stat_info', {}))
    item_info = extract_item_equipment(character_info.get('item_equipment_info', {}))
    ability_info = extract_ability(character_info.get('ability_info', {}))
    link_skill_info = extract_link_skills(character_info.get('link_skill_info', {}))
    vmatrix_info = extract_vmatrix(character_info.get('vmatrix_info', {}))
    symbol_info = extract_symbols(character_info.get('symbol_info', {}))
    hyper_stat_info = character_info.get('hyper_stat_info', {})
    set_effect_info = character_info.get('set_effect_info', {})
    hexamatrix_info = character_info.get('hexamatrix_info', {})
    
    return {
        'stat_info': stat_info,
        'item_info': item_info,
        'ability_info': ability_info,
        'link_skill_info': link_skill_info,
        'vmatrix_info': vmatrix_info,
        'symbol_info': symbol_info,
        'hyper_stat_info': hyper_stat_info,
        'set_effect_info': set_effect_info,
        'hexamatrix_info': hexamatrix_info
    }

def get_character_data():
    """
    캐릭터 이름을 받아 해당 캐릭터의 정보를 반환합니다.
    캐시가 존재하면 캐시에서 데이터를 가져오고, 없으면 API를 호출하여 데이터를 가져옵니다.
    """
    async def fetch_character_data(character_name):
        cache_key = f'character_info_{character_name}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        async with aiohttp.ClientSession() as session:
            character_id_url = get_api_url("get_character_id", characterName=character_name)
            async with session.get(character_id_url, headers={"Authorization": f"Bearer {NEXON_API_KEY}"}) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch character ID: {response.status}")
                    return None
                character_id = await response.json()

            character_info = {}
            for endpoint in API_ENDPOINTS.keys():
                url = get_api_url(endpoint, characterId=character_id)
                async with session.get(url, headers={"Authorization": f"Bearer {NEXON_API_KEY}"}) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {endpoint}: {response.status}")
                        return None
                    data = await response.json()
                    character_info[endpoint] = data

            # 모든 정보 추출
            extracted_info = all_info_extract(character_info)

            # 캐시 저장
            cache.set(cache_key, extracted_info, timeout=CACHE_DURATION.total_seconds())
            return extracted_info

    return fetch_character_data



