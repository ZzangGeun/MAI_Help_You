# -*- coding: utf-8 -*-

import os
from typing import Dict, Any

class ServiceConfig:
    """서비스 공통 설정 클래스"""
    
    @staticmethod
    def get_pg_config() -> Dict[str, str]:
        """PostgreSQL 설정을 반환합니다."""
        return {
            'host': os.getenv('PG_HOST', os.getenv('PGHOST', 'localhost')),
            'port': os.getenv('PG_PORT', os.getenv('PGPORT', '5432')),
            'user': os.getenv('PG_USER', os.getenv('PGUSER', 'postgres')),
            'password': os.getenv('PG_PASSWORD', os.getenv('PGPASSWORD', '')),
            'dbname': os.getenv('PG_DB', os.getenv('PGDATABASE', 'postgres')),
        }
    
    @staticmethod
    def get_rag_config() -> Dict[str, Any]:
        """RAG 설정을 반환합니다."""
        return {
            'embedding_model': os.getenv('RAG_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            'chunk_size': int(os.getenv('RAG_CHUNK_SIZE', '512')),
            'chunk_overlap': int(os.getenv('RAG_CHUNK_OVERLAP', '50')),
            'top_k': int(os.getenv('RAG_TOP_K', '3')),
            'table_name': os.getenv('RAG_TABLE_NAME', 'rag_documents'),
        }
    
    @staticmethod
    def get_llm_config() -> Dict[str, Any]:
        """LLM 설정을 반환합니다."""
        return {
            'huggingface_token': os.getenv('HUGGINGFACE_TOKEN'),
            'base_model': os.getenv('HF_BASE_MODEL', 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'),
            'local_model_path': os.getenv('LOCAL_MODEL_PATH', 'fine_tuned_model/merged_qwen'),
            'fastapi_url': os.getenv('FASTAPI_MODEL_URL', 'http://127.0.0.1:8001/api/chat'),
            'use_remote': os.getenv('USE_REMOTE_LLM', 'auto').lower(),
            'max_length': int(os.getenv('LLM_MAX_LENGTH', '1024')),
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
            'top_p': float(os.getenv('LLM_TOP_P', '0.9')),
            'top_k': int(os.getenv('LLM_TOP_K', '50')),
        }
    
    @staticmethod
    def get_cors_config() -> Dict[str, Any]:
        """CORS 설정을 반환합니다."""
        return {
            'allow_origins': [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:3000",  # React 개발 서버
                "http://127.0.0.1:3000",
            ],
            'allow_credentials': True,
            'allow_methods': ["*"],
            'allow_headers': ["*"],
        }
