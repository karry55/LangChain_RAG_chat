"""文档加载器工厂 - 根据文件类型选择对应的 LangChain Loader"""
from typing import List
from langchain_core.documents import Document
from loguru import logger


def load_document(file_path: str, file_type: str) -> List[Document]:
    """根据文件类型加载文档，返回 LangChain Document 列表"""
    logger.info(f"加载文档: {file_path} (类型: {file_type})")

    loaders = {
        "pdf": _load_pdf,
        "docx": _load_docx,
        "xlsx": _load_xlsx,
        "csv": _load_csv,
        "txt": _load_txt,
        "md": _load_md,
    }

    loader_func = loaders.get(file_type.lower())
    if loader_func is None:
        raise ValueError(f"不支持的文件类型: {file_type}，支持的类型: {list(loaders.keys())}")

    docs = loader_func(file_path)

    # 为每个 Document 设置来源元数据
    doc_title = file_path.replace("\\", "/").split("/")[-1]
    for doc in docs:
        if not doc.metadata:
            doc.metadata = {}
        doc.metadata["source_file"] = doc_title
        doc.metadata["file_type"] = file_type

    logger.info(f"文档加载完成，共 {len(docs)} 个部分")
    return docs


def _load_pdf(file_path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import PDFPlumberLoader
        loader = PDFPlumberLoader(file_path)
        return loader.load()
    except ImportError:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        return loader.load()


def _load_docx(file_path: str) -> List[Document]:
    from langchain_community.document_loaders import Docx2txtLoader
    loader = Docx2txtLoader(file_path)
    return loader.load()


def _load_xlsx(file_path: str) -> List[Document]:
    """Excel 加载 - 逐行转为文档"""
    import pandas as pd
    docs = []
    xl = pd.ExcelFile(file_path)
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # 将每行转为 JSON 字符串作为文档内容
        for idx, row in df.iterrows():
            content = row.to_json(force_ascii=False)
            docs.append(Document(
                page_content=content,
                metadata={"sheet": sheet_name, "row": idx}
            ))
    return docs


def _load_csv(file_path: str) -> List[Document]:
    from langchain_community.document_loaders import CSVLoader
    loader = CSVLoader(file_path, encoding="utf-8")
    return loader.load()


def _load_txt(file_path: str) -> List[Document]:
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def _load_md(file_path: str) -> List[Document]:
    """Markdown 文件加载 - 使用 TextLoader (Markdown 本质就是纯文本)"""
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()
