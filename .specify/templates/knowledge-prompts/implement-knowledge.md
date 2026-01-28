# /speckit.implement 知识库注入模板

> 用于在执行 /speckit.implement 命令时注入相关知识库文档

## 知识库上下文

### AI 编码约束 (L0 - 最高优先级，不可违反)

以下是 AI 辅助编码的强制约束，AI 在任何情况下都不得违反：

```markdown
{AI_CODING_POLICY_CONTENT}
```

**AI 编码红线**：
- ❌ AI 生成的代码必须经过人工 Review 后方可合并
- ❌ AI 不得自动提交到 main/master/release 分支
- ❌ AI 不得修改安全相关配置文件（.env、secrets、credentials）
- ❌ AI 生成的测试必须有有效断言
- ❌ 禁止 AI 自动跳过或删除失败的测试

---

### 安全红线 (L0 - 不可违反)

以下是安全基线要求，代码实现必须遵守：

```markdown
{SECURITY_BASELINE_CONTENT}
```

**安全编码约束**：
- 禁止硬编码密码、API Key、Token
- 禁止 SQL 字符串拼接（使用参数化查询）
- 所有外部输入必须校验
- 敏感数据必须加密
- 必须实现适当的错误处理（不暴露敏感信息）

---

### 语言编码规范 (L0)

以下是对应语言的编码规范：

```markdown
{LANGUAGE_CODING_STANDARDS_CONTENT}
```

---

### 项目编码规范 (L1)

以下是项目级编码规范：

```markdown
{PROJECT_CODING_CONTENT}
```

---

### 项目 API 规范 (L1)

以下是项目 API 规范：

```markdown
{PROJECT_API_CONTENT}
```

---

### 项目测试规范 (L1)

以下是项目测试规范：

```markdown
{PROJECT_TESTING_CONTENT}
```

---

### 模块文档 (L2)

以下是当前任务相关模块的详细文档：

```markdown
{MODULE_DOC_CONTENT}
```

**模块约束**：
- 代码实现需符合模块现有模式和风格
- 新增公共方法需更新模块文档
- 保持与现有代码风格一致

---

## 每个任务执行前检查

在执行每个任务前，AI 必须确认以下检查点：

### 安全检查
| 检查项 | 验证内容 |
|--------|----------|
| 无硬编码凭证 | 代码中无密码、Key、Token |
| 参数化查询 | SQL 使用参数化，无字符串拼接 |
| 输入校验 | 所有外部输入已验证 |
| 错误处理 | 异常不暴露敏感信息 |

### 代码质量检查
| 检查项 | 验证内容 |
|--------|----------|
| 命名规范 | 符合语言/项目命名约定 |
| 代码结构 | 符合分层架构原则 |
| 测试覆盖 | 关键路径有测试覆盖 |
| 文档更新 | 公共 API 有文档注释 |

---

## 任务完成后检查

每个任务完成后，执行以下验证：

1. **单元测试通过**：`npm test` / `mvn test` / `pytest`
2. **静态检查通过**：`lint` / `typecheck`
3. **安全扫描**：无新增安全告警
4. **代码审查**：标记为待人工 Review

---

## 加载状态

| 文档 | 级别 | 状态 | Token |
|------|------|------|-------|
| ai-coding-policy.md | L0 | {AI_POLICY_STATUS} | {AI_POLICY_TOKENS} |
| security-baseline.md | L0 | {SECURITY_STATUS} | {SECURITY_TOKENS} |
| {language}.md | L0 | {LANG_STATUS} | {LANG_TOKENS} |
| coding.md | L1 | {CODING_STATUS} | {CODING_TOKENS} |
| api.md | L1 | {API_STATUS} | {API_TOKENS} |
| testing.md | L1 | {TESTING_STATUS} | {TESTING_TOKENS} |
| {module}.md | L2 | {MODULE_STATUS} | {MODULE_TOKENS} |

**总计 Token**: {TOTAL_TOKENS}
