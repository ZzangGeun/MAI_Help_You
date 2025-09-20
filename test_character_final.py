#!/usr/bin/env python
"""
최종 캐릭터 정보 조회 테스트
"""
import os
import sys
import django
import asyncio
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Django 설정
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAI.settings')
django.setup()

from apps.character_info.get_character_info import get_character_data, load_character_data_from_json

async def test_character_final():
    """최종 캐릭터 정보 조회 테스트"""
    character_name = "무당햄스터"
    
    print(f"🔍 최종 테스트: '{character_name}' 캐릭터 정보 조회")
    print(f"🔑 API Key: {os.getenv('NEXON_API_KEY', 'Not Set')[:10]}...")
    
    # 1. 저장된 JSON 파일 확인
    print(f"\n📂 저장된 JSON 파일 확인...")
    saved_data = load_character_data_from_json(character_name)
    if saved_data:
        print("✅ 저장된 캐릭터 데이터를 찾았습니다!")
        print(f"   - 기본 정보: {saved_data.get('basic_info', {}).get('character_name', 'N/A')}")
        print(f"   - 레벨: {saved_data.get('basic_info', {}).get('character_level', 'N/A')}")
        print(f"   - 직업: {saved_data.get('basic_info', {}).get('character_class', 'N/A')}")
    else:
        print("❌ 저장된 캐릭터 데이터가 없습니다.")
    
    # 2. API를 통한 새로운 데이터 조회
    print(f"\n🌐 API를 통한 새로운 데이터 조회...")
    try:
        character_data = await get_character_data(character_name)
        
        if character_data:
            print("✅ 캐릭터 정보 조회 성공!")
            
            # 기본 정보 상세 출력
            basic_info = character_data.get('basic_info', {})
            print(f"   - 캐릭터명: {basic_info.get('character_name', 'N/A')}")
            print(f"   - 레벨: {basic_info.get('character_level', 'N/A')}")
            print(f"   - 직업: {basic_info.get('character_class', 'N/A')}")
            print(f"   - 길드: {basic_info.get('character_guild_name', 'N/A')}")
            print(f"   - 월드: {basic_info.get('world_name', 'N/A')}")
            print(f"   - 성별: {basic_info.get('character_gender', 'N/A')}")
            
            # 스탯 정보 확인
            if character_data.get('stat_info'):
                print(f"   - 스탯 정보: {len(character_data['stat_info'])}개 항목")
                for stat_name, stat_value in list(character_data['stat_info'].items())[:5]:
                    print(f"     * {stat_name}: {stat_value}")
            
            # 장비 정보 확인
            if character_data.get('item_info'):
                item_info = character_data['item_info']
                print(f"   - 장비 정보:")
                print(f"     * 현재 프리셋: {item_info.get('preset_no', 'N/A')}")
                print(f"     * 기본 장비: {len(item_info.get('item_equipment', {}))}개")
                print(f"     * 프리셋 1: {len(item_info.get('item_equipment_preset_1', {}))}개")
                print(f"     * 프리셋 2: {len(item_info.get('item_equipment_preset_2', {}))}개")
                print(f"     * 프리셋 3: {len(item_info.get('item_equipment_preset_3', {}))}개")
                
                # 기본 장비 몇 개 출력
                for slot, item_data in list(item_info.get('item_equipment', {}).items())[:3]:
                    print(f"       - {slot}: {item_data.get('name', 'N/A')}")
            
            # 기타 정보 확인
            if character_data.get('ability_info'):
                print(f"   - 어빌리티 정보: {len(character_data['ability_info'])}개 프리셋")
            
            if character_data.get('link_skill_info'):
                print(f"   - 링크 스킬 정보: {len(character_data['link_skill_info'])}개")
            
            if character_data.get('vmatrix_info'):
                print(f"   - V매트릭스 정보: {len(character_data['vmatrix_info'].get('cores', []))}개 코어")
                    
        else:
            print("❌ 캐릭터 정보 조회 실패!")
            print("   - 캐릭터 이름을 확인해주세요.")
            print("   - API 키가 올바르게 설정되어 있는지 확인해주세요.")
            print("   - 테스트용 API 키인 경우 실제 데이터 조회가 불가능합니다.")
            
    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_character_final())
