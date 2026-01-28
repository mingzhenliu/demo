# API 设计规范

> 企业级 API 设计基线，适用于 RESTful API 设计、Controller 编写、接口文档场景

---

## 一、RESTful 语义规范 [MUST]

### 1.1 HTTP 方法映射

| 操作 | HTTP 方法 | 幂等性 | URL 示例 |
|------|----------|--------|---------|
| 查询单个 | GET | 是 | `GET /api/v1/orders/{orderId}` |
| 查询列表 | GET | 是 | `GET /api/v1/orders?status=1&pageNum=1` |
| 创建 | POST | 否 | `POST /api/v1/orders` |
| 全量更新 | PUT | 是 | `PUT /api/v1/orders/{orderId}` |
| 部分更新 | PATCH | 是 | `PATCH /api/v1/orders/{orderId}` |
| 删除 | DELETE | 是 | `DELETE /api/v1/orders/{orderId}` |

### 1.2 URL 设计规范

```yaml
rules:
  - 使用名词复数，禁止动词
  - 全小写，连字符分隔
  - 层级清晰，不超过 3 级
  - 版本号放在路径中
```

```java
// ✅ 正确 URL
GET    /api/v1/users                    // 用户列表
GET    /api/v1/users/{userId}           // 用户详情
POST   /api/v1/users                    // 创建用户
PUT    /api/v1/users/{userId}           // 更新用户
DELETE /api/v1/users/{userId}           // 删除用户
GET    /api/v1/users/{userId}/orders    // 用户的订单列表

// ❌ 错误 URL
GET    /api/v1/getUser                  // 动词
GET    /api/v1/user                     // 单数
GET    /api/v1/User                     // 大写
POST   /api/v1/createOrder              // 动词
GET    /api/v1/user_list                // 下划线
```

### 1.3 查询参数规范

```yaml
query_params:
  - pageNum: 页码（从 1 开始）
  - pageSize: 每页条数
  - sortBy: 排序字段
  - sortOrder: 排序方向（asc/desc）
  - 业务过滤字段使用小驼峰
```

```java
// ✅ 正确
GET /api/v1/orders?userId=1001&status=1&pageNum=1&pageSize=10&sortBy=createTime&sortOrder=desc

// ❌ 错误
GET /api/v1/orders?user_id=1001&page=1   // 命名不一致
```

---

## 二、请求规范 [MUST]

### 2.1 请求 DTO 设计

```java
@Data
@Schema(description = "订单创建请求")
public class OrderCreateRequest {

    @NotNull(message = "用户 ID 不能为空")
    @Schema(description = "用户 ID", example = "1001", required = true)
    private Long userId;

    @NotEmpty(message = "商品列表不能为空")
    @Size(min = 1, max = 100, message = "商品数量 1-100 件")
    @Schema(description = "商品列表", required = true)
    private List<OrderItemDTO> items;

    @NotNull(message = "订单金额不能为空")
    @DecimalMin(value = "0.01", message = "订单金额必须大于 0")
    @Schema(description = "订单金额", example = "299.00", required = true)
    private BigDecimal amount;

    @Schema(description = "收货地址 ID")
    private Long addressId;

    @Size(max = 200, message = "备注不超过 200 字")
    @Schema(description = "订单备注")
    private String remark;
}
```

### 2.2 Controller 参数校验

```java
@RestController
@RequestMapping("/api/v1/orders")
@Validated
public class OrderController {

    // 请求体校验
    @PostMapping
    public Result<Long> createOrder(@Valid @RequestBody OrderCreateRequest request) {
        return Result.success(orderService.createOrder(request));
    }

    // 路径参数校验
    @GetMapping("/{orderId}")
    public Result<OrderVO> getOrder(
            @PathVariable @Min(value = 1, message = "订单 ID 必须大于 0") Long orderId) {
        return Result.success(orderService.getOrderById(orderId));
    }

    // 查询参数校验
    @GetMapping
    public Result<PageInfo<OrderVO>> listOrders(
            @RequestParam @NotNull(message = "用户 ID 不能为空") Long userId,
            @RequestParam(defaultValue = "1") @Min(1) Integer pageNum,
            @RequestParam(defaultValue = "10") @Max(100) Integer pageSize) {
        return Result.success(orderService.listOrders(userId, pageNum, pageSize));
    }
}
```

---

## 三、响应规范 [MUST]

### 3.1 统一响应结构

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {

    @Schema(description = "业务状态码", example = "200")
    private String code;

    @Schema(description = "提示消息", example = "成功")
    private String msg;

    @Schema(description = "响应数据")
    private T data;

    @Schema(description = "响应时间戳", example = "1704067200000")
    private long timestamp;

    public static <T> Result<T> success(T data) {
        return new Result<>("200", "成功", data, System.currentTimeMillis());
    }

    public static Result<Void> success() {
        return new Result<>("200", "成功", null, System.currentTimeMillis());
    }

    public static Result<Void> fail(String code, String msg) {
        return new Result<>(code, msg, null, System.currentTimeMillis());
    }
}
```

### 3.2 业务状态码规范

**状态码体系**：采用双层状态码设计，包含 HTTP 状态码和业务响应码。

#### 3.2.1 通用状态码

| 响应状态码 | 响应消息 | HTTP 状态码 | 说明 |
|-----------|---------|------------|------|
| 200 | SUCCESS | 200 | 成功 |
| 101 | TIMEOUT | 101 | 查询超时 |
| 104 | PARAMS_NOT_VALID | 104 | 参数校验失败 |
| 302 | REDIRECT | 302 | 重定向 |
| 400 | PARAM_INVALID | 400 | 参数无效 |
| 401 | AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| 403 | AUTH_PERMISSION_DENIED | 403 | 权限不足 |
| 404 | RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| 422 | BUSINESS_RULE_VIOLATION | 422 | 业务规则违反 |
| 500 | SYSTEM_ERROR | 500 | 系统错误 |
| 503 | SERVICE_UNAVAILABLE | 503 | 服务不可用 |

#### 3.2.2 系统自定义错误码（13位编码）

**编码规则**：`[子系统编号4位][错误类型1位][预留2位][子系统内编码6位]`

**错误类型定义**：
- **B** = 业务类错误（账户、交易、产品、业务参数等业务规则相关）
- **T** = 响应方技术类错误（程序异常、崩溃、编码错误、配置不当、网络失败）
- **C** = 请求方技术类错误（请求报文格式错误、解析失败）
- **U** = 交易结果未知（调用超时等）
- **S** = 成功（第6-13位推荐填0）

**编码示例**：

| 子系统编号 | 错误类型 | 预留位 | 子系统内编码 | 完整错误码 | 说明 |
|-----------|---------|-------|------------|-----------|------|
| 1001 | B | 00 | 000001 | 1001B00000001 | 用户模块-业务错误-用户不存在 |
| 1001 | B | 00 | 000002 | 1001B00000002 | 用户模块-业务错误-密码错误 |
| 1002 | B | 00 | 000001 | 1002B00000001 | 订单模块-业务错误-订单不存在 |
| 1002 | B | 00 | 000002 | 1002B00000002 | 订单模块-业务错误-订单已支付 |
| 1003 | B | 00 | 000001 | 1003B00000001 | 支付模块-业务错误-余额不足 |
| 1001 | T | 00 | 000001 | 1001T00000001 | 用户模块-技术错误-数据库连接失败 |
| 1002 | C | 00 | 000001 | 1002C00000001 | 订单模块-请求错误-报文格式错误 |

**错误码枚举定义**：

```java
public enum BizErrorCode {
    // ==================== 通用状态码 ====================
    SUCCESS("200", "成功"),
    TIMEOUT("101", "查询超时"),
    PARAMS_NOT_VALID("104", "参数校验失败"),
    REDIRECT("302", "重定向"),
    PARAM_INVALID("400", "参数无效"),
    AUTH_TOKEN_EXPIRED("401", "Token 过期"),
    AUTH_PERMISSION_DENIED("403", "权限不足"),
    RESOURCE_NOT_FOUND("404", "资源不存在"),
    BUSINESS_RULE_VIOLATION("422", "业务规则违反"),
    SYSTEM_ERROR("500", "系统错误"),
    SERVICE_UNAVAILABLE("503", "服务不可用"),

    // ==================== 用户模块 1001 ====================
    // 业务错误
    USER_NOT_FOUND("1001B00000001", "用户不存在"),
    USER_PASSWORD_ERROR("1001B00000002", "密码错误"),
    USER_DISABLED("1001B00000003", "用户已禁用"),
    USER_ALREADY_EXISTS("1001B00000004", "用户已存在"),

    // 技术错误
    USER_DB_ERROR("1001T00000001", "用户数据库操作失败"),
    USER_CACHE_ERROR("1001T00000002", "用户缓存操作失败"),

    // ==================== 订单模块 1002 ====================
    // 业务错误
    ORDER_NOT_FOUND("1002B00000001", "订单不存在"),
    ORDER_ALREADY_PAID("1002B00000002", "订单已支付"),
    ORDER_EXPIRED("1002B00000003", "订单已过期"),
    ORDER_CANNOT_CANCEL("1002B00000004", "订单不可取消"),
    ORDER_STOCK_NOT_ENOUGH("1002B00000005", "库存不足"),

    // 技术错误
    ORDER_DB_ERROR("1002T00000001", "订单数据库操作失败"),

    // 请求错误
    ORDER_REQUEST_INVALID("1002C00000001", "订单请求报文格式错误"),

    // ==================== 支付模块 1003 ====================
    // 业务错误
    PAYMENT_BALANCE_NOT_ENOUGH("1003B00000001", "余额不足"),
    PAYMENT_TIMEOUT("1003B00000002", "支付超时"),
    PAYMENT_FAILED("1003B00000003", "支付失败"),

    // 结果未知
    PAYMENT_RESULT_UNKNOWN("1003U00000001", "支付结果未知");

    private final String code;
    private final String msg;

    BizErrorCode(String code, String msg) {
        this.code = code;
        this.msg = msg;
    }

    public String getCode() {
        return code;
    }

    public String getMsg() {
        return msg;
    }
}
```

**子系统编号分配**（参考 L1 知识库 ARCHITECTURE.md）：

| 子系统编号 | 子系统名称 | 说明 |
|-----------|-----------|------|
| 1001 | 用户模块 | 用户注册、登录、认证、授权 |
| 1002 | 订单模块 | 订单创建、查询、取消、支付 |
| 1003 | 支付模块 | 支付、退款、账户余额 |
| 1004 | 商品模块 | 商品管理、库存管理 |
| 1005 | 营销模块 | 优惠券、活动、积分 |
| ... | ... | 根据项目实际情况扩展 |

### 3.3 分页响应结构

```java
@Data
@Schema(description = "分页响应")
public class PageInfo<T> {

    @Schema(description = "当前页", example = "1")
    private Integer pageNum;

    @Schema(description = "每页条数", example = "10")
    private Integer pageSize;

    @Schema(description = "总条数", example = "100")
    private Long total;

    @Schema(description = "总页数", example = "10")
    private Integer pages;

    @Schema(description = "数据列表")
    private List<T> list;

    @Schema(description = "是否有下一页", example = "true")
    private Boolean hasNextPage;
}
```

### 3.4 响应示例

```json
// 成功响应（单条数据）
{
    "code": "200",
    "msg": "成功",
    "data": {
        "orderId": 1001,
        "orderNo": "202401010001",
        "amount": 299.00,
        "status": 1,
        "createTime": "2024-01-01 12:00:00"
    },
    "timestamp": 1704067200000
}

// 成功响应（分页数据）
{
    "code": "200",
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

// 失败响应（通用错误码）
{
    "code": "400",
    "msg": "参数无效",
    "data": null,
    "timestamp": 1704067200000
}

// 失败响应（业务错误 - 订单模块）
{
    "code": "1002B00000001",
    "msg": "订单不存在",
    "data": null,
    "timestamp": 1704067200000
}

// 失败响应（技术错误 - 用户模块）
{
    "code": "1001T00000001",
    "msg": "用户数据库操作失败",
    "data": null,
    "timestamp": 1704067200000
}

// 失败响应（结果未知 - 支付模块）
{
    "code": "1003U00000001",
    "msg": "支付结果未知",
    "data": null,
    "timestamp": 1704067200000
}
```

---

## 四、全局异常处理 [MUST]

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // 参数校验异常（@Valid）
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidException(MethodArgumentNotValidException e) {
        String errorMsg = e.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.joining(", "));
        return Result.fail(BizErrorCode.PARAM_INVALID.getCode(),
                          "参数校验失败: " + errorMsg);
    }

    // 参数校验异常（@Validated）
    @ExceptionHandler(ConstraintViolationException.class)
    public Result<Void> handleConstraintException(ConstraintViolationException e) {
        String errorMsg = e.getConstraintViolations().stream()
                .map(v -> v.getPropertyPath() + ": " + v.getMessage())
                .collect(Collectors.joining(", "));
        return Result.fail(BizErrorCode.PARAM_INVALID.getCode(),
                          "参数校验失败: " + errorMsg);
    }

    // 业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        return Result.fail(e.getCode(), e.getMessage());
    }

    // 认证异常
    @ExceptionHandler(AuthenticationException.class)
    public Result<Void> handleAuthException(AuthenticationException e) {
        return Result.fail(BizErrorCode.AUTH_TOKEN_EXPIRED.getCode(),
                          BizErrorCode.AUTH_TOKEN_EXPIRED.getMsg());
    }

    // 授权异常
    @ExceptionHandler(AccessDeniedException.class)
    public Result<Void> handleAccessDeniedException(AccessDeniedException e) {
        return Result.fail(BizErrorCode.AUTH_PERMISSION_DENIED.getCode(),
                          BizErrorCode.AUTH_PERMISSION_DENIED.getMsg());
    }

    // 未知异常
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.fail(BizErrorCode.SYSTEM_ERROR.getCode(),
                          "系统繁忙，请稍后重试");
    }
}
```

**业务异常类定义**：

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class BusinessException extends RuntimeException {

    private String code;

    public BusinessException(String code, String message) {
        super(message);
        this.code = code;
    }

    public BusinessException(BizErrorCode errorCode) {
        super(errorCode.getMsg());
        this.code = errorCode.getCode();
    }

    public BusinessException(BizErrorCode errorCode, String customMsg) {
        super(customMsg);
        this.code = errorCode.getCode();
    }
}
```

**使用示例**：

```java
@Service
public class OrderService {

    public OrderVO getOrderById(Long orderId) {
        Order order = orderMapper.selectById(orderId);
        if (order == null) {
            // 使用通用错误码
            throw new BusinessException(BizErrorCode.ORDER_NOT_FOUND);
        }
        return convertToVO(order);
    }

    public void payOrder(Long orderId) {
        Order order = orderMapper.selectById(orderId);
        if (order.getStatus() == OrderStatus.PAID) {
            // 使用自定义错误码
            throw new BusinessException(BizErrorCode.ORDER_ALREADY_PAID);
        }
        // 支付逻辑...
    }
}
```

---

## 五、接口文档规范 [MUST]

### 5.1 SpringDoc 配置

```yaml
springdoc:
  api-docs:
    enabled: true
    path: /v3/api-docs
  swagger-ui:
    enabled: true
    path: /swagger-ui.html
  packages-to-scan: com.example.controller
```

### 5.2 Controller 文档注解

```java
@RestController
@RequestMapping("/api/v1/orders")
@Tag(name = "订单接口", description = "订单 CRUD 操作")
public class OrderController {

    @Operation(
        summary = "创建订单",
        description = "用户下单接口，需传入用户 ID、商品列表、金额"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "创建成功"),
        @ApiResponse(responseCode = "400", description = "参数错误 (PARAM_INVALID)"),
        @ApiResponse(responseCode = "400", description = "库存不足 (1002B00000005)")
    })
    @PostMapping
    public Result<Long> createOrder(
            @RequestBody @Valid OrderCreateRequest request) {
        return Result.success(orderService.createOrder(request));
    }

    @Operation(summary = "查询订单详情")
    @Parameter(name = "orderId", description = "订单 ID", required = true, example = "1001")
    @GetMapping("/{orderId}")
    public Result<OrderVO> getOrder(@PathVariable Long orderId) {
        return Result.success(orderService.getOrderById(orderId));
    }
}
```

---

## 六、版本控制规范 [MUST]

### 6.1 版本策略

```yaml
format: /api/v{major}/resource
rules:
  - 主版本号递增表示不兼容变更
  - 新增字段必须设默认值
  - 禁止删除旧字段（标记废弃）
  - 禁止修改字段类型
```

### 6.2 接口废弃流程

```java
// 1. 标记废弃
@Deprecated
@Operation(summary = "【已废弃】查询订单", description = "请使用 /api/v2/orders 替代")
@GetMapping("/api/v1/orders/{orderId}")
public Result<OrderVO> getOrderV1(@PathVariable Long orderId) {
    // ...
}

// 2. 新版本接口
@Operation(summary = "查询订单详情")
@GetMapping("/api/v2/orders/{orderId}")
public Result<OrderDetailVO> getOrderV2(@PathVariable Long orderId) {
    // ...
}
```

---

## 七、安全规范 [MUST]

### 7.1 接口限流

```java
@SentinelResource(
    value = "createOrder",
    blockHandler = "createOrderBlockHandler"
)
@PostMapping
public Result<Long> createOrder(@RequestBody @Valid OrderCreateRequest request) {
    return Result.success(orderService.createOrder(request));
}

public Result<Long> createOrderBlockHandler(OrderCreateRequest request, BlockException e) {
    return Result.fail("429", "请求过于频繁，请稍后重试");
}
```

### 7.2 幂等性设计

#### 7.2.1 X-Request-Id 格式规范

**格式定义**（固定 64 字符）：

```
{时间戳}-{业务码}-{节点ID}-{序列号}-{随机数}
  17位      8位      19位      4位      12位
```

**示例**：

```
20260126200528123-ORDRCREA-f-a1b2c3d4e5f678901-0000-Xt8Yn3KpQ7mL
20260126200528456-PAYTRFND-i-0a1b2c3d4e5f67890-0001-a7Bx9KLmN4pR
```

**各部分定义**：

| 部分 | 长度 | 格式 | 说明 |
|------|------|------|------|
| 时间戳 | 17 | `yyyyMMddHHmmssSSS` | 可读时间，精确到毫秒 |
| 业务码 | 8 | 大写字母 | 子系统(4位)+操作(4位)，如 `ORDRCREA`(订单创建) |
| 节点ID | 19 | `{前缀}-{17位十六进制}` | i-(后端)/f-(前端)/m-(移动端)/t-(第三方) |
| 序列号 | 4 | 数字 | 同毫秒内递增 0000-9999 |
| 随机数 | 12 | Base62 | 安全随机字符串 |

**常用业务码示例**：

| 子系统 | 操作码 | 组合 | 含义 |
|--------|--------|------|------|
| USER | REGI/LOGI/UPDT | USERREGI | 用户-注册/登录/更新 |
| ORDR | CREA/CANL/PAYS | ORDRCREA | 订单-创建/取消/支付 |
| PAYT | EXEC/RFND/CBAK | PAYTEXEC | 支付-执行/退款/回调 |
| INVT | DEDU/ADDI/LOCK | INVTDEDU | 库存-扣减/增加/锁定 |

**格式验证正则**：

```regex
^\d{17}-[A-Z]{8}-[a-z]-[0-9a-f]{17}-\d{4}-[A-Za-z0-9]{12}$
```

#### 7.2.2 幂等实现示例

```java
@PostMapping
public Result<Long> createOrder(
        @RequestHeader("X-Request-Id") String requestId,
        @RequestBody @Valid OrderCreateRequest request) {

    // 幂等检查
    String key = "idempotent:order:" + requestId;
    Boolean isNew = redisTemplate.opsForValue()
        .setIfAbsent(key, "1", 30, TimeUnit.MINUTES);
    if (Boolean.FALSE.equals(isNew)) {
        throw new BusinessException("1002B00000006", "请勿重复提交");
    }

    return Result.success(orderService.createOrder(request));
}
```

### 7.3 敏感数据脱敏

```java
@Data
public class UserVO {
    private Long userId;
    private String userName;

    @JsonSerialize(using = PhoneDesensitizer.class)
    private String phone;  // 138****8000

    @JsonSerialize(using = IdCardDesensitizer.class)
    private String idCard;  // 310***********1234
}
```

---

## 八、反模式检查清单

| 序号 | 反模式 | 检测方式 |
|------|--------|----------|
| 1 | URL 包含动词 | 检查 RequestMapping 路径 |
| 2 | GET 请求带 RequestBody | 检查 GET 方法参数 |
| 3 | 无统一响应格式 | 检查返回类型是否为 Result |
| 4 | 无参数校验注解 | 检查 @Valid/@Validated |
| 5 | 无全局异常处理 | 检查 @RestControllerAdvice |
| 6 | 无接口文档注解 | 检查 @Operation/@Tag |
| 7 | 无版本号 | 检查 URL 是否包含 /v1/ |
| 8 | 响应包含敏感数据 | 检查 password/secret 等字段 |
| 9 | POST 接口无幂等设计 | 检查创建类接口 |
| 10 | 无分页参数 | 检查列表查询接口 |
