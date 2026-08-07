# /rebuild-app — 重新打包 RAG 知识库问答系统前端

请帮我执行以下步骤来重新打包前端：

## 步骤

1. **运行构建命令**：
   ```bash
   cd frontend && npm run build
   ```
   这会在 `frontend/dist/` 文件夹中生成打包后的静态文件。

2. **检查结果**：确认 `frontend/dist/` 文件夹生成成功。

3. **告知用户**：
   - ✅ 打包完成！
   - 📁 打包文件位置：`frontend/dist/` 文件夹
   - 📄 入口文件：`frontend/dist/index.html`
   - ⚠️ 打包后的纯前端文件需要配合后端 API 使用，不能单独运行

## 常见问题

- **构建失败**：检查 TypeScript 编译错误
- **后端呢？**：打包只针对前端，后端需要用 Python 启动
