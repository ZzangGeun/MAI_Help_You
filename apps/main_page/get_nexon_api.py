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