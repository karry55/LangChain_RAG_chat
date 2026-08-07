"""向量数据库管理 - Milvus Lite / ChromaDB"""
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

_vector_store: Optional[VectorStore] = None


def _init_milvus_lite() -> VectorStore:
    """初始化 Milvus Lite (嵌入式)"""
    from langchain_community.vectorstores import Milvus
    from app.rag.embedder import get_embeddings_client

    return Milvus(
        embedding_function=get_embeddings_client(),
        collection_name="ecommerce_knowledge",
        auto_id=True,
    )


def _init_chromadb() -> VectorStore:
    """初始化 ChromaDB (持久化到磁盘)"""
    from langchain_community.vectorstores import Chroma
    from app.rag.embedder import get_embeddings_client

    return Chroma(
        embedding_function=get_embeddings_client(),
        collection_name="ecommerce_knowledge",
        persist_directory="./data/chroma",
    )


def get_vector_store() -> VectorStore:
    """获取向量数据库实例（单例模式）"""
    global _vector_store
    if _vector_store is None:
        store_type = settings.vector_store
        logger.info(f"初始化向量数据库: {store_type}")
        if store_type == "milvus_lite":
            _vector_store = _init_milvus_lite()
        elif store_type == "chromadb":
            _vector_store = _init_chromadb()
        else:
            raise ValueError(f"不支持的向量数据库类型: {store_type}")
    return _vector_store


def add_documents(documents: List[Document]) -> List[str]:
    """将文档块添加到向量数据库，返回向量ID列表"""
    store = get_vector_store()
    return store.add_documents(documents)


def delete_documents_by_filter(filter_dict: dict):
    """根据过滤条件删除向量"""
    store = get_vector_store()
    # ChromaDB 支持 filter 删除
    if hasattr(store, "_collection"):
        store._collection.delete(filter=filter_dict)


def similarity_search_with_score(
    query: str, k: int = 10, filter_dict: Optional[dict] = None
) -> List[tuple]:
    """语义检索 + 相似度分数

    Returns:
        List[(Document, float)]: 文档和相似度分数
    """
    store = get_vector_store()
    return store.similarity_search_with_score(query, k=k, filter=filter_dict)


def similarity_search(
    query: str, k: int = 10, filter_dict: Optional[dict] = None
) -> List[Document]:
    """语义检索"""
    store = get_vector_store()
    return store.similarity_search(query, k=k, filter=filter_dict)
