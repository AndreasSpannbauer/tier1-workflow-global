"""
GitHub Integration Module for V6 Workflow System.

Provides bidirectional sync between local task files and GitHub Issues.
GitHub Issues serve as a presentation layer for human visibility; local files
remain the authoritative source of truth for agents.

This is a portable, project-agnostic version that works in any repository
with .tasks/ directory structure.

Key Components:
- issue_sync_gh: Core sync operations using gh CLI
- progress_reporter: Agent progress updates
- label_manager: Issue label taxonomy
- issue_mapper: Task <-> Issue format conversion
- gh_cli_wrapper: GitHub CLI wrapper (no tokens needed!)
- models: Pydantic data models
- utils: Project-agnostic path detection

Usage Example:
    from pathlib import Path
    from tools.github_integration import create_github_issue_from_epic

    epic_dir = Path(".tasks/backlog/EPIC-007")
    issue_url = create_github_issue_from_epic("EPIC-007", epic_dir)
    print(f"Created: {issue_url}")
"""

from .gh_cli_wrapper import (
    add_labels,
    close_issue,
    create_epic_issue,
    create_issue,
    create_label,
    create_sub_issue,
    get_issue,
    get_repo_name,
    list_labels,
    post_comment,
    remove_labels,
    sync_issue_status,
)
from .issue_mapper import (
    extract_issue_summary,
    format_issue_body,
    format_progress_comment,
)
from .issue_sync_gh import (
    create_github_issue_from_epic,
    get_issue_metadata,
    sync_status_to_github_simple,
    update_task_metadata,
)
from .label_manager import (
    get_label_taxonomy,
    get_labels_for_task,
)
from .models import (
    GitHubIssueMetadata,
    IssueLabel,
    IssueSummary,
    ProgressUpdate,
    SubIssueTask,
)
from .progress_reporter import (
    close_sub_issues,
    create_sub_issues_for_parallel_work,
    post_progress_update,
    retry_failed_updates,
)
from .utils import (
    ensure_tasks_directory,
    find_epic_dir,
    find_task_file,
    get_project_root,
)

__version__ = "2.0.0"

__all__ = [
    # Core sync operations (gh CLI)
    "create_github_issue_from_epic",
    "sync_status_to_github_simple",
    "update_task_metadata",
    "get_issue_metadata",
    # Progress reporting
    "post_progress_update",
    "create_sub_issues_for_parallel_work",
    "close_sub_issues",
    "retry_failed_updates",
    # Label management
    "get_label_taxonomy",
    "get_labels_for_task",
    # Mapping utilities
    "extract_issue_summary",
    "format_issue_body",
    "format_progress_comment",
    # GitHub CLI wrapper
    "create_issue",
    "create_epic_issue",
    "create_sub_issue",
    "add_labels",
    "remove_labels",
    "post_comment",
    "close_issue",
    "get_issue",
    "create_label",
    "list_labels",
    "sync_issue_status",
    "get_repo_name",
    # Data models
    "GitHubIssueMetadata",
    "ProgressUpdate",
    "IssueSummary",
    "IssueLabel",
    "SubIssueTask",
    # Utility functions
    "get_project_root",
    "find_epic_dir",
    "find_task_file",
    "ensure_tasks_directory",
]
