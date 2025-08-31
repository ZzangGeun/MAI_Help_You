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

# 테스트용 함수 - API 데이터 확인
def test_api_data():
    """API 데이터를 콘솔에서 확인하는 테스트 함수"""
    print("=" * 50)
    print("📋 넥슨 API 데이터 테스트")
    print("=" * 50)
    
    # 공지사항 데이터 가져오기
    print("\n🔔 공지사항 데이터:")
    notice_data = get_api_data("/notice")
    if notice_data:
        print(f"✅ 성공! 데이터 타입: {type(notice_data)}")
        print(f"📊 키 목록: {list(notice_data.keys()) if isinstance(notice_data, dict) else '리스트 형태'}")
        
        # 첫 번째 항목 미리보기
        if isinstance(notice_data, dict) and 'notice' in notice_data:
            notices = notice_data['notice']
            if notices and len(notices) > 0:
                print(f"\n📝 첫 번째 공지사항:")
                first_notice = notices[0]
                for key, value in first_notice.items():
                    print(f"   {key}: {value}")
    else:
        print("❌ 공지사항 데이터 가져오기 실패")
    
    # 이벤트 데이터 가져오기
    print("\n🎉 이벤트 데이터:")
    event_data = get_api_data("/notice-event")
    if event_data:
        print(f"✅ 성공! 데이터 타입: {type(event_data)}")
        print(f"📊 키 목록: {list(event_data.keys()) if isinstance(event_data, dict) else '리스트 형태'}")
        
        # 첫 번째 항목 미리보기
        if isinstance(event_data, dict) and 'notice_event' in event_data:
            events = event_data['notice_event']
            if events and len(events) > 0:
                print(f"\n🎪 첫 번째 이벤트:")
                first_event = events[0]
                for key, value in first_event.items():
                    print(f"   {key}: {value}")
    else:
        print("❌ 이벤트 데이터 가져오기 실패")
    
    print("\n" + "=" * 50)

# 직접 실행할 때만 테스트 실행
if __name__ == "__main__":
    test_api_data()