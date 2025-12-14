# -*- coding: utf-8 -*-
"""
Nexon Service Module

넥슨 API와 통신하여 캐릭터 정보를 조회하고 가공하는 서비스 로직을 담당합니다.
기존 character 앱의 get_character_info.py와 extract.py의 기능을 통합하였습니다.
"""

import sys
import os
import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import aiohttp
from django.conf import settings
from django.core.cache import cache

# 로깅 설정
logger = logging.getLogger(__name__)

# 상수 설정
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간 (1시간)
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


# =============================================================================
# Extraction Helpers (from extract.py)
# =============================================================================

async def extract_stat(stat_info: dict) -> dict:
    """스탯 정보를 추출하여 간소화된 딕셔너리로 반환합니다."""
    final_stat = {}
    for stat in stat_info.get('final_stat', []):
        stat_name = stat['stat_name'].replace(" ", "_")
        final_stat[stat_name] = stat['stat_value']
    return final_stat


async def extract_item_equipment(item_equipment_info: dict) -> dict:
    """장비 아이템 정보를 추출하여 정리합니다."""
    if not isinstance(item_equipment_info, dict):
        return _get_empty_equipment_data()
    
    def process_equipment_list(equipment_list):
        """장비 리스트를 처리하는 헬퍼 함수"""
        processed_equipment = {}
        for item in equipment_list:
            slot = item.get("item_equipment_slot", item.get("equipment_slot", "none"))
            processed_equipment[slot] = {
                "part": item.get("item_equipment_part", "none"),
                "slot": slot,
                "name": item.get("item_name", "none"),
                "icon": item.get("item_icon", "none"),
                "description": item.get("item_description", "none"),
                "shape_name": item.get("item_shape_name", "none"),
                "shape_icon": item.get("item_shape_icon", "none"),
                "gender": item.get("item_gender", "none"),
                "total_option": item.get("item_total_option", {}),
                "base_option": item.get("item_base_option", {}),
                "potential_option_flag": item.get("potential_option_flag", "none"),
                "additional_potential_option_flag": item.get("additional_potential_option_flag", "none"),
                "potential_option_grade": item.get("potential_option_grade", "none"),
                "additional_potential_option_grade": item.get("additional_potential_option_grade", "none"),
                "potential_options": [
                    item.get("potential_option_1", "none"),
                    item.get("potential_option_2", "none"),
                    item.get("potential_option_3", "none")
                ],
                "additional_potential_options": [
                    item.get("additional_potential_option_1", "none"),
                    item.get("additional_potential_option_2", "none"),
                    item.get("additional_potential_option_3", "none")
                ],
                "equipment_level_increase": item.get("equipment_level_increase", 0),
                "item_exceptional_option": item.get("item_exceptional_option", {}),
                "add_option": item.get("item_add_option", {}),
                "growth_exp": item.get("growth_exp", 0),
                "growth_level": item.get("growth_level", 0),
                "scroll_upgrade": item.get("scroll_upgrade", "none"),
                "cuttable_count": item.get("cuttable_count", "none"),
                "golden_hammer_flag": item.get("golden_hammer_flag", "none"),
                "scroll_resilience_count": item.get("scroll_resilience_count", "none"),
                "scroll_upgradable_count": item.get("scroll_upgradable_count", "none"),
                "soul_name": item.get("soul_name", "none"),
                "soul_option": item.get("soul_option", "none"),
                "item_etc_option": item.get("item_etc_option", {}),
                "starforce": item.get("starforce", "none"),
                "starforce_scroll_flag": item.get("starforce_scroll_flag", "none"),
                "item_starforce_option": item.get("item_starforce_option", {}),
                "special_ring_level": item.get("special_ring_level", 0),
                "date_expire": item.get("date_expire", "none"),
                "freestyle_flag": item.get("freestyle_flag", "none")
            }
        return processed_equipment
    
    # 기본 장비 정보 처리
    return {
        "date": item_equipment_info.get("date", "정보 없음"),
        "character_gender": item_equipment_info.get("character_gender", "정보 없음"),
        "character_class": item_equipment_info.get("character_class", "정보 없음"),
        "preset_no": item_equipment_info.get("preset_no", 0),
        "item_equipment": process_equipment_list(item_equipment_info.get("item_equipment", [])),
        "item_equipment_preset_1": process_equipment_list(item_equipment_info.get("item_equipment_preset_1", [])),
        "item_equipment_preset_2": process_equipment_list(item_equipment_info.get("item_equipment_preset_2", [])),
        "item_equipment_preset_3": process_equipment_list(item_equipment_info.get("item_equipment_preset_3", [])),
        "title": item_equipment_info.get("title", {}),
        "medal_shape": item_equipment_info.get("medal_shape", {}),
        "dragon_equipment": process_equipment_list(item_equipment_info.get("dragon_equipment", [])),
        "mechanic_equipment": process_equipment_list(item_equipment_info.get("mechanic_equipment", []))
    }


def _get_empty_equipment_data():
    """빈 장비 데이터 반환"""
    return {
        "date": "정보 없음",
        "character_gender": "정보 없음",
        "character_class": "정보 없음",
        "preset_no": 0,
        "item_equipment": {},
        "item_equipment_preset_1": {},
        "item_equipment_preset_2": {},
        "item_equipment_preset_3": {},
        "title": {},
        "medal_shape": {},
        "dragon_equipment": [],
        "mechanic_equipment": []
    }


async def extract_ability(ability_info: dict) -> dict:
    """어빌리티 정보를 추출합니다."""
    if not isinstance(ability_info, dict):
        return {}
    
    extracted_ability = {}
    for preset_key, preset_value in ability_info.items():
        if preset_key.startswith('ability_preset_'):
            preset_number = preset_key.split('_')[-1]
            
            preset_data = {
                "description": preset_value.get("description", "정보 없음"),
                "grade": preset_value.get("ability_preset_grade", "정보 없음"),
                "abilities": []
            }

            for ability in preset_value.get("ability_info", []):
                ability_data = {
                    "no": ability.get("ability_no", "정보 없음"),
                    "grade": ability.get("ability_grade", "정보 없음"),
                    "value": ability.get("ability_value", "정보 없음")
                }
                preset_data["abilities"].append(ability_data)

            extracted_ability[f"preset_{preset_number}"] = preset_data

    return extracted_ability


async def extract_link_skills(link_skill_info: dict) -> dict:
    """링크 스킬 정보를 추출합니다."""
    if not isinstance(link_skill_info, dict):
        return {}

    extracted_skills = {}
    for preset_key, skills in link_skill_info.items():
        if preset_key.startswith('character_link_skill_preset_'):
            preset_number = preset_key.split('_')[-1]
            extracted_skills[f'preset_{preset_number}'] = []
            
            if skills and isinstance(skills, list):
                for skill in skills:
                    skill_data = {
                        "name": skill.get("skill_name", "정보 없음"),
                        "description": skill.get("skill_description", "정보 없음"),
                        "level": skill.get("skill_level", 0),
                        "effect": skill.get("skill_effect", "정보 없음"),
                        "icon": skill.get("skill_icon", "정보 없음")
                    }
                    extracted_skills[f'preset_{preset_number}'].append(skill_data)
    
    return extracted_skills


async def extract_vmatrix(vmatrix_info: dict) -> dict:
    """V매트릭스 정보를 추출합니다."""
    try:
        if not isinstance(vmatrix_info, dict):
            return {"error": "Invalid Data", "cores": []}

        return {
            "date": vmatrix_info.get("date", "정보 없음"),
            "character_class": vmatrix_info.get("character_class", "정보 없음"),
            "cores": [
                {
                    "slot_id": core.get("slot_id", "정보 없음"),
                    "slot_level": int(core.get("slot_level", 0)),
                    "core_name": core.get("v_core_name", "정보 없음"),
                    "core_type": core.get("v_core_type", "정보 없음"),
                    "core_level": int(core.get("v_core_level", 0)),
                    "skill_1": core.get("v_core_skill_1", "정보 없음"),
                    "skill_2": core.get("v_core_skill_2", "정보 없음"),
                    "skill_3": core.get("v_core_skill_3", "정보 없음")
                }
                for core in (vmatrix_info.get("character_v_core_equipment") or [])
            ],
            "remain_points": int(vmatrix_info.get("character_v_matrix_remain_slot_upgrade_point", 0))
        }

    except Exception as e:
        logger.error(f"V매트릭스 정보 처리 중 오류: {e}")
        return {"error": str(e), "cores": []}


async def extract_symbols(symbol_equipment_info: dict) -> dict:
    """심볼 정보를 추출합니다."""
    if not isinstance(symbol_equipment_info, dict):
        return {}

    symbol_data = {
        "date": symbol_equipment_info.get("date", "정보 없음"),
        "character_class": symbol_equipment_info.get("character_class", "정보 없음"),
        "symbol": []
    }

    for symbol in (symbol_equipment_info.get("symbol") or []):
        symbol_data["symbol"].append({
            "symbol_name": symbol.get("symbol_name", "정보 없음"),
            "symbol_icon": symbol.get("symbol_icon", "정보 없음"),
            "symbol_description": symbol.get("symbol_description", "정보 없음"),
            "symbol_force": symbol.get("symbol_force", "정보 없음"),
            "symbol_level": symbol.get("symbol_level", 0),
            "symbol_str": symbol.get("symbol_str", "정보 없음"),
            "symbol_dex": symbol.get("symbol_dex", "정보 없음"),
            "symbol_int": symbol.get("symbol_int", "정보 없음"),
            "symbol_luk": symbol.get("symbol_luk", "정보 없음"),
            "symbol_hp": symbol.get("symbol_hp", "정보 없음"),
            "symbol_drop_rate": symbol.get("symbol_drop_rate", "정보 없음"),
            "symbol_meso_rate": symbol.get("symbol_meso_rate", "정보 없음"),
            "symbol_exp_rate": symbol.get("symbol_exp_rate", "정보 없음"),
            "symbol_growth_count": symbol.get("symbol_growth_count", 0),
            "symbol_require_growth_count": symbol.get("symbol_require_growth_count", 0)
        })

    return symbol_data


async def extract_hyper_stat(hyper_stat_info: dict) -> dict:
    """하이퍼 스탯 정보를 추출합니다."""
    if not isinstance(hyper_stat_info, dict):
        return {}

    hyper_stat_data = {
        "date": hyper_stat_info.get("date", "정보 없음"),
        "character_class": hyper_stat_info.get("character_class", "정보 없음"),
        "use_preset_no": hyper_stat_info.get("use_preset_no", "정보 없음"),
        "use_available_hyper_stat": hyper_stat_info.get("use_available_hyper_stat", 0),
        "presets": {}
    }

    for preset_num in range(1, 4):
        preset_key = f"hyper_stat_preset_{preset_num}"
        remain_point_key = f"hyper_stat_preset_{preset_num}_remain_point"
        
        if preset_key in hyper_stat_info:
            preset_data = {
                "preset_number": preset_num,
                "remain_point": hyper_stat_info.get(remain_point_key, 0),
                "stats": []
            }
            
            for stat in (hyper_stat_info.get(preset_key) or []):
                stat_data = {
                    "stat_type": stat.get("stat_type", "정보 없음"),
                    "stat_point": stat.get("stat_point", 0),
                    "stat_level": stat.get("stat_level", 0),
                    "stat_increase": stat.get("stat_increase", "정보 없음")
                }
                preset_data["stats"].append(stat_data)
            
            hyper_stat_data["presets"][f"preset_{preset_num}"] = preset_data

    return hyper_stat_data


async def extract_hexamatrix(hexamatrix_info: dict) -> dict:
    """헥사매트릭스 정보를 추출합니다."""
    if not isinstance(hexamatrix_info, dict):
        return {"hexamatrix": []}
    
    hexamatrix_data = {
        "date": hexamatrix_info.get("date", "정보 없음"),
        "hexamatrix": []
    }
    
    # 코어 장비 정보 처리 (extract.py의 extract_hexamatrix과 일부 로직 병합)
    # 기존 코드의 extract_hexamatrix 함수와 extract.py의 269라인 함수가 이름이 같지만 내용은 다름.
    # 여기서는 좀 더 상세한 정보를 담고 있는 버전을 우선합니다.
    
    # 1. 헥사매트릭스 설정 정보 (hexamatrix 리스트)
    for hexa in hexamatrix_info.get("hexamatrix", []):
         # 데이터 구조가 다를 수 있으므로 안전하게 처리
         if isinstance(hexa, dict):
            hexa_data = {
                "slot_id": hexa.get("slot_id", "정보 없음"),
                "slot_level": hexa.get("slot_level", 0),
                "main_stat_name": hexa.get("main_stat_name", "정보 없음"),
                "main_stat_level": hexa.get("main_stat_level", 0),
                # 필요한 다른 필드들...
            }
            hexamatrix_data["hexamatrix"].append(hexa_data)
            
    # 2. 헥사 코어 장비 (extract.py 269라인 참조)
    if hexamatrix_info.get("chracter_hexa_core_equipment"):
        for core in (hexamatrix_info.get("chracter_hexa_core_equipment") or []):
             # 필요한 로직 병합
             pass

    return hexamatrix_data


async def extract_hexamatrix_stat(hexamatrix_stat_info: dict) -> dict:
    """헥사 스탯 정보를 추출합니다."""
    if not isinstance(hexamatrix_stat_info, dict):
        return {}

    hexamatrix_stat_data = {
        "date": hexamatrix_stat_info.get("date", "정보 없음"),
        "hexamatrix_stat_1": [],
        "hexamatrix_stat_2": [],
        "hexamatrix_stat_3": []
    }
    
    # Helper for extracting stat lists
    def _extract_stats(source_list):
        result = []
        for stat in (source_list or []):
            result.append({
                "slot_id": stat.get("slot_id", "정보 없음"),
                "main_stat_name": stat.get("main_stat_name", "정보 없음"),
                "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
                "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
                "main_stat_level": int(stat.get("main_stat_level", 0)),
                "sub_stat_level_1": int(stat.get("sub_stat_level_1", 0)),
                "sub_stat_level_2": int(stat.get("sub_stat_level_2", 0)),
                "stat_grade": int(stat.get("stat_grade", 0))
            })
        return result

    hexamatrix_stat_data["hexamatrix_stat_1"] = _extract_stats(hexamatrix_stat_info.get("character_hexa_stat_core"))
    hexamatrix_stat_data["hexamatrix_stat_2"] = _extract_stats(hexamatrix_stat_info.get("character_hexa_stat_core_2"))
    hexamatrix_stat_data["hexamatrix_stat_3"] = _extract_stats(hexamatrix_stat_info.get("character_hexa_stat_core_3"))
    
    return hexamatrix_stat_data


async def extract_other_stat(other_stat_info: dict) -> dict:
    """기타 스탯 정보를 추출합니다."""
    if not isinstance(other_stat_info, dict):
        return {}
    
    other_stat_data = {
        "date": other_stat_info.get("date", "정보 없음"),
        "other_stat": []
    }
    
    for stat in (other_stat_info.get("other_stat") or []):
        entry = {
            "other_stat_type": stat.get("other_stat_type", "정보 없음"),
            "stat_info": []
        }
        for stat_info in (stat.get("stat_info") or []):
            entry["stat_info"].append({
                "stat_name": stat_info.get("stat_name", "정보 없음"),
                "stat_value": stat_info.get("stat_value", "정보 없음")
            })
        other_stat_data["other_stat"].append(entry)
        
    return other_stat_data


async def extract_pet_equipment(pet_equipment_info: dict) -> dict:
    """펫 장비 정보를 추출합니다."""
    if not isinstance(pet_equipment_info, dict):
        return {}

    pet_equipment_data = {
        "date": pet_equipment_info.get("date", "정보 없음"),
        "pets": []
    }

    for pet_num in range(1, 4):
        pet_key_prefix = f"pet_{pet_num}"
        if f"{pet_key_prefix}_name" in pet_equipment_info:
            pet_data = {
                "pet_number": pet_num,
                "name": pet_equipment_info.get(f"{pet_key_prefix}_name", "정보 없음"),
                "nickname": pet_equipment_info.get(f"{pet_key_prefix}_nickname", "정보 없음"),
                "icon": pet_equipment_info.get(f"{pet_key_prefix}_icon", "정보 없음"),
                "description": pet_equipment_info.get(f"{pet_key_prefix}_description", "정보 없음"),
                "pet_type": pet_equipment_info.get(f"{pet_key_prefix}_pet_type", "정보 없음"),
                "date_expire": pet_equipment_info.get(f"{pet_key_prefix}_date_expire", "정보 없음"),
                "appearance": pet_equipment_info.get(f"{pet_key_prefix}_appearance", "정보 없음"),
                "appearance_icon": pet_equipment_info.get(f"{pet_key_prefix}_appearance_icon", "정보 없음"),
                "skills": pet_equipment_info.get(f"{pet_key_prefix}_skill", []),
                "equipment": {},
                "auto_skill": {}
            }

            # 장비
            equipment_key = f"{pet_key_prefix}_equipment"
            if equipment_key in pet_equipment_info and pet_equipment_info[equipment_key]:
                equipment = pet_equipment_info[equipment_key]
                pet_data["equipment"] = {
                    "item_name": equipment.get("item_name", "정보 없음"),
                    "item_icon": equipment.get("item_icon", "정보 없음"),
                    "item_description": equipment.get("item_description", "정보 없음"),
                    "scroll_upgrade": equipment.get("scroll_upgrade", 0),
                    "scroll_upgradable": equipment.get("scroll_upgradable", 0),
                    "item_shape": equipment.get("item_shape", "정보 없음"),
                    "item_shape_icon": equipment.get("item_shape_icon", "정보 없음"),
                    "item_option": []
                }
                for option in equipment.get("item_option", []):
                    pet_data["equipment"]["item_option"].append({
                        "option_type": option.get("option_type", "정보 없음"),
                        "option_value": option.get("option_value", "정보 없음")
                    })

            # 자동 스킬
            auto_skill_key = f"{pet_key_prefix}_auto_skill"
            if auto_skill_key in pet_equipment_info and pet_equipment_info[auto_skill_key]:
                auto_skill = pet_equipment_info[auto_skill_key]
                pet_data["auto_skill"] = {
                    "skill_1": auto_skill.get("skill_1", "정보 없음"),
                    "skill_1_icon": auto_skill.get("skill_1_icon", "정보 없음"),
                    "skill_2": auto_skill.get("skill_2", "정보 없음"),
                    "skill_2_icon": auto_skill.get("skill_2_icon", "정보 없음")
                }

            pet_equipment_data["pets"].append(pet_data)

    return pet_equipment_data


# =============================================================================
# Main Service Logic
# =============================================================================

def get_api_url(endpoint, **params):
    """API 엔드포인트 URL을 생성합니다."""
    url = f"{BASE_URL}{API_ENDPOINTS[endpoint]}"
    if params:
        query_string = urlencode(params)
        url += "?" + query_string
    return url


async def all_info_extract(character_info: dict) -> dict:
    """캐릭터 정보 딕셔너리에서 필요한 모든 세부 정보를 추출하여 종합합니다."""
    try:
        stat_info = await extract_stat(character_info.get('get_character_stat_info', {}))
        item_info = await extract_item_equipment(character_info.get('get_character_item_equipment_info', {}))
        ability_info = await extract_ability(character_info.get('get_character_ability_info', {}))
        link_skill_info = await extract_link_skills(character_info.get('get_character_link_skill_info', {}))
        vmatrix_info = await extract_vmatrix(character_info.get('get_character_vmatrix_info', {}))
        symbol_info = await extract_symbols(character_info.get('get_character_symbol_info', {}))
        hyper_stat_info = await extract_hyper_stat(character_info.get('get_character_hyper_stat_info', {}))
        pet_equipment_info = await extract_pet_equipment(character_info.get('get_character_pet_equipment_info', {}))
        hexamatrix_info = await extract_hexamatrix(character_info.get('get_character_hexamatrix_info', {}))
        hexamatrix_stat_info = await extract_hexamatrix_stat(character_info.get('get_character_hexamatrix_stat_info', {}))
        other_stat_info = await extract_other_stat(character_info.get('get_character_other_stat_info', {}))
        
        # 기본 정보에 인기도 추가
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


def save_character_data_to_json(character_name: str, character_data: dict, save_dir: str = "character_data"):
    """캐릭터 데이터를 JSON 파일로 저장합니다."""
    try:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        file_path = save_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"JSON 파일 저장 중 오류 발생: {str(e)}")
        return None


async def get_character_data(character_name: str, api_key: str = None) -> dict:
    """
    캐릭터 이름을 받아 해당 캐릭터의 종합 정보를 반환합니다.
    캐시 -> API 조회 순으로 동작하며, 조회 성공 시 JSON 파일로도 저장합니다.
    """
    if not character_name or not character_name.strip():
        return None
    
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
            # 1. OCID 조회
            character_id_url = get_api_url("get_character_id", character_name=character_name)
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

            # 2. 상세 정보 병렬 조회 (개선 가능하지만 안정성을 위해 순차 혹은 기존 로직 유지)
            character_info = {}
            for endpoint_key, endpoint_path in API_ENDPOINTS.items():
                if endpoint_key == "get_character_id":
                    continue
                    
                url = get_api_url(endpoint_key, ocid=character_id)
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        character_info[endpoint_key] = await response.json()
                    elif response.status == 429:
                        await asyncio.sleep(1) # Rate limit
                        async with session.get(url, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                character_info[endpoint_key] = await retry_response.json()
                            else:
                                character_info[endpoint_key] = {}
                    else:
                        character_info[endpoint_key] = {}
                
                await asyncio.sleep(0.05) # 약간의 딜레이

            # 3. 데이터 추출 및 종합
            extracted_info = await all_info_extract(character_info)

            # 4. 저장 (캐시 & 파일)
            cache.set(cache_key, extracted_info, timeout=int(CACHE_DURATION.total_seconds()))
            save_character_data_to_json(character_name, extracted_info)
            
            return extracted_info

    except Exception as e:
        logger.error(f"캐릭터 정보 조회 중 오류 발생: {str(e)}")
        return None


async def process_signup_with_key(api_key: str):
    """
    API 키를 사용하여 계정 내 가장 레벨이 높은 캐릭터를 찾아 반환합니다.
    회원가입 자동 연동 시 사용됩니다.
    Returns: (character_name, character_ocid) or None
    """
    if not api_key or not api_key.strip():
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            url = get_api_url("get_account_character_list")
            headers = {"x-nxopen-api-key": api_key}
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"캐릭터 목록 조회 실패: {response.status}")
                    return None
                    
                data = await response.json()
                account_list = data.get('account_list', [])
                
                if not account_list:
                    return None
                
                # 전체 월드 캐릭터 수집
                all_characters = []
                for account in account_list:
                    all_characters.extend(account.get('character_list', []))

                if not all_characters:
                    return None
                
                # 레벨 내림차순 정렬
                all_characters.sort(key=lambda x: int(x.get('character_level', 0)), reverse=True)
                
                best_character = all_characters[0]
                character_name = best_character.get('character_name')
                character_ocid = best_character.get('ocid')
                
                if not character_name:
                    return None
                    
                # 상세 정보 조회 (유효성 검증 겸 데이터 확보)
                result = await get_character_data(character_name, api_key)
                
                if result:
                    return character_name, character_ocid
                return None
                
    except Exception as e:
        logger.error(f"회원가입 캐릭터 자동 연동 실패: {str(e)}")
        return None
