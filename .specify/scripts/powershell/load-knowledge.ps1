#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════
# SpecKit 知识库加载器
# 扁平引用模式：L2 并行引用 L0 和 L1
# 版本：1.0.0 | 创建日期：2025-12-19
# ═══════════════════════════════════════════════════════════════

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Command,

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [string]$Type,

    [Parameter()]
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# 知识库根路径（扁平模式）
$L0_PATH = ".knowledge/upstream/L0-enterprise"
$L1_PATH = ".knowledge/upstream/L1-project"
$L2_PATH = ".knowledge"

# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 获取文件完整路径
function Get-FullPath {
    param(
        [string]$Level,
        [string]$FilePath
    )

    switch ($Level) {
        "L0" { return Join-Path $L0_PATH $FilePath }
        "L1" { return Join-Path $L1_PATH $FilePath }
        "L2" { return Join-Path $L2_PATH $FilePath }
    }
}

# 计算文件 Token 估算（粗略：1 Token ≈ 4 字符）
function Get-TokenEstimate {
    param([string]$FilePath)

    if (Test-Path $FilePath) {
        $chars = (Get-Item $FilePath).Length
        return [math]::Floor($chars / 4)
    }
    return 0
}

# ═══════════════════════════════════════════════════════════════
# 命令知识库映射函数
# ═══════════════════════════════════════════════════════════════

function Get-RequiredDocs {
    param(
        [string]$Command,
        [string]$ChecklistType = ""
    )

    switch ($Command) {
        "specify" {
            return "L1:business/glossary.md L1:business/rules.md L2:context.md"
        }
        "clarify" {
            return "L1:business/glossary.md"
        }
        "plan" {
            return "L0:constitution/architecture-principles.md L0:constitution/security-baseline.md L0:standards/api-design-guide.md L0:standards/testing-standards.md L1:architecture/tech-stack.md L1:standards/coding.md"
        }
        "tasks" {
            return "L2:code-derived/module_tree.json"
        }
        "implement" {
            return "L0:ai-coding/ai-coding-policy.md L0:constitution/security-baseline.md L1:standards/coding.md L1:standards/api.md L1:standards/testing.md"
        }
        "analyze" {
            return "L0:constitution/architecture-principles.md L1:business/glossary.md"
        }
        "constitution" {
            return "L0:constitution/constitution-template.md L0:constitution/architecture-principles.md L0:constitution/security-baseline.md"
        }
        "checklist" {
            switch ($ChecklistType) {
                "security" { return "L0:constitution/security-baseline.md" }
                "testing" { return "L0:standards/testing-standards.md L1:standards/testing.md" }
                "api" { return "L0:standards/api-design-guide.md L1:standards/api.md" }
                "coding" { return "L0:standards/coding-standards/java.md L1:standards/coding.md" }
                default { return "" }
            }
        }
        # ═══════════════════════════════════════════════════════════════
        # Feature-Dev 插件各阶段知识库映射
        # ═══════════════════════════════════════════════════════════════
        { $_ -in @("feature-dev-phase1", "fd-discovery") } {
            return "L1:business/glossary.md L2:context.md"
        }
        { $_ -in @("feature-dev-phase2", "fd-exploration") } {
            return "L2:code-derived/module_tree.json L2:code-derived/overview.md"
        }
        { $_ -in @("feature-dev-phase3", "fd-clarification") } {
            return "L1:business/rules.md L1:business/domain-model.md"
        }
        { $_ -in @("feature-dev-phase4", "fd-architecture") } {
            return "L0:constitution/architecture-principles.md L0:constitution/security-baseline.md L0:technology-radar/hold.md L0:technology-radar/adopt.md L1:architecture/tech-stack.md"
        }
        { $_ -in @("feature-dev-phase5", "fd-implementation") } {
            return "L0:ai-coding/ai-coding-policy.md L0:constitution/security-baseline.md L0:standards/testing-standards.md L1:standards/coding.md"
        }
        { $_ -in @("feature-dev-phase6", "fd-review") } {
            return "L0:constitution/security-baseline.md L0:standards/api-design-guide.md L1:standards/testing.md"
        }
        { $_ -in @("feature-dev-phase7", "fd-summary") } {
            return ""
        }
        default {
            return ""
        }
    }
}

function Get-OptionalDocs {
    param([string]$Command)

    switch ($Command) {
        "specify" { return "L1:business/domain-*.md" }
        "clarify" { return "L1:business/rules.md L1:business/workflows/*.md" }
        "plan" { return "L0:technology-radar/hold.md L0:technology-radar/adopt.md L1:architecture/decisions/*.md L2:code-derived/overview.md" }
        "tasks" { return "L2:code-derived/overview.md" }
        "implement" { return "L0:standards/coding-standards/java.md" }
        "analyze" { return "L0:constitution/security-baseline.md" }
        "constitution" { return "L0:constitution/compliance-requirements.md" }
        # ═══════════════════════════════════════════════════════════════
        # Feature-Dev 插件各阶段可选知识库
        # ═══════════════════════════════════════════════════════════════
        { $_ -in @("feature-dev-phase1", "fd-discovery") } { return "" }
        { $_ -in @("feature-dev-phase2", "fd-exploration") } { return "L1:architecture/service-catalog.md" }
        { $_ -in @("feature-dev-phase3", "fd-clarification") } { return "L1:business/workflows/*.md" }
        { $_ -in @("feature-dev-phase4", "fd-architecture") } { return "L1:architecture/decisions/*.md" }
        { $_ -in @("feature-dev-phase5", "fd-implementation") } { return "L0:standards/coding-standards/*.md L2:code-derived/*.md" }
        { $_ -in @("feature-dev-phase6", "fd-review") } { return "L1:standards/coding.md" }
        { $_ -in @("feature-dev-phase7", "fd-summary") } { return "L1:business/glossary.md" }
        default { return "" }
    }
}

# ═══════════════════════════════════════════════════════════════
# 核心功能
# ═══════════════════════════════════════════════════════════════

function Invoke-LoadCommandKnowledge {
    param(
        [string]$Command,
        [string]$ChecklistType = "",
        [string]$OutputFormat = "text"
    )

    $requiredDocs = Get-RequiredDocs -Command $Command -ChecklistType $ChecklistType
    $optionalDocs = Get-OptionalDocs -Command $Command

    $documents = @()
    $hasError = $false
    $totalTokens = 0
    $docCount = 0

    # 处理必需文档
    if ($requiredDocs) {
        foreach ($docSpec in $requiredDocs -split ' ') {
            if (-not $docSpec) { continue }

            $parts = $docSpec -split ':', 2
            $level = $parts[0]
            $docPath = $parts[1]
            $fullPath = Get-FullPath -Level $level -FilePath $docPath

            $status = "missing"
            $tokens = 0

            if (Test-Path $fullPath) {
                $status = "exists"
                $tokens = Get-TokenEstimate -FilePath $fullPath
                $totalTokens += $tokens

                if ($OutputFormat -eq "text") {
                    Write-Success "[$level] $docPath ($tokens tokens)"
                }
            }
            else {
                # 必需文档缺失处理
                switch ($level) {
                    "L0" {
                        $hasError = $true
                        if ($OutputFormat -eq "text") {
                            Write-Error "[$level] $docPath - MISSING (CRITICAL)"
                        }
                    }
                    "L1" {
                        if ($OutputFormat -eq "text") {
                            Write-Warn "[$level] $docPath - MISSING (WARNING)"
                        }
                    }
                    "L2" {
                        if ($OutputFormat -eq "text") {
                            Write-Info "[$level] $docPath - MISSING (SKIPPED)"
                        }
                    }
                }
            }

            $documents += @{
                level = $level
                path = $docPath
                status = $status
                required = $true
                tokens = $tokens
            }
            $docCount++
        }
    }

    # 处理可选文档
    if ($optionalDocs) {
        foreach ($docSpec in $optionalDocs -split ' ') {
            if (-not $docSpec) { continue }

            $parts = $docSpec -split ':', 2
            $level = $parts[0]
            $docPath = $parts[1]
            $fullPath = Get-FullPath -Level $level -FilePath $docPath

            # 处理通配符
            if ($docPath -like "*`**") {
                $basePath = switch ($level) {
                    "L0" { $L0_PATH }
                    "L1" { $L1_PATH }
                    "L2" { $L2_PATH }
                }

                $searchPath = Join-Path $basePath (Split-Path $docPath -Parent)
                $pattern = Split-Path $docPath -Leaf

                if (Test-Path $searchPath) {
                    Get-ChildItem -Path $searchPath -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
                        $tokens = Get-TokenEstimate -FilePath $_.FullName
                        $totalTokens += $tokens
                        $relPath = $_.FullName.Substring((Resolve-Path $basePath).Path.Length + 1)

                        $documents += @{
                            level = $level
                            path = $relPath
                            status = "exists"
                            required = $false
                            tokens = $tokens
                        }
                        $docCount++

                        if ($OutputFormat -eq "text") {
                            Write-Info "[$level] $relPath (optional, $tokens tokens)"
                        }
                    }
                }
            }
            else {
                if (Test-Path $fullPath) {
                    $tokens = Get-TokenEstimate -FilePath $fullPath
                    $totalTokens += $tokens

                    if ($OutputFormat -eq "text") {
                        Write-Info "[$level] $docPath (optional, $tokens tokens)"
                    }

                    $documents += @{
                        level = $level
                        path = $docPath
                        status = "exists"
                        required = $false
                        tokens = $tokens
                    }
                    $docCount++
                }
            }
        }
    }

    if ($OutputFormat -eq "json") {
        $result = @{
            command = $Command
            status = if ($hasError) { "error" } else { "success" }
            documents = $documents
            total_tokens = $totalTokens
            doc_count = $docCount
        }

        if ($hasError) {
            $result.error_code = "KNOW-001"
            $result.error_message = "L0 知识库文档缺失"
        }

        return $result | ConvertTo-Json -Depth 10
    }
    else {
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Host "总计: $docCount 个文档, 约 $totalTokens tokens"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        if ($hasError) {
            Write-Error "知识库加载失败：L0 必需文档缺失"
            return 1
        }
    }

    return 0
}

# 验证知识库结构
function Test-KnowledgeStructure {
    param([string]$OutputFormat = "text")

    if ($OutputFormat -eq "text") {
        Write-Host "═══════════════════════════════════════════════════════════════"
        Write-Host "知识库结构验证（扁平模式）"
        Write-Host "═══════════════════════════════════════════════════════════════"
    }

    $l0Status = "ok"
    $l1Status = "ok"
    $l2Status = "ok"

    # 检查 L0
    if (-not (Test-Path $L0_PATH)) {
        $l0Status = "missing"
        if ($OutputFormat -eq "text") {
            Write-Error "L0 企业级知识库不存在: $L0_PATH"
        }
    }
    else {
        if ($OutputFormat -eq "text") {
            Write-Success "L0 企业级知识库: $L0_PATH"
        }
    }

    # 检查 L1
    if (-not (Test-Path $L1_PATH)) {
        $l1Status = "missing"
        if ($OutputFormat -eq "text") {
            Write-Warn "L1 项目级知识库不存在: $L1_PATH"
        }
    }
    else {
        if ($OutputFormat -eq "text") {
            Write-Success "L1 项目级知识库: $L1_PATH"
        }
    }

    # 检查 L2
    if (-not (Test-Path $L2_PATH)) {
        $l2Status = "missing"
        if ($OutputFormat -eq "text") {
            Write-Info "L2 仓库级知识库不存在: $L2_PATH"
        }
    }
    else {
        if ($OutputFormat -eq "text") {
            Write-Success "L2 仓库级知识库: $L2_PATH"
        }
    }

    if ($OutputFormat -eq "json") {
        return @{
            L0 = $l0Status
            L1 = $l1Status
            L2 = $l2Status
        } | ConvertTo-Json
    }

    if ($l0Status -eq "missing") {
        return 1
    }
    return 0
}

# 列出所有可用命令
function Show-Commands {
    Write-Host "可用命令："
    Write-Host ""
    Write-Host "  SpecKit 命令："
    Write-Host "  specify      - 功能规格创建"
    Write-Host "  clarify      - 需求澄清"
    Write-Host "  plan         - 实施计划生成"
    Write-Host "  tasks        - 任务列表生成"
    Write-Host "  implement    - 代码实现"
    Write-Host "  analyze      - 跨产物分析"
    Write-Host "  checklist    - 检查清单生成 (可加类型: security/testing/api/coding)"
    Write-Host "  constitution - 项目章程创建/更新"
    Write-Host ""
    Write-Host "  Feature-Dev 插件阶段："
    Write-Host "  feature-dev-phase1 (fd-discovery)      - 阶段1：发现"
    Write-Host "  feature-dev-phase2 (fd-exploration)    - 阶段2：代码库探索"
    Write-Host "  feature-dev-phase3 (fd-clarification)  - 阶段3：澄清问题"
    Write-Host "  feature-dev-phase4 (fd-architecture)   - 阶段4：架构设计 (关键)"
    Write-Host "  feature-dev-phase5 (fd-implementation) - 阶段5：实现"
    Write-Host "  feature-dev-phase6 (fd-review)         - 阶段6：质量审查"
    Write-Host "  feature-dev-phase7 (fd-summary)        - 阶段7：总结"
}

# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

function Show-Usage {
    Write-Host "用法: $($MyInvocation.MyCommand.Name) <command> [options]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  <command>     加载指定命令所需的知识库 (specify/clarify/plan/tasks/implement/analyze/checklist)"
    Write-Host "  validate      验证知识库结构"
    Write-Host "  list          列出所有可用命令"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -Json         输出 JSON 格式"
    Write-Host "  -Type <type>  checklist 类型 (security/testing/api/coding)"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\load-knowledge.ps1 plan                       # 加载 plan 命令所需知识库"
    Write-Host "  .\load-knowledge.ps1 plan -Json                 # JSON 格式输出"
    Write-Host "  .\load-knowledge.ps1 checklist -Type security   # 加载安全检查清单知识库"
    Write-Host "  .\load-knowledge.ps1 validate                   # 验证知识库结构"
}

# 主逻辑
if ($Help) {
    Show-Usage
    exit 0
}

$outputFormat = if ($Json) { "json" } else { "text" }

switch ($Command) {
    "" {
        Show-Usage
        exit 1
    }
    "validate" {
        $result = Test-KnowledgeStructure -OutputFormat $outputFormat
        exit $result
    }
    "list" {
        Show-Commands
        exit 0
    }
    default {
        # 验证命令是否有效
        $validCommands = @(
            "specify", "clarify", "plan", "tasks", "implement", "analyze", "checklist", "constitution",
            "feature-dev-phase1", "feature-dev-phase2", "feature-dev-phase3", "feature-dev-phase4",
            "feature-dev-phase5", "feature-dev-phase6", "feature-dev-phase7",
            "fd-discovery", "fd-exploration", "fd-clarification", "fd-architecture",
            "fd-implementation", "fd-review", "fd-summary"
        )

        if ($Command -notin $validCommands) {
            Write-Error "未知命令: $Command"
            Show-Commands
            exit 1
        }

        # 加载知识库
        if ($outputFormat -eq "text") {
            Write-Host "═══════════════════════════════════════════════════════════════"
            Write-Host "加载 /speckit.$Command 命令知识库"
            Write-Host "═══════════════════════════════════════════════════════════════"
        }

        $result = Invoke-LoadCommandKnowledge -Command $Command -ChecklistType $Type -OutputFormat $outputFormat
        if ($outputFormat -eq "json") {
            Write-Output $result
        }
    }
}
