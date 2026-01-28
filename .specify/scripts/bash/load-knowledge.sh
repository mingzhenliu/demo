#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# SpecKit 知识库加载器
# 扁平引用模式：L2 并行引用 L0 和 L1
# 版本：1.0.0 | 创建日期：2025-12-19
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 知识库根路径（扁平模式）
L0_PATH=".knowledge/upstream/L0-enterprise"
L1_PATH=".knowledge/upstream/L1-project"
L2_PATH=".knowledge"

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

# 获取文件完整路径
get_full_path() {
    local level=$1
    local file_path=$2

    case $level in
        "L0") echo "${L0_PATH}/${file_path}" ;;
        "L1") echo "${L1_PATH}/${file_path}" ;;
        "L2") echo "${L2_PATH}/${file_path}" ;;
    esac
}

# 计算文件 Token 估算（粗略：1 Token ≈ 4 字符）
estimate_tokens() {
    local file_path=$1

    if [[ -f "$file_path" ]]; then
        local chars
        chars=$(wc -c < "$file_path" | tr -d ' ')
        echo $((chars / 4))
    else
        echo 0
    fi
}

# ═══════════════════════════════════════════════════════════════
# 命令知识库映射函数
# ═══════════════════════════════════════════════════════════════

get_required_docs() {
    local command=$1
    local checklist_type=${2:-""}

    case $command in
        "specify")
            echo "L1:business/glossary.md L1:business/rules.md L2:context.md"
            ;;
        "clarify")
            echo "L1:business/glossary.md"
            ;;
        "plan")
            echo "L0:constitution/architecture-principles.md L0:constitution/security-baseline.md L0:standards/api-design-guide.md L0:standards/testing-standards.md L1:architecture/tech-stack.md L1:standards/coding.md"
            ;;
        "tasks")
            echo "L2:code-derived/module_tree.json"
            ;;
        "implement")
            echo "L0:ai-coding/ai-coding-policy.md L0:constitution/security-baseline.md L1:standards/coding.md L1:standards/api.md L1:standards/testing.md"
            ;;
        "analyze")
            echo "L0:constitution/architecture-principles.md L1:business/glossary.md"
            ;;
        "constitution")
            echo "L0:constitution/constitution-template.md L0:constitution/architecture-principles.md L0:constitution/security-baseline.md"
            ;;
        "checklist")
            case $checklist_type in
                "security")
                    echo "L0:constitution/security-baseline.md"
                    ;;
                "testing")
                    echo "L0:standards/testing-standards.md L1:standards/testing.md"
                    ;;
                "api")
                    echo "L0:standards/api-design-guide.md L1:standards/api.md"
                    ;;
                "coding")
                    echo "L0:standards/coding-standards/java.md L1:standards/coding.md"
                    ;;
                *)
                    echo ""
                    ;;
            esac
            ;;
        # ═══════════════════════════════════════════════════════════════
        # Feature-Dev 插件各阶段知识库映射
        # ═══════════════════════════════════════════════════════════════
        "feature-dev-phase1"|"fd-discovery")
            echo "L1:business/glossary.md L2:context.md"
            ;;
        "feature-dev-phase2"|"fd-exploration")
            echo "L2:code-derived/module_tree.json L2:code-derived/overview.md"
            ;;
        "feature-dev-phase3"|"fd-clarification")
            echo "L1:business/rules.md L1:business/domain-model.md"
            ;;
        "feature-dev-phase4"|"fd-architecture")
            # Critical + Required 合并
            echo "L0:constitution/architecture-principles.md L0:constitution/security-baseline.md L0:technology-radar/hold.md L0:technology-radar/adopt.md L1:architecture/tech-stack.md"
            ;;
        "feature-dev-phase5"|"fd-implementation")
            echo "L0:ai-coding/ai-coding-policy.md L0:constitution/security-baseline.md L0:standards/testing-standards.md L1:standards/coding.md"
            ;;
        "feature-dev-phase6"|"fd-review")
            echo "L0:constitution/security-baseline.md L0:standards/api-design-guide.md L1:standards/testing.md"
            ;;
        "feature-dev-phase7"|"fd-summary")
            echo ""  # 无必需文档
            ;;
        *)
            echo ""
            ;;
    esac
}

get_optional_docs() {
    local command=$1

    case $command in
        "specify")
            echo "L1:business/domain-*.md"
            ;;
        "clarify")
            echo "L1:business/rules.md L1:business/workflows/*.md"
            ;;
        "plan")
            echo "L0:technology-radar/hold.md L0:technology-radar/adopt.md L1:architecture/decisions/*.md L2:code-derived/overview.md"
            ;;
        "tasks")
            echo "L2:code-derived/overview.md"
            ;;
        "implement")
            echo "L0:standards/coding-standards/java.md"
            ;;
        "analyze")
            echo "L0:constitution/security-baseline.md"
            ;;
        "constitution")
            echo "L0:constitution/compliance-requirements.md"
            ;;
        # ═══════════════════════════════════════════════════════════════
        # Feature-Dev 插件各阶段可选知识库
        # ═══════════════════════════════════════════════════════════════
        "feature-dev-phase1"|"fd-discovery")
            echo ""
            ;;
        "feature-dev-phase2"|"fd-exploration")
            echo "L1:architecture/service-catalog.md"
            ;;
        "feature-dev-phase3"|"fd-clarification")
            echo "L1:business/workflows/*.md"
            ;;
        "feature-dev-phase4"|"fd-architecture")
            echo "L1:architecture/decisions/*.md"
            ;;
        "feature-dev-phase5"|"fd-implementation")
            echo "L0:standards/coding-standards/*.md L2:code-derived/*.md"
            ;;
        "feature-dev-phase6"|"fd-review")
            echo "L1:standards/coding.md"
            ;;
        "feature-dev-phase7"|"fd-summary")
            echo "L1:business/glossary.md"
            ;;
        *)
            echo ""
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════
# 核心功能
# ═══════════════════════════════════════════════════════════════

# 加载命令所需的知识库
load_command_knowledge() {
    local command=$1
    local checklist_type=${2:-""}
    local output_format=${3:-"text"}

    local required_docs
    local optional_docs

    required_docs=$(get_required_docs "$command" "$checklist_type")
    optional_docs=$(get_optional_docs "$command")

    local result_json="{"
    result_json+="\"command\":\"$command\","
    result_json+="\"status\":\"success\","
    result_json+="\"documents\":["

    local has_error=false
    local total_tokens=0
    local doc_count=0
    local first_doc=true

    # 处理必需文档
    if [[ -n "$required_docs" ]]; then
        for doc_spec in $required_docs; do
            local level="${doc_spec%%:*}"
            local doc_path="${doc_spec#*:}"
            local full_path
            full_path=$(get_full_path "$level" "$doc_path")

            local status="missing"
            local tokens=0

            if [[ -f "$full_path" ]]; then
                status="exists"
                tokens=$(estimate_tokens "$full_path")
                total_tokens=$((total_tokens + tokens))

                if [[ "$output_format" == "text" ]]; then
                    log_success "[$level] $doc_path (${tokens} tokens)"
                fi
            else
                # 必需文档缺失处理
                case $level in
                    "L0")
                        has_error=true
                        if [[ "$output_format" == "text" ]]; then
                            log_error "[$level] $doc_path - MISSING (CRITICAL)"
                        fi
                        ;;
                    "L1")
                        if [[ "$output_format" == "text" ]]; then
                            log_warn "[$level] $doc_path - MISSING (WARNING)"
                        fi
                        ;;
                    "L2")
                        if [[ "$output_format" == "text" ]]; then
                            log_info "[$level] $doc_path - MISSING (SKIPPED)"
                        fi
                        ;;
                esac
            fi

            if [[ "$first_doc" == true ]]; then
                first_doc=false
            else
                result_json+=","
            fi
            result_json+="{\"level\":\"$level\",\"path\":\"$doc_path\",\"status\":\"$status\",\"required\":true,\"tokens\":$tokens}"
            doc_count=$((doc_count + 1))
        done
    fi

    # 处理可选文档
    if [[ -n "$optional_docs" ]]; then
        for doc_spec in $optional_docs; do
            local level="${doc_spec%%:*}"
            local doc_path="${doc_spec#*:}"
            local full_path
            full_path=$(get_full_path "$level" "$doc_path")

            # 处理通配符
            if [[ "$doc_path" == *"*"* ]]; then
                local base_path=""
                case $level in
                    "L0") base_path="$L0_PATH" ;;
                    "L1") base_path="$L1_PATH" ;;
                    "L2") base_path="$L2_PATH" ;;
                esac

                # 使用 find 查找匹配的文件
                while IFS= read -r matched_file; do
                    if [[ -n "$matched_file" && -f "$matched_file" ]]; then
                        local tokens
                        tokens=$(estimate_tokens "$matched_file")
                        total_tokens=$((total_tokens + tokens))

                        local rel_path="${matched_file#$base_path/}"

                        if [[ "$first_doc" == true ]]; then
                            first_doc=false
                        else
                            result_json+=","
                        fi
                        result_json+="{\"level\":\"$level\",\"path\":\"$rel_path\",\"status\":\"exists\",\"required\":false,\"tokens\":$tokens}"
                        doc_count=$((doc_count + 1))

                        if [[ "$output_format" == "text" ]]; then
                            log_info "[$level] $rel_path (optional, ${tokens} tokens)"
                        fi
                    fi
                done < <(find "$base_path" -path "$base_path/$doc_path" -type f 2>/dev/null || true)
            else
                local status="missing"
                local tokens=0

                if [[ -f "$full_path" ]]; then
                    status="exists"
                    tokens=$(estimate_tokens "$full_path")
                    total_tokens=$((total_tokens + tokens))

                    if [[ "$output_format" == "text" ]]; then
                        log_info "[$level] $doc_path (optional, ${tokens} tokens)"
                    fi

                    if [[ "$first_doc" == true ]]; then
                        first_doc=false
                    else
                        result_json+=","
                    fi
                    result_json+="{\"level\":\"$level\",\"path\":\"$doc_path\",\"status\":\"$status\",\"required\":false,\"tokens\":$tokens}"
                    doc_count=$((doc_count + 1))
                fi
            fi
        done
    fi

    result_json+="],"
    result_json+="\"total_tokens\":$total_tokens,"
    result_json+="\"doc_count\":$doc_count"

    if [[ "$has_error" == true ]]; then
        result_json+=",\"status\":\"error\",\"error_code\":\"KNOW-001\",\"error_message\":\"L0 知识库文档缺失\""
    fi

    result_json+="}"

    if [[ "$output_format" == "json" ]]; then
        echo "$result_json"
    else
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "总计: $doc_count 个文档, 约 $total_tokens tokens"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        if [[ "$has_error" == true ]]; then
            log_error "知识库加载失败：L0 必需文档缺失"
            return 1
        fi
    fi
}

# 验证知识库结构
validate_knowledge_structure() {
    local output_format=${1:-"text"}

    if [[ "$output_format" == "text" ]]; then
        echo "═══════════════════════════════════════════════════════════════"
        echo "知识库结构验证（扁平模式）"
        echo "═══════════════════════════════════════════════════════════════"
    fi

    local l0_status="ok"
    local l1_status="ok"
    local l2_status="ok"

    # 检查 L0
    if [[ ! -d "$L0_PATH" ]]; then
        l0_status="missing"
        if [[ "$output_format" == "text" ]]; then
            log_error "L0 企业级知识库不存在: $L0_PATH"
        fi
    else
        if [[ "$output_format" == "text" ]]; then
            log_success "L0 企业级知识库: $L0_PATH"
        fi
    fi

    # 检查 L1
    if [[ ! -d "$L1_PATH" ]]; then
        l1_status="missing"
        if [[ "$output_format" == "text" ]]; then
            log_warn "L1 项目级知识库不存在: $L1_PATH"
        fi
    else
        if [[ "$output_format" == "text" ]]; then
            log_success "L1 项目级知识库: $L1_PATH"
        fi
    fi

    # 检查 L2
    if [[ ! -d "$L2_PATH" ]]; then
        l2_status="missing"
        if [[ "$output_format" == "text" ]]; then
            log_info "L2 仓库级知识库不存在: $L2_PATH"
        fi
    else
        if [[ "$output_format" == "text" ]]; then
            log_success "L2 仓库级知识库: $L2_PATH"
        fi
    fi

    if [[ "$output_format" == "json" ]]; then
        echo "{\"L0\":\"$l0_status\",\"L1\":\"$l1_status\",\"L2\":\"$l2_status\"}"
    fi

    if [[ "$l0_status" == "missing" ]]; then
        return 1
    fi
    return 0
}

# 列出所有可用命令
list_commands() {
    echo "可用命令："
    echo ""
    echo "  SpecKit 命令："
    echo "  specify      - 功能规格创建"
    echo "  clarify      - 需求澄清"
    echo "  plan         - 实施计划生成"
    echo "  tasks        - 任务列表生成"
    echo "  implement    - 代码实现"
    echo "  analyze      - 跨产物分析"
    echo "  checklist    - 检查清单生成 (可加类型: security/testing/api/coding)"
    echo "  constitution - 项目章程创建/更新"
    echo ""
    echo "  Feature-Dev 插件阶段："
    echo "  feature-dev-phase1 (fd-discovery)      - 阶段1：发现"
    echo "  feature-dev-phase2 (fd-exploration)    - 阶段2：代码库探索"
    echo "  feature-dev-phase3 (fd-clarification)  - 阶段3：澄清问题"
    echo "  feature-dev-phase4 (fd-architecture)   - 阶段4：架构设计 (关键)"
    echo "  feature-dev-phase5 (fd-implementation) - 阶段5：实现"
    echo "  feature-dev-phase6 (fd-review)         - 阶段6：质量审查"
    echo "  feature-dev-phase7 (fd-summary)        - 阶段7：总结"
}

# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

usage() {
    echo "用法: $0 <command> [options]"
    echo ""
    echo "命令:"
    echo "  <command>     加载指定命令所需的知识库 (specify/clarify/plan/tasks/implement/analyze/checklist)"
    echo "  validate      验证知识库结构"
    echo "  list          列出所有可用命令"
    echo ""
    echo "选项:"
    echo "  --json        输出 JSON 格式"
    echo "  --type <type> checklist 类型 (security/testing/api/coding)"
    echo ""
    echo "示例:"
    echo "  $0 plan                       # 加载 plan 命令所需知识库"
    echo "  $0 plan --json                # JSON 格式输出"
    echo "  $0 checklist --type security  # 加载安全检查清单知识库"
    echo "  $0 validate                   # 验证知识库结构"
}

main() {
    local command=""
    local output_format="text"
    local checklist_type=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --json)
                output_format="json"
                shift
                ;;
            --type)
                checklist_type="$2"
                shift 2
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            validate)
                validate_knowledge_structure "$output_format"
                exit $?
                ;;
            list)
                list_commands
                exit 0
                ;;
            *)
                command="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$command" ]]; then
        usage
        exit 1
    fi

    # 验证命令是否有效
    local valid_commands="specify clarify plan tasks implement analyze checklist constitution feature-dev-phase1 feature-dev-phase2 feature-dev-phase3 feature-dev-phase4 feature-dev-phase5 feature-dev-phase6 feature-dev-phase7 fd-discovery fd-exploration fd-clarification fd-architecture fd-implementation fd-review fd-summary"
    if [[ ! " $valid_commands " =~ " $command " ]]; then
        log_error "未知命令: $command"
        list_commands
        exit 1
    fi

    # 加载知识库
    if [[ "$output_format" == "text" ]]; then
        echo "═══════════════════════════════════════════════════════════════"
        echo "加载 /speckit.$command 命令知识库"
        echo "═══════════════════════════════════════════════════════════════"
    fi

    load_command_knowledge "$command" "$checklist_type" "$output_format"
}

main "$@"
