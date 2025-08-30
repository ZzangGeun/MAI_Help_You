import os
from typing import Dict, Any


def get_pg_config() -> Dict[str, Any]:
    return {
        "host": os.getenv("PG_HOST", os.getenv("PGHOST", "localhost")),
        "port": int(os.getenv("PG_PORT", os.getenv("PGPORT", "5432"))),
        "db": os.getenv("PG_DB", os.getenv("PGDATABASE", "postgres")),
        "user": os.getenv("PG_USER", os.getenv("PGUSER", "postgres")),
        "password": os.getenv("PG_PASSWORD", os.getenv("PGPASSWORD", "postgres")),
        "table": os.getenv("PGVECTOR_TABLE", "mai_rag_index"),
        "truncate_on_reindex": os.getenv("PGVECTOR_TRUNCATE_ON_REINDEX", "false").lower() == "true",
    }


def get_rag_config() -> Dict[str, Any]:
    return {
        "data_path": os.getenv("RAG_DATA_PATH", "MAI_db/json_data"),
        "top_k": int(os.getenv("RAG_TOP_K", "3")),
        "embed_model": os.getenv("RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "embed_dim": int(os.getenv("RAG_EMBED_DIM", "384")),
    }


def get_llm_config() -> Dict[str, Any]:
    return {
        "local_model_path": os.getenv("LOCAL_MODEL_PATH", "fine_tuned_model/merged_qwen"),
        "hf_base_model": os.getenv("HF_BASE_MODEL", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"),
        "hf_token": os.getenv("HUGGINGFACE_TOKEN"),
    }


def get_remote_config() -> Dict[str, Any]:
    use_remote = os.getenv("USE_REMOTE_LLM", "auto").lower()
    fastapi_url = os.getenv("FASTAPI_MODEL_URL", "http://127.0.0.1:8001/api/chat")
    if use_remote not in {"true", "false"}:
        remote_mode = bool(fastapi_url)
    else:
        remote_mode = use_remote == "true"
    return {
        "fastapi_url": fastapi_url,
        "remote_mode": remote_mode,
    }
