# 数据流

## 钱包开户流程

~~~mermaid
sequenceDiagram
    box 客户端
        participant Customer as 客户
        participant Teller as 银行柜员
        participant BankApp as 银行APP
        participant Web3H5 as WEB3 H5
    end
    
    box 银行系统
        participant BankBackend as Web2银行后台
    end
    
    box WeDAP
        participant Gateway as wedap-gateway
        participant Adapter as wedap-adapter
        participant Core as wedap-web2-core
        participant Connector as wedap-adapter-connector
        participant Counter as wedap-counter
    end
    
    box 外部服务
        participant Wallet as 钱包
        participant BitGo as BitGo
    end

    rect rgb(200, 220, 255)
        Note over Customer, BankBackend: 1. 银行账户开户
        Customer->>BankApp: 发起开户申请
        BankApp->>BankBackend: 提交开户请求
        BankBackend->>BankBackend: KYC 刷脸 OTP 验证
        BankBackend-->>BankApp: 开户成功
        BankApp-->>Customer: 返回开户结果
    end

    rect rgb(220, 255, 220)
        Note over Teller, Counter: 2. 提前上传客户资料
        Teller->>Counter: 上传客户KYC资料
        Counter-->>Teller: 上传成功
    end

    rect rgb(255, 230, 200)
        Note over Customer, Wallet: 3. 钱包开户申请
        Customer->>Web3H5: 发起钱包开户
        Web3H5->>Gateway: 钱包开户请求
        Gateway->>Wallet: 转发开户请求
    end

    rect rgb(255, 220, 220)
        Note over Wallet, Counter: 4. 查询银行客户和KYC数据
        Wallet->>Adapter: 查询客户KYC数据
        Adapter->>Connector: 转发查询请求
        Connector->>Counter: 获取客户资料
        Counter-->>Connector: 返回客户KYC数据
        Connector-->>Adapter: 返回数据
        Adapter-->>Wallet: 返回KYC验证结果
    end

    rect rgb(230, 220, 255)
        Note over Wallet, BitGo: 5. 钱包开户完成
        Wallet->>BitGo: 创建托管钱包
        BitGo-->>Wallet: 返回钱包地址
        Wallet-->>Gateway: 开户成功
        Gateway-->>Web3H5: 返回钱包信息
        Web3H5-->>Customer: 显示钱包开户成功
    end
~~~

## 钱包申购稳定币

~~~mermaid
sequenceDiagram
    box 客户端
        participant Customer as 客户
        participant Operator as 银行运营人员
        participant Web3H5 as WEB3 H5
    end

    box 银行系统
        participant BankCounter as 银行柜面
    end

    box WeDAP
        participant Gateway as wedap-gateway
        participant Adapter as wedap-adapter
        participant Connector as wedap-adapter-connector
        participant Counter as wedap-counter
    end

    box 外部服务
        participant Wallet as 钱包
        participant Circle as Circle
    end

    rect rgb(200, 220, 255)
        Note over Customer, Wallet: 1. 请求充值
        Customer->>Web3H5: 发起充值申请
        Web3H5->>Gateway: 提交充值请求
        Gateway->>Wallet: 转发充值请求
        Wallet-->>Gateway: 返回充值工单
        Gateway-->>Web3H5: 返回工单信息
        Web3H5-->>Customer: 显示充值处理中
    end

    rect rgb(220, 255, 220)
        Note over Wallet, Counter: 2. 客户账户扣款
        Wallet->>Adapter: 请求账户扣款
        Adapter->>Connector: 转发扣款请求
        Connector->>Counter: 创建扣款工单
        Counter-->>Connector: 返回工单状态
        Connector-->>Adapter: 返回处理结果
        Adapter-->>Wallet: 扣款请求已受理
    end

    rect rgb(255, 230, 200)
        Note over Operator, BankCounter: 3. 手工记账
        Operator->>BankCounter: 执行转账到Circle
        BankCounter->>BankCounter: 扣除手续费
        BankCounter-->>Operator: 记账完成
    end

    rect rgb(255, 220, 220)
        Note over Operator, Counter: 4. 完成工单
        Operator->>Counter: 处理工单
        Counter->>Counter: 更新工单状态
        Counter-->>Operator: 工单处理完成
    end

    rect rgb(230, 220, 255)
        Note over Counter, Wallet: 5. 通知记账完成
        Counter->>Connector: 发送记账完成通知
        Connector->>Adapter: 转发通知
        Adapter->>Wallet: 通知记账已完成
    end

    rect rgb(220, 240, 255)
        Note over Circle, Wallet: 6. Circle通知到账（双重确认）
        Circle->>Wallet: 资金到账通知
        Wallet->>Wallet: 核对到账信息
    end

    rect rgb(255, 240, 220)
        Note over Wallet, Wallet: 7. 更新钱包余额
        Wallet->>Wallet: 更新用户稳定币余额
        Wallet-->>Gateway: 充值成功通知
        Gateway-->>Web3H5: 推送充值结果
        Web3H5-->>Customer: 显示充值成功
    end
~~~

## 钱包提现交易时序图

~~~mermaid
sequenceDiagram
    box 客户端
        participant Customer as 客户
        participant Teller as 银行柜员
        participant BankApp as 银行APP
        participant Web3H5 as WEB3 H5
    end

    box 银行系统
        participant BankBackend as Web2银行后台
    end

    box WeDAP
        participant Gateway as wedap-gateway
        participant Adapter as wedap-adapter
        participant Core as wedap-web2-core
        participant Connector as wedap-adapter-connector
        participant Counter as wedap-counter
    end

    box 外部服务
        participant Wallet as 钱包
        participant BitGo as BitGo
        participant Circle as Circle
    end

    rect rgb(200, 220, 255)
        Note over Customer, Wallet: 1. 客户查询钱包余额
        Customer->>Web3H5: 查询钱包余额
        Web3H5->>Gateway: 转发查询请求
        Gateway->>Wallet: 查询余额
        Wallet-->>Gateway: 返回余额信息
        Gateway-->>Web3H5: 返回余额
        Web3H5-->>Customer: 显示钱包余额
    end

    rect rgb(220, 255, 220)
        Note over Customer, BankBackend: 2. 查询银行账户列表
        Customer->>Web3H5: 查询银行账户
        Web3H5->>Gateway: 转发查询请求
        Gateway->>Wallet: 查询关联账户
        Wallet->>Adapter: 请求银行账户列表
        Adapter->>Connector: 转发查询请求
        Connector->>Gateway: 查询银行数据
        Gateway->>BankBackend: 获取账户列表
        BankBackend-->>Gateway: 返回账户信息
        Gateway-->>Connector: 返回数据
        Connector-->>Adapter: 返回账户列表
        Adapter-->>Wallet: 返回银行账户
        Wallet-->>Gateway: 返回账户列表
        Gateway-->>Web3H5: 返回数据
        Web3H5-->>Customer: 显示银行账户列表
    end

    rect rgb(255, 230, 200)
        Note over Customer, Wallet: 3. 客户发起提现
        Customer->>Web3H5: 发起提现申请
        Web3H5->>Gateway: 提交提现请求
        Gateway->>Wallet: 转发提现请求
        Wallet-->>Gateway: 返回提现工单
        Gateway-->>Web3H5: 返回工单信息
        Web3H5-->>Customer: 显示提现处理中
    end

    rect rgb(255, 220, 220)
        Note over Wallet, BitGo: 4. 数字货币交易转稳定币
        Wallet->>BitGo: 发起数字货币兑换
        BitGo->>BitGo: 执行交易转换
        BitGo-->>Wallet: 返回稳定币
    end

    rect rgb(230, 220, 255)
        Note over Wallet, Circle: 5. 稳定币赎回
        Wallet->>Circle: 发起稳定币赎回
        Circle->>Circle: 处理赎回请求
        Circle-->>Wallet: 赎回成功确认
    end

    rect rgb(220, 240, 255)
        Note over Wallet, BankBackend: 6. 转客户银行账户
        Wallet->>Adapter: 请求转账到银行账户
        Adapter->>Connector: 转发转账请求
        Connector->>Gateway: 发起银行转账
        Gateway->>BankBackend: 执行入账操作
        BankBackend->>BankBackend: 客户账户入账
        BankBackend-->>Gateway: 入账成功
        Gateway-->>Connector: 返回结果
        Connector-->>Adapter: 转账完成
        Adapter-->>Wallet: 转账成功确认
    end

    rect rgb(255, 240, 220)
        Note over Wallet, Customer: 7. 提现完成通知
        Wallet->>Gateway: 提现完成通知
        Gateway->>Web3H5: 推送提现结果
        Web3H5->>Customer: 显示提现成功
    end
~~~

