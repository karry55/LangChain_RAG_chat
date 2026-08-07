"""应用配置中心"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """全局配置，从 .env 文件自动加载"""

    # 阿里云百炼
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    embedding_model: str = "text-embedding-v3"

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./rag_kb.db"

    # 向量数据库
    vector_store: str = "milvus_lite"  # milvus_lite | chromadb

    # JWT
    secret_key: str = "rag-enterprise-secret-key-change-me"
    access_token_expire_hours: int = 24

    # 服务
    backend_port: int = 8000
    frontend_port: int = 5173

    # 文件上传
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50

    # RAG 参数
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 10
    mmr_fetch_k: int = 20
    mmr_lambda_mult: float = 0.7
    final_top_k: int = 5

    # 缓存
    embedding_cache_dir: str = "./data/cache/embeddings"
    embedding_cache_ttl_days: int = 30

    # 限流
    rate_limit_per_minute: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
