# /speckit.checklist 知识库注入模板

> 用于在执行 /speckit.checklist 命令时注入相关知识库文档
> 根据检查清单类型动态加载对应知识库

## 安全检查清单知识库 (type: security)

### 安全基线 (L0)

以下是企业安全基线要求，用于生成安全检查清单：

```markdown
{SECURITY_BASELINE_CONTENT}
```

**安全检查维度**：
- 认证与授权
- 输入验证
- 数据保护
- 审计日志
- 错误处理
- 依赖安全

---

## 测试检查清单知识库 (type: testing)

### 测试标准 (L0)

以下是企业测试标准：

```markdown
{TESTING_STANDARDS_CONTENT}
```

### 项目测试规范 (L1)

以下是项目测试规范：

```markdown
{PROJECT_TESTING_CONTENT}
```

**测试检查维度**：
- 单元测试覆盖
- 集成测试策略
- E2E 测试场景
- 性能测试指标
- 测试数据管理

---

## API 检查清单知识库 (type: api)

### API 设计指南 (L0)

以下是企业 API 设计指南：

```markdown
{API_DESIGN_CONTENT}
```

### 项目 API 规范 (L1)

以下是项目 API 规范：

```markdown
{PROJECT_API_CONTENT}
```

**API 检查维度**：
- RESTful 设计
- 版本控制
- 错误响应格式
- 认证方式
- 限流策略
- 文档完整性

---

## 编码检查清单知识库 (type: coding)

### 语言编码规范 (L0)

以下是对应语言的编码规范：

```markdown
{LANGUAGE_CODING_CONTENT}
```

### 项目编码规范 (L1)

以下是项目编码规范：

```markdown
{PROJECT_CODING_CONTENT}
```

**编码检查维度**：
- 命名规范
- 代码结构
- 注释规范
- 异常处理
- 日志规范
- 性能考量

---

## 检查清单生成指南

根据加载的知识库，生成包含以下结构的检查清单：

```markdown
## {TYPE} 检查清单

### 必须项 (MUST)
- [ ] 检查项 1：[描述] - 来源：[L0/L1 文档]
- [ ] 检查项 2：[描述] - 来源：[L0/L1 文档]

### 应该项 (SHOULD)
- [ ] 检查项 3：[描述] - 来源：[L0/L1 文档]

### 建议项 (MAY)
- [ ] 检查项 4：[描述] - 来源：[L0/L1 文档]

### 验证方法
| 检查项 | 验证方式 | 工具/命令 |
|--------|----------|----------|
| 项 1 | 自动化 | `lint command` |
| 项 2 | 人工 Review | Code Review |
```

---

## 加载状态

### Security Type
| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| security-baseline.md | L0 | {SECURITY_STATUS} | {SECURITY_TOKENS} |

### Testing Type
| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| testing-standards.md | L0 | {TESTING_L0_STATUS} | {TESTING_L0_TOKENS} |
| testing.md | L1 | {TESTING_L1_STATUS} | {TESTING_L1_TOKENS} |

### API Type
| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| api-design-guide.md | L0 | {API_L0_STATUS} | {API_L0_TOKENS} |
| api.md | L1 | {API_L1_STATUS} | {API_L1_TOKENS} |

### Coding Type
| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| {language}.md | L0 | {CODING_L0_STATUS} | {CODING_L0_TOKENS} |
| coding.md | L1 | {CODING_L1_STATUS} | {CODING_L1_TOKENS} |

**当前类型**: {CHECKLIST_TYPE}
**总计 Token**: {TOTAL_TOKENS}
