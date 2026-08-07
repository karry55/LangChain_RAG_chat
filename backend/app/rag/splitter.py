"""中文语义优化的文本分块器"""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings

settings = get_settings()


def create_splitter(
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> RecursiveCharacterTextSplitter:
    """创建中文优化的递归文本分块器"""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        # 分隔符优先级: 段落 → 换行 → 中文标点 → 空格 → 字符
        separators=[
            "\n\n",     # 段落
            "\n",       # 换行
            "。",       # 句号
            "！", "？", # 感叹/疑问
            "；",       # 分号
            "，",       # 逗号
            " ",        # 空格
            "",         # 字符
        ],
        length_function=len,
        is_separator_regex=False,
    )


def split_documents(
    documents: List[Document],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Document]:
    """将文档列表分块，保留元数据"""
    splitter = create_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(documents)

    # 为每个 chunk 添加序号
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks
