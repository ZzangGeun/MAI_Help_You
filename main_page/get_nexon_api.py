from django.conf import settings
import asyncio
import requests

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = settings.NEXON_API_KEY

#메인 페이지는 공지, 이벤트 목록 가져오기


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

async def get_notice_list():

    event_info = await get_api_data("/notice-event")
    notice_info = await get_api_data("/notice")


    return {
        "event_info" : event_info,
        "notice_info" : notice_info
    }