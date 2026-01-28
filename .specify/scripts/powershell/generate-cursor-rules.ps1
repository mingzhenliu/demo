#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════
# Cursor Rules 生成器
# 为 .claude/agents 目录下的子代理生成对应的 .cursor/rules 规则文件
# 版本：1.0.0 | 创建日期：2025-12-24
# ═══════════════════════════════════════════════════════════════

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$TargetFile,

    [Parameter()]
    [Alias("f")]
    [switch]$Force,

    [Parameter()]
    [Alias("h")]
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# 路径定义
try {
    $REPO_ROOT = git rev-parse --show-toplevel 2>$null
    if (-not $REPO_ROOT) {
        $REPO_ROOT = Get-Location
    }
}
catch {
    $REPO_ROOT = Get-Location
}

$AGENTS_DIR = Join-Path $REPO_ROOT ".claude" "agents"
$RULES_DIR = Join-Path $REPO_ROOT ".cursor" "rules" "agents"

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

# 显示使用说明
function Show-Usage {
    Write-Host @"
用法: $($MyInvocation.MyCommand.Name) [选项] [文件路径]

选项:
  -Force, -f     强制覆盖已存在的规则文件
  -Help, -h      显示此帮助信息

参数:
  文件路径       可选，指定要处理的代理文件
                可以是完整路径或相对于 .claude/agents/ 的文件名
                如果未指定，将处理所有 .md 文件

示例:
  .\generate-cursor-rules.ps1                                    # 为所有代理生成规则文件
  .\generate-cursor-rules.ps1 code-architect.md                 # 为指定代理生成规则文件
  .\generate-cursor-rules.ps1 .claude/agents/api-analyzer.md    # 使用完整路径
  .\generate-cursor-rules.ps1 -Force code-reviewer.md           # 强制覆盖已存在的文件
"@
}

# 从代理文件中提取 name（从 frontmatter）
function Get-AgentName {
    param([string]$FilePath)

    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        if ($content -match '(?m)^name:\s*(.+)$') {
            return $Matches[1].Trim()
        }
    }
    return [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
}

# 从代理文件中提取 description（从 frontmatter）
function Get-AgentDescription {
    param([string]$FilePath)

    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        if ($content -match '(?m)^description:\s*(.+)$') {
            return $Matches[1].Trim()
        }
    }
    return "引用 $FilePath 子代理的规则"
}

# 生成 .mdc 规则文件
function New-RuleFile {
    param(
        [string]$AgentFile,
        [bool]$ForceOverwrite = $false
    )

    # 检查源文件是否存在
    if (-not (Test-Path $AgentFile)) {
        Write-Error "代理文件不存在: $AgentFile"
        return 1
    }

    # 获取文件名（不含扩展名）
    $agentName = [System.IO.Path]::GetFileNameWithoutExtension($AgentFile)
    $ruleFile = Join-Path $RULES_DIR "$agentName.mdc"

    # 检查目标文件是否已存在
    if ((Test-Path $ruleFile) -and (-not $ForceOverwrite)) {
        Write-Warn "规则文件已存在: $ruleFile"
        Write-Warn "使用 -Force 或 -f 选项强制覆盖"
        return 0
    }

    # 提取代理信息
    $agentDisplayName = Get-AgentName -FilePath $AgentFile
    $agentDescription = Get-AgentDescription -FilePath $AgentFile

    # 首字母大写
    $agentTitle = $agentDisplayName.Substring(0, 1).ToUpper() + $agentDisplayName.Substring(1)

    # 计算相对路径（从仓库根目录）
    $relativePath = ".claude/agents/$agentName.md"

    # 生成规则文件内容
    # 注意：alwaysApply 设置为 false，避免性能问题
    # 规则文件按需加载，不会在启动时全部加载
    $ruleContent = @"
---
description: $agentDescription
globs: ["**/*"]
alwaysApply: false
---

# $agentTitle 代理规则

本规则文件引用并应用 ``$relativePath`` 中定义的子代理。

**源文件**: ``$relativePath``

请直接参考源文件获取完整的代理定义、能力说明、使用场景和知识库集成要求。
"@

    $ruleContent | Out-File -FilePath $ruleFile -Encoding utf8

    Write-Success "已生成规则文件: $ruleFile"
    return 0
}

# ═══════════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════════

if ($Help) {
    Show-Usage
    exit 0
}

# 检查目录是否存在
if (-not (Test-Path $AGENTS_DIR)) {
    Write-Error "代理目录不存在: $AGENTS_DIR"
    exit 1
}

# 创建规则目录（如果不存在）
if (-not (Test-Path $RULES_DIR)) {
    New-Item -ItemType Directory -Path $RULES_DIR -Force | Out-Null
}

# 处理文件
if ($TargetFile) {
    # 处理单个文件
    $agentFile = ""

    # 如果是完整路径
    if ([System.IO.Path]::IsPathRooted($TargetFile) -or $TargetFile.StartsWith(".")) {
        $agentFile = $TargetFile
    }
    # 如果包含路径分隔符
    elseif ($TargetFile -match "[/\\]") {
        $agentFile = Join-Path $REPO_ROOT $TargetFile
    }
    # 否则假设是文件名
    else {
        $agentFile = Join-Path $AGENTS_DIR $TargetFile
    }

    # 确保文件扩展名是 .md
    if (-not $agentFile.EndsWith(".md")) {
        $agentFile = "$agentFile.md"
    }

    Write-Info "处理代理文件: $agentFile"
    New-RuleFile -AgentFile $agentFile -ForceOverwrite $Force
}
else {
    # 处理所有文件
    Write-Info "扫描代理目录: $AGENTS_DIR"
    $count = 0

    Get-ChildItem -Path $AGENTS_DIR -Filter "*.md" -File | ForEach-Object {
        New-RuleFile -AgentFile $_.FullName -ForceOverwrite $Force
        $count++
    }

    if ($count -eq 0) {
        Write-Warn "未找到任何代理文件"
    }
    else {
        Write-Success "共处理 $count 个代理文件"
    }
}
