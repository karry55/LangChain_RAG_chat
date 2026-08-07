# RAG 企业级知识库问答系统

> 毕业设计项目 — 基于 LangChain + 阿里云百炼的智能问答系统

[![技术栈](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![前端框架](https://img.shields.io/badge/React-18-blue)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)](https://www.langchain.com/)
[![大模型](https://img.shields.io/badge/LLM-通义千问-purple)](https://bailian.console.aliyun.com/)

一个面向电商场景的企业级 RAG（检索增强生成）知识库问答系统。用户可以上传商品文档，系统自动解析、分块、向量化存入知识库，用户通过浏览器以自然语言提问，系统从知识库中检索相关片段，结合 LLM 生成准确回答并标注引用来源。

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📚 知识库管理 | 上传 PDF/Word/Excel/Markdown 等文档，自动解析分块向量化（仅管理员） |
| 💬 智能问答 | 基于 RAG 的流式问答（SSE），回答中标注引用来源片段 |
| 👥 多用户支持 | 用户注册登录，独立会话管理，历史记录持久化 |
| 🔐 权限控制 | 管理员（admin/123456）管理知识库，普通用户只能问答 |
| 📎 引用溯源 | LLM 回答中标注 `[来源X]`，前端展示原文片段和相似度 |
| 🚀 企业级优化 | Embedding 缓存、MMR 去重、查询重写、流式输出 |

---

## 🏗️ 技术架构

```
浏览器 (React + Ant Design)
    │
    ├── HTTP/SSE ──→ FastAPI 网关 (JWT + CORS + 限流)
    │                    │
    │    ┌───────────────┼───────────────┐
    │    ▼               ▼               ▼
    │  RAG 管道      用户服务        文档服务
    │  (LangChain)   (SQLAlchemy)    (异步处理)
    │    │               │               │
    │    ├── 查询重写    ├── 注册登录     ├── 文档解析
    │    ├── 向量检索    ├── JWT 认证     ├── 文本分块
    │    ├── MMR 去重    └── 角色权限     ├── 向量嵌入
    │    ├── 重排序                       └── ChromaDB
    │    └── LLM 生成 (百炼 qwen-plus)
    │
    ├── PostgreSQL/SQLite (业务数据)
    ├── ChromaDB (向量存储)
    └── LRU + DiskCache (缓存)
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- 阿里云百炼 API Key（[免费注册](https://bailian.console.aliyun.com/)）

### 1. 克隆项目

```bash
git clone https://gitee.com/liang-kailin/langchainragvibe.git
cd langchainragvibe
```

### 2. 配置 API Key

编辑 `backend/.env`（复制 `.env` 到 `backend/` 目录下）：

```bash
DASHSCOPE_API_KEY=你的百炼API-Key
LLM_MODEL=qwen-plus
```

### 3. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 4. 启动服务

**方式一：一键启动**

双击项目根目录的 `start.bat`。

**方式二：手动启动**

终端 1（后端）：
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

终端 2（前端）：
```bash
cd frontend
npm run dev
```

### 5. 打开浏览器

> **http://localhost:5173**

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | 123456 | 管理员（可管理知识库） |
| 自行注册 | — | 普通用户（只能问答） |

---

## 📁 项目结构

```
langchainragvibe/
├── backend/                    # 后端
│   ├── app/
│   │   ├── api/               # API 路由（auth, chat, knowledge, conversation）
│   │   ├── core/              # 核心配置（config, security, database）
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── rag/               # RAG 核心管道
│   │   │   ├── loader.py      # 文档加载器
│   │   │   ├── splitter.py    # 文本分块器
│   │   │   ├── embedder.py    # 向量嵌入（百炼 API + 缓存）
│   │   │   ├── retriever.py   # 检索器（向量 + MMR）
│   │   │   ├── generator.py   # LLM 生成器（流式）
│   │   │   └── chain.py       # RAG 流水线编排
│   │   └── main.py            # FastAPI 入口
│   ├── tests/                 # 后端测试（pytest）
│   └── requirements.txt
├── frontend/                   # 前端
│   └── src/
│       ├── pages/             # 页面（Chat, KnowledgeBase, Login, Profile）
│       ├── components/        # 组件（Layout, SourceCitation）
│       ├── stores/            # Zustand 状态管理
│       ├── api/               # API 调用 + SSE 解析
│       └── __tests__/         # 前端测试（Vitest）
├── .claude/
│   ├── commands/              # Claude Code 斜杠命令
│   └── agents/                # Claude Code 子代理
├── start.bat                  # 一键启动脚本
└── README.md
```

---

## 🧪 运行测试

```bash
# 后端测试（pytest）
cd backend && python -m pytest tests/ -v

# 前端测试（Vitest）
cd frontend && npx vitest run
```

当前测试覆盖：**50 个用例全部通过**
- 后端 30 个（密码哈希、JWT、文本分块、Prompt 模板）
- 前端 20 个（认证状态管理、会话消息管理）

---

## 📝 文档格式支持

| 格式 | 扩展名 | 
|------|--------|
| PDF | `.pdf` |
| Word | `.docx` |
| Excel | `.xlsx` |
| CSV | `.csv` |
| 纯文本 | `.txt` |
| Markdown | `.md` |

---

## 🔧 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DASHSCOPE_API_KEY` | 百炼 API Key | — |
| `LLM_MODEL` | 对话模型 | `qwen-plus` |
| `EMBEDDING_MODEL` | 嵌入模型 | `text-embedding-v3` |
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./rag_kb.db` |
| `VECTOR_STORE` | 向量数据库 | `chromadb` |
| `SECRET_KEY` | JWT 密钥 | `rag-enterprise-secret-key-2024` |

---

## 📄 License

MIT — 毕业设计项目，仅供学习参考。
