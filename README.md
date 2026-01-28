# 项目级知识库 (L1)

## 概述

本仓库是 **L1 项目级知识库**，负责管理跨仓库的业务知识、项目级架构决策，以及 AI 定期聚合的内容。

## 知识层级

```
┌─────────────────────────────────────────────────────┐
│  L0 企业级 (Enterprise Standards)                   │
│  └── upstream/L0-enterprise/ (Git Subtree 引入)     │
├─────────────────────────────────────────────────────┤
│  L1 项目级 (Project Knowledge) ← 当前仓库           │
│  └── 业务领域、服务目录、架构决策                   │
├─────────────────────────────────────────────────────┤
│  L2 仓库级 (Repository Context)                     │
│  └── 各业务仓库引用本知识库                         │
└─────────────────────────────────────────────────────┘
```

## 目录结构

```
project-knowledge/
├── README.md                   # 项目总览（本文件）
├── BUSINESS.md                 # 业务知识入口
├── ARCHITECTURE.md             # 架构知识入口
│
├── upstream/                   # 上级知识库（Git Subtree 引入）
│   └── L0-enterprise/          # 企业级知识库
│       ├── constitution/       # 技术宪法（不可覆盖）
│       ├── standards/          # 编码规范（可细化）
│       ├── governance/         # 治理流程
│       ├── ai-coding/          # AI 编码策略
│       └── technology-radar/   # 技术雷达
│
├── business/                   # 业务领域知识
│   ├── domain-model.md         # 领域模型
│   ├── glossary.md             # 术语词典
│   ├── workflows/              # 业务流程
│   └── rules.md                # 业务规则
│
├── architecture/               # 架构知识
│   ├── service-catalog.md      # 服务目录
│   ├── repo-map.md             # 仓库地图
│   ├── data-flow.md            # 数据流图
│   ├── tech-stack.md           # 技术栈
│   └── decisions/              # 架构决策记录 (ADR)
│
├── standards/                  # 项目规范（继承并细化 L0）
│   ├── coding.md               # 项目编码规范
│   ├── api.md                  # 项目 API 规范
│   └── testing.md              # 项目测试规范
│
└── aggregated/                 # AI 聚合区（自动生成）
    ├── last-updated.json       # 更新元信息
    ├── repo-summaries/         # 各仓库摘要
    ├── service-topology.md     # 服务拓扑
    └── cross-repo-patterns.md  # 跨仓库模式
```

## 维护方式

- **人工维护**: business/, architecture/, standards/ 目录
- **AI 聚合**: aggregated/ 目录由 AI 定期从各 L2 仓库聚合生成
- **上游同步**: upstream/ 通过 Git Subtree 从企业级知识库同步

## 快速链接

- [业务知识入口](./BUSINESS.md)
- [架构知识入口](./ARCHITECTURE.md)
- [企业级规范](./upstream/L0-enterprise/)

## L0 知识库同步命令

```bash
# 添加远程仓库（一次性）
git remote add L0-knowledge git@github.com:WeTechHK/knowledge-enterprise-standards.git

# 首次引入 L0 subtree
git subtree add --prefix=upstream/L0-enterprise L0-knowledge main --squash

# 更新 L0 Subtree
git subtree pull --prefix=upstream/L0-enterprise L0-knowledge main --squash
```
