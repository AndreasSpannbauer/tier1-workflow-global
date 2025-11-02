#!/usr/bin/env python3
"""
Commit Message Generator - Conventional Commits Format

Generates commit messages following Conventional Commits specification:
<type>[(scope)]: <description>

Types: feat, fix, docs, refactor, test, chore
Scopes: agents, tools, commands, epic-registry, etc.

Usage:
    from generate_commit_message import generate_commit_message, CommitType

    message = generate_commit_message(
        commit_type=CommitType.FEAT,
        scope="agents",
        description="Add implementation agent",
        files=["src/agent.py"]
    )
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional


class CommitType(Enum):
    """Conventional Commit types"""
    FEAT = "feat"        # New feature
    FIX = "fix"          # Bug fix
    DOCS = "docs"        # Documentation only
    REFACTOR = "refactor"  # Code change that neither fixes bug nor adds feature
    TEST = "test"        # Adding or updating tests
    CHORE = "chore"      # Other changes (build, CI, dependencies)


def generate_commit_message(
    commit_type: CommitType,
    description: str,
    scope: Optional[str] = None,
    files: Optional[List[str]] = None,
    max_length: int = 72
) -> str:
    """
    Generate Conventional Commits formatted message.

    Args:
        commit_type: Type of commit (feat, fix, docs, etc.)
        description: Short description of change
        scope: Optional scope (agents, tools, etc.)
        files: Optional list of modified files
        max_length: Maximum length of first line (default 72)

    Returns:
        Formatted commit message
    """
    # Build first line
    if scope:
        first_line = f"{commit_type.value}({scope}): {description}"
    else:
        first_line = f"{commit_type.value}: {description}"

    # Truncate if too long
    if len(first_line) > max_length:
        first_line = first_line[:max_length-3] + "..."

    # Add file list if provided (for context)
    if files and len(files) <= 10:  # Don't list too many files
        file_list = "\n\nFiles modified:\n" + "\n".join(f"- {f}" for f in files)
        return first_line + file_list

    return first_line


def infer_commit_type_from_files(files: List[str]) -> CommitType:
    """Infer commit type from modified files"""
    if any('test' in f.lower() for f in files):
        return CommitType.TEST
    elif any(f.endswith('.md') or 'docs/' in f for f in files):
        return CommitType.DOCS
    else:
        return CommitType.CHORE  # Safe default


def infer_scope_from_files(files: List[str]) -> Optional[str]:
    """Infer scope from file paths"""
    if any('.claude/agents/' in f for f in files):
        return 'agents'
    elif any('.tasks/' in f for f in files):
        return 'epic-registry'
    elif any('tools/' in f for f in files):
        return 'tools'
    elif any('.claude/commands/' in f for f in files):
        return 'commands'
    else:
        return None


if __name__ == "__main__":
    # Example usage
    msg = generate_commit_message(
        commit_type=CommitType.FEAT,
        scope="agents",
        description="Add implementation agent with validation",
        files=["src/agents/implementation.py", "tests/test_implementation.py"]
    )
    print(msg)
