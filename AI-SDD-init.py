#!/usr/bin/env python3
# ============================================================================
# AI-SDD-init.py
# 从 AI-SDD-template 模板仓库获取 .claude 和 .specify 目录
#
# 支持两种模式：
# 1. 首次初始化：复制所有文件
# 2. 增量更新：只更新白名单中的文件
# ============================================================================

import argparse
import subprocess
import sys
import os
import shutil
import atexit
import time
import stat
from pathlib import Path

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# 配置
TEMPLATE_REPO = "git@github.com:WeTechHK/AI-SDD-template.git"
TEMPLATE_BRANCH = "main"
TEMP_DIR = ".tmp-ai-sdd-template"
DIRS_TO_COPY = [".claude", ".specify"]
FILES_TO_COPY = ["docs/AI-SDD-guide.md", "AI-SDD-init.py"]
# 使用 load-knowledge.py 存在性作为全量/增量更新判断标准
KNOWLEDGE_LOAD_SCRIPT = ".specify/scripts/python/load-knowledge.py"

# 全局变量用于清理
temp_dir_path = None


def print_info(message: str) -> None:
    """打印信息消息"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message: str) -> None:
    """打印成功消息"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message: str) -> None:
    """打印警告消息"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message: str) -> None:
    """打印错误消息"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def remove_readonly(func, path, exc_info):
    """处理只读文件的删除"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        # 如果仍然失败，记录但不抛出异常
        pass


def force_remove_tree(path: str, max_retries: int = 3, delay: float = 0.5) -> bool:
    """强制删除目录树，带重试机制"""
    if not os.path.isdir(path):
        return True
    
    for attempt in range(max_retries):
        try:
            # 在 Windows 上，先尝试修改文件权限
            if sys.platform == 'win32':
                # 递归修改所有文件的权限
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                        except:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
                        except:
                            pass
            
            # 尝试删除
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except (PermissionError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # 递增延迟
                continue
            else:
                # 最后一次尝试失败，使用延迟删除标记
                if sys.platform == 'win32':
                    try:
                        # 在 Windows 上，尝试使用系统命令标记为删除
                        subprocess.run(
                            ['cmd', '/c', 'rmdir', '/s', '/q', path],
                            capture_output=True,
                            timeout=2
                        )
                    except:
                        pass
                return False
    return False


def cleanup() -> None:
    """清理临时目录"""
    global temp_dir_path
    if temp_dir_path and os.path.isdir(temp_dir_path):
        if force_remove_tree(temp_dir_path):
            print_info("已清理临时目录")
        else:
            # 如果删除失败，给出提示但不抛出异常
            print_warning(f"无法立即删除临时目录 {temp_dir_path}，可能被系统锁定")
            print_info("目录将在系统释放文件后自动删除，或可手动删除")


def confirm(prompt: str) -> bool:
    """确认函数"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("请输入 y 或 n")


def check_git_repo() -> None:
    """检查是否在 git 仓库中"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error("当前目录不是 git 仓库")
            sys.exit(1)
    except FileNotFoundError:
        print_error("未找到 git 命令")
        sys.exit(1)


def run_git_clone(repo: str, branch: str, target: str) -> bool:
    """克隆 git 仓库"""
    try:
        process = subprocess.Popen(
            ['git', 'clone', '--depth', '1', '--branch', branch, repo, target],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(f"  {line.rstrip()}")
        process.wait()
        return process.returncode == 0
    except FileNotFoundError:
        print_error("未找到 git 命令")
        return False


def is_initialized() -> bool:
    """检测是否已经初始化过（通过 load-knowledge.py 存在性判断）"""
    return os.path.isfile(KNOWLEDGE_LOAD_SCRIPT)


def check_l0_mounted() -> bool:
    """检查 L0 知识库是否已挂载"""
    return os.path.isdir(".knowledge/upstream/L0-enterprise")


def check_l0_remote() -> bool:
    """检查 L0-knowledge remote 是否存在"""
    try:
        result = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True,
            text=True,
            check=True
        )
        return 'L0-knowledge' in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def add_l0_remote() -> bool:
    """添加 L0-knowledge remote"""
    L0_REPO = "git@github.com:WeTechHK/knowledge-enterprise-standards.git"
    print_info(f"正在添加 L0-knowledge remote: {L0_REPO}")

    try:
        result = subprocess.run(
            ['git', 'remote', 'add', 'L0-knowledge', L0_REPO],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("L0-knowledge remote 添加成功")
            return True
        else:
            print_warning(f"添加 remote 失败: {result.stderr}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_warning(f"添加 remote 时出错: {e}")
        return False


def has_uncommitted_changes() -> bool:
    """检查工作区是否有未提交的内容"""
    try:
        result = subprocess.run(
            ['git', 'diff-index', '--quiet', 'HEAD', '--'],
            capture_output=True
        )
        return result.returncode != 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def sync_l0_knowledge() -> bool:
    """同步 L0 知识库（支持 stash 流程处理未提交内容）"""
    print_info("正在同步 L0 企业级知识库...")

    # 检查是否有未提交的内容
    has_changes = has_uncommitted_changes()
    did_stash = False

    if has_changes:
        print_info("检测到未提交的内容，使用 stash 暂存...")
        try:
            result = subprocess.run(
                ['git', 'stash', 'push', '-u', '-m', 'temp: save before sync knowledge'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success("已暂存未提交的内容")
                did_stash = True
            else:
                print_warning(f"Stash 失败: {result.stderr}")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print_warning(f"Stash 时出错: {e}")
            return False

    # 执行同步
    try:
        result = subprocess.run(
            ['git', 'subtree', 'pull', '--prefix=.knowledge/upstream/L0-enterprise',
             'L0-knowledge', 'main', '--squash', '-m',
            'chore: sync L0 enterprise knowledge base'],
            capture_output=True,
            text=True
        )

        sync_success = False
        if result.returncode == 0:
            # 检查是否有实际更新
            if 'Already up to date.' in result.stdout or result.stdout.strip() == '':
                print_success("L0 知识库已是最新")
            else:
                print_success("L0 知识库已更新")
            sync_success = True
        else:
            print_warning(f"同步 L0 知识库失败: {result.stderr}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_warning(f"同步 L0 知识库时出错: {e}")
        sync_success = False

    # 如果之前 stash 了，现在恢复
    if did_stash:
        print_info("正在恢复暂存的内容...")
        try:
            result = subprocess.run(
                ['git', 'stash', 'pop'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success("已恢复暂存的内容")
            else:
                print_warning(f"Stash pop 失败: {result.stderr}")
                print_info("请手动执行 'git stash pop' 恢复暂存内容")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print_warning(f"Stash pop 时出错: {e}")
            print_info("请手动执行 'git stash pop' 恢复暂存内容")

    return sync_success


def mount_l0_knowledge() -> bool:
    """挂载 L0 知识库"""
    L0_REPO = "git@github.com:WeTechHK/knowledge-enterprise-standards.git"
    print_info("正在挂载 L0 企业级知识库...")

    # 检查是否有 remote，没有则添加
    if not check_l0_remote():
        print_info(f"正在添加 L0-knowledge remote: {L0_REPO}")
        try:
            result = subprocess.run(
                ['git', 'remote', 'add', 'L0-knowledge', L0_REPO],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print_warning(f"添加 remote 失败: {result.stderr}")
                return False
            print_success("L0-knowledge remote 添加成功")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print_warning(f"添加 remote 时出错: {e}")
            return False

    # 执行 subtree add 挂载知识库
    try:
        print_info("正在从 L0-knowledge 拉取知识库...")
        result = subprocess.run(
            ['git', 'subtree', 'add', '--prefix=.knowledge/upstream/L0-enterprise',
             'L0-knowledge', 'main', '--squash', '-m',
             'chore: mount L0 enterprise knowledge base'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("L0 知识库挂载成功")
            return True
        else:
            print_warning(f"挂载 L0 知识库失败: {result.stderr}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_warning(f"挂载 L0 知识库时出错: {e}")
        return False


def run_incremental_update() -> bool:
    """运行增量更新"""
    update_script = Path(".knowledge/upstream/L0-enterprise/speckit-config/scripts/update-speckit.py")

    print_info("检测到已初始化，执行增量更新...")
    print()

    # 检查 L0 知识库是否已挂载
    if not check_l0_mounted():
        print_warning("未检测到 L0 知识库，正在自动挂载...")
        print()
        if not mount_l0_knowledge():
            print_error("L0 知识库挂载失败，无法继续增量更新")
            print_info("请手动执行: /speckit.knowledge")
            return False
        print()

    # 如果 L0 知识库已挂载，先同步知识库
    if check_l0_mounted():
        # 检查是否有 remote，没有则自动添加
        if not check_l0_remote():
            print_warning("未检测到 L0-knowledge remote，正在自动添加...")
            if not add_l0_remote():
                print_warning("添加 remote 失败，跳过知识库同步...")
            else:
                print()
                if not sync_l0_knowledge():
                    print_warning("知识库同步失败，继续执行增量更新...")
        else:
            # remote 已存在，直接同步
            if not sync_l0_knowledge():
                print_warning("知识库同步失败，继续执行增量更新...")
        print()

    # 再次检查更新脚本是否存在
    if not update_script.exists():
        print_error("更新脚本不存在，请先挂载 L0 知识库")
        print_info("执行: /speckit.knowledge")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(update_script)],
            cwd=os.getcwd()
        )
        return result.returncode == 0
    except Exception as e:
        print_error(f"增量更新失败: {e}")
        return False


def full_init(force_full: bool = False) -> None:
    """完整初始化流程"""
    global temp_dir_path
    temp_dir_path = TEMP_DIR

    # 注册退出时清理
    atexit.register(cleanup)

    print("")
    print("==============================================")
    print("       AI-SDD 初始化脚本")
    print("==============================================")
    print("")

    print_info(f"模板仓库: {TEMPLATE_REPO}")
    print_info(f"目标目录: {' '.join(DIRS_TO_COPY)}")
    print_info(f"目标文件: {' '.join(FILES_TO_COPY)}")
    print("")

    # 检查 git 仓库
    check_git_repo()

    # 记录备份的目录
    dirs_backed_up = []

    # 检查每个目录是否存在，存在则备份
    for dir_name in DIRS_TO_COPY:
        if os.path.isdir(dir_name):
            backup_dir = f"{dir_name}_bak"
            # 如果备份目录已存在，先删除
            if os.path.isdir(backup_dir):
                shutil.rmtree(backup_dir)
            print_warning(f"检测到 {dir_name} 目录已存在")
            print_info(f"正在备份为 {backup_dir} ...")
            shutil.move(dir_name, backup_dir)
            dirs_backed_up.append(backup_dir)
            print_success(f"已备份 {dir_name} -> {backup_dir}")
        else:
            print_info(f"{dir_name} 目录不存在，将创建")
        print("")

    # 克隆模板仓库
    print_info("正在克隆模板仓库...")
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    if not run_git_clone(TEMPLATE_REPO, TEMPLATE_BRANCH, TEMP_DIR):
        print_error("克隆模板仓库失败")
        sys.exit(1)

    if not os.path.isdir(TEMP_DIR):
        print_error("克隆模板仓库失败")
        sys.exit(1)

    print_success("模板仓库克隆完成")
    print("")

    # 复制目录
    for dir_name in DIRS_TO_COPY:
        src_dir = os.path.join(TEMP_DIR, dir_name)
        if os.path.isdir(src_dir):
            shutil.copytree(src_dir, dir_name)
            print_success(f"已复制 {dir_name} 目录")
        else:
            print_warning(f"模板仓库中不存在 {dir_name} 目录，跳过")

    # 复制文件
    print("")
    print_info("正在复制文档文件...")
    for file_path in FILES_TO_COPY:
        src_file = os.path.join(TEMP_DIR, file_path)
        if os.path.isfile(src_file):
            filename = os.path.basename(file_path)
            shutil.copy2(src_file, f"./{filename}")
            print_success(f"已复制 {filename}")
        else:
            print_warning(f"模板仓库中不存在 {file_path}，跳过")

    print("")
    print("==============================================")
    print("       初始化完成")
    print("==============================================")
    print("")

    # 显示结果摘要
    print_success("已复制的目录:")
    for dir_name in DIRS_TO_COPY:
        print(f"  - {dir_name}")

    if dirs_backed_up:
        print("")
        print_warning("已备份的旧目录:")
        for dir_name in dirs_backed_up:
            print(f"  - {dir_name}")
        print("")
        print_warning("⚠️  请检查备份目录，将项目特定配置合并到新目录中")

    if FILES_TO_COPY:
        print("")
        print_success("已复制的文件:")
        for file_path in FILES_TO_COPY:
            filename = os.path.basename(file_path)
            print(f"  - {filename}")

    print("")
    print_info("下一步: 执行 /speckit.knowledge 挂载知识库")
    print("")

    # 立即清理临时目录，而不是等到程序退出
    # 在 Windows 上，等待一小段时间确保 Git 进程完全释放文件
    if sys.platform == 'win32':
        time.sleep(0.5)
    print_info("正在清理临时目录...")
    cleanup()
    # 取消注册 atexit，因为已经手动清理了
    atexit.unregister(cleanup)


def main() -> None:
    """主函数 - 支持命令行参数"""
    parser = argparse.ArgumentParser(
        description='AI-SDD 初始化脚本 v2.0 - 支持增量更新',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python AI-SDD-init.py           # 自动检测：首次初始化或增量更新
  python AI-SDD-init.py --full    # 强制执行完整初始化
  python AI-SDD-init.py --update  # 强制执行增量更新
        '''
    )
    parser.add_argument('--full', '-f', action='store_true',
                        help='强制执行完整初始化（会备份现有目录）')
    parser.add_argument('--update', '-u', action='store_true',
                        help='强制执行增量更新')

    args = parser.parse_args()

    # 检查 git 仓库
    try:
        subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("当前目录不是 git 仓库")
        sys.exit(1)

    # 根据参数和状态选择模式
    if args.full:
        # 强制完整初始化
        full_init(force_full=True)
    elif args.update or is_initialized():
        # 增量更新
        if not run_incremental_update():
            print_error("增量更新失败")
            sys.exit(1)
    else:
        # 首次初始化
        full_init()


if __name__ == "__main__":
    main()
