"""
Pydantic models for GitHub integration data structures.

These models provide type safety and validation for GitHub issue sync operations.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class GitHubIssueMetadata(BaseModel):
    """
    Metadata stored in task.md frontmatter for GitHub sync.

    This metadata tracks the bidirectional sync state between local task files
    and GitHub Issues.
    """

    issue_number: Optional[int] = None
    issue_url: Optional[str] = None
    sync_enabled: bool = True
    last_synced: Optional[datetime] = None
    sub_issues: List[int] = Field(default_factory=list)


class IssueLabel(BaseModel):
    """
    GitHub issue label definition.

    Represents a single label that can be applied to GitHub issues.
    """

    name: str
    color: str
    description: Optional[str] = None


class IssueSummary(BaseModel):
    """
    Summary data for creating GitHub issue body.

    Extracts key information from epic artifacts for presentation in GitHub.
    Limited to 500-1000 words for readability.
    """

    title: str
    epic_id: str
    status: str
    domain: str
    effort: Literal["LOW", "MEDIUM", "HIGH"]
    complexity: Literal["LOW", "MEDIUM", "HIGH"]
    problem_statement: str
    requirements: List[str]
    services: List[str]
    impact_summary: str
    artifact_links: List[str]


class ProgressUpdate(BaseModel):
    """
    Agent progress update to post as GitHub comment.

    Represents a single progress update from a V6 agent during workflow execution.
    """

    epic_id: str
    phase: str
    status: Literal["started", "in_progress", "complete", "failed", "blocked"]
    agent_id: str
    duration_minutes: Optional[int] = None
    files_modified: int = 0
    details: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SubIssueTask(BaseModel):
    """
    Definition of a sub-issue for parallel work.

    Used when creating sub-issues for parallel agent execution.
    """

    name: str
    domain: str
    epic_id: str
    description: Optional[str] = None
    estimated_effort: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
