# 项目编码规范

## 概述

本文档定义项目级编码规范，继承并细化 L0 企业级规范。

> **注意**: L0 安全红线和架构底线不可覆盖，参考 [L0 规范](../upstream/L0-enterprise/)

## 通用规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `UserService` |
| 方法名 | camelCase | `getUserById` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 包名 | 小写点分隔 | `com.example.user` |
| 数据库表 | snake_case | `user_order` |
| API 路径 | kebab-case | `/api/user-orders` |

### 代码组织

```
src/
├── main/
│   ├── java/com/example/
│   │   ├── controller/     # API 层
│   │   ├── service/        # 业务逻辑层
│   │   │   └── impl/       # 实现类
│   │   ├── repository/     # 数据访问层
│   │   ├── domain/         # 领域模型
│   │   │   ├── entity/     # 实体
│   │   │   ├── vo/         # 值对象
│   │   │   └── event/      # 领域事件
│   │   ├── dto/            # 数据传输对象
│   │   ├── config/         # 配置类
│   │   └── util/           # 工具类
│   └── resources/
└── test/
```

## Java 规范

### 异常处理

```java
// 正确：使用自定义业务异常
throw new BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在: " + userId);

// 错误：直接抛出 RuntimeException
throw new RuntimeException("用户不存在");
```

### 日志规范

```java
// 正确：使用占位符，避免字符串拼接
log.info("用户登录成功, userId={}, ip={}", userId, ip);

// 错误：字符串拼接
log.info("用户登录成功, userId=" + userId + ", ip=" + ip);
```

### 注释规范

```java
/**
 * 计算订单总金额
 *
 * @param orderId 订单ID
 * @return 订单总金额（单位：分）
 * @throws OrderNotFoundException 订单不存在时抛出
 */
public Long calculateOrderAmount(Long orderId) {
    // ...
}
```

## TypeScript/React 规范

### 组件规范

```typescript
// 函数组件优先
const UserCard: React.FC<UserCardProps> = ({ user, onEdit }) => {
  // hooks 放在顶部
  const [isLoading, setIsLoading] = useState(false);

  // 事件处理函数
  const handleEdit = useCallback(() => {
    onEdit(user.id);
  }, [user.id, onEdit]);

  return (
    // JSX
  );
};
```

### 类型定义

```typescript
// 接口定义
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// Props 类型
interface UserCardProps {
  user: User;
  onEdit: (userId: string) => void;
}
```

## 数据库规范

### 表设计

| 约束 | 要求 |
|------|------|
| 主键 | 必须有主键，推荐使用 BIGINT 自增或雪花算法 |
| 创建时间 | 必须有 `created_at` 字段 |
| 更新时间 | 必须有 `updated_at` 字段 |
| 软删除 | 使用 `deleted_at` 字段，非 `is_deleted` |
| 索引 | 查询条件字段必须有索引 |

### SQL 规范

```sql
-- 正确：使用别名，字段明确
SELECT u.id, u.name, o.total_amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'ACTIVE'
  AND o.created_at >= '2024-01-01';

-- 错误：SELECT *，无别名
SELECT * FROM users, orders WHERE users.id = orders.user_id;
```

## Git 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（非新功能、非修复） |
| test | 测试相关 |
| chore | 构建/工具变动 |

### 示例

```
feat(user): 添加用户登录功能

- 实现手机号+验证码登录
- 添加登录日志记录
- 集成 Redis 存储验证码

Closes #123
```

## 维护说明

- 编码规范变更需团队讨论后更新
- 规范检查通过 CI/CD 自动化执行
- 新成员需阅读本规范并完成培训
