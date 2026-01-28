#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
Cursor Rules 生成器
为 .claude/agents 目录下的子代理生成对应的 .cursor/rules 规则文件
版本：1.0.0 | 创建日期：2025-12-24
═══════════════════════════════════════════════════════════════
"""

import argparse
import re
import sys
from pathlib import Path

from common import (
    get_repo_root,
    log_info,
    log_success,
    log_warn,
    log_error,
)


def extract_agent_name(file_path: Path) -> str:
    """从代理文件中提取 name（从 frontmatter）"""
    if file_path.is_file():
        try:
            content = file_path.read_text(encoding='utf-8')
            match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
    return file_path.stem


def extract_agent_description(file_path: Path) -> str:
    """从代理文件中提取 description（从 frontmatter）"""
    if file_path.is_file():
        try:
            content = file_path.read_text(encoding='utf-8')
            match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
    return f"引用 {file_path.name} 子代理的规则"


def generate_rule_file(agent_file: Path, rules_dir: Path, force: bool = False) -> bool:
    """生成 .mdc 规则文件"""
    # 检查源文件是否存在
    if not agent_file.is_file():
        log_error(f"代理文件不存在: {agent_file}")
        return False

    # 获取文件名（不含扩展名）
    agent_name = agent_file.stem
    rule_file = rules_dir / f"{agent_name}.mdc"

    # 检查目标文件是否已存在
    if rule_file.exists() and not force:
        log_warn(f"规则文件已存在: {rule_file}")
        log_warn("使用 -f 或 --force 选项强制覆盖")
        return True

    # 提取代理信息
    agent_display_name = extract_agent_name(agent_file)
    agent_description = extract_agent_description(agent_file)

    # 首字母大写
    agent_title = agent_display_name[0].upper() + agent_display_name[1:] if agent_display_name else agent_name

    # 计算相对路径（从仓库根目录）
    relative_path = f".claude/agents/{agent_name}.md"

    # 生成规则文件内容
    # 注意：alwaysApply 设置为 false，避免性能问题
    # 规则文件按需加载，不会在启动时全部加载
    rule_content = f'''---
description: {agent_description}
globs: ["**/*"]
alwaysApply: false
---

# {agent_title} 代理规则

本规则文件引用并应用 `{relative_path}` 中定义的子代理。

**源文件**: `{relative_path}`

请直接参考源文件获取完整的代理定义、能力说明、使用场景和知识库集成要求。
'''

    # 确保目录存在
    rules_dir.mkdir(parents=True, exist_ok=True)

    # 写入文件
    rule_file.write_text(rule_content, encoding='utf-8')
    log_success(f"已生成规则文件: {rule_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='为 .claude/agents 目录下的子代理生成对应的 .cursor/rules/agents 规则文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python generate-cursor-rules.py                      # 为所有代理生成规则文件
  python generate-cursor-rules.py code-architect.md    # 为指定代理生成规则文件
  python generate-cursor-rules.py -f code-reviewer.md  # 强制覆盖已存在的文件
'''
    )
    parser.add_argument('-f', '--force', action='store_true',
                        help='强制覆盖已存在的规则文件')
    parser.add_argument('target_file', nargs='?', default='',
                        help='可选，指定要处理的代理文件')

    args = parser.parse_args()

    # 路径定义
    repo_root = get_repo_root()
    agents_dir = repo_root / '.claude' / 'agents'
    rules_dir = repo_root / '.cursor' / 'rules' / 'agents'

    # 检查目录是否存在
    if not agents_dir.is_dir():
        log_error(f"代理目录不存在: {agents_dir}")
        sys.exit(1)

    # 创建规则目录（如果不存在）
    rules_dir.mkdir(parents=True, exist_ok=True)

    # 处理文件
    if args.target_file:
        # 处理单个文件
        target = args.target_file

        # 如果是完整路径或相对路径
        if target.startswith('/') or target.startswith('.'):
            agent_file = Path(target)
        # 如果包含路径分隔符
        elif '/' in target or '\\' in target:
            agent_file = repo_root / target
        # 否则假设是文件名
        else:
            agent_file = agents_dir / target

        # 确保文件扩展名是 .md
        if not str(agent_file).endswith('.md'):
            agent_file = Path(str(agent_file) + '.md')

        log_info(f"处理代理文件: {agent_file}")
        generate_rule_file(agent_file, rules_dir, args.force)
    else:
        # 处理所有文件
        log_info(f"扫描代理目录: {agents_dir}")
        count = 0

        for agent_file in agents_dir.glob('*.md'):
            if agent_file.is_file():
                generate_rule_file(agent_file, rules_dir, args.force)
                count += 1

        if count == 0:
            log_warn("未找到任何代理文件")
        else:
            log_success(f"共处理 {count} 个代理文件")


if __name__ == '__main__':
    main()
