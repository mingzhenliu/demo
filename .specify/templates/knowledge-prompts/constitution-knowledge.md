# /speckit.constitution 知识库注入模板

> 用于在执行 /speckit.constitution 命令时注入企业级宪章规范

## 知识库上下文

### 企业级宪章模板 (L0 - 参考)

以下是企业级宪章模板，项目章程应基于此模板创建：

```markdown
{CONSTITUTION_TEMPLATE_CONTENT}
```

**模板使用约束**：
- 核心原则章节必须保留
- 可根据项目特性扩展原则
- 禁止删除或弱化 L0 定义的原则
- 保留标题层次结构和格式规范

---

### 架构原则 (L0 - 不可违反)

以下是企业架构原则，项目章程必须完全符合：

```markdown
{ARCHITECTURE_PRINCIPLES_CONTENT}
```

**架构约束**：
- 分层架构约束不可修改
- 依赖规则必须遵守（L0 > L1 > L2）
- 技术栈选型需符合企业标准
- 禁止创建与架构原则冲突的项目规范

---

### 安全红线 (L0 - 不可违反)

以下是安全基线要求，项目章程不得弱化：

```markdown
{SECURITY_BASELINE_CONTENT}
```

**安全约束**：
- 认证授权要求不可降低
- 数据保护标准为最低门槛
- 审计追踪要求必须满足
- 加密算法要求不可弱化
- 输入校验规则必须遵守

---

### 合规要求 (L0 - 参考)

以下是合规性要求，项目章程应参考遵循：

```markdown
{COMPLIANCE_REQUIREMENTS_CONTENT}
```

**合规约束**：
- 个保法/GDPR 相关要求必须满足
- 等保 2.0 要求按项目级别执行
- 数据留存与删除规则必须明确

---

## 章程合规检查

在生成/更新项目章程前，请执行以下检查：

| 检查项 | 来源 | 严重级别 |
|--------|------|----------|
| 包含所有 L0 核心原则 | constitution-template.md | CRITICAL |
| 安全红线完整性 | security-baseline.md | CRITICAL |
| 架构约束符合性 | architecture-principles.md | CRITICAL |
| 合规要求覆盖 | compliance-requirements.md | HIGH |

**处理规则**：
- ✅ 全部合规 → 继续生成/更新章程
- ⚠️ 需扩展 → 补充缺失的 L0 要求后继续
- ❌ CRITICAL 违规 → 阻止流程，报告冲突项

---

## L0 原则继承规则

### 必须继承的原则

项目章程必须包含以下 L0 核心原则（可扩展但不可删除）：

1. **测试驱动开发** - TDD 强制执行
2. **规则至上架构** - 规则分层与优先级
3. **分层架构纯粹性** - 架构边界约束
4. **安全红线** - 认证授权、输入校验、数据保护
5. **RESTful API 标准化** - API 设计规范
6. **生产就绪代码完整性** - 代码质量标准
7. **可观测性要求** - 健康检查、日志规范
8. **简洁性原则** - YAGNI 与 KISS
9. **容器化部署规范** - Dockerfile 与 K8s 配置
10. **审计追踪与合规** - 审计日志要求

### 可扩展的章节

项目章程可根据项目特性扩展以下内容：

- 项目特有的业务规则
- 额外的技术栈约束
- 更严格的安全要求
- 项目特定的命名规范
- 额外的质量门禁

### 禁止操作

- ❌ 删除 L0 定义的核心原则
- ❌ 弱化安全红线要求
- ❌ 降低测试覆盖率标准
- ❌ 修改架构分层约束
- ❌ 更改规则优先级（L0 > L1 > L2）

---

## 加载状态

| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| constitution-template.md | L0 | {TEMPLATE_STATUS} | {TEMPLATE_TOKENS} |
| architecture-principles.md | L0 | {ARCH_STATUS} | {ARCH_TOKENS} |
| security-baseline.md | L0 | {SECURITY_STATUS} | {SECURITY_TOKENS} |
| compliance-requirements.md | L0 | {COMPLIANCE_STATUS} | {COMPLIANCE_TOKENS} |

**总计 Token**: {TOTAL_TOKENS}
