from django.conf import settings
import asyncio
import logging
import json
import os
import requests
from datetime import datetime, timedelta
from .api_client import get_api_data
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)

# JSON 파일 저장 경로
NOTICE_JSON_PATH = os.path.join(settings.BASE_DIR, 'character_data', 'notice_data.json')
RANKING_JSON_PATH = os.path.join(settings.BASE_DIR, 'character_data', 'ranking_data.json')

def get_og_image(url):
    """
    URL에서 og:image 메타 태그를 찾아 이미지 URL을 반환합니다.
    """
    try:
        if not url: return None
        response = requests.get(url, timeout=3) # 타임아웃 3초
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image:
                return og_image["content"]
    except Exception as e:
        logger.error(f"이미지 크롤링 실패 ({url}): {e}")
    return None

def get_notice_list():
    """
    공지사항 데이터를 Nexon API에서 가져와서 JSON 파일로 저장하고 반환합니다.
    JSON 파일이 있고 최신이면(1시간 이내) API 호출 없이 파일 내용을 반환합니다.
    """
    # 캐시 확인
    if os.path.exists(NOTICE_JSON_PATH):
        try:
            modified_time = datetime.fromtimestamp(os.path.getmtime(NOTICE_JSON_PATH))
            if datetime.now() - modified_time < CACHE_DURATION:
                data = load_notice_data_from_json()
                if data:
                    logger.info("캐시된 공지사항 데이터를 사용합니다.")
                    return data
        except Exception as e:
            logger.warning(f"캐시 확인 중 오류: {e}")

    # API 호출
    notice_event = get_api_data("/notice-event")
    notice_cashshop = get_api_data("/notice-cashshop")
    notice_update = get_api_data("/notice-update")

    # 이미지 크롤링 (상위 1개만)
    def inject_image(data, key):
        if data and isinstance(data, dict) and key in data:
            items = data[key]
            if isinstance(items, list) and len(items) > 0:
                first_item = items[0]
                if 'url' in first_item:
                    logger.info(f"이미지 크롤링 시도: {first_item['title']}")
                    img_url = get_og_image(first_item['url'])
                    if img_url:
                        first_item['image_url'] = img_url
                        logger.info(f"이미지 크롤링 성공: {img_url}")

    inject_image(notice_event, 'event_notice')
    inject_image(notice_cashshop, 'cashshop_notice')

    notice_data = {
        "notice_event": notice_event,
        "notice_cashshop": notice_cashshop,
        "notice_update": notice_update
    }
    
    # JSON 파일로 저장
    save_notice_data_to_json(notice_data)

    return notice_data


def save_notice_data_to_json(notice_data):
    """
    공지사항 데이터를 JSON 파일로 저장합니다.
    
    Args:
        notice_data (dict): 저장할 공지사항 데이터
    """
    try:
        # character_data 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(NOTICE_JSON_PATH), exist_ok=True)
        
        # JSON 파일로 저장 (한글 지원)
        with open(NOTICE_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(notice_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"공지사항 데이터가 {NOTICE_JSON_PATH}에 저장되었습니다.")
    except Exception as e:
        logger.error(f"공지사항 데이터 저장 중 오류 발생: {e}")


def load_notice_data_from_json():
    """
    JSON 파일에서 공지사항 데이터를 로드합니다.
    
    Returns:
        dict: 로드된 공지사항 데이터, 파일이 없으면 빈 딕셔너리
    """
    try:
        if os.path.exists(NOTICE_JSON_PATH):
            with open(NOTICE_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"공지사항 데이터 로드 중 오류 발생: {e}")
    
    return {}


def save_ranking_data_to_json(ranking_data):
    """
    랭킹 데이터를 JSON 파일로 저장합니다.
    
    Args:
        ranking_data (dict): 저장할 랭킹 데이터
    """
    try:
        # character_data 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(RANKING_JSON_PATH), exist_ok=True)
        
        # JSON 파일로 저장 (한글 지원)
        with open(RANKING_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(ranking_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"랭킹 데이터가 {RANKING_JSON_PATH}에 저장되었습니다.")
    except Exception as e:
        logger.error(f"랭킹 데이터 저장 중 오류 발생: {e}")


def load_ranking_data_from_json():
    """
    JSON 파일에서 랭킹 데이터를 로드합니다.
    
    Returns:
        dict: 로드된 랭킹 데이터, 파일이 없으면 빈 딕셔너리
    """
    try:
        if os.path.exists(RANKING_JSON_PATH):
            with open(RANKING_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"랭킹 데이터 로드 중 오류 발생: {e}")
    
    return {}


def get_ranking_list():
    """
    랭킹 데이터를 Nexon API에서 가져와서 JSON 파일로 저장하고 반환합니다.
    상위 50위까지만 저장합니다.
    """
    overall_ranking = get_api_data("/ranking/overall")
    
    # JSON 구조: overall_ranking -> ranking 배열
    ranking_list = []
    if overall_ranking and isinstance(overall_ranking, dict):
        ranking_list = overall_ranking.get('ranking', [])
    elif isinstance(overall_ranking, list):
        ranking_list = overall_ranking
    
    # 상위 50위까지만 저장
    ranking_list = ranking_list[:50] if ranking_list else []
    
    ranking_data = {
        "overall_ranking": ranking_list
    }
    
    # JSON 파일로 저장
    save_ranking_data_to_json(ranking_data)
    
    return ranking_data


