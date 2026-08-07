"""LLM 对话生成器 - 百炼 ChatTongyi + 流式输出"""
from typing import AsyncIterator, List
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from loguru import logger

from app.core.config import get_settings
from app.rag.prompts import SYSTEM_PROMPT

settings = get_settings()


def get_llm(streaming: bool = True):
    """获取百炼 LLM 实例"""
    return ChatTongyi(
        model=settings.llm_model,
        dashscope_api_key=settings.dashscope_api_key,
        temperature=0.3,
        top_p=0.8,
        streaming=streaming,
    )


def build_messages(
    question: str,
    context_docs: List[tuple],
    history_messages: List[dict] = None,
) -> list:
    """构建发给 LLM 的消息列表

    Args:
        question: 用户问题
        context_docs: [(Document, score), ...] 检索到的文档片段
        history_messages: [{"role":"user"|"assistant","content":"..."}, ...]

    Returns:
        LangChain Message 列表
    """
    # 构建上下文
    context_parts = []
    for i, (doc, score) in enumerate(context_docs, 1):
        title = doc.metadata.get("source_file", doc.metadata.get("source", "未知文档"))
        context_parts.append(
            f"【参考资料 {i}】来源: {title} (相关度: {score:.2f})\n{doc.page_content}"
        )
    context = "\n\n".join(context_parts)

    # 构建历史
    history = ""
    if history_messages:
        recent = history_messages[-8:]  # 最近 4 轮 (8条)
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "助手"
            history += f"{role}: {msg['content']}\n"

    # 构建 System Prompt
    system_content = SYSTEM_PROMPT.format(
        context=context,
        history=history or "（无历史对话）",
        question=question,
    )

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=question),
    ]


async def generate_stream(
    question: str,
    context_docs: List[tuple],
    history_messages: List[dict] = None,
) -> AsyncIterator[str]:
    """流式生成回答

    Yields:
        str: 每次 yield 一个 token 片段
    """
    messages = build_messages(question, context_docs, history_messages)
    llm = get_llm(streaming=True)

    logger.info(f"开始流式生成, 消息长度: {len(str(messages))}")

    try:
        async for chunk in llm.astream(messages):
            content = chunk.content
            if content:
                yield content
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        yield f"\n\n[生成失败: {str(e)}]"


def format_sources(context_docs: List[tuple]) -> list:
    """将检索结果格式化为前端可用的引用来源列表"""
    sources = []
    for doc, score in context_docs:
        title = doc.metadata.get("source_file", doc.metadata.get("source", "未知文档"))
        chunk_idx = doc.metadata.get("chunk_index", 0)
        sources.append({
            "document_title": title,
            "chunk_index": chunk_idx,
            "content": doc.page_content[:200],  # 前 200 字预览
            "score": round(score, 4),
        })
    return sources
