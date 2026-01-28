# /speckit.specify 知识库注入模板

> 用于在执行 /speckit.specify 命令时注入相关知识库文档

## 知识库上下文

### 术语规范 (L1)

以下是项目标准术语词典，创建功能规格时必须使用这些标准术语：

```markdown
{GLOSSARY_CONTENT}
```

**术语使用约束**：
- 必须使用术语词典中的标准术语
- 禁止混用同义词（如"用户"不可写成"客户"，除非词典明确允许）
- 新术语需在规格中明确定义，并建议纳入词典

---

### 领域模型 (L1)

以下是项目领域模型定义，功能规格中的实体必须符合此模型：

```markdown
{DOMAIN_MODEL_CONTENT}
```

**领域模型约束**：
- 不得重新定义已有实体
- 新实体需与现有模型关系清晰
- 实体属性需符合领域模型定义
- 实体关系需遵循已有的聚合边界

---

### 业务规则参考 (L1)

以下是项目业务规则，功能规格需符合这些规则：

```markdown
{BUSINESS_RULES_CONTENT}
```

---

### 仓库上下文 (L2)

以下是本仓库的职责边界定义：

```markdown
{CONTEXT_CONTENT}
```

**边界约束**：
- 功能边界必须在本仓库职责范围内
- 跨仓库依赖需在规格中明确标注
- 超出边界的功能需拆分到对应仓库

---

## 验证检查点

在完成功能规格后，请执行以下验证：

| 检查项 | 通过标准 | 来源 |
|--------|----------|------|
| 术语一致性 | 所有术语来自 glossary.md | L1 |
| 实体合规性 | 实体符合 domain-model.md | L1 |
| 边界检查 | 功能在仓库职责范围内 | L2 |
| 规则符合 | 不违反 rules.md | L1 |

---

## 加载状态

| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| glossary.md | L1 | {GLOSSARY_STATUS} | {GLOSSARY_TOKENS} |
| domain-model.md | L1 | {DOMAIN_MODEL_STATUS} | {DOMAIN_MODEL_TOKENS} |
| rules.md | L1 | {RULES_STATUS} | {RULES_TOKENS} |
| context.md | L2 | {CONTEXT_STATUS} | {CONTEXT_TOKENS} |

**总计 Token**: {TOTAL_TOKENS}
