---
name: finalize
description: 结尾操作 — 更新上下文记录和 README，提交并推送到远端
allowed-tools: [Bash, Read, Edit, Write, Glob, Grep]
---

# 结尾操作

当用户说"结尾操作"/"收尾"/"推送"/"finalize"时，执行以下三步：

## 步骤

1. **更新 `EABI_CONTEXT.md`** — 把当前会话的新改动追加到"后续新增功能"章节，并在 TODO 列表中勾选已完成项
2. **更新 `README.md`** — 把新功能要点合并到版本历史 `V20260525` 条目中
3. **Git 提交并推送** — `git add` 变更文件，写简洁的中文 commit message，`git push` 到远端

## 规则

- 仅更新 `EABI_CONTEXT.md` 和 `README.md`，不提交其他文件（除非用户要求）
- commit message 用中文，格式：`docs: <简述>`
- 推送前确认当前分支是 `eabi兼容`
- 如果用户当前不在 `eabi兼容` 分支，先询问
