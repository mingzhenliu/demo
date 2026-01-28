#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Cursor Rules 生成器
# 为 .claude/agents 目录下的子代理生成对应的 .cursor/rules 规则文件
# 版本：1.0.0 | 创建日期：2025-12-24
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径定义
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_DIR="${REPO_ROOT}/.claude/agents"
RULES_DIR="${REPO_ROOT}/.cursor/rules/agents"

# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示使用说明
usage() {
    cat << EOF
用法: $0 [选项] [文件路径]

选项:
  -f, --force      强制覆盖已存在的规则文件
  -h, --help       显示此帮助信息

参数:
  文件路径         可选，指定要处理的代理文件
                  可以是完整路径或相对于 .claude/agents/ 的文件名
                  如果未指定，将处理所有 .md 文件

示例:
  $0                                    # 为所有代理生成规则文件
  $0 code-architect.md                 # 为指定代理生成规则文件
  $0 .claude/agents/api-analyzer.md    # 使用完整路径
  $0 -f code-reviewer.md               # 强制覆盖已存在的文件
EOF
}

# 从代理文件中提取 name（从 frontmatter）
extract_agent_name() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # 提取 frontmatter 中的 name 字段
        grep -E "^name:\s*" "$file" | head -1 | sed -E 's/^name:\s*//' | tr -d '[:space:]' || basename "$file" .md
    else
        basename "$file" .md
    fi
}

# 从代理文件中提取 description（从 frontmatter）
extract_agent_description() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # 提取 frontmatter 中的 description 字段（可能跨多行）
        awk '/^description:/ {found=1; sub(/^description:\s*/, ""); if ($0) print; next} found && /^[a-zA-Z-]+:/ {found=0} found && NF {print}' "$file" | head -1 || echo "引用 ${file} 子代理的规则"
    else
        echo "引用子代理的规则"
    fi
}

# 生成 .mdc 规则文件
generate_rule_file() {
    local agent_file="$1"
    local force="${2:-false}"
    
    # 检查源文件是否存在
    if [[ ! -f "$agent_file" ]]; then
        log_error "代理文件不存在: $agent_file"
        return 1
    fi
    
    # 获取文件名（不含扩展名）
    local agent_name=$(basename "$agent_file" .md)
    local rule_file="${RULES_DIR}/${agent_name}.mdc"
    
    # 检查目标文件是否已存在
    if [[ -f "$rule_file" && "$force" != "true" ]]; then
        log_warn "规则文件已存在: $rule_file"
        log_warn "使用 -f 或 --force 选项强制覆盖"
        return 0
    fi
    
    # 提取代理信息
    local agent_display_name=$(extract_agent_name "$agent_file")
    local agent_description=$(extract_agent_description "$agent_file")
    
    # 首字母大写（兼容不同系统）
    local first_char=$(echo "$agent_display_name" | cut -c1 | tr '[:lower:]' '[:upper:]')
    local rest_chars=$(echo "$agent_display_name" | cut -c2-)
    local agent_title="${first_char}${rest_chars}"
    
    # 计算相对路径（从仓库根目录）
    local relative_path=".claude/agents/${agent_name}.md"
    
    # 生成规则文件内容
    # 注意：alwaysApply 设置为 false，避免性能问题
    # 规则文件按需加载，不会在启动时全部加载
    cat > "$rule_file" << EOF
---
description: ${agent_description}
globs: ["**/*"]
alwaysApply: false
---

# ${agent_title} 代理规则

本规则文件引用并应用 \`${relative_path}\` 中定义的子代理。

**源文件**: \`${relative_path}\`

请直接参考源文件获取完整的代理定义、能力说明、使用场景和知识库集成要求。
EOF
    
    log_success "已生成规则文件: $rule_file"
}

# ═══════════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════════

main() {
    local force=false
    local target_file=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                force=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                usage
                exit 1
                ;;
            *)
                target_file="$1"
                shift
                ;;
        esac
    done
    
    # 检查目录是否存在
    if [[ ! -d "$AGENTS_DIR" ]]; then
        log_error "代理目录不存在: $AGENTS_DIR"
        exit 1
    fi
    
    # 创建规则目录（如果不存在）
    mkdir -p "$RULES_DIR"
    
    # 处理文件
    if [[ -n "$target_file" ]]; then
        # 处理单个文件
        local agent_file=""
        
        # 如果是完整路径
        if [[ "$target_file" == /* ]] || [[ "$target_file" == .* ]]; then
            agent_file="$target_file"
        # 如果包含路径分隔符
        elif [[ "$target_file" == */* ]]; then
            agent_file="${REPO_ROOT}/${target_file}"
        # 否则假设是文件名
        else
            agent_file="${AGENTS_DIR}/${target_file}"
        fi
        
        # 确保文件扩展名是 .md
        if [[ ! "$agent_file" =~ \.md$ ]]; then
            agent_file="${agent_file}.md"
        fi
        
        log_info "处理代理文件: $agent_file"
        generate_rule_file "$agent_file" "$force"
    else
        # 处理所有文件
        log_info "扫描代理目录: $AGENTS_DIR"
        local count=0
        while IFS= read -r -d '' agent_file; do
            generate_rule_file "$agent_file" "$force"
            ((count++))
        done < <(find "$AGENTS_DIR" -maxdepth 1 -name "*.md" -type f -print0)
        
        if [[ $count -eq 0 ]]; then
            log_warn "未找到任何代理文件"
        else
            log_success "共处理 $count 个代理文件"
        fi
    fi
}

# 执行主函数
main "$@"

