#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a new feature branch and spec directory.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from common import get_repo_root, log_warn


# Common stop words to filter out
STOP_WORDS = {
    'i', 'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with',
    'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can',
    'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those', 'my',
    'your', 'our', 'their', 'want', 'need', 'add', 'get', 'set'
}


def has_git() -> bool:
    """Check if we're in a git repository."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_highest_from_specs(specs_dir: Path) -> int:
    """Get highest number from specs directory."""
    highest = 0
    if specs_dir.is_dir():
        for item in specs_dir.iterdir():
            if item.is_dir():
                match = re.match(r'^(\d+)', item.name)
                if match:
                    number = int(match.group(1))
                    if number > highest:
                        highest = number
    return highest


def get_highest_from_branches() -> int:
    """Get highest number from git branches."""
    highest = 0
    try:
        result = subprocess.run(
            ['git', 'branch', '-a'],
            capture_output=True, text=True, check=True
        )
        branches = result.stdout.strip()
        if branches:
            for line in branches.split('\n'):
                # Clean branch name: remove leading markers and remote prefixes
                branch = re.sub(r'^[* ]+', '', line)
                branch = re.sub(r'^remotes/[^/]+/', '', branch)

                # Extract feature number if branch matches pattern ###-*
                match = re.match(r'^(\d{3})-', branch)
                if match:
                    number = int(match.group(1))
                    if number > highest:
                        highest = number
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return highest


def check_existing_branches(specs_dir: Path) -> int:
    """Check existing branches and return next available number."""
    # Fetch all remotes to get latest branch info
    try:
        subprocess.run(
            ['git', 'fetch', '--all', '--prune'],
            capture_output=True, check=False
        )
    except FileNotFoundError:
        pass

    # Get highest number from ALL branches
    highest_branch = get_highest_from_branches()

    # Get highest number from ALL specs
    highest_spec = get_highest_from_specs(specs_dir)

    # Take the maximum of both
    max_num = max(highest_branch, highest_spec)

    # Return next number
    return max_num + 1


def clean_branch_name(name: str) -> str:
    """Clean and format a branch name."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name


def generate_branch_name(description: str) -> str:
    """Generate branch name with stop word filtering and length filtering."""
    # Convert to lowercase and split into words
    clean_desc = re.sub(r'[^a-z0-9]', ' ', description.lower())
    words = clean_desc.split()

    # Filter words: remove stop words and words shorter than 3 chars
    meaningful_words = []
    for word in words:
        if not word:
            continue
        if word not in STOP_WORDS:
            if len(word) >= 3:
                meaningful_words.append(word)
            elif word.upper() in description:
                # Keep short words if they appear as uppercase in original (likely acronyms)
                meaningful_words.append(word)

    # If we have meaningful words, use first 3-4 of them
    if meaningful_words:
        max_words = 4 if len(meaningful_words) == 4 else 3
        result = '-'.join(meaningful_words[:max_words])
        return result
    else:
        # Fallback to original logic if no meaningful words found
        cleaned = clean_branch_name(description)
        parts = [p for p in cleaned.split('-') if p][:3]
        return '-'.join(parts)


def main():
    parser = argparse.ArgumentParser(
        description='Create a new feature branch and spec directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python create-new-feature.py 'Add user authentication system' --short-name 'user-auth'
  python create-new-feature.py 'Implement OAuth2 integration for API' --number 5
'''
    )
    parser.add_argument('--json', '-j', action='store_true', dest='json_mode',
                        help='Output in JSON format')
    parser.add_argument('--short-name', '-s', dest='short_name', default='',
                        help='Provide a custom short name (2-4 words) for the branch')
    parser.add_argument('--number', '-n', dest='branch_number', type=int, default=0,
                        help='Specify branch number manually (overrides auto-detection)')
    parser.add_argument('feature_description', nargs='*',
                        help='Feature description')

    args = parser.parse_args()

    feature_description = ' '.join(args.feature_description)
    if not feature_description:
        parser.print_usage()
        sys.exit(1)

    # Resolve repository root
    repo_root = get_repo_root()
    is_git = has_git()

    os.chdir(repo_root)

    specs_dir = repo_root / 'specs'
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Generate branch name
    if args.short_name:
        branch_suffix = clean_branch_name(args.short_name)
    else:
        branch_suffix = generate_branch_name(feature_description)

    # Determine branch number
    if args.branch_number:
        branch_number = args.branch_number
    else:
        if is_git:
            branch_number = check_existing_branches(specs_dir)
        else:
            highest = get_highest_from_specs(specs_dir)
            branch_number = highest + 1

    feature_num = f"{branch_number:03d}"
    branch_name = f"{feature_num}-{branch_suffix}"

    # GitHub enforces a 244-byte limit on branch names
    MAX_BRANCH_LENGTH = 244
    if len(branch_name) > MAX_BRANCH_LENGTH:
        # Truncate suffix
        max_suffix_length = MAX_BRANCH_LENGTH - 4  # 3 for number + 1 for hyphen
        truncated_suffix = branch_suffix[:max_suffix_length].rstrip('-')
        original_branch_name = branch_name
        branch_name = f"{feature_num}-{truncated_suffix}"

        log_warn(f"Branch name exceeded GitHub's 244-byte limit")
        log_warn(f"Original: {original_branch_name} ({len(original_branch_name)} bytes)")
        log_warn(f"Truncated to: {branch_name} ({len(branch_name)} bytes)")

    # Create git branch if in git repo
    if is_git:
        try:
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        log_warn(f"Git repository not detected; skipped branch creation for {branch_name}")

    # Create feature directory
    feature_dir = specs_dir / branch_name
    feature_dir.mkdir(parents=True, exist_ok=True)

    # Copy spec template
    template = repo_root / '.specify' / 'templates' / 'spec-template.md'
    spec_file = feature_dir / 'spec.md'
    if template.is_file():
        shutil.copy2(template, spec_file)
    else:
        spec_file.touch()

    # Set the SPECIFY_FEATURE environment variable
    os.environ['SPECIFY_FEATURE'] = branch_name

    # Output results
    if args.json_mode:
        result = {
            'BRANCH_NAME': branch_name,
            'SPEC_FILE': str(spec_file),
            'FEATURE_NUM': feature_num
        }
        print(json.dumps(result))
    else:
        print(f"BRANCH_NAME: {branch_name}")
        print(f"SPEC_FILE: {spec_file}")
        print(f"FEATURE_NUM: {feature_num}")
        print(f"SPECIFY_FEATURE environment variable set to: {branch_name}")


if __name__ == '__main__':
    main()
