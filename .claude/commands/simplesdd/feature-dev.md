---
description: 具有代码库理解、架构重点和知识库集成的引导式功能开发
argument-hint: 可选的功能描述
---
# 功能开发

你正在帮助开发者实现一个新功能。遵循系统化的方法：深入理解代码库，识别并询问所有未充分说明的细节，设计优雅的架构，然后实现。

## 核心原则

- **提出澄清问题**：识别所有歧义、边缘情况和未充分说明的行为。提出具体、明确的问题而不是做出假设。等待用户回答后再继续实现。在早期提问（理解代码库之后，设计架构之前）。
- **行动前理解**：首先阅读和理解现有代码模式
- **阅读代理识别的文件**：启动代理时，要求它们返回最重要的文件列表。代理完成后，阅读这些文件以在继续之前建立详细的上下文。
- **简单优雅**：优先考虑可读、可维护、架构合理的代码
- **使用 TodoWrite**：全程跟踪所有进度
- **TDD原则**：如果有必要，使用测试驱动开发原则。
- **知识库合规**：确保所有设计和实现要符合章程的权威性，L0/L1/L2 知识库约束，需要加载文档的时候要加载。
- **遵守文档规范要求**

## 目录结构

每个功能在 `specs/` 目录下创建一个子目录，命名格式为 `###-short-name`：

```
specs/
└── 001-user-auth/
    ├── spec.md           # 功能规格（阶段 1 输出）
    ├── plan.md           # 实施计划（阶段 4 输出）
    ├── research.md       # 研究文档（阶段 2 输出）
    └── contracts/        # API 契约（阶段 4 输出）
```

## 文档规范

每个阶段完成后,必须按照指定格式保存文档到功能目录。

**模板位置**: `.specify/templates/`

- `spec-template.md` - 功能规格模板
- `plan-template.md` - 实施计划模板

**文档保存快速参考**:

| 阶段    | 输出文档           | 模板             | 关键内容                                         |
| ------- | ------------------ | ---------------- | ------------------------------------------------ |
| 1: 发现 | `spec.md`        | spec-template.md | 用户场景、需求(FR-xxx)、实体、成功标准           |
| 2: 探索 | `research.md`    | 无               | 代码模式、关键文件(5-10个)、架构见解             |
| 3: 澄清 | 更新 `spec.md`   | -                | 解决所有 `[NEEDS CLARIFICATION]`标记           |
| 4: 架构 | `plan.md`        | plan-template.md | 技术上下文、架构设计、数据流、实施步骤、合规检查 |
| 5: 实施 | 源代码             | -                | 按plan.md实施                                    |
| 6: 审查 | -                  | -                | 代码审查(无新文档)                               |
| 7: 总结 | 追加到 `plan.md`, 生成独立的 `summary.md`| -                | 构建内容、决策、合规状态、修改文件、后续步骤     |

## 知识库集成

此工作流与多级知识空间（L0/L1/L2）集成：

| 级别 | 来源                                   | 优先级         | 缺失时处理 |
| ---- | -------------------------------------- | -------------- | ---------- |
| 章程 | `.specify/memory/constitution.md`    | **最高** | 阻止工作流 |
| L0   | `.knowledge/upstream/L0-enterprise/` | CRITICAL       | 阻止工作流 |
| L1   | `.knowledge/upstream/L1-project/`    | Required       | 警告并继续 |
| L2   | `.knowledge/`                        | Optional       | 静默跳过   |

**知识库加载方式**：每个阶段通过脚本加载所需文档：

```bash
python3 .specify/scripts/python/load-knowledge.py <phase>
# 例如：fd-discovery, fd-exploration, fd-architecture, fd-implementation
```

脚本会输出关键约束和需要读取的文档列表。

---

## 🚨 章程权威（不可协商）

> **项目章程（`.specify/memory/constitution.md`）具有最高权威**

**优先级**：章程 > L0 > L1 > L2 > 用户偏好

**强制规则**：

- 章程冲突 → 自动升级为 **CRITICAL**，必须修改设计
- ❌ 绝不稀释、重新解释或忽略章程原则
- ❌ 绝不以"用户要求"为由绕过章程
- 如需修改章程 → 必须先退出 `/feature-dev`，单独进行章程审查
- **注入宪章到上下文**：阶段 1（发现）→ 阶段 4（架构设计）→ 阶段 5（实现）→ 阶段 7（总结）

---

## 阶段 0：初始化

**目标**：创建功能目录并初始化文档

**操作**：

1. **明确创建功能目录**：

   ```bash
   python3 .specify/scripts/python/create-simple-feature.py --json "功能描述" --short-name "short-name"
   ```

   **必需参数**：

   - `--short-name "name"`：**必须指定**短名称（2-4 个单词，用连字符分隔，如 "email-management"）

   可选参数：

   - `--number N`：指定功能编号（不指定则自动递增）

   **示例**：

   ```bash
   # 正确示例
   python3 .specify/scripts/python/create-simple-feature.py --json "简单的邮箱管理模块" --short-name "email-management"
   ```
2. **解析 JSON 输出**获取功能路径信息
3. **明确输出创建的文档的路径和文件名**。

**⚠️ 必须保留：** `spec.md`（初始模板）

---

## 阶段 1：发现

**目标**：理解需要构建什么

初始请求：$ARGUMENTS

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-discovery
```

脚本会输出关键约束和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档

**操作**：

1. 创建包含所有阶段的待办事项列表
2. **验证术语**：用户描述必须使用 glossary.md 中的标准术语
3. **检查仓库范围**：功能必须在 context.md 定义的仓库职责范围内
4. 如果功能不清楚，询问用户：
   - 他们在解决什么问题？
   - 功能应该做什么？
   - 有什么约束或要求？
5. 总结理解并与用户确认
   - 在总结中使用标准术语
   - 标记任何跨仓库依赖

**文档保存**: 按照"文档规范"章节的快速参考表,更新 `spec.md`

**⚠️ 必须保留：** `spec.md`（发现阶段）

---

## 阶段 2：代码库探索

**目标**：在高层和低层理解相关的现有代码和模式

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-exploration
```

脚本会输出关键约束和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档

**操作**：

1. 并行启动 2-3 个 code-explorer 代理。每个代理应该：

   - 全面追踪代码，专注于全面理解抽象、架构和控制流
   - 针对代码库的不同方面（例如类似功能、高层理解、架构理解、用户体验等）
   - 包含 5-10 个要阅读的关键文件列表
   - **注入知识上下文**：向代理提供 module_tree.json 和 service_catalog

   **示例代理提示**：

   - "查找与 [功能] 类似的功能并全面追踪其实现"
   - "映射 [功能区域] 的架构和抽象，全面追踪代码"
   - "分析 [现有功能/区域] 的当前实现，全面追踪代码"
   - "识别与 [功能] 相关的 UI 模式、测试方法或扩展点"
2. 代理返回后，请阅读代理识别的所有文件以建立深入理解
3. 呈现发现和发现的模式的综合总结

   - 将发现与 module_tree.json 中的模块结构关联
   - 注明任何相关的现有 ADR

**文档保存**: **按照"文档规范"章节的快速参考表,更新 `research.md`**

**⚠️ 必须保留：** `research.md`

---

## 阶段 3：澄清问题

**目标**：在设计之前填补空白并解决所有歧义

**关键**：这是最重要的阶段之一。不要跳过。

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-clarification
```

脚本会输出关键约束和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档

**操作**：

1. 审查代码库发现和原始功能请求
2. **与业务规则交叉引用**：确保问题符合 rules.md
3. **根据领域模型验证**：检查实体是否与 domain-model.md 定义匹配
4. 识别未充分说明的方面：边缘情况、错误处理、集成点、范围边界、设计偏好、向后兼容性、性能需求
5. **以清晰、有组织的列表形式向用户呈现所有问题**
   - 分类：业务逻辑 / 技术实现 / 边界定义
   - 引用相关业务规则作为上下文
6. **等待回答后再继续进行架构设计**

如果用户说"你认为最好的就行"，提供你的建议并获得明确确认。

**文档保存**: **按照"文档规范"章节的快速参考表,更新 `spec.md`,解决所有澄清问题**

**⚠️ 必须保留：** `spec.md`（澄清阶段）

## 阶段 4：架构设计

**目标**：设计具有不同权衡的多个实现方法

**关键**：此阶段具有最严格的知识库要求。L0 违规将阻止工作流。

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-architecture
```

脚本会输出关键约束和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档
- 如果 L0 文档缺失，立即阻止工作流

**操作**：

1. **架构合规预检查**：

   - 验证 L0 知识库文档可访问
   - 如果 L0 文档缺失 → 停止并通知用户
2. 并行启动 2-3 个具有不同焦点的 code-architect 代理：

   - 最小更改（最小改动，最大复用）
   - 清洁架构（可维护性，优雅抽象）
   - 务实平衡（速度 + 质量）
   - **向所有代理注入知识上下文**：**constitution.md（章程）**、architecture-principles、security-baseline、tech-radar-hold、tech-stack、ADR 摘要
3. **代理后合规检查**：

   | 检查         | 来源                                       | 严重级别 |
   | ------------ | ------------------------------------------ | -------- |
   | 分层架构合规 | L0/constitution/architecture-principles.md | CRITICAL |
   | 安全红线合规 | L0/constitution/security-baseline.md       | CRITICAL |
   | 禁用技术检查 | L0/technology-radar/hold.md                | CRITICAL |
   | 推荐技术优先 | L0/technology-radar/adopt.md               | WARNING  |
   | ADR 一致性   | L1/architecture/decisions/                 | WARNING  |

   **处理规则**：


   - ✅ 全部合规 → 继续
   - ⚠️ WARNING 违规 → 在方案中标记风险，用户决定
   - ❌ CRITICAL 违规 → 阻止工作流，要求修改设计
4. 审查所有方法并形成哪个最适合此特定任务的意见
5. 向用户呈现：

   - 每种方法的简要总结
   - **每种方法的合规检查结果**
   - **技术选型及其雷达状态（Adopt/Trial/Hold）**
   - 权衡比较
   - **你的建议及其理由**
   - 具体的实现差异
6. **询问用户偏好哪种方法**

**文档保存**: **按照"文档规范"章节的快速参考表,更新 `plan.md`**

**⚠️ 必须保留：** `plan.md`

---

## 阶段 5：实现

**目标**：构建功能

**未经用户批准不要开始**

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-implementation
```

脚本会输出关键约束（AI 编码红线、安全基线等）和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档
- 如果 L0 文档缺失，立即阻止工作流

**操作**：

1. 等待用户明确批准
2. 阅读前几个阶段识别的所有相关文件
3. **加载模块特定文档**：从 `.knowledge/code-derived/{module}.md` 加载目标模块的文档
4. **加载章程约束**：读取 `constitution.md`，确保实现符合章程原则
5. **加载语言编码规范**（根据 plan.md 技术栈动态加载）：
   - Java → `.knowledge/upstream/L0-enterprise/standards/coding-standards/java.md`
   - TypeScript → `.knowledge/upstream/L0-enterprise/standards/coding-standards/typescript.md`
   - Python → `.knowledge/upstream/L0-enterprise/standards/coding-standards/python.md`
6. 按照选择的架构实现
7. 严格遵循代码库约定
8. **应用知识库中的编码规范**
9. 编写清晰、文档完善的代码
10. **每任务安全检查**：验证没有安全红线违规
11. 随着进展更新待办事项

**⚠️ 此阶段无新文档**（仅代码实现）

---

## 阶段 6：质量审查

**目标**：确保代码简单、DRY、优雅、易于阅读且功能正确

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-review
```

脚本会输出关键约束和需要读取的文档列表。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档

**操作**：

1. 并行启动 3 个具有不同焦点的 code-reviewer 代理：

   - 简洁性/DRY/优雅
   - Bug/功能正确性
   - 项目约定/抽象
   - **向所有代理注入知识上下文**：**constitution.md（章程）**、security-baseline、api-design-guide、testing-standards
2. **带知识库的审查维度**：

   | 维度         | 来源                                 | 置信度阈值 |
   | ------------ | ------------------------------------ | ---------- |
   | 安全红线违规 | L0/constitution/security-baseline.md | 90+        |
   | API 规范违规 | L0/standards/api-design-guide.md     | 80+        |
   | 测试覆盖不足 | L1/standards/testing.md              | 70+        |
   | 编码风格违规 | L1/standards/coding.md               | 60+        |
3. 整合发现并识别最高严重性问题

   - **L0 违规 → CRITICAL（必须修复）**
   - **L1 违规 → WARNING（建议修复）**
4. **向用户呈现发现并询问他们想怎么做**（现在修复、稍后修复或按原样继续）

   - CRITICAL 问题应强烈建议"现在修复"
5. 根据用户决定处理问题

**⚠️ 此阶段无新文档**（审查结果）

---

## 阶段 7：总结

**目标**：记录完成的工作

**知识库加载**：

```bash
python3 .specify/scripts/python/load-knowledge.py fd-summary
```

脚本会输出需要读取的文档列表（如术语词典）。

**你必须**：

- 仔细阅读脚本输出的所有约束
- 使用 Read 工具读取列出的每个文档

**操作**：

1. 将所有待办事项标记为完成
2. 总结：
   - 构建了什么（使用术语词典中的标准术语）
   - 做出的关键决策
   - **合规状态**：L0/L1 合规摘要
   - 修改的文件
   - 建议的后续步骤
   - **ADR 建议**：建议是否需要创建新 ADR
   - **领域模型更新**：建议是否需要更新 domain-model.md

**文档保存**: **按照"文档规范"章节的快速参考表,追加总结到 `plan.md`**

**⚠️ 必须保留：** `plan.md`（追加总结）

3. 直接调用 `spec-summary-skill` 生成工作总结：

```
使用 Skill tool 调用 spec-summary，传入 $ARGUMENTS（可选参数）
```

`spec-summary-skill` 会自动：

1. 检测 SDD 上下文和 Git 变更
2. 根据可用文档选择生成模式（基础/标准/完整）
3. 读取 `spec.md`、`plan.md`、`tasks.md` 等文档
4. 委托 `work-summarizer` agent 生成文档
5. 输出到 `{FEATURE_DIR}/summary.md`

**输出内容**：

- 构建了什么（使用术语词典中的标准术语）
- 做出的关键决策
- **合规状态**：L0/L1 合规摘要
- 修改的文件（Git 变更统计）
- 建议的后续步骤
- **ADR 建议**：建议是否需要创建新 ADR
- **领域模型更新**：建议是否需要更新 domain-model.md

**注意**：生成独立的 `summary.md` 文件


---

## 合规摘要

在工作流结束时，提供合规摘要：

```
## 合规报告

### L0 企业级约束
- [ ] 架构原则：PASS/FAIL
- [ ] 安全红线：PASS/FAIL
- [ ] 技术雷达：PASS/FAIL
- [ ] AI 编码策略：PASS/FAIL

### L1 项目级标准
- [ ] 技术栈对齐：PASS/WARNING
- [ ] ADR 一致性：PASS/WARNING
- [ ] 编码规范：PASS/WARNING
- [ ] 测试规范：PASS/WARNING

### L2 仓库级上下文
- [ ] 仓库范围：PASS/WARNING
- [ ] 模块结构：PASS/WARNING
```

---
