# -*- coding: utf-8 -*-
"""
캐릭터 정보 JSON을 RAG 문서로 변환하는 컨버터

Nexon API 형식의 캐릭터 정보를 RAG 검색 가능한 문서로 변환합니다.
"""

import os
import sys
import django
import json
from pathlib import Path

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maple_chatbot.settings')
django.setup()

from mai_chat.rag.document_loader import load_document_from_text


def convert_character_to_rag_document(character_data: dict) -> str:
    """
    캐릭터 정보 JSON을 RAG 문서 텍스트로 변환합니다.
    
    Args:
        character_data: Nexon API 형식의 캐릭터 데이터
        
    Returns:
        str: RAG 문서용 텍스트
    """
    basic = character_data.get('basic_info', {})
    stat = character_data.get('stat_info', {})
    items = character_data.get('item_info', {})
    
    # 캐릭터 기본 정보
    char_name = basic.get('character_name', '알 수 없음')
    char_class = basic.get('character_class', '알 수 없음')
    char_level = basic.get('character_level', 0)
    world = basic.get('world_name', '알 수 없음')
    guild = basic.get('character_guild_name', '없음')
    
    # 문서 텍스트 생성
    content_parts = [
        f"# {char_name} 캐릭터 정보\n",
        f"## 기본 정보",
        f"- 직업: {char_class}",
        f"- 레벨: {char_level}",
        f"- 월드: {world}",
        f"- 길드: {guild}",
        f"- 생성일: {basic.get('character_date_create', '알 수 없음')}",
        f"- 인기도: {basic.get('character_popularity', 0)}\n",
    ]
    
    # 주요 스탯 정보
    if stat:
        content_parts.extend([
            f"## 전투 스탯",
            f"- 전투력: {stat.get('전투력', 'N/A')}",
            f"- 스탯 공격력: {stat.get('최소_스탯공격력', 'N/A')} ~ {stat.get('최대_스탯공격력', 'N/A')}",
            f"- 보스 데미지: {stat.get('보스_몬스터_데미지', 'N/A')}%",
            f"- 방무: {stat.get('방어율_무시', 'N/A')}%",
            f"- 크리티컬 확률: {stat.get('크리티컬_확률', 'N/A')}%",
            f"- 크리티컬 데미지: {stat.get('크리티컬_데미지', 'N/A')}%",
            f"- 최종 데미지: {stat.get('최종_데미지', 'N/A')}%",
            f"- 스타포스: {stat.get('스타포스', 'N/A')}",
            f"- 아케인포스: {stat.get('아케인포스', 'N/A')}",
            f"- 어센틱포스: {stat.get('어센틱포스', 'N/A')}\n",
            f"## 기본 능력치",
            f"- STR: {stat.get('STR', 'N/A')}",
            f"- DEX: {stat.get('DEX', 'N/A')}",
            f"- INT: {stat.get('INT', 'N/A')}",
            f"- LUK: {stat.get('LUK', 'N/A')}",
            f"- HP: {stat.get('HP', 'N/A')}",
            f"- MP: {stat.get('MP', 'N/A')}",
            f"- 공격력: {stat.get('공격력', 'N/A')}",
            f"- 마력: {stat.get('마력', 'N/A')}\n",
        ])
    
    # 주요 장비 정보
    if items and 'item_equipment' in items:
        content_parts.append(f"## 주요 장비")
        equipment = items['item_equipment']
        
        for slot_name, item in equipment.items():
            if not isinstance(item, dict):
                continue
            
            item_name = item.get('name', '알 수 없음')
            starforce = item.get('starforce', '0')
            potential = item.get('potential_option_grade', '없음')
            
            content_parts.append(f"- {slot_name}: {item_name} (★{starforce}, {potential})")
    
    return '\n'.join(content_parts)


def convert_character_file_to_rag(file_path: str) -> bool:
    """
    캐릭터 정보 JSON 파일을 RAG 문서로 변환하여 저장합니다.
    
    Args:
        file_path: 캐릭터 정보 JSON 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
        
        # 캐릭터 이름 추출
        char_name = character_data.get('basic_info', {}).get('character_name', '알 수 없는 캐릭터')
        
        # RAG 문서 텍스트 생성
        content = convert_character_to_rag_document(character_data)
        
        # RAG 문서로 저장
        doc = load_document_from_text(
            title=f"{char_name} 캐릭터 정보",
            content=content,
            content_type="other",
            source=file_path,
            metadata={
                "type": "character",
                "character_name": char_name,
                "class": character_data.get('basic_info', {}).get('character_class'),
                "level": character_data.get('basic_info', {}).get('character_level')
            }
        )
        
        print(f"✓ '{char_name}' 캐릭터 정보를 RAG 문서로 변환 완료")
        print(f"  - 문서 ID: {doc.id}")
        print(f"  - 청크 수: {doc.chunks.count()}")
        
        return True
        
    except Exception as e:
        print(f"✗ 변환 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def convert_all_character_files(directory: str) -> int:
    """
    디렉토리 내 모든 캐릭터 JSON 파일을 RAG 문서로 변환합니다.
    
    Args:
        directory: 캐릭터 JSON 파일들이 있는 디렉토리
        
    Returns:
        int: 변환 성공한 파일 개수
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {directory}")
        return 0
    
    json_files = list(directory_path.glob('*.json'))
    
    if not json_files:
        print(f"⚠️  {directory}에 JSON 파일이 없습니다.")
        return 0
    
    print(f"\n📂 {len(json_files)}개의 캐릭터 파일 발견")
    print("=" * 60)
    
    success_count = 0
    for json_file in json_files:
        print(f"\n📄 처리 중: {json_file.name}")
        if convert_character_file_to_rag(str(json_file)):
            success_count += 1
    
    return success_count


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("캐릭터 정보를 RAG 문서로 변환")
    print("=" * 60)
    
    print("\n선택하세요:")
    print("1. rag_documents/character 폴더의 모든 캐릭터 파일 변환")
    print("2. 특정 캐릭터 파일 변환")
    print("3. 종료")
    
    choice = input("\n선택 (1-3): ")
    
    if choice == "1":
        base_dir = Path(__file__).resolve().parent.parent
        char_dir = base_dir / "rag_documents" / "character"
        
        if not char_dir.exists():
            print(f"\n⚠️  {char_dir} 폴더가 없습니다.")
            return
        
        total = convert_all_character_files(str(char_dir))
        print("\n" + "=" * 60)
        print(f"✓ 총 {total}개 캐릭터 문서 변환 완료")
        print("=" * 60)
        
    elif choice == "2":
        file_path = input("캐릭터 JSON 파일 경로: ")
        if convert_character_file_to_rag(file_path):
            print("\n✓ 변환 완료")
        else:
            print("\n❌ 변환 실패")
            
    elif choice == "3":
        print("종료합니다.")
        return
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
