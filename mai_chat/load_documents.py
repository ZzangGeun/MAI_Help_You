# -*- coding: utf-8 -*-
"""
RAG 문서 로딩 스크립트

rag_documents 폴더의 JSON 파일들을 읽어서 데이터베이스에 로드합니다.
"""

import os
import sys
import django
from pathlib import Path

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maple_chatbot.settings')
django.setup()

from mai_chat.rag.document_loader import load_document_from_json_file, load_document_from_text


def load_all_documents_from_directory(directory_path: str) -> int:
    """
    지정된 디렉토리의 모든 JSON 파일을 재귀적으로 로드합니다.
    
    Args:
        directory_path: 문서가 있는 디렉토리 경로
        
    Returns:
        int: 로드된 문서 개수
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {directory_path}")
        return 0
    
    total_loaded = 0
    json_files = list(directory.rglob('*.json'))
    
    if not json_files:
        print(f"⚠️  {directory_path}에 JSON 파일이 없습니다.")
        return 0
    
    print(f"\n📂 {len(json_files)}개의 JSON 파일 발견")
    print("=" * 60)
    
    for json_file in json_files:
        print(f"\n📄 처리 중: {json_file.relative_to(directory.parent)}")
        try:
            documents = load_document_from_json_file(str(json_file))
            print(f"   ✓ {len(documents)}개 문서 로드 완료")
            total_loaded += len(documents)
        except Exception as e:
            print(f"   ✗ 로드 실패: {e}")
    
    return total_loaded


def load_single_text_document():
    """
    단일 텍스트 문서를 직접 입력받아 로드합니다.
    """
    print("\n" + "=" * 60)
    print("단일 문서 직접 입력")
    print("=" * 60)
    
    title = input("문서 제목: ")
    print("문서 내용 (입력 완료 후 빈 줄에서 Ctrl+Z 후 Enter [Windows] 또는 Ctrl+D [Linux/Mac]):")
    
    content_lines = []
    try:
        while True:
            line = input()
            content_lines.append(line)
    except EOFError:
        pass
    
    content = '\n'.join(content_lines)
    
    if not title or not content:
        print("❌ 제목과 내용은 필수입니다.")
        return
    
    content_type = input("문서 타입 (guide/notice/item/quest/skill/other) [기본: guide]: ") or "guide"
    source = input("출처 (선택사항): ") or None
    
    try:
        doc = load_document_from_text(
            title=title,
            content=content,
            content_type=content_type,
            source=source
        )
        print(f"\n✓ 문서 '{doc.title}' 로드 완료")
        print(f"  - ID: {doc.id}")
        print(f"  - 청크 수: {doc.chunks.count()}")
    except Exception as e:
        print(f"\n❌ 문서 로드 실패: {e}")


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("RAG 문서 로더")
    print("=" * 60)
    
    print("\n선택하세요:")
    print("1. rag_documents 폴더의 모든 JSON 파일 로드")
    print("2. 특정 JSON 파일 로드")
    print("3. 단일 문서 직접 입력")
    print("4. 종료")
    
    choice = input("\n선택 (1-4): ")
    
    if choice == "1":
        # 프로젝트 루트의 rag_documents 폴더
        base_dir = Path(__file__).resolve().parent.parent
        rag_docs_dir = base_dir / "rag_documents"
        
        if not rag_docs_dir.exists():
            print(f"\n⚠️  {rag_docs_dir} 폴더가 없습니다.")
            create = input("폴더를 생성하시겠습니까? (y/n): ")
            if create.lower() == 'y':
                rag_docs_dir.mkdir(parents=True, exist_ok=True)
                (rag_docs_dir / "guides").mkdir(exist_ok=True)
                (rag_docs_dir / "notices").mkdir(exist_ok=True)
                (rag_docs_dir / "items").mkdir(exist_ok=True)
                print(f"✓ {rag_docs_dir} 폴더 생성 완료")
                print("\n이제 JSON 파일을 해당 폴더에 넣고 다시 실행하세요.")
            return
        
        total = load_all_documents_from_directory(str(rag_docs_dir))
        print("\n" + "=" * 60)
        print(f"✓ 총 {total}개 문서 로드 완료")
        print("=" * 60)
        
    elif choice == "2":
        file_path = input("JSON 파일 경로: ")
        try:
            documents = load_document_from_json_file(file_path)
            print(f"\n✓ {len(documents)}개 문서 로드 완료")
        except Exception as e:
            print(f"\n❌ 로드 실패: {e}")
            
    elif choice == "3":
        load_single_text_document()
        
    elif choice == "4":
        print("종료합니다.")
        return
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
