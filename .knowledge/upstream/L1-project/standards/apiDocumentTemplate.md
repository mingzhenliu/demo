# 接口文档模板

## 1.接口文档说明

​    这个接口文档为xxx提供服务。主要提供服务。

## 2. 文档变更日志 (Change Log)

| 版本   | 日期       | 修改人 | 类型   | 描述                                 |
| :----- | :--------- | :----- | :----- | :----------------------------------- |
| v1.0.0 | 2025-01-01 | 张三   | ✨ 新增 | 初始版本发布，包含用户、订单基础接口 |
| v1.0.1 | 2025-01-15 | 李四   | 🐛 修复 | 修正订单创建接口金额字段精度问题     |
| v1.1.0 | 2025-02-01 | 王五   | ⚡ 优化 | 增加接口幂等性 Header 支持           |

每次变更后增加一条变更日志（Must）

---

## 3. 全局说明 (Global Context)

### 3.1 通信协议与交互

*   **传输协议**: HTTPS
*   **字符编码**: UTF-8
*   **请求格式**: `application/json` (文件上传除外)
*   **时间格式**: 所有时间字段均使用 ISO 8601 格式，例如 `2025-01-01T12:00:00+08:00` 或时间戳（毫秒）

### 3.2 HTTP 说明

所有接口调用必须包含以下 Header 信息，鉴权失败将返回 `401 Unauthorized`。

#### 3.2.1 请求头 (Headers)

| Header       | 类型   | 必填 | 说明         | 示例               |
| ------------ | ------ | ---- | ------------ | ------------------ |
| Content-Type | string | 是   | 请求内容类型 | `application/json` |
| xxx          |        |      |              |                    |

#### 3.2.2 响应报文 (Response)

响应报文严格遵守 @.knowledge/upstream/L1-project/standards/api.md  规范 生成。



#### 3.2.3 响应状态码（Code）

响应状态码Code 严格遵守 @.knowledge/upstream/L1-project/standards/api.md    规范生成



### 3.3 接口文档设计规范[MUST]

接口文档不包含3.3 报文规范章节，需严格遵守该规范。

#### 3.3.1 接口设计规范[MUST]

接口设计原则，严格遵守 @api.md  和  @api-design-guide.md

#### 3.3.1 请求规范 [MUST]

1. 请求参数不自动增加请求时间，时间由后台自动生成

2. 请求参数不自动增加请求流水号，默认在httpHead

3. 请求参数和请求示例默认增加

   bizSeqNo  String  Y   32  业务流水号

   channelId  string  Y 3  交易渠道 

4. 交易类接口请求参数增加对账码

   reconCode  对账代码  string  32



#### 3.3.2 响应规范 [MUST]

1. 响应参数和响应示例 默认增加 

   sysTime  交易系统时间，unix时间戳

   bizSeqNo  String  Y  32  业务流水号 

   requestId  请求流水号

   

#### 3.3.3 字段格式规范 [MUST]

  1. 字段名称、长度、数据字典等优先从标准字段 @standardField.md 中获取
  2. 如果标准字段没有则根据需求创建新数据字典
  3. 接口文档 5.1 数据字典 章节增加所有引用数据字段

## 4. 接口详情 (API Details)

### 4.1 用户模块

#### 4.1.1 用户登录

- **接口名称**: 需求指定
- **接口功能描述**: 根据接口需求和定义，生成功能说明。
- **接口使用说明**：根据接口需求和定义，生成使用说明。例如账号和卡号必须二选一输入
- **请求方式**: 严格遵守 @.knowledge/upstream/L1-project/standards/api.md @.knowledge/upstream/L0-enterprise/standards/api-design-guide.md  规范生成
- **接口地址**: 严格遵守 @.knowledge/upstream/L1-project/standards/api.md @.knowledge/upstream/L0-enterprise/standards/api-design-guide.md  规范生成

**请求参数 (Request Body)**

| 参数名     | 类型   | 必填 | 最大长度 | 描述                            | 约束       | 示例值                           |
| ---------- | ------ | ---- | -------- | ------------------------------- | ---------- | -------------------------------- |
| username   | String | Y    | 32       | 用户账号/手机号                 | 长度大于16 | admin                            |
| password   | String | Y    | 64       | 密码 (建议前端MD5/SHA256后传输) |            | e10adc3949ba59abbe56e057f20f883e |
| deviceType | String | N    | 10       | 设备类型 (ios/android/web)      |            | web                              |

**响应参数 (Response Data)**

| 参数名       | 类型    | 空值 | 长度                  | 描述                          | 约束     | 示例值 |
| ------------ | ------- | ---- | ----------------------------- | -------- | ------ | ------ |
| accessToken  | String  | N    | 256 | 访问令牌 (JWT)，有效期 2 小时 | 长度大于16 | 1001 |
| refreshToken | String  | N    | 256      | 刷新令牌，有效期 7 天         |          |        |
| expireIn     | Integer | N    | 10               | 过期时间 (秒)                 |          |        |
| userInfo     | Object  | N    |               | 用户基础信息对象              |          |        |
| └ userId     | Long    | N    | 64               | 用户唯一 ID                   |          |        |
| └ nickname   | String  | Y    | 64                    | 用户昵称                      |          |        |

**请求示例**

```
{
  "username": “name”
  "password": “e10adc3949ba59abbe56e057f20f883e”
}
```

**响应示例**

```
{
  "code": 200,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsIn...",
    "refreshToken": "dGhpcyBpcyBhIHJlZnJl...",
    "expireIn": 7200,
    "userInfo": {
      "userId": 10001,
      "nickname": "架构师小张"
    }
  },
  "timestamp": 1672531200000
}
```

**响应状态码**
| 响应状态码Code | 响应报文message | HTTP 状态码 | 说明 |
|--------|-------------|------|------|
| 200 | SUCCESS | 200 | 成功 |
| 101 | TIMEOUT | 101 | 查询超时 |
| 104 | PARAMS_NOT_VALID | 104 | 参数校验失败 |
| 401 | AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| 500 | SYSTEM_ERROR | 500 | 系统错误 |

自定义状态码严格遵守 @.knowledge/upstream/L0-enterprise/standards/api-design-guide.md  响应状态码规范生成

#### 4.1.2 xxxx

### 4.2 xx模块

#### 4.2.1 xxxx



## 5. 附录

### 5.1 数据字典

#### 5.1.1 账户状态 (AccountStatus)

| 值         | 含义                |
| :--------- | :------------------ |
| ACTIVE     | 正常 (Active)       |
| FROZEN     | 冻结 (Frozen)       |
| UNFREEZING | 解冻中 (Unfreezing) |
| CLOSED     | 已关闭 (Closed)     |

#### 5.2.2 x x x

所有接口应用

