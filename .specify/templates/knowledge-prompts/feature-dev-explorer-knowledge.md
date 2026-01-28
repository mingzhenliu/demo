# Knowledge Context for Code Explorer Agent

> 此模板用于增强 code-explorer 代理的知识库上下文

## 仓库结构参考

**模块树（来自 `.knowledge/code-derived/module_tree.json`）**：
{MODULE_TREE_JSON}

**仓库概览（来自 `.knowledge/code-derived/overview.md`）**：
{OVERVIEW_CONTENT}

## 服务目录参考

**服务目录（来自 `.knowledge/upstream/L1-project/architecture/service-catalog.md`）**：
{SERVICE_CATALOG_CONTENT}

## 探索约束

在进行代码探索时，请遵循以下约束：

1. **模块边界意识**
   - 识别的代码模式需与模块树中的结构对应
   - 跨模块依赖需明确标注
   - 发现与模块定义不符的代码时需标记为潜在问题

2. **服务关联**
   - 发现跨服务调用时，参考服务目录验证调用关系
   - 识别服务间的依赖方向是否符合架构设计
   - 标注任何未在服务目录中记录的服务调用

3. **ADR 关联**
   - 在探索结果中关联相关的架构决策记录（ADR）
   - 如发现与现有 ADR 冲突的实现，明确标注

4. **输出要求**
   - 提供入口点的 file:line 引用
   - 按模块组织发现的模式和实现
   - 列出对理解该功能至关重要的 5-10 个文件
