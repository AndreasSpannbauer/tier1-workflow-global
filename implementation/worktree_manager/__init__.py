"""Git Worktree Manager - Parallel agent execution with directory isolation.

This module provides git worktree management for parallel agent execution,
enabling multiple agents to work concurrently without merge conflicts.

Each agent gets an isolated directory (worktree) on a separate feature branch,
allowing true parallel development with sequential merge coordination.

Key Features:
- Worktree creation with automatic branch management
- Metadata tracking for worktree lifecycle
- Sequential cleanup and archival
- Basic operations for Tier 1 workflow

Basic Usage:
    >>> from worktree_manager import (
    ...     create_worktree_for_agent,
    ...     list_worktrees,
    ...     get_worktree_metadata,
    ...     update_worktree_status,
    ...     cleanup_epic_worktrees
    ... )
    >>>
    >>> # Create worktree
    >>> metadata = create_worktree_for_agent("TASK-001", "Backend API")
    >>> print(metadata.path)  # .worktrees/TASK-001-backend-api-a3f2b1
    >>>
    >>> # List worktrees
    >>> worktrees = list_worktrees()
    >>>
    >>> # Update status
    >>> update_worktree_status(metadata.name, "completed")
    >>>
    >>> # Cleanup
    >>> cleanup_epic_worktrees("TASK-001", delete_branches=True)

Architecture:
    - worktree_manager.py: Core worktree operations (create, list, metadata)
    - cleanup.py: Worktree removal and archival
    - models.py: Pydantic data structures for type safety

Directory Structure:
    .worktrees/                    # Root directory for all worktrees
    ├── TASK-001-api-a3f2b1/       # Individual worktree directory
    ├── TASK-001-frontend-b4c3d2/
    └── .metadata/                 # Metadata tracking
        ├── TASK-001-api-a3f2b1.json
        └── archived/              # Historical records
            └── TASK-001-api-a3f2b1-20251019-143000.json
"""

# Core worktree operations
from .worktree_manager import (
    METADATA_DIR,
    WORKTREE_ROOT,
    create_worktree_for_agent,
    get_all_git_worktrees,
    get_worktree_metadata,
    list_worktrees,
    sanitize_name,
    save_worktree_metadata,
    update_worktree_status,
    worktree_exists,
)

# Cleanup operations
from .cleanup import (
    ARCHIVE_DIR,
    archive_worktree_metadata,
    cleanup_abandoned_worktrees,
    cleanup_all_worktrees,
    cleanup_epic_worktrees,
    cleanup_worktree,
    list_archived_worktrees,
)

# Data models
from .models import MergeResult, MergeSummary, WorktreeExecutionResult, WorktreeMetadata

__version__ = "1.0.0"

__all__ = [
    # Core operations
    "create_worktree_for_agent",
    "list_worktrees",
    "get_worktree_metadata",
    "update_worktree_status",
    "save_worktree_metadata",
    "sanitize_name",
    "worktree_exists",
    "get_all_git_worktrees",
    # Cleanup operations
    "cleanup_worktree",
    "cleanup_epic_worktrees",
    "archive_worktree_metadata",
    "cleanup_abandoned_worktrees",
    "list_archived_worktrees",
    "cleanup_all_worktrees",
    # Models
    "WorktreeMetadata",
    "MergeResult",
    "MergeSummary",
    "WorktreeExecutionResult",
    # Constants
    "WORKTREE_ROOT",
    "METADATA_DIR",
    "ARCHIVE_DIR",
]
