# 项目测试规范

## 概述

本文档定义项目测试规范，包括测试策略、覆盖率要求和最佳实践。

## 测试金字塔

```
          /\
         /  \        E2E 测试 (10%)
        /────\       - 关键用户流程
       /      \      - 跨服务集成
      /────────\     集成测试 (20%)
     /          \    - API 测试
    /            \   - 数据库集成
   /──────────────\  单元测试 (70%)
  /                \ - 业务逻辑
 /                  \- 工具函数
```

## 覆盖率要求

| 测试类型 | 覆盖率要求 | 说明 |
|----------|------------|------|
| 单元测试 | ≥ 80% | 核心业务逻辑 |
| 分支覆盖 | ≥ 70% | if/else/switch |
| 集成测试 | 核心 API | 所有对外接口 |
| E2E 测试 | 关键流程 | 核心业务流程 |

## 单元测试

### 命名规范

```java
// 方法名_场景_期望结果
@Test
void calculateAmount_withValidOrder_returnsCorrectTotal() {
    // ...
}

@Test
void validateUser_withExpiredToken_throwsAuthException() {
    // ...
}
```

### 测试结构 (AAA 模式)

```java
@Test
void getUserById_withExistingUser_returnsUser() {
    // Arrange - 准备测试数据
    Long userId = 1L;
    User expectedUser = new User(userId, "张三");
    when(userRepository.findById(userId)).thenReturn(Optional.of(expectedUser));

    // Act - 执行被测方法
    User result = userService.getUserById(userId);

    // Assert - 验证结果
    assertThat(result).isNotNull();
    assertThat(result.getName()).isEqualTo("张三");
}
```

### Mock 规范

```java
// 使用 @Mock 注解
@Mock
private UserRepository userRepository;

@InjectMocks
private UserServiceImpl userService;

// 明确 Mock 行为
when(userRepository.findById(anyLong())).thenReturn(Optional.empty());
when(userRepository.save(any(User.class))).thenAnswer(i -> i.getArgument(0));
```

## 集成测试

### API 测试

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class UserControllerIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createUser_withValidData_returns201() {
        // Given
        CreateUserRequest request = new CreateUserRequest("张三", "13800138000");

        // When
        ResponseEntity<ApiResponse<User>> response = restTemplate.postForEntity(
            "/api/users",
            request,
            new ParameterizedTypeReference<>() {}
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getData().getName()).isEqualTo("张三");
    }
}
```

### 数据库测试

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE)
@Testcontainers
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_withExistingEmail_returnsUser() {
        // Given
        User user = new User("张三", "zhangsan@example.com");
        userRepository.save(user);

        // When
        Optional<User> result = userRepository.findByEmail("zhangsan@example.com");

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getName()).isEqualTo("张三");
    }
}
```

## E2E 测试

### 测试场景

| 场景 | 描述 | 优先级 |
|------|------|--------|
| 用户注册登录 | 完整注册和登录流程 | P0 |
| 核心业务流程 | 主要业务场景 | P0 |
| 异常流程 | 边界和异常处理 | P1 |

### Playwright 示例

```typescript
test('用户登录流程', async ({ page }) => {
  // 访问登录页
  await page.goto('/login');

  // 输入登录信息
  await page.fill('[data-testid="phone"]', '13800138000');
  await page.fill('[data-testid="password"]', 'password123');

  // 点击登录
  await page.click('[data-testid="login-btn"]');

  // 验证登录成功
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="user-name"]')).toHaveText('张三');
});
```

## 测试数据管理

### 测试数据原则

- 每个测试用例独立，不依赖其他测试
- 使用 Builder 模式创建测试数据
- 敏感数据使用脱敏/Mock 数据

### TestDataBuilder 示例

```java
public class UserTestDataBuilder {
    private Long id = 1L;
    private String name = "测试用户";
    private String email = "test@example.com";

    public UserTestDataBuilder withId(Long id) {
        this.id = id;
        return this;
    }

    public UserTestDataBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public User build() {
        return new User(id, name, email);
    }
}

// 使用
User user = new UserTestDataBuilder()
    .withName("张三")
    .build();
```

## CI/CD 集成

### 测试阶段

```yaml
stages:
  - unit-test      # 单元测试
  - integration    # 集成测试
  - e2e            # E2E 测试（仅主分支）

unit-test:
  script:
    - ./gradlew test
  coverage:
    min: 80%

integration-test:
  script:
    - ./gradlew integrationTest
  services:
    - postgres:15
    - redis:7
```

### 质量门禁

| 指标 | 阈值 | 阻断 |
|------|------|------|
| 单元测试覆盖率 | < 80% | 是 |
| 测试失败 | > 0 | 是 |
| 新代码覆盖率 | < 70% | 是 |
| 重复代码 | > 5% | 否 |

## 禁止事项

- ❌ 禁止测试中使用 `Thread.sleep()` 等固定等待
- ❌ 禁止测试依赖执行顺序
- ❌ 禁止测试访问生产数据库
- ❌ 禁止跳过失败的测试（除非有明确的 issue 跟踪）
- ❌ 禁止测试中硬编码敏感信息

## 维护说明

- 测试代码与生产代码同等重要
- 修复 Bug 时必须补充对应测试
- 定期清理无效/过时的测试
