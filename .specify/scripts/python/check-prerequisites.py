#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidated prerequisite checking script.

This script provides unified prerequisite checking for Spec-Driven Development workflow.
It replaces the functionality previously spread across multiple scripts.

Usage: ./check-prerequisites.py [OPTIONS]

OPTIONS:
  --json              Output in JSON format
  --require-tasks     Require tasks.md to exist (for implementation phase)
  --include-tasks     Include tasks.md in AVAILABLE_DOCS list
  --paths-only        Only output path variables (no validation)
  --help, -h          Show help message
"""

import argparse
import json
import sys
from pathlib import Path

from common import (
    get_feature_paths,
    check_feature_branch,
    check_file,
    check_dir,
)


def main():
    parser = argparse.ArgumentParser(
        description='Consolidated prerequisite checking for Spec-Driven Development workflow.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Check task prerequisites (plan.md required)
  python check-prerequisites.py --json

  # Check implementation prerequisites (plan.md + tasks.md required)
  python check-prerequisites.py --json --require-tasks --include-tasks

  # Get feature paths only (no validation)
  python check-prerequisites.py --paths-only
"""
    )
    parser.add_argument('--json', '-j', action='store_true', dest='json_mode',
                        help='Output in JSON format')
    parser.add_argument('--require-tasks', action='store_true',
                        help='Require tasks.md to exist (for implementation phase)')
    parser.add_argument('--include-tasks', action='store_true',
                        help='Include tasks.md in AVAILABLE_DOCS list')
    parser.add_argument('--paths-only', action='store_true',
                        help='Only output path variables (no prerequisite validation)')

    args = parser.parse_args()

    # Get feature paths and validate branch
    paths = get_feature_paths()
    repo_root = paths['REPO_ROOT']
    current_branch = paths['CURRENT_BRANCH']
    has_git = paths['HAS_GIT'] == 'true'
    feature_dir = Path(paths['FEATURE_DIR'])
    feature_spec = paths['FEATURE_SPEC']
    impl_plan = Path(paths['IMPL_PLAN'])
    tasks = Path(paths['TASKS'])
    research = Path(paths['RESEARCH'])
    data_model = Path(paths['DATA_MODEL'])
    quickstart = Path(paths['QUICKSTART'])
    contracts_dir = Path(paths['CONTRACTS_DIR'])

    # Check feature branch
    success, error = check_feature_branch(current_branch, has_git)
    if not success:
        print(error, file=sys.stderr)
        sys.exit(1)

    # If paths-only mode, output paths and exit
    if args.paths_only:
        if args.json_mode:
            result = {
                'REPO_ROOT': repo_root,
                'BRANCH': current_branch,
                'FEATURE_DIR': str(feature_dir),
                'FEATURE_SPEC': feature_spec,
                'IMPL_PLAN': str(impl_plan),
                'TASKS': str(tasks)
            }
            print(json.dumps(result))
        else:
            print(f"REPO_ROOT: {repo_root}")
            print(f"BRANCH: {current_branch}")
            print(f"FEATURE_DIR: {feature_dir}")
            print(f"FEATURE_SPEC: {feature_spec}")
            print(f"IMPL_PLAN: {impl_plan}")
            print(f"TASKS: {tasks}")
        sys.exit(0)

    # Validate required directories and files
    if not feature_dir.is_dir():
        print(f"ERROR: Feature directory not found: {feature_dir}", file=sys.stderr)
        print("Run /speckit.specify first to create the feature structure.", file=sys.stderr)
        sys.exit(1)

    if not impl_plan.is_file():
        print(f"ERROR: plan.md not found in {feature_dir}", file=sys.stderr)
        print("Run /speckit.plan first to create the implementation plan.", file=sys.stderr)
        sys.exit(1)

    # Check for tasks.md if required
    if args.require_tasks and not tasks.is_file():
        print(f"ERROR: tasks.md not found in {feature_dir}", file=sys.stderr)
        print("Run /speckit.tasks first to create the task list.", file=sys.stderr)
        sys.exit(1)

    # Build list of available documents
    docs = []

    # Always check these optional docs
    if research.is_file():
        docs.append("research.md")
    if data_model.is_file():
        docs.append("data-model.md")

    # Check contracts directory (only if it exists and has files)
    if contracts_dir.is_dir() and any(contracts_dir.iterdir()):
        docs.append("contracts/")

    if quickstart.is_file():
        docs.append("quickstart.md")

    # Include tasks.md if requested and it exists
    if args.include_tasks and tasks.is_file():
        docs.append("tasks.md")

    # Output results
    if args.json_mode:
        result = {
            'FEATURE_DIR': str(feature_dir),
            'AVAILABLE_DOCS': docs
        }
        print(json.dumps(result))
    else:
        print(f"FEATURE_DIR:{feature_dir}")
        print("AVAILABLE_DOCS:")

        # Show status of each potential document
        print(check_file(str(research), "research.md"))
        print(check_file(str(data_model), "data-model.md"))
        print(check_dir(str(contracts_dir), "contracts/"))
        print(check_file(str(quickstart), "quickstart.md"))

        if args.include_tasks:
            print(check_file(str(tasks), "tasks.md"))


if __name__ == '__main__':
    main()
