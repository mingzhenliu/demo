---
description: 生成模块架构文档与工作总结，输出到 FEATURE_DIR/summary.md（委托模式）
---
## 用户输入

```text
$ARGUMENTS
```

你**必须**在继续之前考虑用户输入（如果非空）。

## 概述

生成当前模块的**架构文档 + 工作总结**，写入 `{FEATURE_DIR}/summary.md`。

**执行模式**: 委托给 `spec-summary` skill，后者调用 `work-summarizer` agent 在独立上下文中执行，降低主会话上下文占用。

**何时使用**: 完成开发任务后、执行 git commit 之前

**输出文件**: `{FEATURE_DIR}/summary.md`

---

## 调用方式

```text
/speckit.summary [options]
```

选项：

- `--force`: 强制重新生成（覆盖现有）
- `--minimal`: 生成简化版本

---

## 预期输出

### 成功

```
✅ 工作总结已生成

📁 文件: {FEATURE_DIR}/summary.md
📊 模式: {basic|standard|full}
📝 变更: {X} 新增, {Y} 修改, {Z} 删除

下一步: 使用 /git-commit 提交代码
```

### 常见错误

| 错误           | 原因       | 解决方案                  |
| -------------- | ---------- | ------------------------- |
| 无 FEATURE_DIR | 未初始化   | 运行 `/speckit.specify` |
| 无 spec.md     | 流程不完整 | 运行 `/speckit.specify` |
