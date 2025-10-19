"""
Core GitHub issue synchronization using gh CLI.

Handles bidirectional sync between local task files and GitHub Issues.
Uses the already-authenticated `gh` CLI tool - no tokens or PyGithub needed!

All operations are non-blocking: failures are logged but don't raise exceptions.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from .gh_cli_wrapper import (
    GitHubCLIError,
    create_epic_issue,
    get_repo_name,
    post_comment,
    sync_issue_status,
)
from .issue_mapper import extract_issue_summary, format_issue_body
from .label_manager import get_labels_for_task
from .models import GitHubIssueMetadata

logger = logging.getLogger(__name__)


def create_github_issue_from_epic(epic_id: str, epic_dir: Path) -> Optional[str]:
    """
    Create GitHub Issue from complete epic specification.

    Uses the already-authenticated `gh` CLI tool - no token needed!

    Args:
        epic_id: Epic identifier (e.g., "EPIC-007")
        epic_dir: Path to epic directory (e.g., .tasks/backlog/EPIC-007/)

    Returns:
        issue_url (e.g., "https://github.com/user/repo/issues/123")
        Returns None if creation fails

    Side Effects:
        - Creates GitHub issue with formatted body
        - Applies labels based on task metadata
        - Updates task.md with GitHubIssueMetadata

    Example:
        >>> from pathlib import Path
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> url = create_github_issue_from_epic("EPIC-007", epic_dir)
        >>> print(url)
        "https://github.com/user/repo/issues/123"
    """
    try:
        logger.info(f"Creating GitHub issue for {epic_id}")

        # Extract summary from epic artifacts
        summary = extract_issue_summary(epic_dir)

        # Format issue body
        body = format_issue_body(summary)

        # Load task metadata for domain/priority
        task_file = epic_dir / "task.md"
        task_metadata = _parse_task_frontmatter(task_file)

        domain = task_metadata.get("domain", "backend")
        priority = task_metadata.get("priority", "medium")

        # Create issue via gh CLI
        issue = create_epic_issue(
            title=summary.title, body=body, domain=domain, priority=priority
        )

        issue_url = issue["url"]
        issue_number = issue["number"]

        logger.info(f"✅ Created GitHub issue: {issue_url}")

        # Update task.md with metadata
        github_metadata = GitHubIssueMetadata(
            issue_number=issue_number,
            issue_url=issue_url,
            sync_enabled=True,
            last_synced=datetime.utcnow(),
            sub_issues=[],
        )
        update_task_metadata(task_file, github_metadata)

        return issue_url

    except FileNotFoundError as e:
        logger.error(f"Failed to create issue for {epic_id}: Missing artifact - {e}")
        return None
    except GitHubCLIError as e:
        logger.error(f"GitHub CLI error for {epic_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to create GitHub issue for {epic_id}: {e}")
        return None


def sync_status_to_github_simple(
    epic_id: str, new_status: str, epic_dir: Path
) -> None:
    """
    Update GitHub Issue labels when task status changes.

    Uses gh CLI - no token needed!
    Non-blocking: logs warnings on failure but doesn't raise exceptions.

    Args:
        epic_id: Epic identifier
        new_status: New status value (planned, in-progress, review, blocked, completed)
        epic_dir: Path to epic directory

    Side Effects:
        - Updates GitHub issue labels (removes old status, adds new)
        - Posts status change comment
        - Updates task.md last_synced timestamp

    Example:
        >>> from pathlib import Path
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> sync_status_to_github_simple("EPIC-007", "in-progress", epic_dir)
    """
    try:
        logger.info(f"Syncing status for {epic_id} to {new_status}")

        # Load task metadata to get issue number
        task_file = epic_dir / "task.md"
        task_metadata = _parse_task_frontmatter(task_file)

        github_metadata = task_metadata.get("github", {})
        issue_number = github_metadata.get("issue_number")

        if not issue_number:
            logger.warning(f"No issue_number found in task.md for {epic_id}")
            return

        # Update status using gh CLI
        old_statuses = ["planned", "in-progress", "review", "blocked", "completed"]
        sync_issue_status(issue_number, new_status, old_statuses)

        # Update task.md last_synced
        github_metadata["last_synced"] = datetime.utcnow().isoformat()
        _update_frontmatter_field(task_file, "github", github_metadata)

        logger.info(f"✅ Synced status for {epic_id} to {new_status}")

    except GitHubCLIError as e:
        logger.warning(f"GitHub CLI error syncing status for {epic_id}: {e}")
    except Exception as e:
        logger.warning(f"Failed to sync status for {epic_id}: {e}")


def update_task_metadata(task_file: Path, github_metadata: GitHubIssueMetadata) -> None:
    """
    Update task.md frontmatter with GitHub metadata.

    Parses YAML frontmatter, updates GitHub-related fields, and writes back.
    Preserves all other frontmatter fields.

    Args:
        task_file: Path to task.md
        github_metadata: GitHubIssueMetadata object with sync data

    Side Effects:
        - Modifies task.md file in place
    """
    try:
        content = task_file.read_text()

        # Parse frontmatter
        if not content.startswith("---"):
            logger.warning(f"No frontmatter found in {task_file}")
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            logger.warning(f"Invalid frontmatter structure in {task_file}")
            return

        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2]

        # Update GitHub metadata
        frontmatter["github"] = {
            "issue_number": github_metadata.issue_number,
            "issue_url": github_metadata.issue_url,
            "sync_enabled": github_metadata.sync_enabled,
            "last_synced": (
                github_metadata.last_synced.isoformat()
                if github_metadata.last_synced
                else None
            ),
            "sub_issues": github_metadata.sub_issues,
        }

        # Write back
        new_content = (
            "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---" + body
        )
        task_file.write_text(new_content)
        logger.info(f"✅ Updated task metadata in {task_file}")

    except Exception as e:
        logger.error(f"Failed to update task metadata in {task_file}: {e}")


def get_issue_metadata(task_file: Path) -> Optional[GitHubIssueMetadata]:
    """
    Load GitHub metadata from task.md frontmatter.

    Args:
        task_file: Path to task.md

    Returns:
        GitHubIssueMetadata object, or None if not found or invalid
    """
    try:
        frontmatter = _parse_task_frontmatter(task_file)
        github_data = frontmatter.get("github", {})

        if not github_data:
            return None

        last_synced = github_data.get("last_synced")
        if isinstance(last_synced, str):
            last_synced = datetime.fromisoformat(last_synced)

        return GitHubIssueMetadata(
            issue_number=github_data.get("issue_number"),
            issue_url=github_data.get("issue_url"),
            sync_enabled=github_data.get("sync_enabled", True),
            last_synced=last_synced,
            sub_issues=github_data.get("sub_issues", []),
        )
    except Exception as e:
        logger.error(f"Failed to load issue metadata from {task_file}: {e}")
        return None


# ============================================================================
# Helper Functions
# ============================================================================


def _parse_task_frontmatter(task_file: Path) -> dict:
    """Parse YAML frontmatter from task.md."""
    content = task_file.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML frontmatter: {e}")
                return {}
    return {}


def _update_frontmatter_field(task_file: Path, field: str, value: any) -> None:
    """Update a single field in task.md frontmatter."""
    try:
        content = task_file.read_text()

        if not content.startswith("---"):
            logger.warning(f"No frontmatter found in {task_file}")
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            logger.warning(f"Invalid frontmatter structure in {task_file}")
            return

        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2]

        frontmatter[field] = value

        new_content = (
            "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---" + body
        )
        task_file.write_text(new_content)

    except Exception as e:
        logger.error(f"Failed to update frontmatter field {field} in {task_file}: {e}")
