"""Embedding 服务 - 百炼 text-embedding-v3 + 本地缓存"""
import hashlib
from typing import List
from diskcache import Cache
from langchain_community.embeddings import DashScopeEmbeddings
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# 磁盘缓存（持久化 Embedding 结果）
_cache = Cache(settings.embedding_cache_dir)

# 百炼 Embedding 客户端
_embeddings = DashScopeEmbeddings(
    model=settings.embedding_model,
    dashscope_api_key=settings.dashscope_api_key,
)


def _hash_text(text: str) -> str:
    """计算文本的 MD5 哈希作为缓存 key"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """批量文本转向量，带缓存

    Args:
        texts: 文本列表

    Returns:
        向量列表，每个向量是 float 列表
    """
    vectors = []
    texts_to_embed = []
    cache_indices = []

    # 先查缓存
    for i, text in enumerate(texts):
        key = f"emb:{_hash_text(text)}"
        cached = _cache.get(key)
        if cached is not None:
            vectors.append(cached)
        else:
            vectors.append(None)  # 占位
            texts_to_embed.append(text)
            cache_indices.append(i)

    # 对未缓存的文本批量调用 API
    if texts_to_embed:
        logger.info(f"调用百炼 Embedding API: {len(texts_to_embed)} 条文本")
        new_vectors = _embeddings.embed_documents(texts_to_embed)

        for idx, vec in zip(cache_indices, new_vectors):
            vectors[idx] = vec
            # 写入缓存
            key = f"emb:{_hash_text(texts[idx])}"
            _cache.set(key, vec, expire=settings.embedding_cache_ttl_days * 86400)

    return vectors


def embed_query(text: str) -> List[float]:
    """单条查询文本转向量"""
    key = f"emb:{_hash_text(text)}"
    cached = _cache.get(key)
    if cached is not None:
        return cached

    vec = _embeddings.embed_query(text)
    _cache.set(key, vec, expire=settings.embedding_cache_ttl_days * 86400)
    return vec


def get_embeddings_client() -> DashScopeEmbeddings:
    """获取 Embedding 客户端实例（用于 ChromaDB 等）"""
    return _embeddings
