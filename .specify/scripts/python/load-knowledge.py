#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
SpecKit 知识库加载器 v2.2
配置驱动模式：三级配置加载，输出关键约束
版本：2.2.0 | 更新日期：2025-01-19
═══════════════════════════════════════════════════════════════

核心改进：
1. 三级配置加载：L0(基础) → L1(扩展) → 本地(覆盖)
2. 配置存放在 L0 知识库中，同步更新
3. 输出关键约束到终端（确保 AI 看到）
4. 支持 --read-content 参数直接输出文档内容
5. 仅使用 Python 标准库，无第三方依赖

配置加载优先级：
1. L0: .knowledge/upstream/L0-enterprise/speckit-config/knowledge-config.json (企业级基础)
2. L1: .knowledge/upstream/L1-project/speckit-config/local-override.json (项目扩展，可选)
3. 本地: .specify/local-override.json (本地覆盖，可选，向后兼容)
4. 遗留: .specify/knowledge-config.json (向后兼容)
"""

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from common import (
    get_repo_root,
    log_info,
    log_success,
    log_warn,
    log_error,
)


# ═══════════════════════════════════════════════════════════════
# 配置加载
# ═══════════════════════════════════════════════════════════════

def deep_merge(base: Dict, override: Dict) -> Dict:
    """深度合并两个字典，override 覆盖 base 的值"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """加载单个 JSON 文件"""
    if not file_path.exists():
        return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_error(f"JSON 解析错误 {file_path}: {e}")
        return {}


def load_json_config(repo_root: Path) -> Dict[str, Any]:
    """
    加载知识库 JSON 配置 - 三级加载

    加载优先级：
    1. L0 基础配置 (必须存在)
    2. L1 项目扩展 (可选)
    3. 本地覆盖 (可选)
    4. 遗留配置 (向后兼容)

    Returns:
        合并后的配置字典
    """
    config = {}
    config_source = "unknown"

    # 1. L0 基础配置 - 企业级标准配置
    l0_config_path = repo_root / ".knowledge" / "upstream" / "L0-enterprise" / "speckit-config" / "knowledge-config.json"

    # 2. L1 项目扩展 - 项目级覆盖
    l1_config_path = repo_root / ".knowledge" / "upstream" / "L1-project" / "speckit-config" / "local-override.json"

    # 3. 本地覆盖 - 临时调试用
    local_config_path = repo_root / ".specify" / "local-override.json"

    # 4. 遗留配置 - 向后兼容
    legacy_config_path = repo_root / ".specify" / "knowledge-config.json"

    # 尝试加载 L0 配置
    if l0_config_path.exists():
        config = load_json_file(l0_config_path)
        config_source = "L0"
        if not config:
            log_error(f"L0 配置文件为空或解析失败: {l0_config_path}")
            return {}
    else:
        # L0 不存在，尝试遗留配置
        log_warn("L0 配置不存在，尝试遗留配置")
        if legacy_config_path.exists():
            config = load_json_file(legacy_config_path)
            config_source = "legacy"
            if not config:
                log_error("遗留配置文件为空或解析失败")
                return {}
        else:
            log_error(f"知识库配置文件不存在: {l0_config_path} 或 {legacy_config_path}")
            return {}

    # 2. 加载 L1 扩展（可选）
    if l1_config_path.exists():
        l1_config = load_json_file(l1_config_path)
        if l1_config:
            config = deep_merge(config, l1_config)
            config_source += " + L1"

    # 3. 加载本地覆盖（可选）
    if local_config_path.exists():
        local_config = load_json_file(local_config_path)
        if local_config:
            config = deep_merge(config, local_config)
            config_source += " + local"

    # 调试信息
    import os
    if os.environ.get('DEBUG_CONFIG'):
        log_info(f"配置来源: {config_source}")

    return config


def get_base_path(repo_root: Path, level: str, config: Dict[str, Any]) -> Path:
    """获取知识库基础路径"""
    sources = config.get('knowledge_sources', {})
    level_config = sources.get(level, {})
    rel_path = level_config.get('path', '')

    if not rel_path:
        # 默认路径
        defaults = {
            'L0': '.knowledge/upstream/L0-enterprise',
            'L1': '.knowledge/upstream/L1-project',
            'L2': '.knowledge'
        }
        rel_path = defaults.get(level, '.knowledge')

    return repo_root / rel_path


def get_full_path(repo_root: Path, level: str, file_path: str, config: Dict[str, Any]) -> Path:
    """获取文件完整路径"""
    base_path = get_base_path(repo_root, level, config)
    return base_path / file_path


def estimate_tokens(file_path: Path) -> int:
    """计算文件 Token 估算（粗略：1 Token ≈ 4 字符）"""
    if file_path.is_file():
        try:
            chars = file_path.stat().st_size
            return chars // 4
        except OSError:
            return 0
    return 0


# ═══════════════════════════════════════════════════════════════
# 核心功能
# ═══════════════════════════════════════════════════════════════

def get_command_config(config: Dict[str, Any], command: str, checklist_type: str = "") -> Dict[str, Any]:
    """获取命令的知识库配置"""
    cmd_knowledge = config.get('command_knowledge', {})

    # 处理 checklist 的特殊类型
    if command == 'checklist' and checklist_type:
        checklist_config = cmd_knowledge.get('checklist', {})
        types = checklist_config.get('types', {})
        type_config = types.get(checklist_type, {})
        return {
            'description': type_config.get('description', f'{checklist_type} 检查清单'),
            'documents': type_config.get('documents', [])
        }

    # 处理 feature-dev 阶段
    if command.startswith('feature-dev-') or command.startswith('fd-'):
        feature_dev = config.get('feature_dev', {})

        # 映射短名称到完整阶段名
        phase_mapping = {
            'feature-dev-phase1': 'phase1_discovery',
            'fd-discovery': 'phase1_discovery',
            'feature-dev-phase2': 'phase2_exploration',
            'fd-exploration': 'phase2_exploration',
            'feature-dev-phase3': 'phase3_clarification',
            'fd-clarification': 'phase3_clarification',
            'feature-dev-phase4': 'phase4_architecture',
            'fd-architecture': 'phase4_architecture',
            'feature-dev-phase5': 'phase5_implementation',
            'fd-implementation': 'phase5_implementation',
            'feature-dev-phase6': 'phase6_review',
            'fd-review': 'phase6_review',
            'feature-dev-phase7': 'phase7_summary',
            'fd-summary': 'phase7_summary',
        }

        phase_key = phase_mapping.get(command)
        if phase_key:
            return feature_dev.get(phase_key, {})

    return cmd_knowledge.get(command, {})


def load_command_knowledge(
    repo_root: Path,
    command: str,
    checklist_type: str = "",
    output_format: str = "text",
    read_content: bool = False
) -> Tuple[bool, Optional[dict]]:
    """加载命令所需的知识库"""

    config = load_json_config(repo_root)
    if not config:
        return False, {"error": "KNOW-004", "error_message": "知识库配置文件不存在或解析失败"}

    cmd_config = get_command_config(config, command, checklist_type)
    if not cmd_config:
        return False, {"error": "UNKNOWN_COMMAND", "error_message": f"未知命令: {command}"}

    documents: List[dict] = []
    has_error = False
    has_critical_error = False
    total_tokens = 0
    all_constraints: List[Dict[str, Any]] = []

    cmd_description = cmd_config.get('description', command)
    doc_list = cmd_config.get('documents', [])

    # 收集所有约束
    for doc in doc_list:
        if doc.get('constraints'):
            all_constraints.append({
                'description': doc.get('description', doc.get('path')),
                'level': doc.get('level'),
                'critical': doc.get('critical', False),
                'constraints': doc.get('constraints', [])
            })

    # 文本格式输出
    if output_format == "text":
        print("═══════════════════════════════════════════════════════════════")
        print(f"命令: /speckit.{command}")
        print(f"描述: {cmd_description}")
        print("═══════════════════════════════════════════════════════════════")
        print()

        # 输出关键约束（这是重点！确保 AI 看到）
        if all_constraints:
            print("⚠️  【关键约束 - 必须遵守】")
            print("─────────────────────────────────────────────────────────────────")

            for item in all_constraints:
                level_icon = "🔴" if item['critical'] else "🟡"
                print(f"\n{level_icon} [{item['level']}] {item['description']}:")
                for constraint in item['constraints']:
                    print(f"   • {constraint}")

            print()
            print("─────────────────────────────────────────────────────────────────")
        print()

    # 处理文档
    for doc in doc_list:
        level = doc.get('level', 'L2')
        doc_path = doc.get('path', '')
        required = doc.get('required', False)
        critical = doc.get('critical', False)
        description = doc.get('description', '')
        glob_pattern = doc.get('glob_pattern')
        dynamic = doc.get('dynamic', False)

        # 跳过动态加载的文档（需要运行时上下文）
        if dynamic and not glob_pattern:
            continue

        # 处理 glob 模式
        if glob_pattern or '*' in doc_path:
            pattern = glob_pattern or doc_path
            base_path = get_base_path(repo_root, level, config)
            full_pattern = str(base_path / pattern)

            matched_files = glob.glob(full_pattern, recursive=True)

            for matched_file in matched_files:
                matched_path = Path(matched_file)
                if matched_path.is_file():
                    tokens = estimate_tokens(matched_path)
                    total_tokens += tokens

                    try:
                        rel_path = matched_path.relative_to(base_path)
                    except ValueError:
                        rel_path = matched_path.name

                    documents.append({
                        "level": level,
                        "path": str(rel_path),
                        "full_path": str(matched_path),
                        "description": description,
                        "status": "exists",
                        "required": required,
                        "critical": critical,
                        "tokens": tokens
                    })

                    if output_format == "text":
                        log_info(f"[{level}] {rel_path} ({tokens} tokens)")
                        print(f"       └─ {description}")
        else:
            # 单个文件
            full_path = get_full_path(repo_root, level, doc_path, config)

            status = "missing"
            tokens = 0

            if full_path.is_file():
                status = "exists"
                tokens = estimate_tokens(full_path)
                total_tokens += tokens

                if output_format == "text":
                    req_tag = "必需" if required else "可选"
                    crit_tag = " ⚠️ CRITICAL" if critical else ""
                    log_success(f"[{level}] {doc_path} ({req_tag}{crit_tag}, {tokens} tokens)")
                    print(f"       └─ {description}")
            else:
                # 处理缺失
                if level == "L0" and required:
                    has_error = True
                    if critical:
                        has_critical_error = True
                    if output_format == "text":
                        log_error(f"[{level}] {doc_path} - 缺失 (CRITICAL)")
                        print(f"       └─ {description}")
                elif level == "L1" and required:
                    if output_format == "text":
                        log_warn(f"[{level}] {doc_path} - 缺失 (WARNING)")
                        print(f"       └─ {description}")
                else:
                    if output_format == "text":
                        log_info(f"[{level}] {doc_path} - 缺失 (跳过)")

            documents.append({
                "level": level,
                "path": doc_path,
                "full_path": str(full_path),
                "description": description,
                "status": status,
                "required": required,
                "critical": critical,
                "tokens": tokens
            })

    # 构建结果
    result = {
        "command": command,
        "description": cmd_description,
        "status": "error" if has_error else "success",
        "has_critical_error": has_critical_error,
        "documents": documents,
        "constraints": all_constraints,
        "total_tokens": total_tokens,
        "doc_count": len(documents),
        "paths": {
            "required": [d["full_path"] for d in documents if d["required"] and d["status"] == "exists"],
            "optional": [d["full_path"] for d in documents if not d["required"] and d["status"] == "exists"],
            "missing": [d["full_path"] for d in documents if d["status"] == "missing"]
        }
    }

    if has_error:
        result["error_code"] = "KNOW-001"
        result["error_message"] = "L0 知识库文档缺失，流程被阻止"

    # 输出格式处理
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print()
        print("═══════════════════════════════════════════════════════════════")
        print(f"总计: {len(documents)} 个文档, 约 {total_tokens} tokens")
        print("═══════════════════════════════════════════════════════════════")

        if has_critical_error:
            log_error("❌ 流程被阻止：L0 CRITICAL 文档缺失")
            print()
            print("下一步：请确保 L0 知识库文档存在，然后重新运行命令。")
        elif has_error:
            log_error("❌ 知识库加载失败：L0 必需文档缺失")
        else:
            print()
            print("✅ 知识库加载成功")
            print()
            print("📋 需要读取的文档列表：")
            for doc in documents:
                if doc["status"] == "exists":
                    print(f"   - {doc['full_path']}")

    # 如果需要读取内容
    if read_content and output_format == "text":
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("📖 文档内容")
        print("═══════════════════════════════════════════════════════════════")

        for doc in documents:
            if doc["status"] == "exists":
                full_path = Path(doc["full_path"])
                print()
                print(f"### [{doc['level']}] {doc['path']}")
                print(f"### {doc['description']}")
                print("---")
                try:
                    content = full_path.read_text(encoding='utf-8')
                    # 限制输出长度
                    max_chars = 8000  # 约 2000 tokens
                    if len(content) > max_chars:
                        content = content[:max_chars] + "\n\n... [内容已截断] ..."
                    print(content)
                except Exception as e:
                    print(f"[读取错误: {e}]")
                print("---")

    return not has_error, result


def validate_knowledge_structure(repo_root: Path, output_format: str = "text") -> bool:
    """验证知识库结构"""
    config = load_json_config(repo_root)

    if output_format == "text":
        print("═══════════════════════════════════════════════════════════════")
        print("知识库结构验证")
        print("═══════════════════════════════════════════════════════════════")

    sources = config.get('knowledge_sources', {})
    results = {}

    for level in ['L0', 'L1', 'L2']:
        level_config = sources.get(level, {})
        path = get_base_path(repo_root, level, config)

        if path.is_dir():
            results[level] = "ok"
            if output_format == "text":
                log_success(f"{level} {level_config.get('description', '')}: {path}")
        else:
            on_missing = level_config.get('on_missing', 'skip')
            results[level] = "missing"

            if on_missing == 'error':
                if output_format == "text":
                    log_error(f"{level} {level_config.get('description', '')}: {path} - 缺失")
            elif on_missing == 'warn':
                if output_format == "text":
                    log_warn(f"{level} {level_config.get('description', '')}: {path} - 缺失")
            else:
                if output_format == "text":
                    log_info(f"{level} {level_config.get('description', '')}: {path} - 缺失 (跳过)")

    if output_format == "json":
        print(json.dumps(results, ensure_ascii=False))

    return results.get('L0') != 'missing'


def list_commands(config: Dict[str, Any]):
    """列出所有可用命令"""
    print("可用命令：")
    print()

    cmd_knowledge = config.get('command_knowledge', {})

    print("  SpecKit 命令：")
    for cmd, cfg in cmd_knowledge.items():
        desc = cfg.get('description', '')
        doc_count = len(cfg.get('documents', []))
        print(f"  {cmd:15} - {desc} ({doc_count} 个文档)")

    print()
    print("  Feature-Dev 插件阶段：")
    feature_dev = config.get('feature_dev', {})
    phase_names = {
        'phase1_discovery': 'fd-discovery',
        'phase2_exploration': 'fd-exploration',
        'phase3_clarification': 'fd-clarification',
        'phase4_architecture': 'fd-architecture',
        'phase5_implementation': 'fd-implementation',
        'phase6_review': 'fd-review',
        'phase7_summary': 'fd-summary',
    }

    for phase_key, short_name in phase_names.items():
        phase_cfg = feature_dev.get(phase_key, {})
        desc = phase_cfg.get('description', '')
        doc_count = len(phase_cfg.get('documents', []))
        print(f"  {short_name:15} - {desc} ({doc_count} 个文档)")


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='SpecKit 知识库加载器 v2.0 - 配置驱动模式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python load-knowledge.py implement                 # 加载 implement 命令所需知识库
  python load-knowledge.py implement --json          # JSON 格式输出
  python load-knowledge.py implement --read-content  # 输出文档内容
  python load-knowledge.py checklist --type security # 加载安全检查清单知识库
  python load-knowledge.py validate                  # 验证知识库结构
  python load-knowledge.py list                      # 列出所有可用命令

特性:
  - 从 .specify/knowledge-config.json 读取配置
  - 输出关键约束到终端（确保 AI 看到）
  - 支持 --read-content 直接输出文档内容
  - 仅使用 Python 标准库，无第三方依赖
'''
    )
    parser.add_argument('--json', '-j', action='store_true', dest='json_mode',
                        help='输出 JSON 格式')
    parser.add_argument('--type', '-t', dest='checklist_type', default='',
                        help='checklist 类型 (security/testing/api/coding)')
    parser.add_argument('--read-content', '-r', action='store_true', dest='read_content',
                        help='读取并输出文档内容')
    parser.add_argument('command', nargs='?', default='',
                        help='命令名称或 validate/list')

    args = parser.parse_args()
    output_format = "json" if args.json_mode else "text"

    repo_root = get_repo_root()
    config = load_json_config(repo_root)

    # 处理特殊命令
    if args.command == "validate":
        success = validate_knowledge_structure(repo_root, output_format)
        sys.exit(0 if success else 1)

    if args.command == "list":
        list_commands(config)
        sys.exit(0)

    if not args.command:
        parser.print_usage()
        sys.exit(1)

    # 验证命令是否有效
    cmd_config = get_command_config(config, args.command, args.checklist_type)
    if not cmd_config:
        log_error(f"未知命令: {args.command}")
        list_commands(config)
        sys.exit(1)

    # 加载知识库
    success, _ = load_command_knowledge(
        repo_root,
        args.command,
        args.checklist_type,
        output_format,
        args.read_content
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
