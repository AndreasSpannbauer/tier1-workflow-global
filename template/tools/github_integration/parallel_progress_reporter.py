"""
Parallel workflow progress reporting to GitHub Issues.

Tracks multiple parallel agents simultaneously and updates GitHub issues with
real-time progress tables showing per-agent status, file counts, and overall
execution progress.

MIT License - Copyright (c) 2025
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

from .gh_cli_wrapper import post_comment
from .issue_sync_gh import _parse_task_frontmatter

logger = logging.getLogger(__name__)

# Agent status types
AgentStatus = Literal["pending", "in_progress", "completed", "failed"]


@dataclass
class AgentProgress:
    """Progress tracking for a single parallel agent."""

    agent_id: str
    domain: str
    status: AgentStatus = "pending"
    files_completed: int = 0
    files_total: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_summary: Optional[str] = None

    @property
    def progress_percentage(self) -> int:
        """Calculate completion percentage."""
        if self.files_total == 0:
            return 0
        return int((self.files_completed / self.files_total) * 100)

    @property
    def status_emoji(self) -> str:
        """Get emoji for current status."""
        emoji_map = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
        }
        return emoji_map.get(self.status, "❓")


@dataclass
class ParallelExecution:
    """Tracking state for parallel workflow execution."""

    epic_id: str
    issue_number: int
    started_at: datetime
    agents: Dict[str, AgentProgress] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    merge_summary: Optional[str] = None

    @property
    def total_files(self) -> int:
        """Total files across all agents."""
        return sum(agent.files_total for agent in self.agents.values())

    @property
    def completed_files(self) -> int:
        """Completed files across all agents."""
        return sum(agent.files_completed for agent in self.agents.values())

    @property
    def overall_progress(self) -> int:
        """Overall completion percentage."""
        if self.total_files == 0:
            return 0
        return int((self.completed_files / self.total_files) * 100)

    @property
    def is_complete(self) -> bool:
        """Check if all agents are complete."""
        return all(
            agent.status in ("completed", "failed") for agent in self.agents.values()
        )


class ParallelProgressReporter:
    """
    Reporter for parallel workflow progress to GitHub Issues.

    Tracks multiple parallel agents and posts real-time progress updates as
    GitHub issue comments with formatted tables.

    Example:
        >>> reporter = ParallelProgressReporter()
        >>> reporter.initialize_parallel_tracking("EPIC-007", ["backend", "frontend", "tests"])
        >>> reporter.update_agent_progress("agent-abc", "in_progress", 3, 7)
        >>> reporter.mark_agent_complete("agent-abc", "Implemented all features")
    """

    def __init__(self, metadata_dir: Optional[Path] = None):
        """
        Initialize parallel progress reporter.

        Args:
            metadata_dir: Directory for worktree metadata (default: .worktrees/.metadata/)
        """
        self.metadata_dir = metadata_dir or Path(".worktrees/.metadata")
        self.execution_state: Optional[ParallelExecution] = None
        self.offline_queue_dir: Optional[Path] = None

    def initialize_parallel_tracking(
        self, epic_id: str, domains: List[str], epic_dir: Path
    ) -> None:
        """
        Initialize parallel execution tracking.

        Creates tracking state for all parallel agents and posts initial
        progress comment to GitHub issue.

        Args:
            epic_id: Epic identifier
            domains: List of domain names for parallel agents
            epic_dir: Path to epic directory

        Side Effects:
            - Creates ParallelExecution state
            - Posts initial progress comment to GitHub
            - Creates offline queue directory

        Example:
            >>> reporter.initialize_parallel_tracking(
            ...     "EPIC-007",
            ...     ["backend", "frontend", "tests"],
            ...     Path(".tasks/backlog/EPIC-007")
            ... )
        """
        try:
            # Load task metadata to get issue number
            task_file = epic_dir / "task.md"
            task_metadata = _parse_task_frontmatter(task_file)
            github_metadata = task_metadata.get("github", {})
            issue_number = github_metadata.get("issue_number")

            if not issue_number:
                logger.warning(
                    f"No issue_number found for {epic_id}, skipping GitHub tracking"
                )
                return

            # Check if sync is enabled
            if not github_metadata.get("sync_enabled", True):
                logger.info(
                    f"GitHub sync disabled for {epic_id}, skipping parallel tracking"
                )
                return

            # Create execution state
            self.execution_state = ParallelExecution(
                epic_id=epic_id, issue_number=issue_number, started_at=datetime.utcnow()
            )

            # Initialize agent progress for each domain
            for domain in domains:
                agent_id = f"impl-{domain[:3]}-{datetime.utcnow().strftime('%H%M%S')}"
                self.execution_state.agents[agent_id] = AgentProgress(
                    agent_id=agent_id, domain=domain
                )

            # Setup offline queue
            self.offline_queue_dir = epic_dir / ".github_parallel_queue"
            self.offline_queue_dir.mkdir(exist_ok=True)

            # Post initial progress comment
            comment = self._format_progress_table("Parallel execution initialized")
            self._post_or_queue_comment(comment)

            logger.info(
                f"Initialized parallel tracking for {epic_id} with {len(domains)} domains"
            )

        except Exception as e:
            logger.error(f"Failed to initialize parallel tracking for {epic_id}: {e}")
            # Non-blocking: continue workflow execution

    def update_agent_progress(
        self,
        agent_id: str,
        status: AgentStatus,
        files_completed: int,
        files_total: int,
    ) -> None:
        """
        Update progress for a specific agent.

        Args:
            agent_id: Agent identifier
            status: Current agent status
            files_completed: Number of files completed
            files_total: Total number of files

        Side Effects:
            - Updates agent progress state
            - Posts progress update to GitHub

        Example:
            >>> reporter.update_agent_progress("agent-abc", "in_progress", 3, 7)
        """
        if not self.execution_state:
            logger.warning("No parallel execution state initialized")
            return

        try:
            agent = self.execution_state.agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not found in execution state")
                return

            # Update agent state
            agent.status = status
            agent.files_completed = files_completed
            agent.files_total = files_total

            if status == "in_progress" and not agent.started_at:
                agent.started_at = datetime.utcnow()

            # Post progress update
            comment = self._format_progress_table(
                f"Agent {agent_id} progress updated"
            )
            self._post_or_queue_comment(comment)

            logger.info(
                f"Updated progress for {agent_id}: {files_completed}/{files_total} files ({agent.progress_percentage}%)"
            )

        except Exception as e:
            logger.error(f"Failed to update agent progress for {agent_id}: {e}")
            # Non-blocking: continue workflow execution

    def mark_agent_complete(self, agent_id: str, result_summary: str) -> None:
        """
        Mark agent as completed.

        Args:
            agent_id: Agent identifier
            result_summary: Summary of agent results

        Side Effects:
            - Updates agent status to "completed"
            - Posts completion update to GitHub

        Example:
            >>> reporter.mark_agent_complete("agent-abc", "Implemented all features")
        """
        if not self.execution_state:
            logger.warning("No parallel execution state initialized")
            return

        try:
            agent = self.execution_state.agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not found in execution state")
                return

            # Mark as complete
            agent.status = "completed"
            agent.completed_at = datetime.utcnow()
            agent.result_summary = result_summary

            # Post completion update
            comment = self._format_progress_table(f"Agent {agent_id} completed")
            self._post_or_queue_comment(comment)

            logger.info(f"Marked agent {agent_id} as completed")

        except Exception as e:
            logger.error(f"Failed to mark agent complete for {agent_id}: {e}")
            # Non-blocking: continue workflow execution

    def mark_agent_failed(self, agent_id: str, error_message: str) -> None:
        """
        Mark agent as failed.

        Args:
            agent_id: Agent identifier
            error_message: Error message or failure reason

        Side Effects:
            - Updates agent status to "failed"
            - Posts failure update to GitHub

        Example:
            >>> reporter.mark_agent_failed("agent-abc", "Compilation error in main.py")
        """
        if not self.execution_state:
            logger.warning("No parallel execution state initialized")
            return

        try:
            agent = self.execution_state.agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not found in execution state")
                return

            # Mark as failed
            agent.status = "failed"
            agent.completed_at = datetime.utcnow()
            agent.error_message = error_message

            # Post failure update
            comment = self._format_progress_table(
                f"Agent {agent_id} failed: {error_message}"
            )
            self._post_or_queue_comment(comment)

            logger.error(f"Marked agent {agent_id} as failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to mark agent failed for {agent_id}: {e}")
            # Non-blocking: continue workflow execution

    def finalize_parallel_execution(self, merge_summary: str) -> None:
        """
        Finalize parallel execution after all agents complete.

        Args:
            merge_summary: Summary of merge and integration results

        Side Effects:
            - Marks execution as complete
            - Posts final summary to GitHub
            - Processes offline queue

        Example:
            >>> reporter.finalize_parallel_execution("All changes merged successfully")
        """
        if not self.execution_state:
            logger.warning("No parallel execution state initialized")
            return

        try:
            # Mark execution complete
            self.execution_state.completed_at = datetime.utcnow()
            self.execution_state.merge_summary = merge_summary

            # Calculate duration
            duration = (
                self.execution_state.completed_at - self.execution_state.started_at
            )
            duration_minutes = int(duration.total_seconds() / 60)

            # Post final summary
            comment_parts = [
                self._format_progress_table("Parallel execution completed"),
                "",
                "## 🎉 Final Summary",
                "",
                f"**Total Duration:** {duration_minutes} minutes",
                f"**Total Files:** {self.execution_state.completed_files}/{self.execution_state.total_files}",
                "",
                "### Merge Results",
                "",
                merge_summary,
                "",
                "---",
                "",
                f"_🤖 Parallel execution completed at {self.execution_state.completed_at.strftime('%Y-%m-%d %H:%M UTC')}_",
            ]

            comment = "\n".join(comment_parts)
            self._post_or_queue_comment(comment)

            # Process offline queue
            self._retry_offline_queue()

            logger.info(
                f"Finalized parallel execution for {self.execution_state.epic_id}"
            )

        except Exception as e:
            logger.error(f"Failed to finalize parallel execution: {e}")
            # Non-blocking: continue workflow execution

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _format_progress_table(self, header_message: str) -> str:
        """
        Format progress update as markdown table.

        Args:
            header_message: Header message for the update

        Returns:
            Formatted markdown comment
        """
        if not self.execution_state:
            return ""

        # Sort agents by domain for consistent ordering
        sorted_agents = sorted(
            self.execution_state.agents.values(), key=lambda a: a.domain
        )

        # Build progress table
        table_rows = [
            "| Domain | Agent | Status | Files | Progress |",
            "|--------|-------|--------|-------|----------|",
        ]

        for agent in sorted_agents:
            files_display = f"{agent.files_completed}/{agent.files_total}"
            progress_display = f"{agent.progress_percentage}%"
            status_display = f"{agent.status_emoji} {agent.status.replace('_', ' ').title()}"

            table_rows.append(
                f"| {agent.domain} | {agent.agent_id} | {status_display} | {files_display} | {progress_display} |"
            )

        # Build full comment
        comment_parts = [
            "## 🔄 Parallel Execution Progress",
            "",
            f"**{header_message}**",
            "",
            f"**Mode:** Parallel ({len(self.execution_state.agents)} domains)",
            f"**Started:** {self.execution_state.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            *table_rows,
            "",
            f"**Overall:** {self.execution_state.overall_progress}% ({self.execution_state.completed_files}/{self.execution_state.total_files} files)",
            "",
            "---",
            "",
            f"_🤖 Updated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_",
        ]

        return "\n".join(comment_parts)

    def _post_or_queue_comment(self, comment: str) -> None:
        """
        Post comment to GitHub or queue if offline.

        Args:
            comment: Comment body to post
        """
        if not self.execution_state:
            return

        try:
            post_comment(self.execution_state.issue_number, comment)
            logger.debug(
                f"Posted progress update to issue #{self.execution_state.issue_number}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to post comment to GitHub, queuing for retry: {e}"
            )
            self._queue_failed_comment(comment)

    def _queue_failed_comment(self, comment: str) -> None:
        """
        Queue failed comment for offline retry.

        Args:
            comment: Comment body that failed to post
        """
        if not self.offline_queue_dir:
            logger.error("No offline queue directory configured")
            return

        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            queue_file = self.offline_queue_dir / f"comment_{timestamp}.json"

            queue_data = {
                "issue_number": (
                    self.execution_state.issue_number
                    if self.execution_state
                    else None
                ),
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat(),
            }

            queue_file.write_text(json.dumps(queue_data, indent=2))
            logger.info(f"Queued failed comment for retry: {queue_file}")

        except Exception as e:
            logger.error(f"Failed to queue comment for retry: {e}")

    def _retry_offline_queue(self) -> int:
        """
        Retry posting queued comments from offline queue.

        Returns:
            Number of comments successfully retried
        """
        if not self.offline_queue_dir or not self.offline_queue_dir.exists():
            return 0

        retry_count = 0

        try:
            for queue_file in self.offline_queue_dir.glob("comment_*.json"):
                try:
                    queue_data = json.loads(queue_file.read_text())
                    issue_number = queue_data["issue_number"]
                    comment = queue_data["comment"]

                    # Retry posting
                    post_comment(issue_number, comment)
                    queue_file.unlink()  # Delete on success
                    retry_count += 1

                    logger.info(f"Successfully retried queued comment from {queue_file}")

                except Exception as e:
                    logger.warning(f"Failed to retry comment from {queue_file}: {e}")

            if retry_count > 0:
                logger.info(f"Retried {retry_count} queued comments from offline queue")

        except Exception as e:
            logger.error(f"Failed to process offline queue: {e}")

        return retry_count


# ============================================================================
# Convenience Functions
# ============================================================================


def create_parallel_reporter(epic_dir: Path) -> ParallelProgressReporter:
    """
    Create a parallel progress reporter for an epic.

    Args:
        epic_dir: Path to epic directory

    Returns:
        Configured ParallelProgressReporter instance

    Example:
        >>> from pathlib import Path
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> reporter = create_parallel_reporter(epic_dir)
    """
    return ParallelProgressReporter(metadata_dir=epic_dir / ".github_parallel_queue")
