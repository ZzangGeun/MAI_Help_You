from django.core.management.base import BaseCommand
from sqlalchemy import create_engine, text

from core.legacy_config.env import get_pg_config
from apps.chatbot.rag_engine import RagEngine


class Command(BaseCommand):
    help = "Reindex RAG data into PostgreSQL(pgvector). Optionally truncate table first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Truncate vector table before reindexing",
        )

    def handle(self, *args, **options):
        pg = get_pg_config()
        if options.get("truncate") or pg.get("truncate_on_reindex"):
            url = f"postgresql+psycopg2://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE {pg['table']};"))
                conn.commit()
            self.stdout.write(self.style.WARNING(f"Truncated table {pg['table']}"))

        rag = RagEngine()
        # RagEngine ctor will ingest if empty. Force ingest regardless.
        rag._ingest_from_dir()
        self.stdout.write(self.style.SUCCESS("RAG reindex completed."))
