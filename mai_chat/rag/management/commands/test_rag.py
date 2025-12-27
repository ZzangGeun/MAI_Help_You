from django.core.management.base import BaseCommand
from mai_chat.rag.rag_service import RAGService
import asyncio

class Command(BaseCommand):
    help = 'RAG 검색 테스트'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='검색할 질문')
        parser.add_argument('--top_k', type=int, default=3, help='검색할 문서 개수')

    def handle(self, *args, **options):
        query = options['query']
        top_k = options['top_k']

        self.stdout.write(f"질문: {query}")
        self.stdout.write("-" * 50)

        # 비동기 실행을 위해 asyncio.run 사용
        try:
            rag_service = RAGService(top_k=top_k)
            context, documents = rag_service.retrieve_context(query)
            
            if not documents:
                self.stdout.write(self.style.WARNING("검색 결과가 없습니다."))
                return

            self.stdout.write(self.style.SUCCESS(f"검색된 문서: {len(documents)}개"))
            for idx, doc in enumerate(documents, 1):
                self.stdout.write(f"\n[{idx}] {doc.title} (유사도: {doc.similarity_score:.4f})")
                self.stdout.write(f"출처: {doc.source or 'N/A'}")
                self.stdout.write(f"내용: {doc.content[:200]}...")
                self.stdout.write("-" * 30)
            
            self.stdout.write("\n[LLM 프롬프트용 컨텍스트 미리보기]")
            self.stdout.write(context[:500] + "..." if len(context) > 500 else context)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"오류 발생: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
