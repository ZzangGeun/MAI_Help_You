from django.conf import settings
import asyncio
import logging
import json
import os
from datetime import timedelta
from .api_client import get_api_data

logger = logging.getLogger(__name__)
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 설정 (1시간)

# JSON 파일 저장 경로
NOTICE_JSON_PATH = os.path.join(settings.BASE_DIR, 'character_data', 'notice_data.json')
RANKING_JSON_PATH = os.path.join(settings.BASE_DIR, 'character_data', 'ranking_data.json')

def get_notice_list():
    """
    공지사항 데이터를 Nexon API에서 가져와서 JSON 파일로 저장하고 반환합니다.
    """
    notice_event = get_api_data("/notice-event")
    notice_cashshop = get_api_data("/notice-cashshop")
    notice_update = get_api_data("/notice-update")

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


