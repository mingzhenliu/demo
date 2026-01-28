---
description: 使用计划模板执行实施规划工作流以生成设计制品。
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
---

## 用户输入

```text
$ARGUMENTS
```

你**必须**在继续之前考虑用户输入（如果非空）。

## 概述

1. **设置**：从仓库根目录运行 `python3 .specify/scripts/python/setup-plan.py --json` 并解析 JSON 以获取 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH。对于参数中的单引号，如 "I'm Groot"，使用转义语法：例如 'I'\''m Groot'（或如果可能使用双引号："I'm Groot"）。

2. **加载知识库**：

   运行以下命令加载知识库配置：
   ```bash
   python3 .specify/scripts/python/load-knowledge.py plan
   ```

   脚本会输出：
   - ⚠️ 关键约束（架构原则、安全红线、API/测试规范）
   - 📋 需要读取的文档列表

   **你必须**：
   - 仔细阅读脚本输出的所有约束
   - 使用 Read 工具读取列出的每个文档
   - 如果 L0 文档缺失，立即阻止流程

3. **架构合规检查**：

   根据知识库约束执行合规检查。检查项来自步骤 2 输出的约束。

   **处理规则**：
   - ✅ 全部合规 → 继续
   - ⚠️ 需调整 → 修改设计后继续
   - ❌ CRITICAL 违规 → **阻止流程，报告违规项**

4. **技术雷达检查**：

   检查 plan 中的技术选型（如存在技术雷达文档）：
   - 对照禁用技术列表检查是否使用禁用技术
   - 新技术需在 plan.md 中说明选型理由

5. **加载上下文**：读取 FEATURE_SPEC 和 `.specify/memory/constitution.md`。加载 IMPL_PLAN 模板（已复制）。

6. **执行计划工作流**：遵循 IMPL_PLAN 模板中的结构以：
   - 填写技术上下文（将未知标记为 "NEEDS CLARIFICATION"）
   - 从章程填写章程检查章节
   - 评估门（如果违规未经证实则出错）
   - 阶段 0：生成 research.md（解决所有 NEEDS CLARIFICATION）
   - 阶段 1：生成 data-model.md、contracts/、quickstart.md
   - 阶段 1：通过运行代理脚本更新代理上下文
   - 重新评估设计后的章程检查

7. **停止并报告**：命令在阶段 2 规划后结束。报告分支、IMPL_PLAN 路径和生成的制品。

## 阶段

### 阶段 0：概述和研究

1. **从上面的技术上下文中提取未知**：
   - 对于每个 NEEDS CLARIFICATION → 研究任务
   - 对于每个依赖关系 → 最佳实践任务
   - 对于每个集成 → 模式任务

2. **代码库探索（可选，当存在现有代码时）**：

   如果仓库已有相关代码，并行启动 1-2 个 code-explorer 代理：

   ```text
   代理提示示例：
   - "查找与 {功能} 类似的现有功能并追踪其实现模式"
   - "映射 {目标模块} 的架构层和数据流"
   ```

   **注入知识上下文**：向代理提供 module_tree.json、service-catalog（如存在）

   代理返回后，阅读识别的关键文件，将发现整合到研究中。

3. **生成和调度研究代理**：

   ```text
   对于技术上下文中的每个未知：
     任务："为 {功能上下文} 研究 {未知}"
   对于每个技术选择：
     任务："在 {领域} 中查找 {技术} 的最佳实践"
   ```

4. **在 `research.md` 中合并发现**，使用格式：
   - 决策：[选择的内容]
   - 理由：[为什么选择]
   - 考虑的替代方案：[还评估了什么]

**输出**：research.md，所有 NEEDS CLARIFICATION 已解决

### 阶段 1：设计和合同

**先决条件：** `research.md` 完成

0. **架构设计（可选，复杂功能时启用）**：

   对于涉及多模块或需要架构决策的功能，启动 code-architect 代理：

   ```text
   代理提示：
   - "为 {功能} 设计架构，重点关注与现有 {模块} 的集成"
   ```

   **注入知识上下文**：architecture-principles、security-baseline、tech-radar、tech-stack、ADR 摘要

   **代理后合规检查**：

   | 检查 | 来源 | 严重级别 |
   |------|------|----------|
   | 分层架构合规 | L0/constitution/architecture-principles.md | CRITICAL |
   | 安全红线合规 | L0/constitution/security-baseline.md | CRITICAL |
   | 禁用技术检查 | L0/technology-radar/hold.md | CRITICAL |

   将代理输出作为后续设计的输入参考。

1. **从功能规范中提取实体** → `data-model.md`：
   - 实体名称、字段、关系
   - 来自需求的验证规则
   - 状态转换（如果适用）

2. **从功能需求生成 API 合同**：
   - 对于每个用户操作 → 端点
   - 使用标准 REST/GraphQL 模式
   - 将 OpenAPI/GraphQL 模式输出到 `/contracts/`
   - **必须符合知识库中的 API 设计规范**

3. **代理上下文更新**：
   - 运行 `python3 .specify/scripts/python/update-agent-context.py claude`
   - 这些脚本检测正在使用的 AI 代理
   - 更新适当的代理特定上下文文件
   - 仅添加当前计划中的新技术
   - 在标记之间保留手动添加

**输出**：data-model.md、/contracts/*、quickstart.md、代理特定文件

## 关键规则

- 使用绝对路径
- 对于门失败或未解决的澄清，出错
- **L0 知识库缺失时阻止流程**
- **遵守知识库脚本输出的所有约束**
- **CRITICAL 级别违规阻止流程**
- **禁止使用 HOLD 列表中的技术**