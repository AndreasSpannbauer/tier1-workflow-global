"""
Data models for epic registry system.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class EpicStatus(str, Enum):
    """Epic lifecycle states."""
    DEFINED = "defined"          # spec.md created, not yet prepared
    PREPARED = "prepared"         # file-tasks.md exists
    READY = "ready"               # passed preflight checks
    IMPLEMENTED = "implemented"   # workflow executed successfully
    ARCHIVED = "archived"         # deprecated/cancelled


class EpicDependencies(BaseModel):
    """Epic dependency relationships."""
    blocks: List[str] = Field(default_factory=list, description="Epic IDs this epic blocks")
    blocked_by: List[str] = Field(default_factory=list, description="Epic IDs blocking this epic")
    integrates_with: List[str] = Field(default_factory=list, description="Epic IDs this integrates with")


class Epic(BaseModel):
    """Complete epic metadata."""
    epic_id: str = Field(..., description="Unique epic identifier (e.g., EPIC-001)")
    epic_number: int = Field(..., description="Sequential epic number")
    title: str = Field(..., description="Human-readable epic title")
    slug: str = Field(..., description="URL-safe slug for directory name")
    status: EpicStatus = Field(..., description="Current lifecycle status")

    # Dates
    created_date: str = Field(..., description="Date epic was created (YYYY-MM-DD)")
    prepared_date: Optional[str] = Field(None, description="Date file-tasks.md was created")
    implemented_date: Optional[str] = Field(None, description="Date workflow completed")

    # Paths
    directory: str = Field(..., description="Relative path to epic directory")

    # GitHub
    github_issue: Optional[int] = Field(None, description="GitHub issue number")
    github_url: Optional[str] = Field(None, description="GitHub issue URL")

    # Implementation stats
    execution_mode: Optional[str] = Field(None, description="sequential or parallel")
    files_created: Optional[int] = Field(None, description="Number of files created")
    files_modified: Optional[int] = Field(None, description="Number of files modified")

    # Knowledge
    post_mortem: Optional[str] = Field(None, description="Path to post-mortem report")
    integration_notes: Optional[str] = Field(None, description="How this epic integrates")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    dependencies: EpicDependencies = Field(default_factory=EpicDependencies)


class MasterSpecCoverage(BaseModel):
    """Master specification coverage tracking."""
    total_requirements: int = Field(..., description="Total requirements in master spec")
    covered_by_epics: int = Field(..., description="Requirements covered by epics")
    coverage_percentage: float = Field(..., description="Coverage as percentage")
    uncovered_requirements: List[str] = Field(default_factory=list, description="Requirements not yet covered")


class RegistryStatistics(BaseModel):
    """Aggregate registry statistics."""
    total_epics: int = 0
    defined: int = 0
    prepared: int = 0
    ready: int = 0
    implemented: int = 0
    archived: int = 0


class EpicRegistryData(BaseModel):
    """Root epic registry structure."""
    schema_version: str = "2.0"
    project_name: str = Field(..., description="Project name")
    master_spec_path: str = Field(default=".tasks/master_spec.md")
    created: str = Field(..., description="Registry creation timestamp (ISO 8601)")
    last_updated: str = Field(..., description="Last modification timestamp (ISO 8601)")
    github_repo: Optional[str] = Field(None, description="GitHub repo (user/repo)")
    next_epic_number: int = Field(1, description="Next epic number to assign")
    statistics: RegistryStatistics = Field(default_factory=RegistryStatistics)
    epics: List[Epic] = Field(default_factory=list)
    master_spec_coverage: Optional[MasterSpecCoverage] = Field(None)
