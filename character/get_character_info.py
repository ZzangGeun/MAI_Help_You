from django.conf import settings
import asyncio
import requests
import json
from datetime import datetime, timedelta
import logging
import aiohttp
from django.core.cache import cache
from pathlib import Path
from .extract import (
    extract_stat, extract_item_equipment, extract_ability, 
    extract_link_skills, extract_vmatrix, extract_symbols,
    extract_hyper_stat, extract_pet_equipment, extract_hexamatrix,
    extract_hexamatrix_stat, extract_other_stat
)
import os

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = os.getenv('NEXON_API_KEY')


# API 엔드 포인트 리스트
API_ENDPOINTS = {
    "get_character_id": "/id",
    "get_character_basic_info": "/character/basic",
    "get_character_stat_info": "/character/stat",
    "get_character_hyper_stat_info": "/character/hyper-stat",
    "get_character_ability_info": "/character/ability",
    "get_character_item_equipment_info": "/character/item-equipment",
    "get_character_pet_equipment_info": "/character/pet-equipment",
    "get_character_symbol_info": "/character/symbol-equipment",
    "get_character_set_effect_info": "/character/set-effect",
    "get_character_link_skill_info": "/character/link-skill",
    "get_character_vmatrix_info": "/character/vmatrix",
    "get_character_hexamatrix_info": "/character/hexamatrix",
    "get_character_hexamatrix_stat_info": "/character/hexamatrix-stat",
    "get_character_other_stat_info": "/character/other-stat",
    "get_character_popularity_info": "/character/popularity",
    "get_account_character_list": "/character/list",
}

def get_api_url(endpoint, **params):
    """
    API 엔드 포인트에 맞는 URL을 생성합니다.
    """
    from urllib.parse import urlencode
    
    url = f"{BASE_URL}{API_ENDPOINTS[endpoint]}"
    if params:
        # URL 인코딩을 사용하여 파라미터 추가
        query_string = urlencode(params)
        url += "?" + query_string
    return url

async def all_info_extract(character_info):
    """
    캐릭터 정보에서 모든 정보를 추출합니다.
    """
    try:
        # 각 API 응답 데이터를 extract 함수들로 처리
        stat_info = await extract_stat(character_info.get('get_character_stat_info', {}))
        item_info = await extract_item_equipment(character_info.get('get_character_item_equipment_info', {}))
        ability_info = await extract_ability(character_info.get('get_character_ability_info', {}))
        link_skill_info = await extract_link_skills(character_info.get('get_character_link_skill_info', {}))
        vmatrix_info = await extract_vmatrix(character_info.get('get_character_vmatrix_info', {}))
        symbol_info = await extract_symbols(character_info.get('get_character_symbol_info', {}))
        
        # 하이퍼 스탯 정보 추출
        hyper_stat_info = await extract_hyper_stat(character_info.get('get_character_hyper_stat_info', {}))
        
        # 펫 장비 정보 추출
        pet_equipment_info = await extract_pet_equipment(character_info.get('get_character_pet_equipment_info', {}))
        
        # 헥사매트릭스 정보 추출
        hexamatrix_info = await extract_hexamatrix(character_info.get('get_character_hexamatrix_info', {}))
        hexamatrix_stat_info = await extract_hexamatrix_stat(character_info.get('get_character_hexamatrix_stat_info', {}))
        
        # 기타 스탯 정보 추출
        other_stat_info = await extract_other_stat(character_info.get('get_character_other_stat_info', {}))
        
        # 인기도 정보 처리 (basic_info에 병합)
        basic_info = character_info.get('get_character_basic_info', {})
        popularity_info = character_info.get('get_character_popularity_info', {})
        if popularity_info and 'popularity' in popularity_info:
            basic_info['character_popularity'] = popularity_info['popularity']
        
        return {
            'basic_info': basic_info,
            'stat_info': stat_info,
            'item_info': item_info,
            'ability_info': ability_info,
            'link_skill_info': link_skill_info,
            'vmatrix_info': vmatrix_info,
            'symbol_info': symbol_info,
            'hyper_stat_info': hyper_stat_info,
            'pet_equipment_info': pet_equipment_info,
            'hexamatrix_info': hexamatrix_info,
            'hexamatrix_stat_info': hexamatrix_stat_info,
            'other_stat_info': other_stat_info
        }
        
    except Exception as e:
        logger.error(f"정보 추출 중 오류 발생: {str(e)}")
        raise

async def get_character_data(character_name, api_key=None):
    """
    캐릭터 이름을 받아 해당 캐릭터의 정보를 반환합니다.
    캐시가 존재하면 캐시에서 데이터를 가져오고, 없으면 API를 호출하여 데이터를 가져옵니다.
    
    Args:
        character_name (str): 캐릭터 이름
        api_key (str, optional): 넥슨 API 키. 없으면 환경변수 사용.
    """
    # 입력 검증
    if not character_name or not character_name.strip():
        return None
    
    # API 키 결정: 인자로 받은 것 우선, 없으면 전역 변수(환경변수) 사용
    final_api_key = api_key if api_key else NEXON_API_KEY
    
    if not final_api_key or not final_api_key.strip():
        logger.error("NEXON_API_KEY가 설정되지 않았습니다.")
        return None
    
    cache_key = f'character_info_{character_name}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    try:
        async with aiohttp.ClientSession() as session:
            # 1. 캐릭터 이름으로 ocid 조회
            character_id_url = get_api_url("get_character_id", character_name=character_name)
            
            # API 키 헤더 설정
            headers = {
                "x-nxopen-api-key": final_api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "MAI-Help-You/1.0"
            }
            
            async with session.get(character_id_url, headers=headers) as response:
                if response.status != 200:
                    return None
                
                character_id_data = await response.json()
                character_id = character_id_data.get('ocid', '')

            if not character_id:
                return None

            # 2. 모든 캐릭터 정보 조회
            character_info = {}
            for endpoint_key, endpoint_path in API_ENDPOINTS.items():
                if endpoint_key == "get_character_id":
                    continue
                    
                url = get_api_url(endpoint_key, ocid=character_id)
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        character_info[endpoint_key] = data
                    elif response.status == 429:
                        # Rate limit 오류 시 대기
                        await asyncio.sleep(1)
                        # 재시도
                        async with session.get(url, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                data = await retry_response.json()
                                character_info[endpoint_key] = data
                            else:
                                character_info[endpoint_key] = {}
                    else:
                        character_info[endpoint_key] = {}
                
                # API 호출 간 지연 시간 추가 (rate limit 방지)
                await asyncio.sleep(0.1)

            # 3. 모든 정보 추출
            extracted_info = await all_info_extract(character_info)

            # 4. 캐시 저장
            cache.set(cache_key, extracted_info, timeout=int(CACHE_DURATION.total_seconds()))
            
            # 5. JSON 파일로 저장
            save_character_data_to_json(character_name, extracted_info)
            
            return extracted_info

    except Exception as e:
        logger.error(f"캐릭터 정보 조회 중 오류 발생: {str(e)}")
        return None


def save_character_data_to_json(character_name, character_data, save_dir="character_data"):
    """
    캐릭터 데이터를 JSON 파일로 저장합니다.
    """
    try:
        # 저장 디렉토리 생성
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        # 파일명 생성 (특수문자 제거)
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        file_path = save_path / filename
        
        # JSON 파일로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"JSON 파일 저장 중 오류 발생: {str(e)}")
        return None


def load_character_data_from_json(character_name, save_dir="character_data"):
    """
    저장된 캐릭터 데이터를 JSON 파일에서 불러옵니다.
    """
    try:
        save_path = Path(save_dir)
        if not save_path.exists():
            return None
        
        # 해당 캐릭터의 가장 최근 파일 찾기
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        pattern = f"{safe_name}_*.json"
        files = list(save_path.glob(pattern))
        
        if not files:
            return None
        
        # 가장 최근 파일 선택
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        
        # JSON 파일 읽기
        with open(latest_file, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
        
        return character_data
        
    except Exception as e:
        logger.error(f"JSON 파일 불러오기 중 오류 발생: {str(e)}")
        return None


async def process_signup_with_key(api_key):
    """
    회원가입 시 API 키를 사용하여 첫 번째 캐릭터 정보를 자동으로 가져와 저장합니다.
    """


    if not api_key or not api_key.strip():
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. 캐릭터 목록 조회
            url = get_api_url("get_account_character_list")
            headers = {
                "x-nxopen-api-key": api_key
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"캐릭터 목록 조회 실패: {response.status}")
                    return None
                    
                data = await response.json()
                account_list = data.get('account_list', [])
                
                if not account_list:
                    return None
                
                # 모든 월드의 캐릭터 리스트 수집
                all_characters = []
                for account in account_list:
                    chars = account.get('character_list', [])
                    all_characters.extend(chars)

                if not all_characters:
                    return None
                
                # 레벨 순으로 정렬 (높은 레벨 우선)
                all_characters.sort(key=lambda x: int(x.get('character_level', 0)), reverse=True)
                
                # 가장 레벨이 높은 캐릭터 선택
                best_character = all_characters[0]
                character_name = best_character.get('character_name')
                character_ocid = best_character.get('ocid')
                
                if not character_name:
                    return None
                    
                # 2. 캐릭터 상세 정보 조회 및 저장
                result = await get_character_data(character_name, api_key)
                
                if result:
                    return character_name, character_ocid
                return None
                
    except Exception as e:
        logger.error(f"회원가입 캐릭터 자동 연동 실패: {str(e)}")
        return None


