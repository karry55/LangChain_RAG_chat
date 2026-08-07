"""RAG 核心流水线编排 - LangChain Chain 组装"""
from typing import AsyncIterator, List
from langchain_core.documents import Document
from loguru import logger

from app.rag.retriever import AdvancedRetriever
from app.rag.generator import generate_stream, format_sources


class RAGChain:
    """RAG 问答流水线：检索 → 生成"""

    def __init__(self):
        self.retriever = AdvancedRetriever()

    async def query(
        self,
        question: str,
        history_messages: List[dict] = None,
    ) -> AsyncIterator[dict]:
        """执行 RAG 问答，流式返回

        Yields:
            dict: {"type": "token"|"sources"|"done", "content": ...}
        """
        # Step 1: 检索
        logger.info(f"RAG 查询: {question[:50]}...")
        retrieved = self.retriever.retrieve(question)

        if not retrieved:
            yield {"type": "token", "content": "抱歉，知识库中暂无与您问题相关的信息。请尝试换一种方式提问。\n\n建议：\n- 使用更具体的关键词\n- 检查知识库是否已上传相关文档"}
            yield {"type": "sources", "sources": []}
            yield {"type": "done"}
            return

        # Step 2: 流式生成
        sources = format_sources(retrieved)
        full_answer = ""

        async for token in generate_stream(question, retrieved, history_messages):
            full_answer += token
            yield {"type": "token", "content": token}

        # Step 3: 返回引用来源
        yield {"type": "sources", "sources": sources}
        yield {"type": "done"}

        logger.info(f"RAG 完成, 回答长度: {len(full_answer)}, 引用数: {len(sources)}")


# 全局单例
rag_chain = RAGChain()
