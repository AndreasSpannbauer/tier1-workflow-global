"""Pydantic models for git worktree metadata and tracking."""

from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class WorktreeMetadata(BaseModel):
    """Metadata for a git worktree.

    Tracks the complete lifecycle of a worktree from creation through
    agent assignment, execution, merging, and cleanup.
    """

    name: str = Field(description="Unique worktree identifier (e.g., 'EPIC-007-api-a3f2b1')")
    epic_id: str = Field(description="Epic identifier (e.g., 'EPIC-007')")
    task_name: str = Field(description="Human-readable task name")
    path: Path = Field(description="Absolute path to worktree directory")
    branch: str = Field(description="Feature branch name")
    base_branch: str = Field(default="dev", description="Branch worktree was created from")
    agent_id: Optional[str] = Field(default=None, description="Assigned agent identifier")
    status: Literal["created", "assigned", "in_progress", "completed", "failed", "merged", "cleaned", "conflict"] = (
        Field(default="created", description="Current worktree lifecycle status")
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    cleaned_at: Optional[datetime] = None

    # Integration
    github_sub_issue: Optional[int] = Field(default=None, description="Linked GitHub sub-issue number")

    # Execution tracking
    commits: List[str] = Field(default_factory=list, description="Commit hashes created in worktree")
    error_message: Optional[str] = Field(default=None, description="Error details if status='failed'")

    class Config:
        """Pydantic configuration."""

        json_encoders = {Path: str, datetime: lambda v: v.isoformat() if v else None}


class MergeResult(BaseModel):
    """Result of merging a single worktree branch."""

    worktree_name: str = Field(description="Worktree that was merged")
    branch: str = Field(description="Feature branch name")
    status: Literal["merged", "conflict", "failed"] = Field(description="Merge outcome")
    message: str = Field(description="Human-readable merge result message")
    conflict_files: List[str] = Field(default_factory=list, description="Files with merge conflicts")

    @property
    def success(self) -> bool:
        """Check if merge was successful."""
        return self.status == "merged"


class MergeSummary(BaseModel):
    """Summary of merging all worktrees for an epic.

    Provides aggregate statistics and detailed results for each
    worktree merge operation.
    """

    epic_id: str = Field(description="Epic identifier")
    target_branch: str = Field(default="dev", description="Branch that worktrees were merged into")
    total_worktrees: int = Field(description="Total number of worktrees processed")
    successful_merges: int = Field(description="Number of successful merges")
    failed_merges: int = Field(description="Number of failed merges")
    conflicts: int = Field(description="Number of merge conflicts")
    results: List[MergeResult] = Field(default_factory=list, description="Detailed merge results")

    @property
    def all_merged(self) -> bool:
        """Check if all worktrees merged successfully."""
        return self.successful_merges == self.total_worktrees

    @property
    def has_conflicts(self) -> bool:
        """Check if any conflicts occurred."""
        return self.conflicts > 0


class WorktreeExecutionResult(BaseModel):
    """Result of executing agent task within a worktree."""

    worktree_name: str = Field(description="Worktree where task executed")
    success: bool = Field(description="Whether task completed successfully")
    summary: str = Field(description="Execution summary")
    files_modified: List[str] = Field(default_factory=list, description="Files changed during execution")
    duration_minutes: float = Field(description="Execution duration in minutes")
    commits: List[str] = Field(default_factory=list, description="Commits created")
    error_message: Optional[str] = Field(default=None, description="Error details if failed")
