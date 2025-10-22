from django.conf import settings
import asyncio
import requests
import aiohttp
import logging
from datetime import datetime, timedelta



BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = settings.NEXON_API_KEY
logger = logging.getLogger(__name__)
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)

#메인 페이지는 공지, 이벤트 목록 가져오기


def get_api_data(endpoint, params=None):
    headers = {'x-nxopen-api-key': NEXON_API_KEY}
    url = f'{BASE_URL}{endpoint}'

    try: 
        response = requests.get(url, headers = headers , params=params)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'API 요청 실패: {url}, 상태 코드: {response.status_code}')
            return None
    
    except requests.RequestException as e:
        return None

def get_notice_list():

    event_info = get_api_data("/notice-event")
    notice_info = get_api_data("/notice")


    return {
        "event_info" : event_info,
        "notice_info" : notice_info
    }

def get_ranking_info(ranking_type='overall', world_name=None, character_class=None):
    """
    전체 랭킹 정보를 가져옵니다.
    ranking_type: 'overall', 'union' 등
    """
    endpoint = f"/ranking/{ranking_type}"
    params = {
        'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), # 어제 날짜 기준
        'page_size': 10 # 상위 10개만 가져옴
    }
    if world_name:
        params['world_name'] = world_name
    if character_class:
        params['character_class'] = character_class

    data = get_api_data(endpoint, params=params)
    return data['ranking'] if data and 'ranking' in data else []

def get_ocid(character_name):
    """캐릭터 이름으로 ocid를 조회합니다."""
    data = get_api_data("/id", params={'character_name': character_name})
    return data.get('ocid') if data else None

def get_character_full_info(character_name):
    """
    캐릭터 이름으로 모든 관련 정보를 조회하여 통합된 딕셔너리로 반환합니다.
    """
    ocid = get_ocid(character_name)
    if not ocid:
        return None

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    params = {'ocid': ocid, 'date': yesterday}

    # 각 API 엔드포인트에서 데이터 비동기적으로 가져오기 (여기서는 순차적으로 구현)
    basic_info = get_api_data("/character/basic", params)
    stat_info = get_api_data("/character/stat", params)
    union_info = get_api_data("/user/union", params)

    if not basic_info:
        return None

    # 전투력 찾기
    combat_power = 0
    if stat_info and stat_info.get('final_stat'):
        for stat in stat_info['final_stat']:
            if stat['stat_name'] == '전투력':
                combat_power = int(stat['stat_value'])
                break

    # 데이터 통합
    full_info = {
        'name': basic_info.get('character_name'),
        'server': basic_info.get('world_name'),
        'level': basic_info.get('character_level'),
        'job': basic_info.get('character_class'),
        'fame': basic_info.get('fame'),
        'power': combat_power,
        'unionLevel': union_info.get('union_level') if union_info else 0,
    }
    return full_info