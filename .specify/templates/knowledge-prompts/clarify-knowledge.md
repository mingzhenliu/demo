# /speckit.clarify 知识库注入模板

> 用于在执行 /speckit.clarify 命令时注入相关知识库文档

## 知识库上下文

### 术语理解 (L1)

以下是项目标准术语词典，澄清问题时需确保术语理解一致：

```markdown
{GLOSSARY_CONTENT}
```

---

### 业务规则 (L1)

以下是项目业务规则，用于判断澄清问题答案的合理性：

```markdown
{BUSINESS_RULES_CONTENT}
```

**澄清约束**：
- 澄清问题的答案不得违反业务规则
- 如发现规格与规则冲突，需标记为待澄清项

---

### 业务流程 (L1)

以下是相关业务流程定义，用于理解功能上下文：

```markdown
{WORKFLOWS_CONTENT}
```

**流程约束**：
- 功能需符合现有流程节点定义
- 新增流程需与现有流程衔接

---

## 澄清问题生成指南

生成澄清问题时，请参考以下维度：

1. **术语澄清**：规格中是否有歧义术语？
2. **规则验证**：功能是否可能违反业务规则？
3. **流程衔接**：功能在业务流程中的位置是否清晰？
4. **边界确认**：功能边界是否明确？

---

## 加载状态

| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| glossary.md | L1 | {GLOSSARY_STATUS} | {GLOSSARY_TOKENS} |
| rules.md | L1 | {RULES_STATUS} | {RULES_TOKENS} |
| workflows/*.md | L1 | {WORKFLOWS_STATUS} | {WORKFLOWS_TOKENS} |

**总计 Token**: {TOTAL_TOKENS}
