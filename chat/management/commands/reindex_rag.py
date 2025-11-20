from django.core.management.base import BaseCommand
from sqlalchemy import create_engine, text

from core.legacy_config.env import get_pg_config
from chat.rag_engine import RagEngine


class Command(BaseCommand):
    help = "Reindex RAG data into PostgreSQL(pgvector) using LangChain. Optionally truncate table first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Truncate LangChain vector table before reindexing",
        )

    def handle(self, *args, **options):
        pg = get_pg_config()
        
        try:
            rag = RagEngine()
            
            if options.get("truncate") or pg.get("truncate_on_reindex"):
                # LangChain 테이블 정리
                if rag.clear_documents():
                    self.stdout.write(self.style.WARNING(f"Cleared LangChain vector collection: {rag.collection_name}"))
                else:
                    self.stdout.write(self.style.ERROR("Failed to clear existing documents"))

            # 강제 재인덱싱
            self.stdout.write(self.style.SUCCESS("Starting LangChain RAG reindexing..."))
            rag._ingest_from_dir()
            self.stdout.write(self.style.SUCCESS("LangChain RAG reindex completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"RAG reindexing failed: {e}"))
