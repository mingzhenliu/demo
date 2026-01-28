# Knowledge Context for Code Reviewer Agent

> 此模板用于增强 code-reviewer 代理的知识库上下文
> **注意**：L0 违规为 CRITICAL 级别，必须修复

## L0 安全红线检查清单

**来源**：`.knowledge/upstream/L0-enterprise/constitution/security-baseline.md`

{SECURITY_BASELINE_CONTENT}

### 安全审查检查项（置信度阈值：90+）

| 检查项 | 严重级别 | 检查方法 |
|--------|----------|----------|
| 硬编码密码/密钥 | CRITICAL | 搜索 password=, apiKey=, secret=, token= |
| SQL 注入风险 | CRITICAL | 检查字符串拼接 SQL |
| XSS 风险 | CRITICAL | 检查用户输入直接输出 |
| 敏感信息日志 | CRITICAL | 检查日志中的 PII 数据 |
| 不安全反序列化 | CRITICAL | 检查 eval(), exec(), deserialize() |
| 禁用 SSL 校验 | CRITICAL | 搜索 verify=False, InsecureSkipVerify |

## L0 API 设计规范

**来源**：`.knowledge/upstream/L0-enterprise/standards/api-design-guide.md`

{API_DESIGN_GUIDE_CONTENT}

### API 审查检查项（置信度阈值：80+）

| 检查项 | 严重级别 | 检查方法 |
|--------|----------|----------|
| RESTful 规范 | HIGH | 检查 HTTP 方法使用是否正确 |
| 响应格式一致 | HIGH | 检查响应结构是否统一 |
| 错误处理规范 | HIGH | 检查错误码和错误信息格式 |
| 版本控制 | MEDIUM | 检查 API 版本标识 |
| 幂等性设计 | HIGH | 检查写接口是否支持重试 |

## L1 测试标准

**来源**：`.knowledge/upstream/L1-project/standards/testing.md`

{TESTING_STANDARDS_CONTENT}

### 测试审查检查项（置信度阈值：70+）

| 检查项 | 严重级别 | 检查方法 |
|--------|----------|----------|
| 测试覆盖率 | MEDIUM | 检查是否有对应测试 |
| 有效断言 | HIGH | 检查断言是否验证预期行为 |
| 边界条件测试 | MEDIUM | 检查边界值和异常情况 |
| Mock 合理性 | MEDIUM | 检查 Mock 是否过度 |

## L1 编码风格

**来源**：`.knowledge/upstream/L1-project/standards/coding.md`

{CODING_STANDARDS_CONTENT}

### 编码风格检查项（置信度阈值：60+）

| 检查项 | 严重级别 | 检查方法 |
|--------|----------|----------|
| 命名规范 | LOW | 检查变量/函数命名 |
| 代码重复 | MEDIUM | 检查 DRY 原则 |
| 函数复杂度 | MEDIUM | 检查圈复杂度 |
| 注释规范 | LOW | 检查关键逻辑注释 |

## 审查优先级规则

按以下优先级报告问题：

1. **CRITICAL**（置信度 90+）- L0 违规
   - 安全红线违规
   - 架构底线违规
   - 必须修复后才能合并

2. **HIGH**（置信度 80+）- 重要问题
   - API 规范违规
   - 数据一致性问题
   - 强烈建议修复

3. **MEDIUM**（置信度 70+）- 一般问题
   - 测试覆盖不足
   - 代码重复
   - 建议修复

4. **LOW**（置信度 60+）- 建议改进
   - 编码风格问题
   - 可选优化
   - 可后续处理

## 输出要求

1. **按严重级别分组**
   - 先报告 CRITICAL 和 HIGH 级别问题
   - 提供具体的 file:line 引用
   - 给出明确的修复建议

2. **合规检查结果**
   - L0 安全红线：PASS/FAIL
   - L0 API 规范：PASS/FAIL
   - L1 测试标准：PASS/WARNING
   - L1 编码风格：PASS/WARNING

3. **修复建议**
   - CRITICAL 问题必须提供修复代码示例
   - HIGH 问题提供修复方向
   - MEDIUM/LOW 问题简要说明
