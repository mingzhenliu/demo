# 技术栈

## 概述

本文档定义项目统一的技术栈选型，L2 仓库级不可覆盖。

## 语言版本

| 语言 | 版本 | 备注 |
|------|------|------|
| Java | 17 | LTS 版本 |
| Node.js | 20 LTS | 前端构建和部分服务 |
| Python | 3.11+ | 数据处理和脚本 |
| Go | 1.21+ | 高性能服务（可选） |

## 后端框架

| 框架 | 版本 | 用途 | 替代方案 |
|------|------|------|----------|
| Spring Boot | 3.3.13| 主要后端框架 | 无 |
| Spring Cloud | 2023.x | 微服务治理 | - |

### Spring Boot 必选组件

| 组件 | 版本 | 用途 |
|------|------|------|
| spring-boot-starter-web | 3.3.13 | Web 服务 |
| spring-boot-starter-validation | 3.3.13 | 参数校验 |
| spring-boot-starter-actuator | 3.3.13 | 健康检查和监控 |

## 前端框架

| 框架 | 版本 | 用途 |
|------|------|------|
| React | 18.x | 主要前端框架 |
| TypeScript | 5.x | 类型安全 |
| Zustand | latest | 状态管理 |
| Ant Design | 5.x | UI 组件库 |

## 数据库

| 数据库 | 版本 | 用途 |
|--------|------|------|
| MySQL | 8.0.x | 主数据库 |
| Redis | 7.x | 缓存和会话 |

## 消息队列

| 组件 | 版本 | 用途 | 场景 |
|------|------|------|------|
| RabbitMQ | 3.12+ | 消息队列 | 常规异步场景 |
| Kafka | 3.x | 流处理 | 高吞吐场景（可选） |

## 服务治理

| 组件 | 版本 | 用途 |
|------|------|------|
| Nacos | 2.x | 注册中心和配置中心 |
| Sentinel | 1.8.x | 流量控制和熔断 |
| OpenFeign | 4.x | 服务调用 |

## 可观测性

| 组件 | 版本 | 用途 |
|------|------|------|
| Prometheus | latest | 指标收集 |
| Grafana | latest | 监控面板 |
| Jaeger/SkyWalking | latest | 链路追踪 |
| ELK Stack | 8.x | 日志聚合 |

## 容器化

| 组件 | 版本 | 用途 |
|------|------|------|
| Docker | 24.x | 容器运行时 |
| Kubernetes | 1.28+ | 容器编排 |

## Web 与 API

- Spring MVC / Spring Web
  - 用途：RESTful API、请求映射、拦截器、参数校验
  - 文档：`https://docs.spring.io/spring-framework/reference/web/webmvc.html`
- Springdoc OpenAPI
  - 用途：OpenAPI 3 文档生成与 Swagger UI
  - 文档：`https://springdoc.org/`

## 数据访问

- MyBatis / MyBatis-Spring
  - 用途：半自动化 SQL 映射、细粒度 SQL 控制（注解模式）
  - 文档：`https://mybatis.org/mybatis-3/` | `https://mybatis.org/spring/`
  - 使用规范：参考 `04-conventions/mapper.mdc`
- 数据库驱动
  - MySQL：`https://dev.mysql.com/doc/` | 驱动 `mysql-connector-j`
- 数据库设计规范
  - 表结构设计：参考 `02-design/database.mdc`
  - 实体类映射：参考 `04-conventions/entity.mdc`

## 校验与序列化

- Jakarta Validation（Hibernate Validator）
  - 用途：Bean 参数校验（@Valid、@NotNull 等）
  - 文档：`https://jakarta.ee/specifications/bean-validation/` | `https://hibernate.org/validator/`
- Jackson
  - 用途：JSON 序列化/反序列化、时间格式、忽略策略
  - 文档：`https://github.com/FasterXML/jackson`

## 安全

- Spring Security
  - 用途：认证、授权、过滤链、方法级安全
  - 文档：`https://docs.spring.io/spring-security/reference/`

## 缓存与会话

- Spring Cache
  - 用途：方法级缓存（@Cacheable/@CacheEvict）
  - 文档：`https://docs.spring.io/spring-framework/reference/integration/cache.html`
- Redis（可选）
  - 用途：分布式缓存、会话共享、限流
  - 文档：`https://redis.io/docs/` | Spring Data Redis：`https://docs.spring.io/spring-data/redis/docs/current/reference/html/`

## 消息与异步

- Spring for Apache Kafka / RabbitMQ（可选）
  - 用途：异步消息、事件驱动架构
  - Kafka 文档：`https://kafka.apache.org/documentation/`
  - Spring Kafka：`https://docs.spring.io/spring-kafka/reference/`
  - RabbitMQ 文档：`https://www.rabbitmq.com/documentation.html`
- Spring @Async / Scheduling
  - 用途：异步任务与定时任务
  - 文档：`https://docs.spring.io/spring-framework/reference/integration/scheduling.html`

## 配置与迁移

- Spring Boot Configuration（外部化配置）
  - 文档：`https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#features.external-config`

## 日志与观测性

- SLF4J + Logback
  - 用途：日志门面与实现、分环境日志策略
  - 文档：`http://www.slf4j.org/` | `https://logback.qos.ch/documentation.html`
- Spring Boot Actuator
  - 用途：健康检查、指标、环境信息
  - 文档：`https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html`

## 测试

- JUnit 5
  - 用途：单元测试标准框架
  - 文档：`https://junit.org/junit5/docs/current/user-guide/`
- Mockito
  - 用途：Mock 依赖、交互验证
  - 文档：`https://site.mockito.org/`
- Spring Boot Test / MockMvc
  - 用途：集成测试、Web 层测试
  - 文档：`https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#features.testing`


## 技术雷达状态

### Adopt (推荐采用)

- Java 17 + Spring Boot 3.3.13
- MySQL 8.0
- React 18 + TypeScript 5
- Kubernetes

### Trial (试用阶段)

- GraalVM Native Image
- Virtual Threads (Java 21)

### Assess (评估阶段)

- 待评估技术列表

### Hold (暂缓使用)

参考 [L0 技术雷达](./upstream/L0-enterprise/technology-radar/hold.md)

## 维护说明

- 技术栈变更需架构委员会审批
- 新技术引入需先进入 Trial 阶段验证
- Hold 技术需制定迁移计划
