# 项目 API 规范

## 概述

本文档定义项目 API 规范，继承L0知识库 api-design-guide.md 接口规范，细化项目特殊定义，规则优先参考L0知识库，确保接口风格一致。

## RESTful 设计原则

### URL 规范

| 操作 | HTTP 方法 | URL 示例 | 说明 |
|------|-----------|----------|------|
| 查询列表 | GET | `/api/users` | 获取资源列表 |
| 查询单个 | GET | `/api/users/{id}` | 获取单个资源 |
| 创建 | POST | `/api/users` | 创建新资源 |
| 全量更新 | PUT | `/api/users/{id}` | 替换整个资源 |
| 部分更新 | PATCH | `/api/users/{id}` | 更新部分字段 |
| 删除 | DELETE | `/api/users/{id}` | 删除资源 |

### URL 命名规范

- 使用小写字母和短横线: `/api/user-orders`
- 使用复数名词表示资源: `/api/users` 而非 `/api/user`
- 避免动词: `/api/users/{id}/activate` 而非 `/api/activateUser`
- 嵌套资源最多两层: `/api/users/{userId}/orders`



## 统一响应格式

### 成功响应

```json
{
  "code": "200",
  "msg": "SUCCESS",
  "data": {
    "id": "123",
    "name": "张三"
  },
  "timestamp": 1704067200000
}
```

### 分页响应

```json
// 成功响应（分页数据）
{
    "code": 200,
    "msg": "成功",
    "data": {
        "pageNum": 1,
        "pageSize": 10,
        "total": 100,
        "pages": 10,
        "list": [...],
        "hasNextPage": true
    },
    "timestamp": 1704067200000
}
```

### 错误响应

```json
// 失败响应
{
    "code": 6001,
    "msg": "订单不存在",
    "data": null,
    "timestamp": 1704067200000
}
```



## 响应状态码(code)

状态码包含http 状态码和响应报文中业务Code。   

### 响应状态码清单

| 响应状态码Code | 响应报文message | HTTP 状态码 | 说明 |
|--------|-------------|------|------|
| 200 | SUCCESS | 200 | 成功 |
| 101 | TIMEOUT | 101 | Query TimeOut |
| 104 | Check Params Not Valid | 104 | Check Params Not Valid |
| 302 | REDIRECT | 302 | REDIRECT |
| 400 | PARAM_INVALID | 400 | 参数无效 |
| 401 | AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| 403 | AUTH_PERMISSION_DENIED | 403 | 权限不足 |
| 404 | USER_NOT_FOUND | 404 | 用户不存在 |
| 422 | ORDER_STATUS_INVALID | 422 | 订单状态不允许此操作 |
| 500 | SYSTEM_ERROR | 500 | 系统错误 |
| 系统自定义 | 系统自定义 | 遵循 RESTful 语义，根据错误类型映射 |  |

### 系统自定义响应状态码Code，系统自定义格式：

非通用错误码采用13位字符编码：

| 位置 | 长度 | 说明 | 示例 |
| ---- | ---- | ---- | ---- |
| 1-4  | 4位  | 子系统编号（参考L1知识库ARCHITECTURE.md） | `1004` |
| 5    | 1位  | 错误类型：B=业务类、T=响应方技术类、C=请求方技术类、U=结果未知 | `B` |
| 6-7  | 2位  | 预留编码（现阶段填0） | `00` |
| 8-13 | 6位  | 子系统内编码（必须数字） | `000001` |



## 请求规范

### 请求头

| Header       | 类型   | 必填 | 说明                                                         | 示例                       |
| ------------ | ------ | ---- | ------------------------------------------------------------ | -------------------------- |
| Content-Type | string | 是   | 请求内容类型                                                 | `application/json`         |
| Authorization | string | 是* | Bearer Token (*公开接口除外)                                  | `Bearer eyJhbGci...`       |
| X-Tenant-Id  | string | 是   | 租户Id，uuid格式                                             | `550e8400-e29b-41d4-a716-446655440000` |
| X-User-Id    | string | 否   | 内部接口调用包含，通过WeDap Apigateway转发接口默认携带银行用户id | `ECIF123456`               |
| X-Custody-User-Id | string | 否 | 内部接口调用包含，通过WeDap Apigateway转发接口默认携带转换后钱包用户id | `custody_user_001`         |
| X-Request-Id | string | 是   | 客户端请求ID，单系统内唯一，系统内可用于防重和幂等。需存储到DB，系统间对账使用。后台系统每次请求重新生成流水上送给下游系统。H5调用后台服务，通过API GateWay生成。外部机构或银行调用，由外部上送。 | `Systemid-20251011-000001` |
| X-Trace-Id   | string | 否   | 分布式链路追踪ID。全链路唯一追踪ID。使用AWS APM能力，自动生成，只落日志不存DB。 | `trace-abc123`             |

### 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码，从 1 开始 |
| pageSize | int | 20 | 每页数量，最大 100 |
| sortBy | string | - | 排序字段 |
| sortOrder | string | desc | asc/desc |

### 查询参数示例

```
GET /api/users?page=1&pageSize=20&status=ACTIVE&sortBy=createdAt&sortOrder=desc
```



### 数据脱敏

提供给前端接口，响应中敏感数据必须脱敏；提供给后段接口调用，响应中敏感数据不脱敏：

| 字段 | 脱敏规则 | 示例 |
|------|----------|------|
| 手机号 | 中间 4 位 | `138****8000` |
| 身份证 | 中间 10 位 | `310***********1234` |
| 邮箱 | @ 前部分 | `z***@example.com` |
| 银行卡 | 保留后 4 位 | `************1234` |

## 序列生成规则
### X-Request-Id生成规则
采用雪花算法
{来源}-{时间戳}-{系统ID}- {节点ID}-{序列号}-{随机数}
2位   - 13位 -   4位   -  2位   -   4位 -    6位
WB-1704067200000-6601-10-0001-1234567

### bizSeqNo生成规则
采用雪花算法
{来源}-{时间戳}-{业务码}- {节点ID}-{序列号}-{随机数}
2位   - 13位 -   4位  -   2位   -   4位 -    6位
WB-1704067200000-PAYS-10-0001-1234567
## 维护说明

- API 变更需更新 Swagger 文档
- 破坏性变更需提前通知调用方
- 新接口需编写接口测试用例

## 接口字段定义

接口字段定义必须遵守 @standardField.md
