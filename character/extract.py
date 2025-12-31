# 스탯 추출 함수
async def extract_stat(stat_info):
    final_stat = {}
    for stat in stat_info.get('final_stat', []):
        stat_name = stat['stat_name'].replace(" ","_")
        final_stat[stat_name] = stat['stat_value']

    return final_stat

async def extract_item_equipment(item_equipment_info):
    if not isinstance(item_equipment_info, dict):
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
    equipment_data = {
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
            
            # skills가 None이거나 리스트가 아닌 경우 처리
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
                for core in (vmatrix_info.get("character_v_core_equipment") or [])
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

async def extract_hyper_stat(hyper_stat_info):
    """
    하이퍼 스탯 정보를 추출하여 캐릭터의 하이퍼 스탯 관련 정보를 정리
    """
    if not isinstance(hyper_stat_info, dict):
        return {}

    hyper_stat_data = {
        "date": hyper_stat_info.get("date", "정보 없음"),
        "character_class": hyper_stat_info.get("character_class", "정보 없음"),
        "use_preset_no": hyper_stat_info.get("use_preset_no", "정보 없음"),
        "use_available_hyper_stat": hyper_stat_info.get("use_available_hyper_stat", 0),
        "presets": {}
    }

    # 각 프리셋별로 하이퍼 스탯 정보 추출
    for preset_num in range(1, 4):  # 프리셋 1, 2, 3
        preset_key = f"hyper_stat_preset_{preset_num}"
        remain_point_key = f"hyper_stat_preset_{preset_num}_remain_point"
        
        if preset_key in hyper_stat_info:
            preset_data = {
                "preset_number": preset_num,
                "remain_point": hyper_stat_info.get(remain_point_key, 0),
                "stats": []
            }
            
            # 해당 프리셋의 스탯 정보 추출
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

async def extarct_hexamatrix(hexamatrix_info):
    if not isinstance(hexamatrix_info, dict):
        return {}
    
    hexamatrix_data = {
        "date": hexamatrix_info.get("date", "정보 없음"),
        "hexamatrix": []
    }

    if hexamatrix_info.get("chracter_hexa_core_equipment"):
        for core in (hexamatrix_info.get("chracter_hexa_core_equipment") or []):
            hexamatrix_data["hexamatrix"].append({
                "hexa_core_name": core.get("hexa_core_name", "정보 없음"),
                "hexa_core_level": int(core.get("hexa_core_level", 0)),
                "hexa_core_type": core.get("hexa_core_type", "정보 없음"),
                "linked_skill": core.get("linked_skill", "정보 없음"),
            })
            for skill in (core.get("linked_skill") or []):
                hexamatrix_data["hexamatrix"][-1]["linked_skill"].append({
                    "hexa_skill_id": skill.get("hexa_skill_id", "정보 없음"),
                })
    
    return hexamatrix_data



async def extract_hexamatrix_stat(hexamatrix_stat_info):

    if not isinstance(hexamatrix_stat_info, dict):
        return {}

    hexamatrix_stat_data = {
        "date": hexamatrix_stat_info.get("date", "정보 없음"),
        "hexamatrix_stat_1": [],
        "hexamatrix_stat_2": [],
        "hexamatrix_stat_3": []
    }
    
    for stat in (hexamatrix_stat_info.get("character_hexa_stat_core") or []):
        hexamatrix_stat_data["hexamatrix_stat_1"].append({
            "slot_id": stat.get("slot_id", "정보 없음"),
            "main_stat_name": stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": int(stat.get("main_stat_level", 0)),
            "sub_stat_level_1": int(stat.get("sub_stat_level_1", 0)),
            "sub_stat_level_2": int(stat.get("sub_stat_level_2", 0)),
            "stat_grade": int(stat.get("stat_grade", 0))
        })

    for stat in (hexamatrix_stat_info.get("character_hexa_stat_core_2") or []):
        hexamatrix_stat_data["hexamatrix_stat_2"].append({
            "slot_id": stat.get("slot_id", "정보 없음"),
            "main_stat_name": stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": int(stat.get("main_stat_level", 0)),
            "sub_stat_level_1": int(stat.get("sub_stat_level_1", 0)),
            "sub_stat_level_2": int(stat.get("sub_stat_level_2", 0)),
            "stat_grade": int(stat.get("stat_grade", 0))
        })
    for stat in (hexamatrix_stat_info.get("character_hexa_stat_core_3") or []):
        hexamatrix_stat_data["hexamatrix_stat_3"].append({
            "slot_id": stat.get("slot_id", "정보 없음"),
            "main_stat_name": stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": int(stat.get("main_stat_level", 0)),
            "sub_stat_level_1": int(stat.get("sub_stat_level_1", 0)),
            "sub_stat_level_2": int(stat.get("sub_stat_level_2", 0)),
            "stat_grade": int(stat.get("stat_grade", 0))
        })
    return hexamatrix_stat_data

async def extract_other_stat(other_stat_info):
    if not isinstance(other_stat_info, dict):
        return {}
    
    other_stat_data = {
        "date": other_stat_info.get("date", "정보 없음"),
        "other_stat": []
    }
    
    for stat in (other_stat_info.get("other_stat") or []):
        other_stat_data["other_stat"].append({
            "other_stat_type": stat.get("other_stat_type", "정보 없음"),
            "stat_info": stat.get("stat_info", [])
        })
        for stat_info in (stat.get("stat_info") or []):
            other_stat_data["other_stat"][-1]["stat_info"].append({
                "stat_name": stat_info.get("stat_name", "정보 없음"),
                "stat_value": stat_info.get("stat_value", "정보 없음")
            })
    return other_stat_data


async def extract_pet_equipment(pet_equipment_info):
    """
    펫 장비 정보를 추출하여 캐릭터의 펫 관련 정보를 정리
    """
    if not isinstance(pet_equipment_info, dict):
        return {}

    pet_equipment_data = {
        "date": pet_equipment_info.get("date", "정보 없음"),
        "pets": []
    }

    # 펫 1, 2, 3에 대해 반복 처리
    for pet_num in range(1, 4):
        pet_key_prefix = f"pet_{pet_num}"
        
        # 펫이 존재하는지 확인 (name이 있으면 펫이 존재)
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

            # 펫 장비 정보 추출
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
                
                # 장비 옵션 정보 추출
                for option in equipment.get("item_option", []):
                    option_data = {
                        "option_type": option.get("option_type", "정보 없음"),
                        "option_value": option.get("option_value", "정보 없음")
                    }
                    pet_data["equipment"]["item_option"].append(option_data)

            # 펫 자동 스킬 정보 추출
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

async def extract_hexamatrix(hexamatrix_info):
    """
    헥사매트릭스 정보를 추출합니다.
    """
    if not isinstance(hexamatrix_info, dict):
        return {
            "date": "정보 없음",
            "hexamatrix": []
        }
    
    hexamatrix_data = {
        "date": hexamatrix_info.get("date", "정보 없음"),
        "hexamatrix": []
    }
    
    for hexa in hexamatrix_info.get("hexamatrix", []):
        hexa_data = {
            "slot_id": hexa.get("slot_id", "정보 없음"),
            "slot_level": hexa.get("slot_level", 0),
            "main_stat_name": hexa.get("main_stat_name", "정보 없음"),
            "main_stat_level": hexa.get("main_stat_level", 0),
            "sub_stat_name_1": hexa.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_level_1": hexa.get("sub_stat_level_1", 0),
            "sub_stat_name_2": hexa.get("sub_stat_name_2", "정보 없음"),
            "sub_stat_level_2": hexa.get("sub_stat_level_2", 0),
            "sub_stat_name_3": hexa.get("sub_stat_name_3", "정보 없음"),
            "sub_stat_level_3": hexa.get("sub_stat_level_3", 0)
        }
        hexamatrix_data["hexamatrix"].append(hexa_data)
    
    return hexamatrix_data

