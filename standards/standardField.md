# WeDAP 标准字段定义文档

## 1. 文档说明

本文档定义了 WeDAP 系统中各 API 接口使用的标准字段规范，所有字段必须严格遵守本规范。

## 2. 通用字段

### 2.1  通用标准[MUST]

1. 所有金额字段，数据库统一使用Decimal(21,4)，保留4位小数。Java代码使用BigDecimal。

2. 所有枚举不允许使用数字，需要使用有业务含义单词

3. 时间格式： 统一使用unix时间戳，数据库统一使用unix时间戳

4. requestId请求流水号规范：

   {来源}-{时间戳}-{业务码}- {节点ID}-{序列号}-{随机数｝
   2位       14位       4位          2位         4位         6位
   WB-20260113121010-PAYS-10-0001-1234567

5. bizSeqNo业务流水规范：

   {来源}-{时间戳}-{业务码}- {节点ID}-{序列号}-{随机数｝
   2位       14位       4位          2位         4位         6位
   WB-20260113121010-PAYS-10-0001-1234567

### 2.2  通用标准字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| sysTime | String | 32 | 系统时间 | 使用unix时间戳 |
| sysDate | String | 8 | 系统日期 | 格式：YYYMMDD |
| bizSeqNo | String | 32 | 业务流水号 | 示例：`2501010A603998306381409200549527` |
| requestId | String | 64 | 请求流水号 | 与请求头中的 X-Request-Id 一致 |
| orgSysReferenceno | String | 32 | 原系统调用流水 | 冲账时使用 |
| channelId | String | 3 | 交易渠道 | 需提前配置授权 |
| chlCode | String | 8 | 请求渠道编码 | 接入时分配 |
| chlTxnDate | String | 8 | 渠道交易日期 | 格式：YYYMMDD |
| txnDate | String | 8 | 交易日期 | 格式：YYYYMMDD |
| reqDateTime | String | 14 | 请求发送时间 | 使用unix时间戳 |
| txnBranchCode | String | 10 | 交易机构 | 需提前配置授权 |
| txnTellerId | String | 32 | 交易柜员 | 操作员标识 |
| reconCode | String | 32 | 对账代码 | 用于对账 |
| transScenario | String | 32 | 场景码 | 交易场景标识 |
| tenantId | String | 16 | 租户Id | 租户Id |



## 3. 账户标识字段

### 3.1 客户标识

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| userId | String | 64 | 银行侧用户ID | 用户唯一标识 |
| custodyUserId | String | 64 | 托管用户ID | Web3 托管系统用户标识 |

### 3.2 钱包标识（Web3）

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| walletAddress | String | 128 | 钱包地址 | 区块链钱包地址 |
| walletId | String | 64 | 钱包ID | 钱包唯一标识 |
| chainType | String | 32 | 链类型 | ETH/BSC/POLYGON/TRON |
| walletStatus | String | 16 | 钱包状态 | ACTIVE/FROZEN/CLOSED |

### 3.3 银行账户标识

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| cardNumber | String | 40 | 卡号 | 银行卡号 |
| custAccountNo | String | 35 | 客户账号 | 客户账户唯一标识 |
| custAccountType | String | 10 | 客户账类型 | 账户业务类型 |
| subaccountSerialNo | String | 8 | 子账户序号 | 子账户唯一序号 |
| accountName | String | 100 | 账户名称 | 账户户名 |
| accountOtherName | String | 100 | 账户别名 | 账户别名 |

### 3.4 内部账户标识

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| hotAccountNo | String | 35 | 热点账号 | 热点账户标识 |
| incomeAccountNo | String | 35 | 收息客户账号 | 利息收入账户 |

---

## 4. 金额与货币字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| txnAmount | Decimal | 21,4 | 交易金额 | DECIMAL(21,4)，保留4位小数，根据币种 |
| currencyCode | String | 3 | 货币代号 | ISO-4217 币种编码。CNY/HKD/USD/JPY/EUR/GBP/AUD/CHF/CAD |
| accountBalance | Decimal | 21,4 | 账户余额 | 当前账户余额 |
| availableBalance | Decimal | 21,4 | 可用余额 | 可动用余额 |
| lastBalance | Decimal | 21,4 | 上日账户余额 | 上一交易日余额 |
| holdAmount | Decimal | 21,4 | 冻结金额 | 已冻结金额 |
| unholdAmount | Decimal | 21,4 | 解冻金额 | 待解冻金额 |
| interestAmount | Decimal | 21,4 | 利息金额 | 利息 |
| chargeAmount | Decimal | 21,4 | 收费金额 | 手续费 |
| deductAmount | Decimal | 21,4 | 扣划金额 | 强制扣划金额 |

---

## 5. 日期时间字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| valueDate | String | 8 | 起息日期 | 格式：YYYMMDD |
| expiryDate | String | 8 | 到期日期 | 格式：YYYMMDD |
| txnDate | String | 8 | 交易日期 | 格式：YYYMMDD |
| opendate | String | 8 | 开户日期 | 格式：YYYMMDD |
| effectiveDate | String | 8 | 生效日期 | 格式：YYYMMDD |
| depositTerm | String | 6 | 存期 | 存款期限 |
| dateOfBirth | String | 8 | 生日 | 格式：YYYMMDD |
| verifiedAt | String | 32 | 验证时间 | ISO 8601 格式 |
| creationDate | String | 32 | 创建日期 | ISO 8601 格式 |
| lastModifiedDate | String | 32 | 最后修改日期 | ISO 8601 格式 |

---

## 6. 利率相关字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| rate | Decimal | 12,6 | 汇率/利率 | DECIMAL(12,6) |
| effectiveRate | Decimal | 11,6 | 实际利率 | DECIMAL(11,6) |
| redeemRate | Decimal | 11,6 | 支取利率 | DECIMAL(11,6) |
| rateId | String | 20 | 利率编号 | 利率标识 |
| liabInterestRateId | String | 20 | 负债利率编号 | 负债端利率标识 |
| rateSource | String | 1 | 利率来源 | 0-参考利率，1-录入 |
| rateFloatingType | String | 1 | 利率浮动方式 | 0-不浮动，1-按点，2-按比率 |
| varFixed | Decimal | 12,7 | 利率浮动点数 | DECIMAL(12,7) |
| varPercentage | Decimal | 27,8 | 利率浮动百分比 | DECIMAL(27,8) |

---

## 7. 跨境支付字段

### 7.1 参与方标识（BIC/账户）

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| debitBic | String | 11 | 付款方 BIC | 8-11位 SWIFT BIC |
| debitAcct | String | 34 | 付款方账户 | 付款客户账户 |
| debitName | String | 140 | 付款方名称 | 付款客户姓名/机构名称 |
| debitCustType | String | 1 | 付款客户类型 | O-机构，P-个人，I-同业 |
| debitId | String | 35 | 付款方ID | 付款客户机构 ID |
| debitIdType | String | 2 | 付款人证件类型 | 01-20 枚举值 |
| debitIdNo | String | 64 | 付款人证件号 | 证件号/机构代码 |
| creditBic | String | 11 | 收款方 BIC | 8-11位 SWIFT BIC |
| creditAcct | String | 34 | 收款方账户 | 收款客户账户 |
| creditName | String | 140 | 收款方名称 | 收款客户姓名/机构名称 |
| creditCustType | String | 1 | 收款客户类型 | O-机构，P-个人，I-同业 |
| creditId | String | 35 | 收款方ID | 收款客户机构 ID |
| creditIdType | String | 2 | 收款人证件类型 | 01-20 枚举值 |
| creditIdNo | String | 64 | 收款人证件号 | 证件号/机构代码 |

### 7.2 银行中介信息

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| creditAgentBic | String | 11 | 收款开户行 BIC | MT103-57a |
| creditAgentAcct | String | 34 | 收款开户行账户 | 开户行账户 |
| creditAgentBankName | String | 150 | 收款开户行名称 | 银行名称 |
| interCorBic | String | 11 | 中间行 BIC | MT103-55a/MT202-56a |
| interCorAcct | String | 34 | 中间行账户 | 中间行账户 |
| midBankCode | String | 11 | 人工指定中间行行号 | 用于智能汇路 |
| posReceiver | String | 11 | 头寸电收报行 | 必须是合法账户行 |

### 7.3 支付路由与报文

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| routeFlag | String | 1 | 路由标记类型 | 1-指定邮路大类，2-智能路由，3-指定邮路 |
| routeSysCode | String | 8 | 邮路大类编码 | SWIFT/CIPS |
| routeCode | String | 8 | 邮路编码 | 具体邮路编码 |
| payRouteCode | String | 8 | 通路编码 | SWIFT/CIPS |
| messageStandard | String | 2 | 报文标准类型 | MT-MT报文，MX-MX报文 |
| transScene | String | 1 | 交易场景 | C-客户汇款，I-金融机构汇款 |
| bizType | String | 10 | 业务种类 | GODX/STRX/CTFX/RMTX/FTFX/OTFX |
| chargeBearer | String | 4 | 费用承担方 | OUR/BEN/SHA/NA |
| priority | String | 8 | 优先级 | EXPRESS-特急，URGE-紧急，GENERAL-普通 |
| postscript | String | 148 | 汇款附言 | 格式 4*35 |
| summaryCode | String | 40 | 摘要码 | 记账摘要码 |

---

## 8. 地址信息字段

### 8.1 详细地址结构

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| street | String | 256 | 街道地址 | 详细街道信息 |
| city | String | 64 | 城市 | 城市名称 |
| subdivision | String | 8 | 省/州代码 | 行政区划代码 |
| country | String | 2 | 国家代码 | ISO 3166-1 alpha-2 |
| department | String | 70 | 部门 | 机构部门 |
| subDepartment | String | 70 | 分部门 | 机构分部门 |
| streetName | String | 70 | 街道名 | 街道名称 |
| buildingNumber | String | 16 | 大楼编号 | 楼号 |
| buildingName | String | 35 | 大楼名称 | 楼名 |
| floor | String | 70 | 楼层 | 楼层信息 |
| postBox | String | 16 | 邮箱 | PO Box |
| room | String | 70 | 房号 | 房间号 |
| postCode | String | 16 | 邮编 | 邮政编码 |
| townName | String | 35 | 镇名 | 城镇名称 |
| townLocationName | String | 35 | 镇内区位 | 区位信息 |
| districtName | String | 35 | 区名 | 行政区名称 |
| addressLines | String[] | 3*35 | 地址全名 | 最多3行，每行不超过35字符 |

---

## 9. 身份证件字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| documentId | String | 32 | 证件号码 | 唯一文件标识 |
| documentType | String | 16 | 证件类型 | ID_CARD/PASSPORT |
| issuingAuthority | String | 64 | 颁发机构 | 证件颁发机构 |
| countryOfIssuance | String | 2 | 签发国家 | ISO 3166-1 alpha-2 |
| validUntil | String | 8 | 有效期至 | 格式：YYYMMDD |
| frontPhoto | String | 512 | 证件正面照片URL | JPEG/PNG 格式 |
| backPhoto | String | 512 | 证件背面照片URL | 身份证必填 |
| selfiePhoto | String | 512 | 自拍照片URL | 人脸识别用 |

---

## 10. 状态与标志字段

### 10.1 账户状态

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| accountStatus | String | 16 | 账户状态 | ACTIVE/INACTIVE/CLOSED |
| kycStatus | String | 16 | KYC状态 | COMPLETED/NOT_EXIST<br />/PENDING/APPROVED/REJECTED |
| ecifStatus | String | 16 | 客户状态 | ACTIVE/INACTIVE |
| totalBlockFlag | String | 1 | 账户封闭冻结标志 | 0-否，1-是 |
| noCreditFlag | String | 1 | 账户只付不收标志 | 0-否，1-是 |
| noDebitFlag | String | 1 | 账户只收不付标志 | 0-否，1-是 |

### 10.2 交易状态

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| txnStatus | String | 8 | 交易状态码 | PROCESSING-处理中<br/>SUCCESS-成功<br/>FAILED-失败 <br/>EXCEPTION-处理异常<br/>REVERSALPENDING-被冲帐中<br/>REVERSALPROCESSING-冲账处理中<br/>REVERSED-被冲帐 |
| returnRemitFlag | String | 1 | 退汇标识 | 0-非退汇，1-退汇 |
| refundType | String | 2 | 退汇类型 | 01-未清算退汇，02-未解付退汇，03-已解付退汇 |
| reversalType | String | 1 | 冲账冲正类型 | 1-冲账，2-冲正 |



### 10.3 业务标志

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| interestFlag | String | 1 | 计息标志 | 0-否，1-是 |
| checkCloseFlg | String | 1 | 是否检查可销户 | 0-否，1-是 |
| fixedCurrentFlag | String | 1 | 定活标志 | 0-活期，1-定期 |
| forceDebitFlag | String | 1 | 是否允许强制借记 | 0-否，1-是 |
| firstInquiryFlg | String | 1 | 首次查询标志 | 0-否，1-是 |
| hasMore | String | 1 | 是否有后续数据 | 0-否，1-是 |

---

## 11. 分页查询字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| pageNum | Integer | - | 当前页码 | 从1开始 |
| pageSize | Integer | - | 每页记录数 | 默认20 |
| total | Integer | - | 总记录数 | 查询结果总数 |
| pages | Integer | - | 总页数 | 总页数 |
| startingRow | Integer | 19 | 起始行数 | 分页起始位置 |
| offset | Integer | - | 偏移量 | 从0开始 |

---

## 12. 产品与机构字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| productId | String | 10 | 产品编号 | 银行产品标识 |
| productCode | String | 8 | 三级产品编码 | 行内三级产品编码 |
| payProductCode | String | 10 | 支付产品编码 | 支付平台产品编码 |
| openBranchCode | String | 10 | 开户机构 | 账户开户机构代码 |
| accountBranchCode | String | 10 | 账户所属机构 | 账户归属机构代码 |
| payeeBranchCode | String | 10 | 收款方机构代码 | 收款账户机构代码 |
| assignedBranchKey | String | 32 | 分支编码键 | Mambu 分支标识 |
| assignedCentreKey | String | 32 | 中心编码键 | Mambu 中心标识 |
| assignedUserKey | String | 32 | 用户编码键 | Mambu 用户标识 |

---

## 13. 冻结相关字段

| 参数名 | 类型 | 最大长度 | 描述 | 约束 |
|--------|------|----------|------|------|
| holdProductCode | String | 8 | 待冻结分类码 | 冻结业务分类 |
| holdStopDate | String | 8 | 待冻结到期日 | 冻结到期日期，格式：YYYMMDD |
| holdReason | String | 200 | 冻结原因 | 冻结说明 |
| oraginHoldSerialNo | String | 21 | 原解冻编号 | 待解冻编号 |
| newHoldId | String | 21 | 冻结编号 | 新增冻结流水号 |

---

## 14. 数据字典引用

### 14.1 币种代码（ISO 4217）

| 代码 | 描述 |
|------|------|
| CNY | 人民币 |
| HKD | 港币 |
| USD | 美元 |
| EUR | 欧元 |
| GBP | 英镑 |
| JPY | 日元 |
| AUD | 澳元 |
| CHF | 瑞士法郎 |
| CAD | 加拿大元 |

### 14.3 证件类型（Web3/BitGo）

| 代码 | 描述 |
|------|------|
| cct | Citizenship Certificate（公民证书） |
| cid | Consular ID（领事馆ID） |
| dl | Driver's License（驾驶证） |
| foid | CO Foreigner ID（哥伦比亚外国人ID） |
| hic | Health Insurance Card（健康保险卡） |
| id | Identification Card（身份证） |
| ipp | Internal Passport（内部护照） |
| keyp | AU Keypass ID（澳大利亚Keypass ID） |
| ltpass | Long Term Pass（长期通行证） |
| munid | US Municipal ID（美国市政ID，如纽约市ID） |
| myn | JP My Number Card（日本个人编号卡） |
| nbi | PH National Bureau of Investigation Certificate（菲律宾NBI证书） |
| nric | SG National Residency ID（新加坡国民居留证） |
| ofw | PH Overseas Foreign Worker Card（菲律宾海外劳工卡） |
| rp | Residence Permit（居留许可） |
| pan | IN Permanent Account Number Card（印度永久账号卡） |
| pid | PH Postal Identity Card（菲律宾邮政身份证） |
| pp | Passport（护照） |
| ppc | Passport Card（护照卡） |
| pr | Permanent Residence Card（永久居留卡） |
| sss | PH Social Security System Card（菲律宾社保卡） |
| td | US Travel Document（美国旅行证件） |
| tribalid | US/CA Tribal ID（美国/加拿大部落ID） |
| umid | PH Unified Multi Purpose ID（菲律宾统一多用途ID） |
| vid | Voter ID（选民ID） |
| visa | Visa（签证） |
| wp | Work Permit（工作许可）|

### 14.4 职业类型（Web3/BitGo occupation）

| 代码 | 描述 | 备注 |
|------|------|------------|
| AGRICULTURE | 农业 | Agriculture |
| ART_DEALER | 艺术品经销商/拍卖行/进出口 | Art Dealer / Auctioneer / Import / Export Company |
| FINANCIAL_SERVICES | 金融服务 | Financial Services (Asset Mgmt., Bank, Broker Dealer, Commodities, Mutual Fund, Ins. Co) |
| CASINO_GAMBLING | 赌场和博彩 | Casinos and Gambling Establishments |
| CHARITY_NGO | 慈善/非营利组织 | Charity/NGO/Non-Profit/Foundation/Endowment |
| IT_TECHNOLOGY | IT/软件/科技 | Computer Programmer / Administrator / Software Engineer / IT or Software / Technology Company |
| CRYPTO_SERVICES | 加密货币服务 | Crypto Services (ATM, Exchange, Lender, Coins/Token) |
| EDUCATION | 教育 | Education / Teacher |
| EXTRACTIVE_PRECIOUS | 采掘业/珠宝/贵金属 | Extractive Industry (Oil, Gas, etc.) / Jewels / Gemstones / Precious Metals |
| FAMILY_OFFICE | 家族办公室 | Family Office |
| ENTERTAINMENT | 影视/娱乐 | Film / TV / Entertainment (not adult) |
| GOVERNMENT | 政府/国有机构 | Government/State owned/Political Org. (i.e. Sovereign Wealth Fund) |
| HEALTHCARE | 医疗保健 | Healthcare |
| LAW_ENFORCEMENT | 执法/军队/安保 | Law Enforcement / Military / Protective Services |
| CRYPTO_MINING | 加密货币挖矿 | Miner / Mining Pool |
| MONEY_SERVICE | 货币服务业务 | Money Service Business |
| PRIVATE_EQUITY | 私募/风投 | Private Equity / Venture Capital |
| PROFESSIONAL_SERVICE | 专业服务（律师/会计） | Professional Service Providers (lawyers accountants etc.) |
| REAL_ESTATE | 房地产 | Real estate brokers developers and appraisers |
| HOSPITALITY | 休闲/酒店 | Recreation / Hospitality |
| STUDENT_UNEMPLOYED | 学生/无业/退休 | Student / Unemployed / Retired |
| TRADING | 交易员/做市商 | Traders / Trading (High Frequency, Proprietary, Market Maker) |
| WEAPONS_DEALER | 武器经销商 | Weapons Dealers |
| OTHER | 其他 | Other |
| OTHER_DEFAULT | 其他（默认） | Other - Default |

### 14.5 费用承担方

| 代码 | 描述 |
|------|------|
| OUR | 付款方承担所有费用 |
| BEN | 收款方承担所有费用 |
| SHA | 双方共同承担费用 |
| NA | 与手续费无关 |

### 14.6 交易优先级

| 代码 | 描述 |
|------|------|
| EXPRESS / 0 | 特急 |
| URGE / 1 | 紧急 |
| GENERAL / 3 | 普通 |

### 14.7 交易渠道（channelId）

| 代码 | 描述         | 备注             |
| ---- | ------------ | ---------------- |
| RWA  | 现实世界资产 | Real World Asset |
| WT   | 钱包         | Wallet           |
| SK   | 质押         | Staking          |
| TKN  | 代币         | Token            |
| LEN  | 贷款         | Lending          |

### 5.2 业务状态流转

---

## 15. 文档版本

| 版本 | 日期 | 修改人 | 描述 |
|------|------|--------|------|
| v1.0.0 | 2026-01-03 | WeDAP | 初始版本，整合5个API文档的标准字段定义 |
| v1.1.0 | 2026-01-16 | WeDAP | 新增 Web3/BitGo 证件类型枚举和职业类型枚举 |
