#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
SpecKit 增量更新脚本 v2.0
从模板仓库增量更新 SpecKit 核心文件
版本：2.0.0 | 更新日期：2026-01-20
═══════════════════════════════════════════════════════════════

功能：
1. 支持目录级别自动同步配置
2. 三层过滤保护机制（目录黑名单、文件黑名单、本地覆盖）
3. 删除名单功能
4. v1.0 配置兼容与自动迁移
5. 预览模式和详细日志
"""

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


# ============================================================================
# 颜色定义
# ============================================================================

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_info(message: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message: str) -> None:
    print(f"{Colors.GREEN}[OK]{Colors.NC} {message}")


def print_warning(message: str) -> None:
    print(f"{Colors.YELLOW}[SKIP]{Colors.NC} {message}")


def print_error(message: str) -> None:
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def print_verbose(message: str, verbose: bool) -> None:
    if verbose:
        print(f"{Colors.CYAN}[DEBUG]{Colors.NC} {message}")


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class ExclusionReason:
    """排除原因常量"""
    NOT_IN_WHITELIST = "不在目录白名单中"
    IN_EXCLUDE_DIR = "在目录黑名单中"
    IN_DELETE_LIST = "在删除名单中"
    IN_BLACKLIST = "在文件黑名单中"
    LOCAL_OVERRIDE = "本地覆盖标记"
    NO_DIFFERENCE = "文件内容相同"
    NOT_EXIST_NEW_POLICY = "目标文件不存在且新文件策略禁用"
    SYMLINK = "符号链接文件"


@dataclass
class FileToSync:
    """需要同步的文件"""
    rel_path: str
    action: str  # create, update, delete, skip
    src: str = ""
    dst: str = ""
    reason: str = ""


@dataclass
class SyncConfig:
    """同步配置"""
    version: str = "2.0.0"
    sync_directories: List[Dict] = field(default_factory=list)
    exclude_directories: List[Dict] = field(default_factory=list)
    delete_list: List[str] = field(default_factory=list)
    file_blacklist: List[str] = field(default_factory=list)
    new_file_policy: Dict = field(default_factory=lambda: {"enabled": False})
    local_overrides: Dict = field(default_factory=lambda: {"enabled": True})
    backup: Dict = field(default_factory=lambda: {"enabled": True})


@dataclass
class SyncResult:
    """同步执行结果"""
    updated: int = 0
    skipped: int = 0
    created: int = 0
    deleted: int = 0
    excluded: int = 0
    errors: int = 0
    files: List[FileToSync] = field(default_factory=list)
    excluded_files: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)


# ============================================================================
# 工具函数
# ============================================================================

def get_repo_root() -> Path:
    """获取 git 仓库根目录"""
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print_error("无法获取 git 仓库根目录")
        sys.exit(1)
    return Path(result.stdout.strip())


def get_script_dir() -> Path:
    """获取脚本所在目录"""
    return Path(__file__).resolve().parent


def normalize_path(path: str) -> str:
    """标准化路径，使用 / 作为分隔符"""
    return path.replace(os.sep, '/')


def match_pattern(pattern: str, file_path: str) -> bool:
    """
    匹配文件路径模式（支持通配符）

    Args:
        pattern: 模式字符串，支持 * 通配符
        file_path: 文件路径（标准化后，使用 / 分隔）

    Returns:
        bool: 是否匹配
    """
    # 标准化路径
    pattern = normalize_path(pattern)
    file_path = normalize_path(file_path)

    # 如果模式不包含通配符，精确匹配
    if '*' not in pattern and '?' not in pattern and '[' not in pattern:
        return file_path == pattern

    # 使用 fnmatch 进行模式匹配
    return fnmatch.fnmatch(file_path, pattern)


def match_any_pattern(patterns: List[str], file_path: str) -> bool:
    """检查文件路径是否匹配任一模式"""
    for pattern in patterns:
        if match_pattern(pattern, file_path):
            return True
    return False


def compute_md5(file_path: Path) -> Optional[str]:
    """
    计算文件的 MD5 哈希值

    Args:
        file_path: 文件路径

    Returns:
        MD5 哈希值，如果文件不存在或读取失败返回 None
    """
    if not file_path.exists() or not file_path.is_file():
        return None

    try:
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError):
        return None


def files_differ(path1: Path, path2: Path) -> bool:
    """
    比较两个文件是否不同（先比较大小，再比较 MD5）

    Args:
        path1: 第一个文件路径
        path2: 第二个文件路径

    Returns:
        bool: True 表示文件不同，False 表示相同或任一文件不存在
    """
    if not path1.exists() or not path2.exists():
        return False

    # 先比较大小
    size1 = path1.stat().st_size
    size2 = path2.stat().st_size
    if size1 != size2:
        return True

    # 大小相同，比较 MD5
    md5_1 = compute_md5(path1)
    md5_2 = compute_md5(path2)

    if md5_1 is None or md5_2 is None:
        return False

    return md5_1 != md5_2


def is_symlink(file_path: Path) -> bool:
    """检查是否为符号链接"""
    return file_path.is_symlink()


# ============================================================================
# 配置加载
# ============================================================================

def parse_v2_config(config_path: Path) -> SyncConfig:
    """
    解析 v2.0 配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        SyncConfig: 解析后的配置对象
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = SyncConfig()
        config.version = data.get('_version', '2.0.0')

        # 解析 sync_directories - 支持简写和完整格式
        sync_dirs = data.get('sync_directories', [])
        if sync_dirs:
            for item in sync_dirs:
                if isinstance(item, str):
                    config.sync_directories.append({"path": item, "mode": "auto"})
                elif isinstance(item, dict):
                    config.sync_directories.append(item)

        # 解析 exclude_directories
        exclude_dirs = data.get('exclude_directories', [])
        if exclude_dirs:
            for item in exclude_dirs:
                if isinstance(item, str):
                    config.exclude_directories.append({"path": item, "reason": ""})
                elif isinstance(item, dict):
                    config.exclude_directories.append(item)

        # 解析删除名单
        config.delete_list = data.get('delete_list', [])

        # 解析文件黑名单
        config.file_blacklist = data.get('file_blacklist', [])

        # 解析新文件策略
        new_file_policy = data.get('new_file_policy', {})
        if isinstance(new_file_policy, bool):
            config.new_file_policy = {"enabled": new_file_policy}
        else:
            config.new_file_policy = new_file_policy

        # 解析本地覆盖配置
        config.local_overrides = data.get('local_overrides', {})

        # 解析备份配置
        config.backup = data.get('backup', {})

        return config

    except (json.JSONDecodeError, IOError) as e:
        print_error(f"解析配置文件失败: {e}")
        return get_default_config()


def parse_v1_config(config_path: Path) -> List[str]:
    """
    解析 v1.0 白名单配置文件

    Args:
        config_path: v1.0 配置文件路径

    Returns:
        List[str]: 白名单模式列表
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        whitelist = []
        for _category, files in data.get('whitelist', {}).items():
            if isinstance(files, list):
                whitelist.extend(files)
            elif isinstance(files, str):
                whitelist.append(files)

        return whitelist
    except (json.JSONDecodeError, IOError):
        return []


def migrate_v1_to_v2(whitelist: List[str]) -> SyncConfig:
    """
    将 v1.0 白名单迁移到 v2.0 配置

    Args:
        whitelist: v1.0 白名单模式列表

    Returns:
        SyncConfig: 迁移后的 v2.0 配置
    """
    config = SyncConfig()

    # 从白名单模式中提取目录
    directories = set()
    for pattern in whitelist:
        # 提取目录部分
        if '/' in pattern:
            dir_part = pattern.split('/')[0]
            # 处理通配符
            if '*' not in dir_part:
                directories.add(dir_part)
            else:
                # 如果目录部分有通配符，尝试提取根目录
                parts = dir_part.split('*')[0].rstrip('.')
                if parts:
                    directories.add(parts)

    # 转换为 sync_directories 格式
    for directory in sorted(directories):
        config.sync_directories.append({
            "path": directory,
            "mode": "auto",
            "description": f"从 v1.0 迁移: {directory}"
        })

    return config


def get_default_config() -> SyncConfig:
    """获取默认配置"""
    config = SyncConfig()
    config.sync_directories = [
        {"path": ".claude/agents", "mode": "auto"},
        {"path": ".claude/commands", "mode": "auto"},
        {"path": ".claude/hooks", "mode": "auto"},
        {"path": ".claude/skills", "mode": "auto"},
        {"path": ".specify/scripts", "mode": "auto"},
        {"path": ".specify/templates", "mode": "auto"}
    ]
    config.exclude_directories = [
        {"path": ".claude/commands/simplesdd", "reason": "SimpleSDD 使用不同的更新策略"}
    ]
    config.file_blacklist = [
        "*.local.md",
        "*.backup.*",
        ".DS_Store",
        "Thumbs.db",
        "*.swp"
    ]
    config.new_file_policy = {"enabled": False}
    config.local_overrides = {"enabled": True}
    config.backup = {"enabled": True}
    return config


def load_config(repo_root: Path) -> Tuple[SyncConfig, str]:
    """
    加载配置，按优先级查找

    优先级：
    1. 项目配置: {repo_root}/.speckit-config.json
    2. L0 v2.0 配置: {l0}/update-config-v2.json
    3. v1.0 配置: {l0}/update-whitelist.json（自动迁移）
    4. 内置默认配置

    Args:
        repo_root: 仓库根目录

    Returns:
        Tuple[SyncConfig, str]: (配置对象, 配置来源描述)
    """
    script_dir = get_script_dir()

    # 1. 尝试加载项目配置
    project_config = repo_root / ".speckit-config.json"
    if project_config.exists():
        print_info(f"使用项目配置: {project_config}")
        return parse_v2_config(project_config), "project"

    # 2. 尝试加载 L0 v2.0 配置
    l0_v2_config = script_dir.parent / "update-config-v2.json"
    if l0_v2_config.exists():
        print_info(f"使用 L0 v2.0 配置: {l0_v2_config}")
        return parse_v2_config(l0_v2_config), "l0-v2"

    # 3. 尝试迁移 v1.0 配置
    l0_v1_config = script_dir.parent / "update-whitelist.json"
    if l0_v1_config.exists():
        print_warning(f"检测到 v1.0 配置: {l0_v1_config}")
        print_warning("已自动迁移到 v2.0 格式")
        print_info("建议创建 .speckit-config.json 使用新格式")
        whitelist = parse_v1_config(l0_v1_config)
        return migrate_v1_to_v2(whitelist), "migrated"

    # 4. 使用内置默认配置
    print_warning("未找到配置文件，使用默认配置")
    return get_default_config(), "default"


# ============================================================================
# 目录扫描
# ============================================================================

def scan_directory(
    directory: str,
    template_dir: Path,
    _repo_root: Path
) -> List[Path]:
    """
    扫描模板仓库中的目录，收集所有文件

    Args:
        directory: 要扫描的目录路径（相对于仓库根）
        template_dir: 模板仓库根目录
        repo_root: 项目仓库根目录

    Returns:
        List[Path]: 找到的文件列表（相对于模板目录的路径）
    """
    files = []
    scan_path = template_dir / directory

    if not scan_path.exists():
        return files

    if scan_path.is_file():
        return [scan_path.relative_to(template_dir)]

    for root, _dirs, filenames in os.walk(scan_path):
        for filename in filenames:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(template_dir)
            files.append(rel_path)

    return files


def scan_local_files(
    directory: str,
    repo_root: Path
) -> List[Path]:
    """
    扫描本地项目目录，收集所有文件

    Args:
        directory: 要扫描的目录路径（相对于仓库根）
        repo_root: 项目仓库根目录

    Returns:
        List[Path]: 找到的文件列表（相对于仓库根的路径）
    """
    files = []
    scan_path = repo_root / directory

    if not scan_path.exists():
        return files

    if scan_path.is_file():
        return [scan_path.relative_to(repo_root)]

    for root, _dirs, filenames in os.walk(scan_path):
        for filename in filenames:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(repo_root)
            files.append(rel_path)

    return files


def is_in_whitelist(rel_path: Path, sync_directories: List[Dict]) -> bool:
    """
    检查文件是否在目录白名单中

    Args:
        rel_path: 文件的相对路径
        sync_directories: 目录白名单配置

    Returns:
        bool: 是否在白名单中
    """
    rel_path_str = normalize_path(str(rel_path))

    for dir_config in sync_directories:
        dir_path = dir_config.get("path", "")
        # 检查文件是否在该目录下
        if rel_path_str.startswith(dir_path + "/") or rel_path_str == dir_path:
            return True

    return False


def is_in_excluded_directory(rel_path: Path, exclude_directories: List[Dict]) -> bool:
    """
    检查文件是否在目录黑名单中

    Args:
        rel_path: 文件的相对路径
        exclude_directories: 目录黑名单配置

    Returns:
        bool: 是否在黑名单中
    """
    rel_path_str = normalize_path(str(rel_path))

    for exclude_config in exclude_directories:
        exclude_path = exclude_config.get("path", "")
        if rel_path_str.startswith(exclude_path + "/") or rel_path_str == exclude_path:
            return True

    return False


def is_in_delete_list(rel_path: Path, delete_list: List[str]) -> bool:
    """
    检查文件是否在删除名单中

    Args:
        rel_path: 文件的相对路径
        delete_list: 删除名单模式列表

    Returns:
        bool: 是否在删除名单中
    """
    rel_path_str = normalize_path(str(rel_path))
    return match_any_pattern(delete_list, rel_path_str)


def is_file_blacklisted(rel_path: Path, file_blacklist: List[str]) -> bool:
    """
    检查文件是否在文件黑名单中

    Args:
        rel_path: 文件的相对路径
        file_blacklist: 文件黑名单模式列表

    Returns:
        bool: 是否在黑名单中
    """
    rel_path_str = normalize_path(str(rel_path))
    # 检查完整路径
    if match_any_pattern(file_blacklist, rel_path_str):
        return True
    # 检查文件名
    filename = rel_path.name
    for pattern in file_blacklist:
        if pattern.startswith("*.") or pattern.startswith("*"):
            if fnmatch.fnmatch(filename, pattern):
                return True
    return False


def is_local_override(rel_path: Path, repo_root: Path, local_overrides: Dict) -> bool:
    """
    检查文件是否有本地覆盖标记

    Args:
        rel_path: 文件的相对路径
        repo_root: 仓库根目录
        local_overrides: 本地覆盖配置

    Returns:
        bool: 是否有本地覆盖标记
    """
    if not local_overrides.get("enabled", True):
        return False

    file_path = repo_root / rel_path

    # 检查文件是否存在
    if not file_path.exists():
        return False

    # 方式1: 检查标记文件
    marker_file = local_overrides.get("marker_file", ".speckit-local")
    marker_path = file_path.parent / marker_file
    if marker_path.exists():
        return True

    # 方式2: 检查文件头标记
    header_markers = local_overrides.get("header_markers", [])
    if header_markers and file_path.is_file():
        try:
            # 只读取前几行检查标记
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline() for _ in range(min(5, 10))]
                content = ''.join(first_lines)
                for marker in header_markers:
                    if marker in content:
                        return True
        except (IOError, OSError):
            pass

    return False


# ============================================================================
# 文件发现
# ============================================================================

def discover_files_to_sync(
    config: SyncConfig,
    template_dir: Path,
    repo_root: Path,
    verbose: bool = False
) -> Tuple[List[FileToSync], List[Tuple[str, str]]]:
    """
    发掘需要同步的文件

    过滤优先级：
    1. 目录白名单（只处理这些目录）
    2. 目录黑名单（排除子目录）
    3. 删除名单（明确排除的文件）
    4. 文件黑名单（通配符排除）
    5. 本地覆盖标记（文件头或标记文件）

    删除逻辑：
    - 检查本地是否存在匹配 delete_list 的文件
    - 如果模板仓库中不存在对应文件，则标记为删除

    Args:
        config: 同步配置
        template_dir: 模板仓库根目录
        repo_root: 项目仓库根目录
        verbose: 是否显示详细日志

    Returns:
        Tuple[List[FileToSync], List[Tuple[str, str]]]: (需要同步的文件列表, 被排除的文件列表)
    """
    files_to_sync = []
    excluded_files = []

    # 收集所有模板文件
    all_template_files = set()
    for dir_config in config.sync_directories:
        directory = dir_config.get("path", "")
        files = scan_directory(directory, template_dir, repo_root)
        all_template_files.update(files)

    print_verbose(f"在模板目录中找到 {len(all_template_files)} 个文件", verbose)

    # 过滤文件
    for rel_path in sorted(all_template_files):
        src_path = template_dir / rel_path
        dst_path = repo_root / rel_path
        rel_path_str = normalize_path(str(rel_path))

        # 跳过符号链接
        if is_symlink(src_path):
            excluded_files.append((rel_path_str, ExclusionReason.SYMLINK))
            continue

        # 1. 检查目录白名单
        if not is_in_whitelist(rel_path, config.sync_directories):
            excluded_files.append((rel_path_str, ExclusionReason.NOT_IN_WHITELIST))
            continue

        # 2. 检查目录黑名单
        if is_in_excluded_directory(rel_path, config.exclude_directories):
            excluded_files.append((rel_path_str, ExclusionReason.IN_EXCLUDE_DIR))
            continue

        # 3. 检查删除名单
        if is_in_delete_list(rel_path, config.delete_list):
            excluded_files.append((rel_path_str, ExclusionReason.IN_DELETE_LIST))
            continue

        # 4. 检查文件黑名单
        if is_file_blacklisted(rel_path, config.file_blacklist):
            excluded_files.append((rel_path_str, ExclusionReason.IN_BLACKLIST))
            continue

        # 5. 检查本地覆盖标记
        if is_local_override(rel_path, repo_root, config.local_overrides):
            excluded_files.append((rel_path_str, ExclusionReason.LOCAL_OVERRIDE))
            continue

        # 确定操作类型
        if not dst_path.exists():
            # 文件不存在
            if config.new_file_policy.get("enabled", False):
                files_to_sync.append(FileToSync(
                    rel_path=rel_path_str,
                    action="create",
                    src=str(src_path),
                    dst=str(dst_path)
                ))
            else:
                excluded_files.append((rel_path_str, ExclusionReason.NOT_EXIST_NEW_POLICY))
        elif files_differ(src_path, dst_path):
            # 文件有差异
            files_to_sync.append(FileToSync(
                rel_path=rel_path_str,
                action="update",
                src=str(src_path),
                dst=str(dst_path)
            ))
        else:
            # 文件相同
            excluded_files.append((rel_path_str, ExclusionReason.NO_DIFFERENCE))

    # 删除逻辑：检查本地匹配 delete_list 的文件
    if config.delete_list:
        print_verbose(f"检查删除名单，共 {len(config.delete_list)} 项", verbose)

        # 收集所有本地文件（在同步目录中）
        all_local_files = set()
        for dir_config in config.sync_directories:
            directory = dir_config.get("path", "")
            files = scan_local_files(directory, repo_root)
            all_local_files.update(files)

        # 将模板文件集合转换为字符串集合便于查找
        template_files_set = {normalize_path(str(p)) for p in all_template_files}

        # 额外处理：检查 delete_list 中的精确路径（可能在同步目录外）
        for pattern in config.delete_list:
            if '*' in pattern or '?' in pattern or '[' in pattern:
                # 通配符模式，跳过（后面在 all_local_files 中处理）
                continue

            # 精确路径模式，检查该文件是否存在
            exact_path = repo_root / pattern
            if exact_path.exists() and exact_path.is_file():
                rel_path = Path(pattern)
                all_local_files.add(rel_path)
                print_verbose(f"发现待删除文件（精确路径）: {pattern}", verbose)

        for rel_path in sorted(all_local_files):
            rel_path_str = normalize_path(str(rel_path))
            local_path = repo_root / rel_path

            # 检查是否在删除名单中
            if not is_in_delete_list(rel_path, config.delete_list):
                continue

            # 检查模板仓库中是否还存在该文件
            if rel_path_str in template_files_set:
                # 模板中还有这个文件，不删除
                continue

            # 检查是否有本地覆盖标记
            if is_local_override(rel_path, repo_root, config.local_overrides):
                excluded_files.append((rel_path_str, "本地覆盖标记，跳过删除"))
                continue

            # 标记为待删除
            files_to_sync.append(FileToSync(
                rel_path=rel_path_str,
                action="delete",
                src="",
                dst=str(local_path)
            ))

    return files_to_sync, excluded_files


# ============================================================================
# 文件操作
# ============================================================================

def backup_file(file_path: Path, backup_dir: Path) -> bool:
    """
    备份文件

    Args:
        file_path: 要备份的文件路径
        backup_dir: 备份目录

    Returns:
        bool: 是否成功
    """
    if not file_path.exists():
        return False

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        rel_path = file_path.relative_to(file_path.anchor)
        backup_path = backup_dir / rel_path

        # 确保备份目录存在
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # 复制文件
        shutil.copy2(file_path, backup_path)
        return True
    except (IOError, OSError):
        return False


def update_files(
    files_to_sync: List[FileToSync],
    config: SyncConfig,
    repo_root: Path,
    dry_run: bool = False,
    _verbose: bool = False
) -> SyncResult:
    """
    执行文件更新

    Args:
        files_to_sync: 需要同步的文件列表
        config: 同步配置
        repo_root: 仓库根目录
        dry_run: 是否为预览模式
        verbose: 是否显示详细日志

    Returns:
        SyncResult: 同步结果
    """
    result = SyncResult()

    # 设置备份目录
    backup_enabled = config.backup.get("enabled", True) and not dry_run
    backup_dir: Optional[Path] = None
    if backup_enabled:
        backup_dir_name = config.backup.get("backup_dir", ".speckit-backup")
        backup_dir = repo_root / backup_dir_name

    for file_info in files_to_sync:
        src_path = Path(file_info.src)
        dst_path = Path(file_info.dst)

        try:
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if file_info.action == "create":
                if dry_run:
                    print(f"  {Colors.CYAN}[CREATE]{Colors.NC} {file_info.rel_path}")
                    result.created += 1
                else:
                    if backup_enabled and dst_path.exists() and backup_dir:
                        backup_file(dst_path, backup_dir)
                    shutil.copy2(src_path, dst_path)
                    print_success(f"  [CREATE] {file_info.rel_path}")
                    result.created += 1

            elif file_info.action == "update":
                if dry_run:
                    print(f"  {Colors.GREEN}[UPDATE]{Colors.NC} {file_info.rel_path}")
                    result.updated += 1
                else:
                    if backup_enabled and backup_dir:
                        backup_file(dst_path, backup_dir)
                    shutil.copy2(src_path, dst_path)
                    print_success(f"  [UPDATE] {file_info.rel_path}")
                    result.updated += 1

            elif file_info.action == "delete":
                if dry_run:
                    print(f"  {Colors.RED}[DELETE]{Colors.NC} {file_info.rel_path}")
                    result.deleted += 1
                else:
                    if backup_enabled and dst_path.exists() and backup_dir:
                        backup_file(dst_path, backup_dir)
                    if dst_path.exists():
                        dst_path.unlink()
                        print_success(f"  [DELETE] {file_info.rel_path}")
                        result.deleted += 1
                    else:
                        print_warning(f"  [SKIP] {file_info.rel_path} (文件不存在)")

        except Exception as e:
            result.errors += 1
            print_error(f"  {file_info.rel_path}: {e}")

    return result


def clone_template_repo(temp_dir: Path, _verbose: bool = False) -> bool:
    """
    克隆模板仓库

    Args:
        temp_dir: 临时目录路径
        verbose: 是否显示详细日志

    Returns:
        bool: 是否成功
    """
    template_repo = "git@github.com:WeTechHK/AI-SDD-template.git"
    branch = "main"

    print_info(f"正在克隆模板仓库: {template_repo}")

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--branch', branch, template_repo, str(temp_dir)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"克隆失败: {result.stderr}")
            return False
        print_success("模板仓库克隆完成")
        return True
    except Exception as e:
        print_error(f"克隆异常: {e}")
        return False


# ============================================================================
# 输出显示
# ============================================================================

def print_summary(
    result: SyncResult,
    excluded_files: List[Tuple[str, str]],
    dry_run: bool = False
) -> None:
    """
    打印执行摘要

    Args:
        result: 同步结果
        excluded_files: 被排除的文件列表
        dry_run: 是否为预览模式
    """
    print()
    print("=" * 60)
    if dry_run:
        print(f"预览完成: {result.updated} 个待更新, {result.created} 个待创建, "
              f"{result.deleted} 个待删除, {len(excluded_files)} 个已排除")
    else:
        print(f"更新完成: {result.updated} 个已更新, {result.created} 个已创建, "
              f"{result.deleted} 个已删除, {result.skipped} 个已跳过, "
              f"{len(excluded_files)} 个已排除")
        if result.errors > 0:
            print(f"{Colors.RED}{result.errors} 个错误{Colors.NC}")
    print("=" * 60)
    print()


def print_excluded_files(excluded_files: List[Tuple[str, str]], show_excluded: bool) -> None:
    """
    打印被排除的文件

    Args:
        excluded_files: 被排除的文件列表 (path, reason)
        show_excluded: 是否显示被排除的文件
    """
    if not show_excluded or not excluded_files:
        return

    print()
    print(f"{Colors.CYAN}📋 被排除的文件:{Colors.NC}")
    print()

    # 按原因分组
    by_reason: Dict[str, List[str]] = {}
    for path, reason in excluded_files:
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(path)

    for reason, paths in sorted(by_reason.items()):
        print(f"{Colors.YELLOW}排除原因: {reason}{Colors.NC}")
        for path in sorted(paths)[:20]:  # 限制显示数量
            print(f"  • {path}")
        if len(paths) > 20:
            print(f"  ... 还有 {len(paths) - 20} 个文件")
        print()


# ============================================================================
# 主函数
# ============================================================================

def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SpecKit 增量更新脚本 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 执行更新
  %(prog)s --dry-run          # 预览模式，不实际更新
  %(prog)s -v --show-excluded # 显示详细日志和被排除的文件
        """
    )
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='模拟运行，不实际更新文件')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细信息')
    parser.add_argument('--show-excluded', action='store_true',
                        help='显示被排除的文件及原因')
    args = parser.parse_args()

    print()
    print("=" * 60)
    print(f"{Colors.BOLD}           SpecKit 增量更新 v2.0{Colors.NC}")
    print("=" * 60)
    print()

    # 获取仓库根目录
    repo_root = get_repo_root()
    os.chdir(repo_root)

    # 加载配置
    config, config_source = load_config(repo_root)
    print_info(f"配置版本: {config.version}")
    print_info(f"配置来源: {config_source}")
    print_info(f"同步目录: {len(config.sync_directories)} 个")
    if config.delete_list:
        print_info(f"删除名单: {len(config.delete_list)} 项")
    print()

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "speckit-update"

        # 克隆模板仓库
        if not clone_template_repo(temp_path, args.verbose):
            sys.exit(1)

        print()

        # 发掘需要同步的文件
        files_to_sync, excluded_files = discover_files_to_sync(
            config, temp_path, repo_root, args.verbose
        )

        print()
        print_info(f"找到 {len(files_to_sync)} 个文件待处理")
        print()

        if args.dry_run:
            print(f"{Colors.CYAN}📋 预览更新清单:{Colors.NC}")
        else:
            print(f"{Colors.GREEN}📋 更新清单:{Colors.NC}")

        if not files_to_sync:
            print_warning("  没有文件需要更新")
        else:
            # 执行更新
            result = update_files(
                files_to_sync, config, repo_root, args.dry_run, args.verbose
            )
            result.excluded_files = excluded_files

        # 显示被排除的文件
        print_excluded_files(excluded_files, args.show_excluded)

        # 显示摘要
        print_summary(
            SyncResult(
                updated=len([f for f in files_to_sync if f.action == "update"]),
                created=len([f for f in files_to_sync if f.action == "create"]),
                deleted=len([f for f in files_to_sync if f.action == "delete"]),
                excluded=len(excluded_files)
            ),
            excluded_files,
            args.dry_run
        )


if __name__ == '__main__':
    main()
