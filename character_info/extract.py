
# 스탯 추출 함수
async def extract_stat(stat_info):
    final_stat = {}
    for stat in stat_info.get('final_stat', []):
        stat_name = stat['stat_name'].replace(" ","_")
        final_stat[stat_name] = stat['stat_value']

    return final_stat

async def extract_item_equipment(item_equipment_info):
    if not isinstance(item_equipment_info, dict) or 'item_equipment' not in item_equipment_info:
        return {}
    
    # 프리셋 구조 나누기
    equipment_data = {
        "preset_no" : item_equipment_info.get("preset_no", "none"),
        "item_equipment" : {}
    }

    for item in item_equipment_info.get("item_equipment", []):

        slot = item.get("item_equipment_slot", "none")

        equipment_data["item_equipment"][slot] = {
            "part" : item.get("item_equipment_part" , "none"),
            "slot" : slot,
            "name" : item.get("item_name" , "none"),
            "icon" : item.get("item_icon" , "none"),
            "shape_name" : item.get("item_shape_name" , "none"),
            "shape_icon" : item.get("item_shape_icon" , "none"),
            "total_option" : item.get("item_total_option" , {}),
            "base_option" : item.get("item_base_option" , {}),
            "potential_option_grade" : item.get("potential_option_grade" , "none"),
            "additional_potential_option_grade" : item.get("additional_potential_option_grade" , "none"),
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

            "item_exceptional_option" : item.get("item_exceptional_option",{}),
            "add_option": item.get("item_add_option", {}),
            "starforce": item.get("starforce", "0"),
            "starforce_scroll_flag": item.get("starforce_scroll_flag", "정보 없음"),
            "scroll_upgrade": item.get("scroll_upgrade", "0"),
            "scroll_upgradeable_count": item.get("scroll_upgradeable_count", "0"),
            "cuttable_count": item.get("cuttable_count", "0"),
            "golden_hammer_flag": item.get("golden_hammer_flag", "정보 없음"),
            "scroll_resilience_count": item.get("scroll_resilience_count", "0"),
            "soul_name": item.get("soul_name", "정보 없음"),
            "soul_option": item.get("soul_option", "정보 없음"),
            "item_etc_option": item.get("item_etc_option", {}),
            "item_starforce_option": item.get("item_starforce_option", {})
        }

        return equipment_data

async def extract_ability(abiliyty_info):
    if not isinstance(abiliyty_info, dict):
        return {}
    
    extracted_ability = {}
    for preset_key, preset_value in abiliyty_info.items():
        if preset_key.startswith('ability_preset_'):
            preset_number = preset_key.split('_')[-1]

        
            preset_data = {
                "description": preset_value.get("description", "정보 없음"),
                "grade": preset_value.get("ability_preset_grade", "정보 없음"),
                "abilities": []
            }

            # 어빌리티 상세 정보를 abilities 리스트에 추가
            for ability in preset_value.get("ability_info", []):
                ability_data = {
                    "no": ability.get("ability_no", "정보 없음"),
                    "grade": ability.get("ability_grade", "정보 없음"),
                    "value": ability.get("ability_value", "정보 없음")
                }
                preset_data["abilities"].append(ability_data)

            # 프리셋 데이터를 저장
            extracted_ability[f"preset_{preset_number}"] = preset_data

    return extracted_ability
    
async def extract_link_skills(link_skill_info):
    if not isinstance(link_skill_info, dict):
        return {}

    extracted_skills = {}
    
    for preset_key, skills in link_skill_info.items():
        if preset_key.startswith('character_link_skill_preset_'):
            preset_number = preset_key.split('_')[-1]
            extracted_skills[f'preset_{preset_number}'] = []
            
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


async def extract_vmatrix(vmatrix_info):

    try:
        if not isinstance(vmatrix_info, dict):
            return {
                "date": "정보 없음",
                "character_class": "정보 없음",
                "cores": [],
                "remain_points": 0
            }

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
                for core in vmatrix_info.get("character_v_core_equipment", [])
            ],
            "remain_points": int(vmatrix_info.get("character_v_matrix_remain_slot_upgrade_point", 0))
        }

    except Exception as e:
        return {
            "error": f"V매트릭스 정보 처리 중 오류 발생: {str(e)}",
            "date": "정보 없음",
            "character_class": "정보 없음",
            "cores": [],
            "remain_points": 0
        }

     


async def extract_symbols(symbol_equipment_info):
    """
    심볼 장비 정보를 추출하여 캐릭터의 심볼 장비 관련 정보를 정리
    """
    if not isinstance(symbol_equipment_info, dict):
        return {}

    symbol_data = {
        "date": symbol_equipment_info.get("date", "정보 없음"),
        "character_class": symbol_equipment_info.get("character_class", "정보 없음"),
        "symbol": []
    }

    for symbol in symbol_equipment_info.get("symbol", []):
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
