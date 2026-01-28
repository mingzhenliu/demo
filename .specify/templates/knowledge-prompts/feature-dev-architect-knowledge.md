# Knowledge Context for Code Architect Agent

> 此模板用于增强 code-architect 代理的知识库上下文
> **注意**：L0 约束不可违反，违反将阻止流程

## L0 架构底线（不可违反）

**来源**：`.knowledge/upstream/L0-enterprise/constitution/architecture-principles.md`

{ARCHITECTURE_PRINCIPLES_CONTENT}

**关键约束摘要**：
- ❌ 禁止 Controller/Handler 直接访问 Repository/DAO（必须经过 Service）
- ❌ 禁止循环依赖（A→B→C→A）
- ❌ 基础设施层不得依赖业务层
- ❌ 领域层不得依赖应用层
- ✅ 跨服务数据修改必须使用分布式事务或最终一致性方案
- ✅ 所有写接口必须支持幂等性

## L0 安全红线（不可违反）

**来源**：`.knowledge/upstream/L0-enterprise/constitution/security-baseline.md`

{SECURITY_BASELINE_CONTENT}

**关键约束摘要**：
- ❌ 禁止硬编码密码、API Key、Token、证书
- ❌ 禁止在日志中输出敏感信息
- ❌ 禁止 SQL 字符串拼接（必须参数化查询）
- ❌ 禁止 eval()、exec() 执行动态代码
- ✅ 所有外部输入必须校验
- ✅ PII 数据必须加密存储

## L0 技术雷达 - 禁用技术

**来源**：`.knowledge/upstream/L0-enterprise/technology-radar/hold.md`

{TECHNOLOGY_RADAR_HOLD_CONTENT}

**禁止使用的技术**（新项目禁止采用）：
{HOLD_TECHNOLOGIES_LIST}

## L0 技术雷达 - 推荐技术

**来源**：`.knowledge/upstream/L0-enterprise/technology-radar/adopt.md`

{TECHNOLOGY_RADAR_ADOPT_CONTENT}

## L1 项目技术栈

**来源**：`.knowledge/upstream/L1-project/architecture/tech-stack.md`

{TECH_STACK_CONTENT}

## L1 现有 ADR 摘要

**来源**：`.knowledge/upstream/L1-project/architecture/decisions/`

{ADR_SUMMARIES}

## 架构设计约束

在进行架构设计时，**必须**遵循以下约束：

### CRITICAL（违反阻止流程）

1. **分层架构合规**
   - 必须遵循 L0 定义的分层结构
   - 禁止跨层直接调用
   - 禁止循环依赖

2. **安全红线合规**
   - 架构设计不得引入安全漏洞
   - 数据流设计必须考虑敏感数据保护
   - 认证授权必须符合 L0 要求

3. **禁用技术检查**
   - 禁止使用 Hold 状态的技术
   - 如有特殊需求，需明确标注并说明替代方案

### WARNING（需在方案中标注风险）

4. **推荐技术优先**
   - 优先使用 Adopt 状态的技术
   - 使用 Trial 状态技术需说明理由

5. **ADR 一致性**
   - 新架构决策需与现有 ADR 保持一致
   - 如有冲突，需明确标注并建议更新 ADR

## 输出要求

每个架构方案必须包含：

1. **合规检查结果**
   - [ ] 分层架构：PASS/FAIL
   - [ ] 安全红线：PASS/FAIL
   - [ ] 禁用技术：PASS/FAIL
   - [ ] ADR 一致性：PASS/WARNING

2. **技术选型标注**
   - 每项技术标注其雷达状态（Adopt/Trial/Assess/Hold）
   - Hold 技术必须提供替代方案

3. **风险标注**
   - WARNING 级别问题需明确标注
   - 提供风险缓解建议
