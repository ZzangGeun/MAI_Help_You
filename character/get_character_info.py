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
        logger.info("=== 정보 추출 시작 ===")
        
        # 각 API 응답 데이터를 extract 함수들로 처리
        logger.info("스탯 정보 추출 중...")
        stat_info = await extract_stat(character_info.get('get_character_stat_info', {}))
        logger.info(f"스탯 정보 추출 완료: {type(stat_info)}")
        
        logger.info("장비 정보 추출 중...")
        item_info = await extract_item_equipment(character_info.get('get_character_item_equipment_info', {}))
        logger.info(f"장비 정보 추출 완료: {type(item_info)}")
        
        logger.info("어빌리티 정보 추출 중...")
        ability_info = await extract_ability(character_info.get('get_character_ability_info', {}))
        logger.info(f"어빌리티 정보 추출 완료: {type(ability_info)}")
        
        logger.info("링크 스킬 정보 추출 중...")
        link_skill_info = await extract_link_skills(character_info.get('get_character_link_skill_info', {}))
        logger.info(f"링크 스킬 정보 추출 완료: {type(link_skill_info)}")
        
        logger.info("V매트릭스 정보 추출 중...")
        vmatrix_info = await extract_vmatrix(character_info.get('get_character_vmatrix_info', {}))
        logger.info(f"V매트릭스 정보 추출 완료: {type(vmatrix_info)}")
        
        logger.info("심볼 정보 추출 중...")
        symbol_info = await extract_symbols(character_info.get('get_character_symbol_info', {}))
        logger.info(f"심볼 정보 추출 완료: {type(symbol_info)}")
        
        # 하이퍼 스탯 정보 추출
        logger.info("하이퍼 스탯 정보 추출 중...")
        hyper_stat_info = await extract_hyper_stat(character_info.get('get_character_hyper_stat_info', {}))
        logger.info(f"하이퍼 스탯 정보 추출 완료: {type(hyper_stat_info)}")
        
        # 펫 장비 정보 추출
        logger.info("펫 장비 정보 추출 중...")
        pet_equipment_info = await extract_pet_equipment(character_info.get('get_character_pet_equipment_info', {}))
        logger.info(f"펫 장비 정보 추출 완료: {type(pet_equipment_info)}")
        
        # 헥사매트릭스 정보 추출
        logger.info("헥사매트릭스 정보 추출 중...")
        hexamatrix_info = await extract_hexamatrix(character_info.get('get_character_hexamatrix_info', {}))
        logger.info(f"헥사매트릭스 정보 추출 완료: {type(hexamatrix_info)}")
        
        logger.info("헥사매트릭스 스탯 정보 추출 중...")
        hexamatrix_stat_info = await extract_hexamatrix_stat(character_info.get('get_character_hexamatrix_stat_info', {}))
        logger.info(f"헥사매트릭스 스탯 정보 추출 완료: {type(hexamatrix_stat_info)}")
        
        # 기타 스탯 정보 추출
        logger.info("기타 스탯 정보 추출 중...")
        other_stat_info = await extract_other_stat(character_info.get('get_character_other_stat_info', {}))
        logger.info(f"기타 스탯 정보 추출 완료: {type(other_stat_info)}")
        
        logger.info("=== 모든 정보 추출 완료 ===")
        
        return {
            'basic_info': character_info.get('get_character_basic_info', {}),
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
        logger.error(f"오류 타입: {type(e)}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        raise

async def get_character_data(character_name):
    """
    캐릭터 이름을 받아 해당 캐릭터의 정보를 반환합니다.
    캐시가 존재하면 캐시에서 데이터를 가져오고, 없으면 API를 호출하여 데이터를 가져옵니다.
    """
    # 입력 검증
    if not character_name or not character_name.strip():
        logger.error("캐릭터 이름이 비어있습니다.")
        return None
    
    if not NEXON_API_KEY or not NEXON_API_KEY.strip():
        logger.error("NEXON_API_KEY가 설정되지 않았습니다.")
        return None
    
    cache_key = f'character_info_{character_name}'
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.info(f"캐시에서 캐릭터 정보를 가져왔습니다: {character_name}")
        return cached_data

    try:
        async with aiohttp.ClientSession() as session:
            # 1. 캐릭터 이름으로 ocid 조회
            # GET /maplestory/v1/id?character_name={character_name}
            # 응답: {"ocid": "string"}
            character_id_url = get_api_url("get_character_id", character_name=character_name)
            
            # API 키 헤더 설정 (x-nxopen-api-key는 헤더에)
            headers = {
                "x-nxopen-api-key": NEXON_API_KEY.strip(),
                "Content-Type": "application/json",
                "User-Agent": "MAI-Help-You/1.0"
            }
            
            logger.info(f"캐릭터 ID 조회 URL: {character_id_url}")
            logger.info(f"API 키 (헤더): {NEXON_API_KEY.strip()[:10]}...")
            logger.info(f"캐릭터명 (쿼리): {character_name.strip()}")
            logger.info(f"요청 헤더: {headers}")
            
            # 파라미터 검증 로그
            logger.info(f"파라미터 검증:")
            logger.info(f"  - character_name: '{character_name.strip()}' (길이: {len(character_name.strip())})")
            logger.info(f"  - api_key: '{NEXON_API_KEY.strip()[:10]}...' (길이: {len(NEXON_API_KEY.strip())})")
            logger.info(f"  - URL: {character_id_url}")
            logger.info(f"  - Headers: {headers}")
            
            # 실제 요청 내용 확인
            logger.info(f"실제 요청 내용:")
            logger.info(f"  - Method: GET")
            logger.info(f"  - URL: {character_id_url}")
            logger.info(f"  - Headers: {headers}")
            logger.info(f"  - character_name 파라미터: {character_name.strip()}")
            
            async with session.get(character_id_url, headers=headers) as response:
                logger.info(f"응답 상태: {response.status}")
                logger.info(f"응답 헤더: {dict(response.headers)}")
                
                if response.status != 200:
                    # 상세 오류 정보 출력
                    try:
                        error_data = await response.json()
                        logger.error(f"캐릭터 ID 조회 실패: {response.status} - {error_data}")
                        
                        # 응답 본문도 로깅
                        response_text = await response.text()
                        logger.error(f"응답 본문: {response_text}")
                        
                    except Exception as e:
                        error_text = await response.text()
                        logger.error(f"캐릭터 ID 조회 실패: {response.status} - {error_text}")
                        logger.error(f"JSON 파싱 오류: {str(e)}")
                    return None
                
                # {"ocid": "string"} 형태의 응답에서 ocid 추출
                character_id_data = await response.json()
                character_id = character_id_data.get('ocid', '')
                logger.info(f"캐릭터 ID 조회 성공: {character_id}")

            if not character_id:
                logger.error(f"캐릭터 ID를 찾을 수 없습니다: {character_name}")
                return None

            # 2. 모든 캐릭터 정보 조회
            character_info = {}
            for endpoint_key, endpoint_path in API_ENDPOINTS.items():
                if endpoint_key == "get_character_id":
                    continue
                    
                url = get_api_url(endpoint_key, ocid=character_id)
                logger.info(f"{endpoint_key} 조회 URL: {url}")
                
                async with session.get(url, headers=headers) as response:
                    logger.info(f"{endpoint_key} 응답 상태: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        character_info[endpoint_key] = data
                        logger.info(f"{endpoint_key} 정보 조회 성공")
                    elif response.status == 429:
                        # Rate limit 오류 시 대기
                        logger.warning(f"{endpoint_key} Rate limit 도달, 1초 대기 후 재시도")
                        await asyncio.sleep(1)
                        # 재시도
                        async with session.get(url, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                data = await retry_response.json()
                                character_info[endpoint_key] = data
                                logger.info(f"{endpoint_key} 재시도 성공")
                            else:
                                logger.warning(f"{endpoint_key} 재시도 실패: {retry_response.status}")
                                character_info[endpoint_key] = {}
                    else:
                        try:
                            error_data = await response.json()
                            logger.warning(f"{endpoint_key} 정보 조회 실패: {response.status} - {error_data}")
                        except:
                            error_text = await response.text()
                            logger.warning(f"{endpoint_key} 정보 조회 실패: {response.status} - {error_text}")
                        character_info[endpoint_key] = {}
                
                # API 호출 간 지연 시간 추가 (rate limit 방지)
                await asyncio.sleep(0.1)

            # 3. 모든 정보 추출
            extracted_info = await all_info_extract(character_info)

            # 4. 캐시 저장
            cache.set(cache_key, extracted_info, timeout=int(CACHE_DURATION.total_seconds()))
            logger.info(f"캐릭터 정보를 캐시에 저장했습니다: {character_name}")
            
            # 5. JSON 파일로 저장
            save_character_data_to_json(character_name, extracted_info)
            
            return extracted_info

    except Exception as e:
        logger.error(f"캐릭터 정보 조회 중 오류 발생: {str(e)}")
        return None


def save_character_data_to_json(character_name, character_data, save_dir="character_data"):
    """
    캐릭터 데이터를 JSON 파일로 저장합니다.
    
    Args:
        character_name (str): 캐릭터 이름
        character_data (dict): 저장할 캐릭터 데이터
        save_dir (str): 저장할 디렉토리명
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
        
        logger.info(f"캐릭터 데이터를 JSON 파일로 저장했습니다: {file_path}")
        print(f"📁 캐릭터 데이터가 저장되었습니다: {file_path}")
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"JSON 파일 저장 중 오류 발생: {str(e)}")
        print(f"❌ JSON 파일 저장 실패: {str(e)}")
        return None


def load_character_data_from_json(character_name, save_dir="character_data"):
    """
    저장된 캐릭터 데이터를 JSON 파일에서 불러옵니다.
    
    Args:
        character_name (str): 캐릭터 이름
        save_dir (str): 저장된 디렉토리명
    
    Returns:
        dict: 캐릭터 데이터 또는 None
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
        
        logger.info(f"캐릭터 데이터를 JSON 파일에서 불러왔습니다: {latest_file}")
        print(f"📂 캐릭터 데이터를 불러왔습니다: {latest_file}")
        
        return character_data
        
    except Exception as e:
        logger.error(f"JSON 파일 불러오기 중 오류 발생: {str(e)}")
        print(f"❌ JSON 파일 불러오기 실패: {str(e)}")
        return None


