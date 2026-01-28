---
description: 管理多级知识库（L0 企业级、L1 项目级）的挂载、同步和状态查看。
---

## 概述

管理 AI-SDD 多级知识库系统，支持知识库的挂载、同步和状态查看。

## 知识库配置

```yaml
L0:
  name: 企业级知识库
  remote: L0-knowledge
  repo: git@github.com:WeTechHK/knowledge-enterprise-standards.git
  prefix: .knowledge/upstream/L0-enterprise
  branch: main
  required: true

L1:
  name: 项目级知识库
  remote: L1-knowledge
  prefix: .knowledge/upstream/L1-project
  branch: main
  required: true
  # 注意: L1 仓库地址必须由用户提供
```

## 执行流程

### 1. 检查当前状态

执行以下命令检查知识库状态：

```bash
# 检查是否在 git 仓库中
git rev-parse --is-inside-work-tree 2>/dev/null

# 检查 L0 是否已挂载
ls -d .knowledge/upstream/L0-enterprise 2>/dev/null

# 检查 L1 是否已挂载
ls -d .knowledge/upstream/L1-project 2>/dev/null

# 检查远程配置
git remote -v | grep -E "(L0-knowledge|L1-knowledge)"
```

### 2. 根据状态给出建议

#### 场景 A: 两个知识库都未挂载

显示状态并给出详细挂载建议：

```markdown
## 知识库状态

| 级别 | 状态 | 路径 |
|------|------|------|
| L0 企业级 | ❌ 未挂载 | `.knowledge/upstream/L0-enterprise` |
| L1 项目级 | ❌ 未挂载 | `.knowledge/upstream/L1-project` |

## 建议操作

您需要挂载知识库才能使用完整的 AI-SDD 功能。

**挂载知识库需要：**
1. 确保工作区干净（无未提交的修改）
2. L0 企业级知识库将自动使用默认地址
3. **L1 项目级知识库需要您提供地址**

**请提供您项目的 L1 知识库地址：**

L1 项目级知识库包含项目特有的：
- 业务领域知识 (business/)
- 架构决策记录 (architecture/)
- 项目技术规范 (standards/)

格式示例: `git@github.com:YourOrg/your-project-knowledge.git`
```

**然后使用 AskUserQuestion 工具询问用户 L1 地址。**

获取 L1 地址后，执行挂载：

```bash
# 检查工作区是否干净
git diff-index --quiet HEAD -- || echo "ERROR: 请先提交所有修改"

# 挂载 L0
git remote add L0-knowledge git@github.com:WeTechHK/knowledge-enterprise-standards.git
git subtree add --prefix=.knowledge/upstream/L0-enterprise L0-knowledge main --squash -m "chore: mount L0 enterprise knowledge base"

# 挂载 L1（使用用户提供的地址）
git remote add L1-knowledge <用户提供的L1地址>
git subtree add --prefix=.knowledge/upstream/L1-project L1-knowledge main --squash -m "chore: mount L1 project knowledge base"
```

#### 场景 B: 只有 L0 挂载，L1 未挂载

```markdown
## 知识库状态

| 级别 | 状态 | 路径 |
|------|------|------|
| L0 企业级 | ✅ 已挂载 | `.knowledge/upstream/L0-enterprise` |
| L1 项目级 | ❌ 未挂载 | `.knowledge/upstream/L1-project` |

## 建议操作

L0 企业级知识库已就绪，但 **缺少 L1 项目级知识库**。

L1 知识库对于项目开发至关重要，包含：
- 项目特定的业务领域知识
- 架构决策记录 (ADR)
- 项目技术栈规范

**请提供您项目的 L1 知识库地址：**
```

**使用 AskUserQuestion 工具询问 L1 地址，然后执行挂载。**

#### 场景 C: 两个知识库都已挂载

```markdown
## 知识库状态

| 级别 | 状态 | 路径 |
|------|------|------|
| L0 企业级 | ✅ 已挂载 | `.knowledge/upstream/L0-enterprise` |
| L1 项目级 | ✅ 已挂载 | `.knowledge/upstream/L1-project` |

### 远程配置
- L0-knowledge: git@github.com:WeTechHK/knowledge-enterprise-standards.git
- L1-knowledge: <当前配置的地址>

## 知识库内容

### L0 企业级
- `constitution/` - 技术宪法
- `standards/` - 编码规范
- `governance/` - 治理流程
- `technology-radar/` - 技术雷达

### L1 项目级
- `business/` - 业务领域
- `architecture/` - 架构知识
- `standards/` - 项目规范
```

**然后询问用户是否需要同步知识库。**

### 3. 同步知识库

如果用户确认需要同步：

```bash
# 检查工作区
git diff-index --quiet HEAD -- || echo "ERROR: 请先提交所有修改"

# 同步 L0
git subtree pull --prefix=.knowledge/upstream/L0-enterprise L0-knowledge main --squash -m "chore: sync L0 enterprise knowledge base"

# 同步 L1
git subtree pull --prefix=.knowledge/upstream/L1-project L1-knowledge main --squash -m "chore: sync L1 project knowledge base"
```

同步完成后显示结果。

## 错误处理

### 错误: 不是 git 仓库

```markdown
## 错误

当前目录不是 git 仓库。

请先初始化 git 仓库：
\`\`\`bash
git init
git add .
git commit -m "init: 初始化项目"
\`\`\`
```

### 错误: 工作区有未提交的修改

```markdown
## 错误

检测到未提交的更改。Git subtree 操作需要干净的工作区。

请先提交所有修改：
\`\`\`bash
git add .
git commit -m "your commit message"
\`\`\`

或者使用 `/git-commit` 命令智能提交。
```

### 错误: 没有仓库访问权限

```markdown
## 错误

无法访问知识库仓库，请确认：

1. 已配置 SSH key 并添加到 GitHub
2. SSH key 有仓库的读取权限
3. 仓库地址正确

测试 SSH 连接：
\`\`\`bash
ssh -T git@github.com
\`\`\`
```

## 输出格式

### 挂载成功

```markdown
## 知识库挂载完成

| 操作 | 级别 | 状态 |
|------|------|------|
| 挂载 | L0 企业级 | ✅ 成功 |
| 挂载 | L1 项目级 | ✅ 成功 |

知识库已就绪，可以开始使用 AI-SDD 工作流。

提示：使用 `/speckit.knowledge` 同步知识库更新。
```

### 同步成功

```markdown
## 知识库同步完成

| 操作 | 级别 | 状态 |
|------|------|------|
| 同步 | L0 企业级 | ✅ 已是最新 |
| 同步 | L1 项目级 | ✅ 更新 3 个文件 |
```

## 注意事项

1. **L1 地址必填**：L1 知识库地址必须由用户提供，每个项目应有独立的知识库
2. **干净工作区**：挂载和同步都需要干净的 git 工作区
3. **SSH 权限**：需要有知识库仓库的 SSH 访问权限
4. **不自动推送**：挂载和同步产生的提交不会自动 push
