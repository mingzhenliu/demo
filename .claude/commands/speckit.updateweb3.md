---
description: 从模板仓库增量更新 SpecKit 核心文件，不覆盖项目配置
---
## 概述

从 AI-SDD-template 模板仓库增量更新 SpecKit 核心文件，只更新白名单中的文件。

白名单配置存放在 L0 知识库：`.knowledge/upstream/L0-enterprise/speckit-config/update-whitelist.json`，具体文件类别和内容由配置文件定义，可通过修改 JSON 配置动态调整。

## 执行流程

```bash
python3 .knowledge/upstream/L0-enterprise/speckit-config/scripts/update-speckit.py
```

1. 从 L0 读取白名单配置
2. 克隆模板仓库到临时目录
3. 按白名单匹配文件并更新
4. 显示更新清单
5. 清理临时目录

## 使用方法

```bash
# 执行更新
python3 .knowledge/upstream/L0-enterprise/speckit-config/scripts/update-speckit.py

# 模拟运行（不实际更新）
python3 .knowledge/upstream/L0-enterprise/speckit-config/scripts/update-speckit.py --dry-run
```

## 输出示例

```
═══════════════════════════════════════════════════
           SpecKit 增量更新
═══════════════════════════════════════════════════

[INFO] 从 L0 加载白名单: .knowledge/upstream/.../update-whitelist.json
[INFO] 白名单包含 42 个模式

[INFO] 正在克隆模板仓库: git@github.com:WeTechHK/AI-SDD-template.git
[OK] 模板仓库克隆完成

[INFO] 找到 28 个文件待更新

📋 更新清单:
[OK]   .claude/agents/code-reviewer.md
[OK]   .claude/commands/speckit.implement.md
[OK]   .claude/commands/speckit.plan.md
[OK]   .specify/scripts/python/load-knowledge.py

═══════════════════════════════════════════════════
更新完成: 4 个已更新, 24 个已跳过, 0 个错误
═══════════════════════════════════════════════════
```

## 自定义白名单

如需自定义，在项目根目录创建 `.speckit-update.json`:

```json
{
  "whitelist": {
    "agents": [".claude/agents/*.md"],
    "commands": [".claude/commands/speckit.*.md"]
  }
}
```

本地白名单会与 L0 白名单合并。

## 保护文件

以下文件不会被覆盖：

- `.specify/knowledge-config.json` - 项目知识库配置(未来)
- `.specify/local-override.json` - 本地配置覆盖
- `.specify/specs/*` - 功能规格
- `.specify/designs/*` - 设计文档
- `.specify/memory/*` - 项目记忆
