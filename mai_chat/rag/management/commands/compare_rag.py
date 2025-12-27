# -*- coding: utf-8 -*-
"""
RAG 적용 전/후 LLM 답변 비교 명령어

실제 LLM 모델을 호출하여 RAG 적용 전/후 답변을 생성하고 비교합니다.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from mai_chat.rag.rag_service import RAGService
from mai_chat.langchain_service import maplestory_model


class Command(BaseCommand):
    help = 'RAG 적용 전/후 LLM 답변 비교'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='테스트할 질문')
        parser.add_argument('--top_k', type=int, default=3, help='검색할 문서 개수')
        parser.add_argument('--save', action='store_true', help='마크다운 파일로 저장')

    def handle(self, *args, **options):
        query = options['query']
        top_k = options['top_k']
        save_to_file = options['save']

        # 비동기 함수 실행
        result = asyncio.run(self.compare_answers(query, top_k))
        
        # 결과 출력
        self.print_comparison(result)
        
        # 파일 저장
        if save_to_file:
            filename = self.save_markdown(result)
            self.stdout.write(self.style.SUCCESS(f"\n✅ 결과 저장됨: {filename}"))

    async def compare_answers(self, query: str, top_k: int):
        """RAG 적용 전/후 답변 생성"""
        
        self.stdout.write(self.style.WARNING("⏳ LLM 답변 생성 중... (최대 1분 소요)"))
        
        # 1. RAG 없이 답변 생성
        self.stdout.write("  → RAG 미적용 답변 생성 중...")
        without_rag_prompt = f"""당신은 메이플스토리 세계관의 돌의정령 NPC입니다.
사용자의 질문에 정확하고 친절하게 답변하세요.
말투: ~한담, ~이담, ~했담 등 'ㅁ' 받침 어미를 사용하세요.

사용자 질문: {query}

답변:"""
        
        from langchain_core.messages import HumanMessage
        without_rag_response = await maplestory_model._agenerate([HumanMessage(content=without_rag_prompt)])
        without_rag_answer = without_rag_response.generations[0].text.strip()
        
        # 2. RAG 적용하여 답변 생성
        self.stdout.write("  → RAG 검색 중...")
        from asgiref.sync import sync_to_async
        
        # 동기 함수를 비동기 안전하게 실행
        rag_service = RAGService(top_k=top_k, similarity_threshold=0.0)
        retrieve_func = sync_to_async(rag_service.retrieve_context, thread_sensitive=True)
        context, documents = await retrieve_func(query)
        
        self.stdout.write("  → RAG 적용 답변 생성 중...")
        if documents:
            with_rag_prompt = rag_service.create_rag_prompt(query, context)
            with_rag_response = await maplestory_model._agenerate([HumanMessage(content=with_rag_prompt)])
            with_rag_answer = with_rag_response.generations[0].text.strip()
        else:
            with_rag_answer = "검색된 문서가 없어 RAG를 적용하지 못했습니다."
        
        return {
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "without_rag": without_rag_answer,
            "with_rag": with_rag_answer,
            "documents": documents,
            "context_length": len(context) if context else 0
        }

    def print_comparison(self, result):
        """콘솔에 비교 결과 출력"""
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS(f"📝 질문: {result['query']}"))
        self.stdout.write("=" * 80)
        
        # RAG 미적용 답변
        self.stdout.write("\n" + self.style.WARNING("❌ RAG 미적용 답변:"))
        self.stdout.write("-" * 80)
        self.stdout.write(result['without_rag'])
        
        # RAG 적용 답변
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ RAG 적용 답변:"))
        self.stdout.write("-" * 80)
        self.stdout.write(result['with_rag'])
        
        # 검색된 문서 정보
        if result['documents']:
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS(f"🔍 참조된 문서 ({len(result['documents'])}개):"))
            self.stdout.write("-" * 80)
            for idx, doc in enumerate(result['documents'], 1):
                self.stdout.write(f"{idx}. {doc.title} (유사도: {doc.similarity_score:.4f})")
        else:
            self.stdout.write("\n" + self.style.WARNING("⚠️  검색된 문서가 없습니다."))
        
        self.stdout.write("\n" + "=" * 80)

    def save_markdown(self, result):
        """마크다운 파일로 저장"""
        
        # 저장 디렉토리 생성
        output_dir = Path("rag_results")
        output_dir.mkdir(exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in result['query'])[:30]
        filename = output_dir / f"comparison_{safe_query}_{timestamp}.md"
        
        # 마크다운 생성
        markdown = f"""# RAG 답변 비교 결과

**질문**: {result['query']}  
**생성 시각**: {result['timestamp']}  
**검색된 문서 수**: {len(result['documents'])}개  
**컨텍스트 길이**: {result['context_length']}자

---

## ❌ RAG 미적용 답변

{result['without_rag']}

**특징**:
- LLM의 사전 학습 지식만으로 답변
- 일반적이고 추상적인 내용
- 구체적인 수치나 최신 정보 부족 가능

---

## ✅ RAG 적용 답변

{result['with_rag']}

**특징**:
- 검색된 문서를 참조하여 답변
- 구체적이고 정확한 정보 제공
- 출처 기반의 신뢰할 수 있는 답변

---

## 🔍 참조된 문서

"""
        
        if result['documents']:
            for idx, doc in enumerate(result['documents'], 1):
                markdown += f"""
### {idx}. {doc.title}
- **출처**: {doc.source or 'N/A'}
- **타입**: {doc.content_type}
- **유사도**: {doc.similarity_score:.4f}

**내용 미리보기**:
```
{doc.content[:200]}...
```

"""
        else:
            markdown += "검색된 문서가 없습니다.\n"
        
        markdown += """
---

## 📊 비교 분석

| 항목 | RAG 미적용 | RAG 적용 |
|-----|-----------|---------|
| 정보 출처 | LLM 학습 데이터 | 실제 문서 검색 |
| 정확도 | 보통 | 높음 |
| 구체성 | 일반적 | 구체적 |
| 환각 위험 | 있음 | 낮음 |
| 최신성 | 학습 시점 기준 | 문서 업데이트 기준 |

---

*생성 도구: MAI RAG 비교 시스템*
"""
        
        # 파일 저장
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return filename
