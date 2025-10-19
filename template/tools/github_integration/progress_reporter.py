"""
Agent progress reporting to GitHub Issues.

Posts agent progress updates as GitHub comments and manages sub-issues
for parallel work execution.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, List

from .gh_cli_wrapper import create_sub_issue, post_comment
from .issue_mapper import format_progress_comment
from .issue_sync_gh import _parse_task_frontmatter, _update_frontmatter_field
from .label_manager import get_labels_for_task
from .models import ProgressUpdate, SubIssueTask

logger = logging.getLogger(__name__)


def post_progress_update(epic_id: str, update: ProgressUpdate, epic_dir: Path) -> None:
    """
    Post agent progress update as GitHub issue comment.

    Uses gh CLI - no token needed!
    Non-blocking: if GitHub API fails, stores update in local queue for retry.

    Args:
        epic_id: Epic identifier
        update: ProgressUpdate object with agent execution data
        epic_dir: Path to epic directory

    Side Effects:
        - Posts comment to GitHub issue
        - Updates task.md last_synced timestamp
        - On failure: stores update in retry queue

    Example:
        >>> from pathlib import Path
        >>> from models import ProgressUpdate
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> update = ProgressUpdate(
        ...     epic_id="EPIC-007",
        ...     phase="Phase 5A",
        ...     status="complete",
        ...     agent_id="agent-1",
        ...     details="Implementation complete"
        ... )
        >>> post_progress_update("EPIC-007", update, epic_dir)
    """
    try:
        logger.info(f"Posting progress update for {epic_id}: {update.phase} - {update.status}")

        # Load task metadata to get issue number
        task_file = epic_dir / "task.md"
        task_metadata = _parse_task_frontmatter(task_file)

        github_metadata = task_metadata.get("github", {})
        issue_number = github_metadata.get("issue_number")

        if not issue_number:
            logger.warning(f"No issue_number found in task.md for {epic_id}")
            _store_failed_update(epic_dir, update)
            return

        # Check if sync is enabled
        if not github_metadata.get("sync_enabled", True):
            logger.info(f"GitHub sync disabled for {epic_id}, skipping progress update")
            return

        # Format and post comment
        comment_body = format_progress_comment(update)
        post_comment(issue_number, comment_body)
        logger.info(f"Posted progress update to issue #{issue_number}")

        # Update task.md last_synced
        github_metadata["last_synced"] = datetime.utcnow().isoformat()
        _update_frontmatter_field(task_file, "github", github_metadata)

    except Exception as e:
        logger.error(f"Failed to post progress update for {epic_id}: {e}")
        _store_failed_update(epic_dir, update)


def create_sub_issues_for_parallel_work(
    parent_issue_number: int, parallel_tasks: List[SubIssueTask], parent_epic_dir: Path
) -> List[int]:
    """
    Create sub-issues for parallel agent execution.

    Creates individual GitHub issues for each parallel task and links them
    to the parent issue via comments.

    Args:
        parent_issue_number: Parent issue number
        parallel_tasks: List of SubIssueTask objects
        parent_epic_dir: Path to parent epic directory

    Returns:
        List of sub-issue numbers

    Side Effects:
        - Creates sub-issues on GitHub
        - Links sub-issues to parent via comments
        - Posts summary comment on parent issue
        - Updates parent task.md with sub_issues list

    Example:
        >>> from pathlib import Path
        >>> from models import SubIssueTask
        >>> tasks = [
        ...     SubIssueTask(
        ...         name="Backend Implementation",
        ...         domain="backend",
        ...         epic_id="EPIC-007",
        ...         estimated_effort="MEDIUM"
        ...     )
        ... ]
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> sub_issues = create_sub_issues_for_parallel_work(123, tasks, epic_dir)
    """
    sub_issue_numbers = []

    try:
        logger.info(f"Creating {len(parallel_tasks)} sub-issues for parent issue #{parent_issue_number}")

        for task in parallel_tasks:
            try:
                # Format sub-issue title and body
                title = f"{task.epic_id}: {task.name}"
                body = _format_sub_issue_body(task, parent_issue_number)

                # Create sub-issue
                sub_issue = create_sub_issue(
                    parent_number=parent_issue_number,
                    title=title,
                    body=body,
                    domain=task.domain
                )

                sub_issue_numbers.append(sub_issue["number"])
                logger.info(f"Created sub-issue #{sub_issue['number']}: {task.name}")

            except Exception as e:
                logger.error(f"Failed to create sub-issue for task {task.name}: {e}")

        # Post summary comment on parent issue
        if sub_issue_numbers:
            issue_links = ", ".join([f"#{num}" for num in sub_issue_numbers])
            summary_comment = (
                f"Created {len(sub_issue_numbers)} sub-issues for parallel work:\n\n"
                f"{issue_links}\n\n"
                f"🤖 These sub-issues track parallel agent execution."
            )
            post_comment(parent_issue_number, summary_comment)
            logger.info(f"Posted sub-issue summary to parent issue #{parent_issue_number}")

            # Update parent task.md
            task_file = parent_epic_dir / "task.md"
            task_metadata = _parse_task_frontmatter(task_file)
            github_metadata = task_metadata.get("github", {})
            github_metadata["sub_issues"] = sub_issue_numbers
            _update_frontmatter_field(task_file, "github", github_metadata)

        return sub_issue_numbers

    except Exception as e:
        logger.error(f"Failed to create sub-issues for parent #{parent_issue_number}: {e}")
        return []


def close_sub_issues(
    sub_issue_numbers: List[int], completion_comment: str = "Sub-task completed. Closing."
) -> None:
    """
    Close completed sub-issues.

    Args:
        sub_issue_numbers: List of sub-issue numbers to close
        completion_comment: Comment to post when closing
    """
    from .gh_cli_wrapper import close_issue

    for issue_num in sub_issue_numbers:
        try:
            close_issue(issue_num, comment=completion_comment)
            logger.info(f"Closed sub-issue #{issue_num}")
        except Exception as e:
            logger.error(f"Failed to close sub-issue #{issue_num}: {e}")


# ============================================================================
# Helper Functions
# ============================================================================


def _format_sub_issue_body(task: SubIssueTask, parent_issue_number: int) -> str:
    """Format body for sub-issue."""
    body_parts = [
        f"## Sub-Task: {task.name}",
        "",
        f"**Parent Issue:** #{parent_issue_number}",
        f"**Epic:** {task.epic_id}",
        f"**Domain:** {task.domain}",
    ]

    if task.estimated_effort:
        body_parts.append(f"**Effort:** {task.estimated_effort}")

    if task.description:
        body_parts.extend(
            [
                "",
                "## Description",
                "",
                task.description,
            ]
        )

    body_parts.extend(
        [
            "",
            "---",
            "",
            "🤖 This is a sub-task for parallel agent execution.",
            "Progress will be tracked via comments and status updates.",
        ]
    )

    return "\n".join(body_parts)


def _store_failed_update(epic_dir: Path, update: ProgressUpdate) -> None:
    """
    Store failed progress update in local queue for retry.

    Creates a retry queue file in the epic directory to store updates
    that failed to post to GitHub.

    Args:
        epic_dir: Path to epic directory
        update: ProgressUpdate that failed to post
    """
    try:
        retry_queue_dir = epic_dir / ".github_sync_queue"
        retry_queue_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        queue_file = retry_queue_dir / f"update_{timestamp}.json"

        # Store update as JSON
        import json

        update_data = update.model_dump()
        # Convert datetime to string
        update_data["timestamp"] = update_data["timestamp"].isoformat()

        queue_file.write_text(json.dumps(update_data, indent=2))
        logger.info(f"Stored failed update in retry queue: {queue_file}")

    except Exception as e:
        logger.error(f"Failed to store update in retry queue: {e}")


def retry_failed_updates(epic_dir: Path) -> int:
    """
    Retry posting failed progress updates from queue.

    Args:
        epic_dir: Path to epic directory

    Returns:
        Number of updates successfully retried

    Example:
        >>> from pathlib import Path
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> count = retry_failed_updates(epic_dir)
        >>> print(f"Retried {count} updates")
    """
    retry_count = 0
    retry_queue_dir = epic_dir / ".github_sync_queue"

    if not retry_queue_dir.exists():
        return 0

    try:
        import json

        for queue_file in retry_queue_dir.glob("update_*.json"):
            try:
                update_data = json.loads(queue_file.read_text())
                # Convert timestamp string back to datetime
                update_data["timestamp"] = datetime.fromisoformat(update_data["timestamp"])

                update = ProgressUpdate(**update_data)
                post_progress_update(update.epic_id, update, epic_dir)

                # Delete queue file on success
                queue_file.unlink()
                retry_count += 1

            except Exception as e:
                logger.error(f"Failed to retry update from {queue_file}: {e}")

        logger.info(f"Retried {retry_count} failed updates from queue")
        return retry_count

    except Exception as e:
        logger.error(f"Failed to process retry queue: {e}")
        return 0
