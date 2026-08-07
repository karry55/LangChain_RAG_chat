# /run-app — 启动 RAG 知识库问答系统

请帮我执行以下步骤来启动项目：

## 项目架构

本项目是前后端分离的全栈应用：
- **后端**：Python FastAPI（端口 8000）
- **前端**：React + Vite（端口 5173）
- **数据库**：SQLite（`backend/rag_kb.db`，零配置）
- **向量库**：ChromaDB（`backend/data/chroma/`，嵌入式运行）

## 步骤

1. **检查后端依赖**：确认 Python 依赖已安装。
   ```bash
   cd backend && pip install -r requirements.txt -q
   ```

2. **启动后端服务**：
   ```bash
   cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **启动前端服务**（另开终端）：
   ```bash
   cd frontend && npm install && npm run dev
   ```

4. **打开浏览器**：
   ```bash
   start http://localhost:5173
   ```

5. **告知用户**：
   - ✅ 系统已启动
   - 🔗 前端：http://localhost:5173
   - 📖 API 文档：http://localhost:8000/docs
   - 👤 管理员：admin / 123456
   - ⚠️ 关闭：在两个终端分别 Ctrl+C

## 一键启动

也可以双击项目根目录的 `start.bat` 一键启动。

## 常见问题

- **端口被占用**：先 `taskkill //F //IM python.exe` 和 `taskkill //F //IM node.exe`
- **前端依赖缺失**：运行 `cd frontend && npm install`
- **后端依赖缺失**：运行 `cd backend && pip install -r requirements.txt`
- **向量库异常**：删除 `backend/data/chroma/` 目录后重启
- **数据库异常**：删除 `backend/rag_kb.db` 后重启（会丢失数据）
