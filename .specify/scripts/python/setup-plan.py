#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup plan for a feature.
Copies the plan template to the feature directory.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# Import common functions
from common import (
    get_repo_root,
    get_feature_paths,
    check_feature_branch,
    log_info,
    log_warn,
)


def main():
    parser = argparse.ArgumentParser(
        description='Setup plan for a feature',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        dest='json_mode',
        help='Output results in JSON format'
    )
    args = parser.parse_args()

    # Get all paths and variables from common functions
    paths = get_feature_paths()
    repo_root = Path(paths['REPO_ROOT'])
    current_branch = paths['CURRENT_BRANCH']
    has_git = paths['HAS_GIT'] == 'true'
    feature_dir = Path(paths['FEATURE_DIR'])
    feature_spec = paths['FEATURE_SPEC']
    impl_plan = Path(paths['IMPL_PLAN'])

    # Check if we're on a proper feature branch (only for git repos)
    success, error = check_feature_branch(current_branch, has_git)
    if not success:
        print(error, file=sys.stderr)
        sys.exit(1)

    # Ensure the feature directory exists
    feature_dir.mkdir(parents=True, exist_ok=True)

    # Copy plan template if it exists
    template = repo_root / '.specify' / 'templates' / 'plan-template.md'
    if template.is_file():
        shutil.copy2(template, impl_plan)
        if not args.json_mode:
            log_info(f"Copied plan template to {impl_plan}")
    else:
        if not args.json_mode:
            log_warn(f"Plan template not found at {template}")
        # Create a basic plan file if template doesn't exist
        impl_plan.touch()

    # Output results
    if args.json_mode:
        result = {
            'FEATURE_SPEC': feature_spec,
            'IMPL_PLAN': str(impl_plan),
            'SPECS_DIR': str(feature_dir),
            'BRANCH': current_branch,
            'HAS_GIT': str(has_git).lower()
        }
        print(json.dumps(result))
    else:
        print(f"FEATURE_SPEC: {feature_spec}")
        print(f"IMPL_PLAN: {impl_plan}")
        print(f"SPECS_DIR: {feature_dir}")
        print(f"BRANCH: {current_branch}")
        print(f"HAS_GIT: {str(has_git).lower()}")


if __name__ == '__main__':
    main()
