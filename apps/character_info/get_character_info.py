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

async def get_character_data(character_name):
    cache_key = f'character_info_{character_name}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    async with aiohttp.ClientSession() as session:
        # 1. Get OCID
        ocid_url = get_api_url("get_character_id", character_name=character_name)
        headers = {"Authorization": f"Bearer {NEXON_API_KEY}"}
        
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            async with session.get(ocid_url, headers=headers) as response:
                response.raise_for_status() # Raise an exception for HTTP errors
                ocid_data = await response.json()
                ocid = ocid_data.get('ocid')
                if not ocid:
                    logger.error(f"OCID not found for character: {character_name}")
                    return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"Failed to fetch OCID for {character_name}: {e.status} - {e.message}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching OCID for {character_name}: {e}")
            return None

        character_info = {}
        # 2. Get basic info using OCID
        try:
            basic_info_url = get_api_url("get_character_basic_info", ocid=ocid, date=today)
            async with session.get(basic_info_url, headers=headers) as response:
                response.raise_for_status()
                character_info['basic_info'] = await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"Failed to fetch basic info for {character_name}: {e.status} - {e.message}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching basic info for {character_name}: {e}")
            return None

        # For now, only fetch basic info. Other endpoints can be added as needed.
        # Example of fetching other info:
        # try:
        #     stat_info_url = get_api_url("get_character_stat_info", ocid=ocid, date=today)
        #     async with session.get(stat_info_url, headers=headers) as response:
        #         response.raise_for_status()
        #         character_info['stat_info'] = await response.json()
        # except aiohttp.ClientError as e:
        #     logger.error(f"Failed to fetch stat info for {character_name}: {e}")
        #     return None

        # Extract and process info (assuming extract.py functions are updated for new structure)
        # For now, just return basic info directly
        extracted_info = character_info['basic_info'] # Simplified for initial integration

        # Cache result
        cache.set(cache_key, extracted_info, timeout=CACHE_DURATION.total_seconds())
        return extracted_info
