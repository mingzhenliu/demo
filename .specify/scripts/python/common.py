#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common functions and variables for all SpecKit scripts.
Cross-platform compatible (Windows, macOS, Linux).
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple


def get_repo_root() -> Path:
    """
    Get repository root, with fallback for non-git repositories.
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True,encoding='utf-8'
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to script location for non-git repos
        script_dir = Path(__file__).parent.resolve()
        return script_dir.parent.parent.parent


def get_current_branch() -> str:
    """
    Get current branch, with fallback for non-git repositories.
    """
    # First check if SPECIFY_FEATURE environment variable is set
    specify_feature = os.environ.get('SPECIFY_FEATURE')
    if specify_feature:
        return specify_feature

    # Then check git if available
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # For non-git repos, try to find the latest feature directory
    repo_root = get_repo_root()
    specs_dir = repo_root / 'specs'

    if specs_dir.is_dir():
        latest_feature = ""
        highest = 0

        for item in specs_dir.iterdir():
            if item.is_dir():
                dirname = item.name
                match = re.match(r'^(\d{3})-', dirname)
                if match:
                    number = int(match.group(1))
                    if number > highest:
                        highest = number
                        latest_feature = dirname

        if latest_feature:
            return latest_feature

    return "main"  # Final fallback


def has_git() -> bool:
    """Check if we have git available and are in a git repo."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_feature_branch(branch: str, has_git_repo: bool) -> Tuple[bool, Optional[str]]:
    """
    Check if on a valid feature branch.
    Returns (success, error_message).
    """
    # For non-git repos, we can't enforce branch naming but still provide output
    if not has_git_repo:
        print("[specify] Warning: Git repository not detected; skipped branch validation", file=sys.stderr)
        return True, None

    if not re.match(r'^\d{3}-', branch):
        error = f"ERROR: Not on a feature branch. Current branch: {branch}\n"
        error += "Feature branches should be named like: 001-feature-name"
        return False, error

    return True, None


def get_feature_dir(repo_root: Path, branch: str) -> Path:
    """Get the feature directory path."""
    return repo_root / 'specs' / branch


def find_feature_dir_by_prefix(repo_root: Path, branch_name: str) -> Path:
    """
    Find feature directory by numeric prefix instead of exact branch match.
    This allows multiple branches to work on the same spec (e.g., 004-fix-bug, 004-add-feature).
    """
    specs_dir = repo_root / 'specs'

    # Extract numeric prefix from branch (e.g., "004" from "004-whatever")
    match = re.match(r'^(\d{3})-', branch_name)
    if not match:
        # If branch doesn't have numeric prefix, fall back to exact match
        return specs_dir / branch_name

    prefix = match.group(1)

    # Search for directories in specs/ that start with this prefix
    matches: List[str] = []
    if specs_dir.is_dir():
        for item in specs_dir.iterdir():
            if item.is_dir() and item.name.startswith(f"{prefix}-"):
                matches.append(item.name)

    # Handle results
    if len(matches) == 0:
        # No match found - return the branch name path (will fail later with clear error)
        return specs_dir / branch_name
    elif len(matches) == 1:
        # Exactly one match - perfect!
        return specs_dir / matches[0]
    else:
        # Multiple matches - this shouldn't happen with proper naming convention
        print(f"ERROR: Multiple spec directories found with prefix '{prefix}': {' '.join(matches)}", file=sys.stderr)
        print("Please ensure only one spec directory exists per numeric prefix.", file=sys.stderr)
        return specs_dir / branch_name  # Return something to avoid breaking the script


def get_feature_paths() -> Dict[str, str]:
    """
    Get all feature-related paths.
    Returns a dictionary with path variables.
    """
    repo_root = get_repo_root()
    current_branch = get_current_branch()
    has_git_repo = has_git()

    # Use prefix-based lookup to support multiple branches per spec
    feature_dir = find_feature_dir_by_prefix(repo_root, current_branch)

    return {
        'REPO_ROOT': str(repo_root),
        'CURRENT_BRANCH': current_branch,
        'HAS_GIT': str(has_git_repo).lower(),
        'FEATURE_DIR': str(feature_dir),
        'FEATURE_SPEC': str(feature_dir / 'spec.md'),
        'IMPL_PLAN': str(feature_dir / 'plan.md'),
        'TASKS': str(feature_dir / 'tasks.md'),
        'RESEARCH': str(feature_dir / 'research.md'),
        'DATA_MODEL': str(feature_dir / 'data-model.md'),
        'QUICKSTART': str(feature_dir / 'quickstart.md'),
        'CONTRACTS_DIR': str(feature_dir / 'contracts'),
    }


def check_file(path: str, label: str) -> str:
    """Check if a file exists and return formatted status."""
    if Path(path).is_file():
        return f"  ✓ {label}"
    return f"  ✗ {label}"


def check_dir(path: str, label: str) -> str:
    """Check if a directory exists and is non-empty."""
    p = Path(path)
    if p.is_dir() and any(p.iterdir()):
        return f"  ✓ {label}"
    return f"  ✗ {label}"


# Color output support
class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

    @classmethod
    def disable(cls):
        """Disable colors (for non-terminal output or Windows without ANSI support)."""
        cls.RED = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.BLUE = ''
        cls.NC = ''


# Check if we should disable colors
if not sys.stdout.isatty() or (sys.platform == 'win32' and 'ANSICON' not in os.environ):
    # Try to enable ANSI on Windows 10+
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            Colors.disable()


def log_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.NC} {message}")


def log_warn(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def log_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


if __name__ == '__main__':
    # Test the functions
    print("Testing common.py functions:")
    print(f"  Repo root: {get_repo_root()}")
    print(f"  Current branch: {get_current_branch()}")
    print(f"  Has git: {has_git()}")
    print("\nFeature paths:")
    for key, value in get_feature_paths().items():
        print(f"  {key}: {value}")
