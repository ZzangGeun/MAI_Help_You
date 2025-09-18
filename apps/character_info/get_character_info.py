from django.conf import settings
import asyncio
import requests
import json
from datetime import datetime, timedelta
import logging
import aiohttp
from .extract import *
from django.core.cache import cache

logger = logging.getLogger(__name__)
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

def all_info_extract(character_info):
    """
    캐릭터 정보에서 모든 정보를 추출합니다.
    """
    basic_info = character_info.get('get_character_basic_info', {})
    stat_info = extract_stat(character_info.get('get_character_stat_info', {}))
    item_info = extract_item_equipment(character_info.get('get_character_item_equipment_info', {}))
    ability_info = extract_ability(character_info.get('get_character_ability_info', {}))
    link_skill_info = extract_link_skills(character_info.get('get_character_link_skill_info', {}))
    vmatrix_info = extract_vmatrix(character_info.get('get_character_vmatrix_info', {}))
    symbol_info = extract_symbols(character_info.get('get_character_symbol_info', {}))
    hyper_stat_info = character_info.get('get_character_hyper_stat_info', {})
    set_effect_info = character_info.get('get_character_set_effect_info', {})
    hexamatrix_info = character_info.get('get_character_hexamatrix_info', {})

    return {
        'name': basic_info.get('character_name'),
        'server': basic_info.get('world_name'),
        'level': basic_info.get('character_level'),
        'image_url': basic_info.get('character_image'),
        'job': basic_info.get('character_class'),
        'fame': stat_info.get('인기도'),
        'power': stat_info.get('전투력'),
        'unionLevel': None, # This needs to be calculated or fetched from another source
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

async def get_character_info(character_name: str):
    """
    캐릭터 이름을 받아 해당 캐릭터의 정보를 반환합니다.
    캐시가 존재하면 캐시에서 데이터를 가져오고, 없으면 API를 호출하여 데이터를 가져옵니다.
    """
    cache_key = f'character_info_{character_name}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    async with aiohttp.ClientSession() as session:
        character_id_url = f"{BASE_URL}{API_ENDPOINTS['get_character_id']}?character_name={character_name}"
        async with session.get(character_id_url, headers={"x-nxopen-api-key": NEXON_API_KEY}) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch character ID: {response.status}")
                return None
            character_id_json = await response.json()
            ocid = character_id_json.get('ocid')

        if not ocid:
            return None

        character_info = {}
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        for endpoint_name, endpoint_path in API_ENDPOINTS.items():
            if endpoint_name == 'get_character_id':
                continue

            params = {'ocid': ocid}
            # Check if the endpoint supports the 'date' parameter
            if endpoint_name in ["get_character_stat_info", "get_character_hyper_stat_info", "get_character_ability_info", "get_character_item_equipment_info", "get_character_symbol_info", "get_character_set_effect_info", "get_character_link_skill_info", "get_character_vmatrix_info", "get_character_hexamatrix_info"]:
                 params['date'] = date

            url = f"{BASE_URL}{endpoint_path}"
            async with session.get(url, params=params, headers={"x-nxopen-api-key": NEXON_API_KEY}) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {endpoint_name}: {response.status}")
                    continue
                data = await response.json()
                character_info[endpoint_name] = data

        extracted_info = all_info_extract(character_info)

        cache.set(cache_key, extracted_info, timeout=CACHE_DURATION.total_seconds())
        return extracted_info
