# /speckit.plan 知识库注入模板

> 用于在执行 /speckit.plan 命令时注入相关知识库文档

## 知识库上下文

### 架构原则 (L0 - 不可违反)

以下是企业架构原则，实施计划必须完全符合：

```markdown
{ARCHITECTURE_PRINCIPLES_CONTENT}
```

**架构约束**：
- 所有设计决策必须符合架构原则
- CRITICAL 级别违规将阻止流程执行
- 需调整的设计需在 plan.md 中说明理由

---

### 安全红线 (L0 - 不可违反)

以下是安全基线要求，任何实施计划不得违反：

```markdown
{SECURITY_BASELINE_CONTENT}
```

**安全约束**：
- 输入校验：所有外部输入必须验证
- 审计日志：关键操作必须记录
- 敏感数据：必须加密存储和传输
- 认证授权：必须实现完整的访问控制

---

### API 设计规范 (L0)

以下是 API 设计指南：

```markdown
{API_DESIGN_CONTENT}
```

---

### 测试规范 (L0)

以下是测试标准，实施计划必须定义测试策略：

```markdown
{TESTING_STANDARDS_CONTENT}
```

**测试约束**：
- 计划必须包含测试策略
- 测试覆盖率目标需明确
- TDD 原则必须体现在任务顺序中

---

### 技术栈 (L1)

以下是项目技术栈定义：

```markdown
{TECH_STACK_CONTENT}
```

---

### 编码规范 (L1)

以下是项目编码规范：

```markdown
{CODING_STANDARDS_CONTENT}
```

---

### 技术雷达 - 禁用技术 (L0)

以下技术被标记为 HOLD，禁止在新项目中使用：

```markdown
{TECH_RADAR_HOLD_CONTENT}
```

### 技术雷达 - 推荐技术 (L0)

以下技术被推荐使用：

```markdown
{TECH_RADAR_ADOPT_CONTENT}
```

---

### ADR 参考 (L1)

以下是相关架构决策记录：

```markdown
{ADR_CONTENT}
```

---

### 模块结构 (L2)

以下是本仓库的模块结构：

```json
{MODULE_TREE_CONTENT}
```

---

### 仓库概览 (L2)

```markdown
{OVERVIEW_CONTENT}
```

---

## 架构合规检查

在生成实施计划前，请执行以下检查：

| 原则 | 检查项 | 严重级别 |
|------|--------|----------|
| TDD | 测试策略是否定义 | CRITICAL |
| 分层架构 | 是否符合分层结构 | CRITICAL |
| 安全红线 | 输入校验、审计日志 | CRITICAL |
| RESTful | API 设计是否合规 | HIGH |
| 技术选型 | 是否使用 HOLD 技术 | HIGH |

**处理规则**：
- ✅ 全部合规 → 继续生成计划
- ⚠️ 需调整 → 修改设计后继续
- ❌ CRITICAL 违规 → 阻止流程，报告违规项

---

## 加载状态

| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| architecture-principles.md | L0 | {ARCH_PRINCIPLES_STATUS} | {ARCH_PRINCIPLES_TOKENS} |
| security-baseline.md | L0 | {SECURITY_STATUS} | {SECURITY_TOKENS} |
| api-design-guide.md | L0 | {API_STATUS} | {API_TOKENS} |
| testing-standards.md | L0 | {TESTING_STATUS} | {TESTING_TOKENS} |
| tech-stack.md | L1 | {TECH_STACK_STATUS} | {TECH_STACK_TOKENS} |
| coding.md | L1 | {CODING_STATUS} | {CODING_TOKENS} |
| hold.md | L0 | {HOLD_STATUS} | {HOLD_TOKENS} |
| adopt.md | L0 | {ADOPT_STATUS} | {ADOPT_TOKENS} |
| module_tree.json | L2 | {MODULE_TREE_STATUS} | {MODULE_TREE_TOKENS} |

**总计 Token**: {TOTAL_TOKENS}
