#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update agent context files with information from plan.md

This script maintains AI agent context files by parsing feature specifications
and updating agent-specific configuration files with project information.

MAIN FUNCTIONS:
1. Environment Validation
   - Verifies git repository structure and branch information
   - Checks for required plan.md files and templates
   - Validates file permissions and accessibility

2. Plan Data Extraction
   - Parses plan.md files to extract project metadata
   - Identifies language/version, frameworks, databases, and project types
   - Handles missing or incomplete specification data gracefully

3. Agent File Management
   - Creates new agent context files from templates when needed
   - Updates existing agent files with new project information
   - Preserves manual additions and custom configurations
   - Supports multiple AI agent formats and directory structures

4. Content Generation
   - Generates language-specific build/test commands
   - Creates appropriate project directory structures
   - Updates technology stacks and recent changes sections
   - Maintains consistent formatting and timestamps

5. Multi-Agent Support
   - Handles agent-specific file paths and naming conventions
   - Supports: Claude, Gemini, Copilot, Cursor, Qwen, opencode, Codex, Windsurf,
     Kilo Code, Auggie CLI, Roo Code, CodeBuddy CLI, Qoder CLI, Amp, SHAI,
     or Amazon Q Developer CLI
   - Can update single agents or all existing agent files
   - Creates default Claude file if no agent files exist

Usage: python update-agent-context.py [agent_type]
Agent types: claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|
             kilocode|auggie|shai|q|bob|qoder
Leave empty to update all existing agent files
"""

import argparse
import atexit
import os
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple

from common import (
    get_repo_root,
    get_feature_paths,
    log_info,
    log_success,
    log_warn,
    log_error,
)


# ═══════════════════════════════════════════════════════════════
# Configuration and Global Variables
# ═══════════════════════════════════════════════════════════════

class AgentConfig:
    """Configuration class for agent file paths and global variables."""

    def __init__(self, repo_root: Path, paths: Dict[str, str]):
        self.repo_root = repo_root
        self.current_branch = paths['CURRENT_BRANCH']
        self.has_git = paths['HAS_GIT'] == 'true'
        self.new_plan = Path(paths['IMPL_PLAN'])

        # Agent-specific file paths
        self.claude_file = repo_root / "CLAUDE.md"
        self.gemini_file = repo_root / "GEMINI.md"
        self.copilot_file = repo_root / ".github" / "agents" / "copilot-instructions.md"
        self.cursor_file = repo_root / ".cursor" / "rules" / "specify-rules.mdc"
        self.qwen_file = repo_root / "QWEN.md"
        self.agents_file = repo_root / "AGENTS.md"
        self.windsurf_file = repo_root / ".windsurf" / "rules" / "specify-rules.md"
        self.kilocode_file = repo_root / ".kilocode" / "rules" / "specify-rules.md"
        self.auggie_file = repo_root / ".augment" / "rules" / "specify-rules.md"
        self.roo_file = repo_root / ".roo" / "rules" / "specify-rules.md"
        self.codebuddy_file = repo_root / "CODEBUDDY.md"
        self.qoder_file = repo_root / "QODER.md"
        self.amp_file = repo_root / "AGENTS.md"
        self.shai_file = repo_root / "SHAI.md"
        self.q_file = repo_root / "AGENTS.md"
        self.bob_file = repo_root / "AGENTS.md"

        # Template file
        self.template_file = repo_root / ".specify" / "templates" / "agent-file-template.md"

        # Parsed plan data
        self.new_lang = ""
        self.new_framework = ""
        self.new_db = ""
        self.new_project_type = ""


# Global config instance (set during initialization)
config: Optional[AgentConfig] = None

# Temporary files to clean up
temp_files: list = []


def cleanup():
    """Cleanup function for temporary files."""
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except OSError:
            pass


# Register cleanup handler
atexit.register(cleanup)


# ═══════════════════════════════════════════════════════════════
# Validation Functions
# ═══════════════════════════════════════════════════════════════

def validate_environment() -> bool:
    """Validate the environment before proceeding."""
    global config

    # Check if we have a current branch/feature (git or non-git)
    if not config.current_branch:
        log_error("Unable to determine current feature")
        if config.has_git:
            log_info("Make sure you're on a feature branch")
        else:
            log_info("Set SPECIFY_FEATURE environment variable or create a feature first")
        return False

    # Check if plan.md exists
    if not config.new_plan.is_file():
        log_error(f"No plan.md found at {config.new_plan}")
        log_info("Make sure you're working on a feature with a corresponding spec directory")
        if not config.has_git:
            log_info("Use: export SPECIFY_FEATURE=your-feature-name or create a new feature first")
        return False

    # Check if template exists (needed for new files)
    if not config.template_file.is_file():
        log_warn(f"Template file not found at {config.template_file}")
        log_warn("Creating new agent files will fail")

    return True


# ═══════════════════════════════════════════════════════════════
# Plan Parsing Functions
# ═══════════════════════════════════════════════════════════════

def extract_plan_field(field_pattern: str, plan_file: Path) -> str:
    """Extract a field from the plan file."""
    try:
        content = plan_file.read_text(encoding='utf-8')
        pattern = rf'^\*\*{re.escape(field_pattern)}\*\*:\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE)

        if match:
            value = match.group(1).strip()
            # Filter out placeholder values
            if value in ["NEEDS CLARIFICATION", "N/A"]:
                return ""
            return value
    except Exception:
        pass

    return ""


def parse_plan_data() -> bool:
    """Parse the plan file to extract project information."""
    global config

    if not config.new_plan.is_file():
        log_error(f"Plan file not found: {config.new_plan}")
        return False

    log_info(f"Parsing plan data from {config.new_plan}")

    config.new_lang = extract_plan_field("Language/Version", config.new_plan)
    config.new_framework = extract_plan_field("Primary Dependencies", config.new_plan)
    config.new_db = extract_plan_field("Storage", config.new_plan)
    config.new_project_type = extract_plan_field("Project Type", config.new_plan)

    # Log what we found
    if config.new_lang:
        log_info(f"Found language: {config.new_lang}")
    else:
        log_warn("No language information found in plan")

    if config.new_framework:
        log_info(f"Found framework: {config.new_framework}")

    if config.new_db and config.new_db != "N/A":
        log_info(f"Found database: {config.new_db}")

    if config.new_project_type:
        log_info(f"Found project type: {config.new_project_type}")

    return True


def format_technology_stack(lang: str, framework: str) -> str:
    """Format technology stack string."""
    parts = []

    if lang and lang != "NEEDS CLARIFICATION":
        parts.append(lang)
    if framework and framework not in ["NEEDS CLARIFICATION", "N/A"]:
        parts.append(framework)

    if not parts:
        return ""
    elif len(parts) == 1:
        return parts[0]
    else:
        return " + ".join(parts)


# ═══════════════════════════════════════════════════════════════
# Template and Content Generation Functions
# ═══════════════════════════════════════════════════════════════

def get_project_structure(project_type: str) -> str:
    """Get project structure based on type."""
    if project_type and "web" in project_type.lower():
        return "backend/\nfrontend/\ntests/"
    else:
        return "src/\ntests/"


def get_commands_for_language(lang: str) -> str:
    """Get build/test commands for a language."""
    if not lang:
        return "# Add commands"

    lang_lower = lang.lower()
    if "python" in lang_lower:
        return "cd src && pytest && ruff check ."
    elif "rust" in lang_lower:
        return "cargo test && cargo clippy"
    elif "javascript" in lang_lower or "typescript" in lang_lower:
        return "npm test && npm run lint"
    else:
        return f"# Add commands for {lang}"


def get_language_conventions(lang: str) -> str:
    """Get language conventions string."""
    if lang:
        return f"{lang}: Follow standard conventions"
    return "Follow standard conventions"


def create_new_agent_file(target_file: Path, project_name: str, current_date: str) -> Optional[Path]:
    """Create a new agent file from template."""
    global config

    if not config.template_file.is_file():
        log_error(f"Template not found at {config.template_file}")
        return None

    log_info("Creating new agent context file from template...")

    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix='.md')
    os.close(fd)
    temp_files.append(temp_path)

    try:
        # Copy template
        shutil.copy2(config.template_file, temp_path)

        # Read template content
        content = Path(temp_path).read_text(encoding='utf-8')

        # Get replacement values
        project_structure = get_project_structure(config.new_project_type)
        commands = get_commands_for_language(config.new_lang)
        language_conventions = get_language_conventions(config.new_lang)

        # Build technology stack and recent change strings
        escaped_lang = config.new_lang or ""
        escaped_framework = config.new_framework or ""
        escaped_branch = config.current_branch or ""

        if escaped_lang and escaped_framework:
            tech_stack = f"- {escaped_lang} + {escaped_framework} ({escaped_branch})"
            recent_change = f"- {escaped_branch}: Added {escaped_lang} + {escaped_framework}"
        elif escaped_lang:
            tech_stack = f"- {escaped_lang} ({escaped_branch})"
            recent_change = f"- {escaped_branch}: Added {escaped_lang}"
        elif escaped_framework:
            tech_stack = f"- {escaped_framework} ({escaped_branch})"
            recent_change = f"- {escaped_branch}: Added {escaped_framework}"
        else:
            tech_stack = f"- ({escaped_branch})"
            recent_change = f"- {escaped_branch}: Added"

        # Perform substitutions
        substitutions = [
            ("[PROJECT NAME]", project_name),
            ("[DATE]", current_date),
            ("[EXTRACTED FROM ALL PLAN.MD FILES]", tech_stack),
            ("[ACTUAL STRUCTURE FROM PLANS]", project_structure),
            ("[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]", commands),
            ("[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE]", language_conventions),
            ("[LAST 3 FEATURES AND WHAT THEY ADDED]", recent_change),
        ]

        for old, new in substitutions:
            content = content.replace(old, new)

        # Write back
        Path(temp_path).write_text(content, encoding='utf-8')

        return Path(temp_path)

    except Exception as e:
        log_error(f"Failed to create new agent file: {e}")
        return None


def update_existing_agent_file(target_file: Path, current_date: str) -> bool:
    """Update an existing agent context file."""
    global config

    log_info("Updating existing agent context file...")

    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix='.md')
    os.close(fd)
    temp_files.append(temp_path)

    try:
        # Prepare new entries
        tech_stack = format_technology_stack(config.new_lang, config.new_framework)
        new_tech_entries = []
        new_change_entry = ""

        content = target_file.read_text(encoding='utf-8')

        if tech_stack and tech_stack not in content:
            new_tech_entries.append(f"- {tech_stack} ({config.current_branch})")

        if (config.new_db and
            config.new_db != "N/A" and
            config.new_db != "NEEDS CLARIFICATION" and
            config.new_db not in content):
            new_tech_entries.append(f"- {config.new_db} ({config.current_branch})")

        # Prepare new change entry
        if tech_stack:
            new_change_entry = f"- {config.current_branch}: Added {tech_stack}"
        elif config.new_db and config.new_db not in ["N/A", "NEEDS CLARIFICATION"]:
            new_change_entry = f"- {config.current_branch}: Added {config.new_db}"

        # Check if sections exist
        has_active_technologies = "## Active Technologies" in content
        has_recent_changes = "## Recent Changes" in content

        # Process file
        lines = content.split('\n')
        new_lines = []
        in_tech_section = False
        in_changes_section = False
        tech_entries_added = False
        existing_changes_count = 0

        for line in lines:
            # Handle Active Technologies section
            if line.strip() == "## Active Technologies":
                new_lines.append(line)
                in_tech_section = True
                continue
            elif in_tech_section and line.startswith("## "):
                # Add new tech entries before closing the section
                if not tech_entries_added and new_tech_entries:
                    new_lines.extend(new_tech_entries)
                    tech_entries_added = True
                new_lines.append(line)
                in_tech_section = False
                continue
            elif in_tech_section and not line.strip():
                # Add new tech entries before empty line in tech section
                if not tech_entries_added and new_tech_entries:
                    new_lines.extend(new_tech_entries)
                    tech_entries_added = True
                new_lines.append(line)
                continue

            # Handle Recent Changes section
            if line.strip() == "## Recent Changes":
                new_lines.append(line)
                # Add new change entry right after the heading
                if new_change_entry:
                    new_lines.append(new_change_entry)
                in_changes_section = True
                continue
            elif in_changes_section and line.startswith("## "):
                new_lines.append(line)
                in_changes_section = False
                continue
            elif in_changes_section and line.startswith("- "):
                # Keep only first 2 existing changes
                if existing_changes_count < 2:
                    new_lines.append(line)
                    existing_changes_count += 1
                continue

            # Update timestamp
            if "**Last updated**:" in line and re.search(r'\d{4}-\d{2}-\d{2}', line):
                line = re.sub(r'\d{4}-\d{2}-\d{2}', current_date, line)

            new_lines.append(line)

        # Post-loop: if still in tech section
        if in_tech_section and not tech_entries_added and new_tech_entries:
            new_lines.extend(new_tech_entries)

        # If sections don't exist, add them at the end
        if not has_active_technologies and new_tech_entries:
            new_lines.append("")
            new_lines.append("## Active Technologies")
            new_lines.extend(new_tech_entries)

        if not has_recent_changes and new_change_entry:
            new_lines.append("")
            new_lines.append("## Recent Changes")
            new_lines.append(new_change_entry)

        # Write to temp file
        Path(temp_path).write_text('\n'.join(new_lines), encoding='utf-8')

        # Move temp file to target atomically
        shutil.move(temp_path, target_file)

        return True

    except Exception as e:
        log_error(f"Failed to update agent file: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# Main Agent File Update Function
# ═══════════════════════════════════════════════════════════════

def update_agent_file(target_file: Path, agent_name: str) -> bool:
    """Update or create an agent context file."""
    global config

    log_info(f"Updating {agent_name} context file: {target_file}")

    project_name = config.repo_root.name
    current_date = date.today().strftime("%Y-%m-%d")

    # Create directory if it doesn't exist
    target_dir = target_file.parent
    if not target_dir.is_dir():
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            log_error(f"Failed to create directory: {target_dir}: {e}")
            return False

    if not target_file.is_file():
        # Create new file from template
        temp_file = create_new_agent_file(target_file, project_name, current_date)
        if temp_file:
            try:
                shutil.move(str(temp_file), target_file)
                log_success(f"Created new {agent_name} context file")
                return True
            except OSError as e:
                log_error(f"Failed to move temporary file to {target_file}: {e}")
                return False
        else:
            log_error("Failed to create new agent file")
            return False
    else:
        # Update existing file
        if not os.access(target_file, os.R_OK):
            log_error(f"Cannot read existing file: {target_file}")
            return False

        if not os.access(target_file, os.W_OK):
            log_error(f"Cannot write to existing file: {target_file}")
            return False

        if update_existing_agent_file(target_file, current_date):
            log_success(f"Updated existing {agent_name} context file")
            return True
        else:
            log_error("Failed to update existing agent file")
            return False


# ═══════════════════════════════════════════════════════════════
# Agent Selection and Processing
# ═══════════════════════════════════════════════════════════════

AGENT_TYPES = {
    "claude": ("claude_file", "Claude Code"),
    "gemini": ("gemini_file", "Gemini CLI"),
    "copilot": ("copilot_file", "GitHub Copilot"),
    "cursor-agent": ("cursor_file", "Cursor IDE"),
    "qwen": ("qwen_file", "Qwen Code"),
    "opencode": ("agents_file", "opencode"),
    "codex": ("agents_file", "Codex CLI"),
    "windsurf": ("windsurf_file", "Windsurf"),
    "kilocode": ("kilocode_file", "Kilo Code"),
    "auggie": ("auggie_file", "Auggie CLI"),
    "roo": ("roo_file", "Roo Code"),
    "codebuddy": ("codebuddy_file", "CodeBuddy CLI"),
    "qoder": ("qoder_file", "Qoder CLI"),
    "amp": ("amp_file", "Amp"),
    "shai": ("shai_file", "SHAI"),
    "q": ("q_file", "Amazon Q Developer CLI"),
    "bob": ("bob_file", "IBM Bob"),
}


def update_specific_agent(agent_type: str) -> bool:
    """Update a specific agent type."""
    global config

    if agent_type not in AGENT_TYPES:
        log_error(f"Unknown agent type '{agent_type}'")
        log_error("Expected: " + "|".join(AGENT_TYPES.keys()))
        return False

    file_attr, agent_name = AGENT_TYPES[agent_type]
    target_file = getattr(config, file_attr)
    return update_agent_file(target_file, agent_name)


def update_all_existing_agents() -> bool:
    """Update all existing agent files."""
    global config

    found_agent = False
    success = True

    # Check each possible agent file and update if it exists
    agent_files = [
        (config.claude_file, "Claude Code"),
        (config.gemini_file, "Gemini CLI"),
        (config.copilot_file, "GitHub Copilot"),
        (config.cursor_file, "Cursor IDE"),
        (config.qwen_file, "Qwen Code"),
        (config.agents_file, "Codex/opencode"),
        (config.windsurf_file, "Windsurf"),
        (config.kilocode_file, "Kilo Code"),
        (config.auggie_file, "Auggie CLI"),
        (config.roo_file, "Roo Code"),
        (config.codebuddy_file, "CodeBuddy CLI"),
        (config.shai_file, "SHAI"),
        (config.qoder_file, "Qoder CLI"),
        (config.q_file, "Amazon Q Developer CLI"),
        (config.bob_file, "IBM Bob"),
    ]

    # Track already processed files (some agents share the same file)
    processed = set()

    for file_path, agent_name in agent_files:
        if file_path.is_file() and str(file_path) not in processed:
            if not update_agent_file(file_path, agent_name):
                success = False
            found_agent = True
            processed.add(str(file_path))

    # If no agent files exist, create a default Claude file
    if not found_agent:
        log_info("No existing agent files found, creating default Claude file...")
        if not update_agent_file(config.claude_file, "Claude Code"):
            success = False

    return success


def print_summary():
    """Print summary of changes."""
    global config

    print()
    log_info("Summary of changes:")

    if config.new_lang:
        print(f"  - Added language: {config.new_lang}")

    if config.new_framework:
        print(f"  - Added framework: {config.new_framework}")

    if config.new_db and config.new_db != "N/A":
        print(f"  - Added database: {config.new_db}")

    print()
    log_info("Usage: python update-agent-context.py [" + "|".join(AGENT_TYPES.keys()) + "]")


# ═══════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════

def main():
    global config

    parser = argparse.ArgumentParser(
        description='Update agent context files with information from plan.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Agent types:
  claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|
  kilocode|auggie|roo|codebuddy|qoder|amp|shai|q|bob

Examples:
  python update-agent-context.py                  # Update all existing agent files
  python update-agent-context.py claude           # Update only Claude file
  python update-agent-context.py cursor-agent    # Update only Cursor file
'''
    )
    parser.add_argument('agent_type', nargs='?', default='',
                        help='Specific agent type to update (optional)')

    args = parser.parse_args()

    # Initialize configuration
    repo_root = get_repo_root()
    paths = get_feature_paths()
    config = AgentConfig(repo_root, paths)

    # Validate environment before proceeding
    if not validate_environment():
        sys.exit(1)

    log_info(f"=== Updating agent context files for feature {config.current_branch} ===")

    # Parse the plan file to extract project information
    if not parse_plan_data():
        log_error("Failed to parse plan data")
        sys.exit(1)

    # Process based on agent type argument
    if not args.agent_type:
        # No specific agent provided - update all existing agent files
        log_info("No agent specified, updating all existing agent files...")
        success = update_all_existing_agents()
    else:
        # Specific agent provided - update only that agent
        log_info(f"Updating specific agent: {args.agent_type}")
        success = update_specific_agent(args.agent_type)

    # Print summary
    print_summary()

    if success:
        log_success("Agent context update completed successfully")
        sys.exit(0)
    else:
        log_error("Agent context update completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main()
