#!/usr/bin/env python3
"""
Git Workflow Commit Automation

Automatically creates focused commits from working directory changes.
Used at workflow START (clean up WIP) and END (save results).

Usage:
    python3 git_workflow_commit.py start [--epic-id EPIC-123]
    python3 git_workflow_commit.py end --epic-id EPIC-123 [--message "desc"]
    python3 git_workflow_commit.py auto  # Analyze and auto-commit
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from generate_commit_message import generate_commit_message, CommitType


class GitWorkflowCommit:
    """Handles git commits for workflow automation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def is_dirty(self) -> bool:
        """Check if working directory has changes"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        return bool(result.stdout.strip())

    def get_status(self) -> Dict[str, List[str]]:
        """Get git status categorized by change type"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            # Git status format: XY filename (X=index, Y=worktree)
            # Format can be "XY filename" where XY is 2 chars
            # The filename starts after a space, which may be at position 2 or 3
            if len(line) < 3:
                continue

            # Split on space to properly separate status from filename
            parts = line.split(None, 1)  # Split on whitespace, max 2 parts
            if len(parts) != 2:
                continue

            state = parts[0]
            file_path = parts[1]

            # Check both index and worktree status
            if 'M' in state:
                status["modified"].append(file_path)
            elif 'A' in state:
                status["added"].append(file_path)
            elif 'D' in state:
                status["deleted"].append(file_path)
            elif state == '??':
                status["untracked"].append(file_path)

        return status

    def group_changes(self, status: Dict[str, List[str]]) -> List[Dict]:
        """Group related changes for focused commits"""
        groups = []

        all_files = (
            status["modified"] +
            status["added"] +
            status["deleted"] +
            status["untracked"]
        )

        # Group 1: Documentation (*.md, docs/)
        doc_files = [f for f in all_files if f.endswith('.md') or 'docs/' in f]
        if doc_files:
            groups.append({
                "type": CommitType.DOCS,
                "scope": None,
                "files": doc_files,
                "description": "Update documentation"
            })

        # Group 2: Tests (test_*, *_test.py, tests/)
        test_files = [f for f in all_files if 'test' in f.lower() and f not in doc_files]
        if test_files:
            groups.append({
                "type": CommitType.TEST,
                "scope": None,
                "files": test_files,
                "description": "Update tests"
            })

        # Group 3: Tools (tools/, scripts/)
        tool_files = [f for f in all_files if f.startswith('tools/') and f not in doc_files + test_files]
        if tool_files:
            groups.append({
                "type": CommitType.CHORE,
                "scope": "tools",
                "files": tool_files,
                "description": "Update tools"
            })

        # Group 4: Config (.claude/, .tasks/, *.json, *.yaml)
        config_files = [
            f for f in all_files
            if (f.startswith('.claude/') or f.startswith('.tasks/') or
                f.endswith('.json') or f.endswith('.yaml') or f.endswith('.yml'))
            and f not in doc_files + test_files + tool_files
        ]
        if config_files:
            groups.append({
                "type": CommitType.CHORE,
                "scope": "config",
                "files": config_files,
                "description": "Update configuration"
            })

        # Group 5: Source code (everything else)
        other_files = [
            f for f in all_files
            if f not in doc_files + test_files + tool_files + config_files
        ]
        if other_files:
            # Infer if feat or fix based on file content changes
            commit_type = self._infer_commit_type(other_files)
            groups.append({
                "type": commit_type,
                "scope": self._infer_scope(other_files),
                "files": other_files,
                "description": "Update implementation"
            })

        return groups

    def _infer_commit_type(self, files: List[str]) -> CommitType:
        """Infer if changes are feat, fix, or refactor"""
        # TODO: Could analyze git diff to detect new functions vs bug fixes
        # For now, default to 'chore' (safest option)
        return CommitType.CHORE

    def _infer_scope(self, files: List[str]) -> Optional[str]:
        """Infer scope from file paths"""
        # Check common patterns
        if any('.claude/agents/' in f for f in files):
            return 'agents'
        elif any('.tasks/' in f for f in files):
            return 'epic-registry'
        elif any('.claude/commands/' in f for f in files):
            return 'commands'
        else:
            return None

    def create_commit(self, group: Dict, context: Optional[str] = None) -> bool:
        """Create a commit for a group of changes"""
        # Stage files
        for file_path in group["files"]:
            subprocess.run(
                ["git", "add", file_path],
                cwd=self.project_root,
                check=True
            )

        # Generate commit message
        description = context if context else group["description"]
        message = generate_commit_message(
            commit_type=group["type"],
            scope=group["scope"],
            description=description,
            files=group["files"]
        )

        # Create commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        return result.returncode == 0

    def commit_workflow_start(self, epic_id: Optional[str] = None):
        """Auto-commit changes at workflow start"""
        if not self.is_dirty():
            print("✅ Working directory clean, no commits needed")
            return

        print("🔍 Analyzing working directory changes...")
        status = self.get_status()
        groups = self.group_changes(status)

        print(f"\n📦 Found {len(groups)} logical change groups:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['type'].value}({group['scope']}): {len(group['files'])} files")

        print("\n🔨 Creating focused commits...")
        for i, group in enumerate(groups, 1):
            context = f"WIP before {epic_id}" if epic_id else "WIP checkpoint"
            success = self.create_commit(group, context)
            if success:
                print(f"  ✅ Commit {i}/{len(groups)} created")
            else:
                print(f"  ❌ Commit {i}/{len(groups)} failed")

        print("\n✅ Working directory cleaned, workflow can proceed")

    def commit_workflow_end(self, epic_id: str, message: Optional[str] = None):
        """Auto-commit changes at workflow end"""
        if not self.is_dirty():
            print("✅ No changes to commit")
            return

        print("🔍 Committing workflow results...")
        status = self.get_status()

        # Commit all changes together
        all_files = (
            status["modified"] +
            status["added"] +
            status["deleted"] +
            status["untracked"]
        )

        # Stage everything
        subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)

        # Generate message
        context = message if message else f"Complete {epic_id} implementation"
        commit_message = generate_commit_message(
            commit_type=CommitType.FEAT,
            scope=None,
            description=context,
            files=all_files
        )

        # Create commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        if result.returncode == 0:
            print(f"✅ Workflow results committed: {epic_id}")
        else:
            print(f"❌ Commit failed: {result.stderr}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Git workflow commit automation")
    parser.add_argument(
        'mode',
        choices=['start', 'end', 'auto'],
        help='Commit mode: start (before workflow), end (after workflow), auto (analyze and commit)'
    )
    parser.add_argument('--epic-id', help='Epic ID (e.g., EPIC-123)')
    parser.add_argument('--message', help='Custom commit message description')

    args = parser.parse_args()

    project_root = Path.cwd()
    committer = GitWorkflowCommit(project_root)

    if args.mode == 'start':
        committer.commit_workflow_start(epic_id=args.epic_id)
    elif args.mode == 'end':
        if not args.epic_id:
            print("Error: --epic-id required for 'end' mode", file=sys.stderr)
            sys.exit(1)
        committer.commit_workflow_end(epic_id=args.epic_id, message=args.message)
    elif args.mode == 'auto':
        # Auto mode: analyze and commit logically
        committer.commit_workflow_start(epic_id=args.epic_id)


if __name__ == "__main__":
    main()
