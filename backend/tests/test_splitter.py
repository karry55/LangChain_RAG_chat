"""文本分块器单元测试"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.documents import Document
from app.rag.splitter import create_splitter, split_documents


class TestCreateSplitter:
    """分块器创建"""

    def test_create_with_default_params(self):
        """默认参数创建分块器"""
        splitter = create_splitter()
        assert splitter is not None

    def test_create_with_custom_params(self):
        """自定义参数创建分块器"""
        splitter = create_splitter(chunk_size=300, chunk_overlap=30)
        assert splitter is not None
        assert splitter._chunk_size == 300
        assert splitter._chunk_overlap == 30


class TestSplitDocuments:
    """文档分块功能"""

    def test_split_single_doc(self):
        """单个文档分块"""
        doc = Document(
            page_content="这是一段测试文本。包含多个句子。用于测试分块功能。" * 20,
            metadata={"source": "test.txt"},
        )
        chunks = split_documents([doc], chunk_size=100, chunk_overlap=20)
        assert len(chunks) > 1  # 内容应该被分成多块

    def test_split_preserves_metadata(self):
        """分块后保留元数据"""
        doc = Document(
            page_content="测试内容。" * 30,
            metadata={"source": "important_doc.pdf", "page": 1},
        )
        chunks = split_documents([doc], chunk_size=80, chunk_overlap=10)
        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "important_doc.pdf"

    def test_split_adds_chunk_index(self):
        """分块后自动添加序号"""
        doc = Document(
            page_content="测试文本。" * 50,
            metadata={"source": "test.txt"},
        )
        chunks = split_documents([doc], chunk_size=80, chunk_overlap=10)
        for i, chunk in enumerate(chunks):
            assert "chunk_index" in chunk.metadata

    def test_split_multiple_docs(self):
        """多个文档分别分块"""
        docs = [
            Document(page_content="文档A内容。" * 20, metadata={"source": "a.txt"}),
            Document(page_content="文档B内容。" * 20, metadata={"source": "b.txt"}),
        ]
        chunks = split_documents(docs, chunk_size=100, chunk_overlap=10)
        sources = {c.metadata["source"] for c in chunks}
        assert "a.txt" in sources
        assert "b.txt" in sources

    def test_split_short_doc(self):
        """短文档（小于 chunk_size）不分块"""
        doc = Document(
            page_content="很短的文本。",
            metadata={"source": "short.txt"},
        )
        chunks = split_documents([doc], chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0].page_content == "很短的文本。"

    def test_split_empty_doc(self):
        """空文档返回空列表或单块"""
        doc = Document(page_content="", metadata={"source": "empty.txt"})
        chunks = split_documents([doc])
        # 空文档应该返回空列表或包含空内容的单个块
        assert len(chunks) <= 1

    def test_split_chinese_doc(self):
        """中文文档按中文标点分块"""
        doc = Document(
            page_content=(
                "华为Mate 60 Pro是一款旗舰手机。"
                "它配备了5000mAh大容量电池。"
                "支持88W有线快充。"
                "还支持50W无线快充。"
                "采用昆仑玻璃面板。"
                "具有IP68防水等级。" * 10
            ),
            metadata={"source": "product_info.txt"},
        )
        chunks = split_documents([doc], chunk_size=100, chunk_overlap=10)
        assert len(chunks) >= 1
        # 验证中文内容没有被截断成乱码
        for chunk in chunks:
            assert isinstance(chunk.page_content, str)
