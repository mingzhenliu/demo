---
name: spec-summary
description: |
  生成 SpecKit SDD 流程的架构文档与工作总结。
  负责流程控制、上下文检测，委托 work-summarizer agent 纯生成文档。
allowed-tools:
  - Bash   # 检测 FEATURE_DIR、git 变更
  - Read   # 读取 SDD 文档
  - Task   # 委托给 work-summarizer agent
---
# Spec Summary Skill

生成 SDD 流程的架构文档与工作总结。

## 何时使用

- 完成功能开发后，准备提交代码前
- 需要生成功能模块的架构文档
- 需要记录本次会话的工作变更

## 用户输入

```text
$ARGUMENTS
```

用户可选：

- 空字符串：自动检测并生成
- `--force`: 强制重新生成
- `--minimal`: 生成简化版本

---

## 执行流程

### 第一步：检测 SDD 上下文

```bash
python3 .specify/scripts/python/check-prerequisites.py --json
```

| 返回状态         | 处理方式                                              |
| ---------------- | ----------------------------------------------------- |
| 无 FEATURE_DIR   | 检查 git 变更 → 有则提示初始化，无则返回"无需总结"   |
| FEATURE_DIR 为空 | 返回错误："请先运行 `/speckit.specify`"             |
| 无 spec.md       | 返回错误："流程不完整，请先运行 `/speckit.specify`" |
| 仅有 spec.md     | **基础模式**                                    |
| spec + plan      | **标准模式**                                    |
| 全部文件         | **完整模式**                                    |

### 第二步：检测 Git 变更

```bash
git diff --name-status HEAD
git ls-files --others --exclude-standard
```

### 第三步：并行读取可用文档

```bash
# 必需
Read: {FEATURE_DIR}/spec.md

# 标准模式/完整模式
Read: {FEATURE_DIR}/plan.md
Read: {FEATURE_DIR}/data-model.md (如存在)

# 完整模式
Read: {FEATURE_DIR}/tasks.md
Read: {FEATURE_DIR}/checklist.md (如存在)
```

### 第四步：构建生成参数

```json
{
  "mode": "basic|standard|full",
  "feature_dir": "{FEATURE_DIR}",
  "feature_name": "{从 spec.md 提取}",
  "has_data_model": true/false,
  "has_tasks": true/false,
  "git_changes": {
    "added": ["file1", "file2"],
    "modified": ["file3"],
    "deleted": []
  },
  "user_options": {
    "force": false,
    "minimal": false
  }
}
```

### 第五步：调用 Agent

```python
Task(
    subagent_type="work-summarizer",
    prompt=f"""生成 SpecKit 工作总结文档。

参数: {params}

SDD 文档内容:
{spec_content}
{plan_content if exists}
{tasks_content if exists}

请生成 {FEATURE_DIR}/summary.md"""
)
```

### 第六步：展示结果

| 状态    | 展示内容                       |
| ------- | ------------------------------ |
| success | 文件路径、模式、变更统计、摘要 |
| warning | 警告信息、文件路径             |
| error   | 错误信息、建议操作             |
| no-work | "无需要总结的内容"             |

---

## 错误处理矩阵

| 场景                    | 检测方式                  | 返回状态      |
| ----------------------- | ------------------------- | ------------- |
| 无 FEATURE_DIR + 无变更 | check-prerequisites       | no-work       |
| 无 FEATURE_DIR + 有变更 | check-prerequisites + git | error         |
| FEATURE_DIR 为空        | ls 检查                   | error         |
| 无 spec.md              | Read 失败                 | error         |
| 仅有 spec.md            | 文件存在                  | basic-mode    |
| spec + plan             | 文件存在                  | standard-mode |
| 全部文件                | 文件存在                  | full-mode     |

---

## 降级处理

Agent 调用失败时：

1. 检查 FEATURE_DIR 是否存在
2. 如果存在且有 spec.md，读取并生成简化版
3. 向用户说明降级情况

---

## 相关文档

- [work-summarizer agent](../../agents/work-summarizer.md) - 纯文档生成器
- [speckit.summary 命令](../../commands/speckit.summary.md) - 用户入口
