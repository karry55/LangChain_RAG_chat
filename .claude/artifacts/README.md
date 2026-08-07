# 通行证目录

这个目录存放质量检查的通行证文件，由 tester 和 quality-engineer agent 自动生成。

- `test-passed.json` — 测试通行证（tester agent 生成）
- `quality-passed.json` — 质量通行证（quality-engineer agent 生成）

通行证有效期：30 分钟。过期后需要重新检查。
提交成功后通行证自动清理。

⚠️ 此目录下的 .json 文件已在 .gitignore 中排除，不会被提交到 Git。
