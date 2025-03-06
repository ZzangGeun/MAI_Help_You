from django.conf import settings
import asyncio
import requests
import json

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = settings.NEXON_API_KEY

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
    

async def get_character_data(character_name, date=None):
    ocid_data = await get_api_data('/id',{'character_name' : character_name})  # 닉네임 입력 후 ocid 가져오기
    
    ocid = ocid_data['ocid']
    params ={"ocid" : ocid}

    #필요한 정보 가져오기

    basic_info = await get_api_data("/character/basic", params)
    stat_info = await get_api_data("/character/stat", params)
    hyper_stat_info = await get_api_data("/character/hyper-stat", params)
    ability_info = await get_api_data("/character/ability", params)
    item_equipment_info = await get_api_data("/character/item-equipment", params)
    symbol_info = await get_api_data("/character/symbol-equipment", params)
    set_effect_info = await get_api_data("/character/set-effect", params)
    link_skill_info = await get_api_data("/character/link-skill", params)
    vmatrix_info = await get_api_data("/character/vmatrix", params)
    hexamatrix_info = await get_api_data("/character/hexamatrix", params)

    print(basic_info)


    return {
        "basic_info": basic_info,
        "stat_info": stat_info,
        "hyper_stat_info":hyper_stat_info,
        "item_equipment_info": item_equipment_info,
        "ability_info": ability_info,
        "set_effect_info": set_effect_info,
        "link_skill_info": link_skill_info,
        "hexamatrix_info": hexamatrix_info,
        "symbol_info": symbol_info,
        "vmatrix_info": vmatrix_info,
    }


# 템플릿에 넘겨주는 views 함수 작성

async def chracter_info_view(request, character_name):
    character_name = request.GET['name']















































# 위에서 가져온 정보에서 필요한 정보만 추출하는 함수 작성









#basic_info는 json 파일 형식
async def extract_basic_info(basic_info):
    """
    {
        "date": "2023-12-21T00:00+09:00",
        "character_name": "string",
        "world_name": "string",
        "character_gender": "string",
        "character_class": "string",
        "character_class_level": "string",
        "character_level": 0,
        "character_exp": 0,
        "character_exp_rate": "string",
        "character_guild_name": "string",
        "character_image": "string",
        "character_date_create": "2023-12-21T00:00+09:00",
        "access_flag": "string",
        "liberation_quest_clear_flag": "string"
    }
    예시 문서 사용
    """

    #코루틴 실행하여 결과 저장

    
    # character_name = basic_info['character_name']
    # character_class = basic_info['character_class']
    # character_level = basic_info['character_level']
    # character_guild_name = basic_info['character_guild_name']
    # character_image = basic_info['character_image']  

    #딕셔너리로 저장



    basic_info = {
        "character_name" : basic_info.get('character_name'),
        "character_class" : basic_info.get('character_class'),
        "character_level" : basic_info.get('character_level'),
        "character_guild_name" : basic_info.get('character_guild_name',[]),
        "character_image" : basic_info.get('character_image'),
    }

    print(basic_info)

    return basic_info


asyncio.run(extract_basic_info('무당햄스터'))





    


