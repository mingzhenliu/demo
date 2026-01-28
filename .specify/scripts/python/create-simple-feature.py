#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a new SimpleSDD feature directory.

SimpleSDD creates a feature directory without git operations.
The directory follows the naming convention: ###-short-name
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Stop words to filter out from auto-generated names
STOP_WORDS = {
    'i', 'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with',
    'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can',
    'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those', 'my',
    'your', 'our', 'their', 'want', 'need', 'add', 'get', 'set', 'make', 'use'
}


def get_repo_root() -> Path:
    """Find repository root by searching for .specify directory."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / '.specify').is_dir():
            return parent
    # Fallback to current directory if .specify not found
    return cwd


def get_next_feature_number(specs_dir: Path) -> int:
    """Get next available feature number from specs directory."""
    highest = 0
    if specs_dir.is_dir():
        for item in specs_dir.iterdir():
            if item.is_dir():
                match = re.match(r'^(\d+)', item.name)
                if match:
                    number = int(match.group(1))
                    if number > highest:
                        highest = number
    return highest + 1


def clean_name(name: str) -> str:
    """Clean and format a name to kebab-case."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')


def generate_short_name(description: str) -> str:
    """Generate short name from description, filtering stop words."""
    clean_desc = re.sub(r'[^a-z0-9]', ' ', description.lower())
    words = clean_desc.split()

    meaningful_words = []
    for word in words:
        if not word:
            continue
        if word not in STOP_WORDS:
            if len(word) >= 3:
                meaningful_words.append(word)
            elif word.upper() in description:
                # Keep short words if uppercase in original (acronyms)
                meaningful_words.append(word)

    if meaningful_words:
        return '-'.join(meaningful_words[:3])

    # Fallback
    cleaned = clean_name(description)
    parts = [p for p in cleaned.split('-') if p][:3]
    return '-'.join(parts)


def main():
    parser = argparse.ArgumentParser(
        description='Create a SimpleSDD feature directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python create-simple-feature.py 'Add user authentication'
  python create-simple-feature.py 'OAuth2 integration' --short-name oauth2
  python create-simple-feature.py 'Payment fix' --number 5
'''
    )
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--short-name', '-s', default='',
                        help='Custom short name (default: auto-generate)')
    parser.add_argument('--number', '-n', type=int, default=0,
                        help='Feature number (default: auto-increment)')
    parser.add_argument('description', nargs='*',
                        help='Feature description')
    args = parser.parse_args()

    description = ' '.join(args.description)
    if not description:
        parser.print_usage()
        print("Error: feature description required", file=sys.stderr)
        sys.exit(1)

    repo_root = get_repo_root()
    specs_dir = repo_root / 'specs'
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Generate feature name
    short_name = clean_name(args.short_name) if args.short_name else generate_short_name(description)
    feature_num = args.number if args.number else get_next_feature_number(specs_dir)
    feature_name = f"{feature_num:03d}-{short_name}"
    feature_dir = specs_dir / feature_name

    # Create directory structure
    feature_dir.mkdir(parents=True, exist_ok=True)

    # Create empty files
    (feature_dir / 'spec.md').touch(exist_ok=True)
    (feature_dir / 'plan.md').touch(exist_ok=True)
    (feature_dir / 'research.md').touch(exist_ok=True)

    # Create subdirectories
    (feature_dir / 'contracts').mkdir(exist_ok=True)
    (feature_dir / 'checklists').mkdir(exist_ok=True)

    # Set environment variable for downstream use
    os.environ['SPECIFY_FEATURE'] = feature_name

    # Output
    if args.json:
        result = {
            'FEATURE_NAME': feature_name,
            'FEATURE_DIR': str(feature_dir),
            'SPEC_FILE': str(feature_dir / 'spec.md'),
            'PLAN_FILE': str(feature_dir / 'plan.md'),
            'FEATURE_NUM': f"{feature_num:03d}"
        }
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"Feature directory: {feature_dir.relative_to(repo_root)}")
        print(f"  spec.md     : {feature_dir / 'spec.md'}")
        print(f"  plan.md     : {feature_dir / 'plan.md'}")
        print(f"  research.md : {feature_dir / 'research.md'}")


if __name__ == '__main__':
    main()
