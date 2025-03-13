
# 스탯 추출 함수수
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

