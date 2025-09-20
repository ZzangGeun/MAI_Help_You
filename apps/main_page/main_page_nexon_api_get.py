from django.conf import settings
import asyncio
import requests
import aiohttp
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = os.getenv('NEXON_API_KEY')
logger = logging.getLogger(__name__)
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)

#메인 페이지는 공지, 이벤트 목록 가져오기
def get_api_data(endpoint, params=None):
    headers = {'x-nxopen-api-key': NEXON_API_KEY}
    url = f'{BASE_URL}{endpoint}'

    # API 요청에 필요한 파라미터 설정
    if params is None:
        params = {}

    # 날짜 파라미터가 필요한 엔드포인트 목록
    date_required_endpoints = [
        "/ranking/overall"  # 공지 관련 API는 date 파라미터를 사용하지 않습니다.
    ]

    # 해당 엔드포인트에 'date' 파라미터가 없으면 어제 날짜를 추가
    if endpoint in date_required_endpoints and 'date' not in params:
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        params['date'] = yesterday

    try: 
        response = requests.get(url, headers = headers , params=params)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f'API 요청 실패: {url}, 상태 코드: {response.status_code}, 파라미터: {params}, 응답: {response.text}')
            return None
    
    except requests.RequestException as e:
        logger.error(f'API 요청 중 예외 발생: {url}, 오류: {e}')
        return None

def get_notice_list():

    notice_event = get_api_data("/notice-event")
    notice = get_api_data("/notice")
    notice_cashshop = get_api_data("/notice-cashshop")
    notice_update = get_api_data("/notice-update")

    return {
        "notice_event" : notice_event,
        "notice" : notice,
        "notice_cashshop" : notice_cashshop,
        "notice_update" : notice_update
    }


def get_ranking_list():

    overall_ranking = get_api_data("/ranking/overall")
    
    return {
        "overall_ranking" : overall_ranking
    }