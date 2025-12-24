# -*- coding: utf-8 -*-
"""
RAG 검색 기능 테스트 스크립트
"""
import os
import sys
import django
import asyncio

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maple_chatbot.settings')
django.setup()

from mai_chat.rag.rag_service import RAGService

async def test_search(query: str):
    print(f"\n🔍 검색어: '{query}'")
    print("=" * 60)
    
    rag_service = RAGService(top_k=3, similarity_threshold=0.0) # 모든 결과를 보기 위해 0으로 설정
    
    # 통계 확인
    try:
        stats = rag_service.retriever.vector_store.get_stats()
        print(f"📊 DB 통계: {stats}")
    except Exception as e:
        print(f"⚠️ 통계 확인 실패: {e}")

    context, docs = await rag_service.retrieve_context_async(query)
    
    if not docs:
        print("❌ 검색 결과가 없습니다.")
        return

    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] 제목: {doc.title}")
        print(f"    유사도: {doc.similarity_score:.4f}")
        print(f"    출처: {doc.source}")
        print(f"    내용 요약: {doc.content[:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "업데이트" # 기본 검색어
        
    asyncio.run(test_search(query))
