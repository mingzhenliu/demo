---
description: 根据 git diff 智能生成符合规范的提交信息并执行提交。
---
## 概述

根据当前 git 变更，智能生成符合规范格式的提交信息并执行 git commit。

## 执行流程

### 1. 检查工作区状态

```bash
git status
git diff --staged
git diff
```

如果没有任何变更，提示用户并退出。

### 2. 分析变更内容

分析所有变更文件，理解：

- 变更涉及的模块/功能
- 变更的性质（新功能、修复、重构等）
- 变更的影响范围

### 3. 生成提交信息

**格式要求**：

```
type(scope): 简短描述

详细说明（可选）

🤖 Generated with git username

Co-Authored-By: git username
```

**type 类型**：

| type     | 说明      | 示例                              |
| -------- | --------- | --------------------------------- |
| feat     | 新功能    | feat(auth): 添加用户登录功能      |
| fix      | 修复 Bug  | fix(api): 修复请求超时问题        |
| docs     | 文档变更  | docs(readme): 更新安装说明        |
| style    | 代码格式  | style(lint): 统一代码缩进         |
| refactor | 重构      | refactor(utils): 优化工具函数结构 |
| test     | 测试相关  | test(auth): 添加登录单元测试      |
| chore    | 构建/工具 | chore(deps): 升级依赖版本         |
| perf     | 性能优化  | perf(query): 优化数据库查询       |

**scope 规则**：

- 使用受影响的模块/目录名
- 多模块时使用最主要的模块
- 通用变更可省略 scope

**描述规则**：

- 使用中文，简洁明了
- 不超过 50 字符
- 使用动词开头：添加、修复、更新、优化、移除、重构

### 4. 执行提交

```bash
# 暂存所有变更（如果用户确认）
git add -A

# 执行提交
git commit -m "$(cat <<'EOF'
type(scope): 简短描述

详细说明

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 5. 验证结果

```bash
git status
git log -1 --oneline
```

## 交互流程

1. **展示变更摘要**：列出所有变更文件和类型
2. **生成提交信息**：根据分析结果生成符合规范的提交信息
3. **确认提交**：展示完整提交信息，等待用户确认
4. **执行提交**：用户确认后执行 git add 和 git commit
5. **报告结果**：展示提交成功信息和 commit hash

## 注意事项

- 不要自动 push 到远程仓库
- 如果检测到敏感文件（.env、credentials 等），需警告用户
- 如果变更过大（超过 10 个文件），建议用户考虑拆分提交
- 遵循现有项目的提交历史风格
