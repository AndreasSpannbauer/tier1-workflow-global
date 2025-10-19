"""Core git worktree operations for parallel agent execution."""

import json
import logging
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import WorktreeMetadata

logger = logging.getLogger(__name__)

# Worktree configuration
WORKTREE_ROOT = Path(".worktrees")
METADATA_DIR = WORKTREE_ROOT / ".metadata"


def ensure_worktree_directories() -> None:
    """Ensure worktree root and metadata directories exist."""
    WORKTREE_ROOT.mkdir(exist_ok=True)
    METADATA_DIR.mkdir(exist_ok=True)


def create_worktree_for_agent(
    epic_id: str, task_name: str, base_branch: str = "dev", project_root: Optional[Path] = None
) -> WorktreeMetadata:
    """Create isolated git worktree for agent execution.

    Creates a new git worktree with its own feature branch, providing
    complete directory isolation for parallel agent work.

    Args:
        epic_id: Epic identifier (e.g., "EPIC-007")
        task_name: Human-readable task name (e.g., "Backend API Implementation")
        base_branch: Branch to create worktree from (default: "dev")
        project_root: Project root directory (default: cwd)

    Returns:
        WorktreeMetadata with path, branch, status="created"

    Raises:
        RuntimeError: If git worktree command fails

    Example:
        >>> metadata = create_worktree_for_agent("EPIC-007", "Backend API")
        >>> print(metadata.path)  # .worktrees/EPIC-007-backend-api-a3f2b1
        >>> print(metadata.branch)  # feature/EPIC-007/backend-api
    """
    if project_root is None:
        project_root = Path.cwd()

    # Ensure directories exist
    ensure_worktree_directories()

    # Generate unique names
    sanitized = sanitize_name(task_name)
    short_id = str(uuid.uuid4())[:8]
    worktree_name = f"{epic_id}-{sanitized}-{short_id}"
    worktree_path = project_root / WORKTREE_ROOT / worktree_name
    branch_name = f"feature/{epic_id}/{sanitized}"

    logger.info(f"Creating worktree: {worktree_name}")
    logger.debug(f"Path: {worktree_path}")
    logger.debug(f"Branch: {branch_name}")
    logger.debug(f"Base branch: {base_branch}")

    # Create worktree with feature branch
    try:
        result = subprocess.run(
            ["git", "worktree", "add", str(worktree_path), "-b", branch_name, base_branch],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        logger.debug(f"Git output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Git worktree creation failed: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Create metadata
    metadata = WorktreeMetadata(
        name=worktree_name,
        epic_id=epic_id,
        task_name=task_name,
        path=worktree_path,
        branch=branch_name,
        base_branch=base_branch,
        status="created",
    )

    # Save metadata
    save_worktree_metadata(metadata)

    logger.info(f"✅ Created worktree: {worktree_path} (branch: {branch_name})")
    return metadata


def list_worktrees(epic_id: Optional[str] = None, status: Optional[str] = None) -> List[WorktreeMetadata]:
    """List all worktrees, optionally filtered by epic_id and status.

    Reads metadata files from .worktrees/.metadata/

    Args:
        epic_id: Filter by epic (optional)
        status: Filter by status (optional)

    Returns:
        List of WorktreeMetadata

    Example:
        >>> # List all active worktrees for EPIC-007
        >>> worktrees = list_worktrees(epic_id="EPIC-007", status="in_progress")
    """
    ensure_worktree_directories()

    worktrees: List[WorktreeMetadata] = []

    # Read all metadata files
    for metadata_file in METADATA_DIR.glob("*.json"):
        try:
            metadata = load_metadata_from_file(metadata_file)

            # Apply filters
            if epic_id and metadata.epic_id != epic_id:
                continue
            if status and metadata.status != status:
                continue

            worktrees.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
            continue

    # Sort by created_at (most recent first)
    worktrees.sort(key=lambda w: w.created_at, reverse=True)

    return worktrees


def get_worktree_metadata(worktree_name: str) -> Optional[WorktreeMetadata]:
    """Load metadata for a specific worktree.

    Args:
        worktree_name: Worktree name (e.g., "EPIC-007-api-a3f2b1")

    Returns:
        WorktreeMetadata or None if not found

    Example:
        >>> metadata = get_worktree_metadata("EPIC-007-api-a3f2b1")
        >>> if metadata:
        >>>     print(f"Status: {metadata.status}")
    """
    ensure_worktree_directories()
    metadata_file = METADATA_DIR / f"{worktree_name}.json"

    if not metadata_file.exists():
        logger.warning(f"Metadata file not found: {metadata_file}")
        return None

    try:
        return load_metadata_from_file(metadata_file)
    except Exception as e:
        logger.error(f"Failed to load metadata for {worktree_name}: {e}")
        return None


def save_worktree_metadata(metadata: WorktreeMetadata) -> None:
    """Save worktree metadata to .worktrees/.metadata/{name}.json

    Args:
        metadata: WorktreeMetadata to save

    Example:
        >>> metadata.status = "completed"
        >>> save_worktree_metadata(metadata)
    """
    ensure_worktree_directories()
    metadata_file = METADATA_DIR / f"{metadata.name}.json"

    try:
        with open(metadata_file, "w") as f:
            json.dump(metadata.model_dump(mode="json"), f, indent=2, default=str)
        logger.debug(f"Saved metadata: {metadata_file}")
    except Exception as e:
        logger.error(f"Failed to save metadata for {metadata.name}: {e}")
        raise


def update_worktree_status(worktree_name: str, status: str, error_message: Optional[str] = None, **kwargs) -> None:
    """Update worktree status in metadata.

    Args:
        worktree_name: Worktree name
        status: New status (created|assigned|in_progress|completed|failed|merged|cleaned|conflict)
        error_message: Optional error message if failed
        **kwargs: Additional fields to update (e.g., agent_id, completed_at)

    Example:
        >>> update_worktree_status(
        ...     "EPIC-007-api-a3f2b1",
        ...     "completed",
        ...     completed_at=datetime.utcnow()
        ... )
    """
    metadata = get_worktree_metadata(worktree_name)
    if not metadata:
        raise ValueError(f"Worktree not found: {worktree_name}")

    # Update status
    metadata.status = status  # type: ignore

    # Update error message if provided
    if error_message:
        metadata.error_message = error_message

    # Update additional fields
    for key, value in kwargs.items():
        if hasattr(metadata, key):
            setattr(metadata, key, value)
        else:
            logger.warning(f"Ignoring unknown field: {key}")

    # Save updated metadata
    save_worktree_metadata(metadata)
    logger.info(f"Updated worktree {worktree_name} status: {status}")


def sanitize_name(name: str) -> str:
    """Sanitize task name for use in branch/worktree names.

    Replace spaces with hyphens, remove special chars, lowercase.

    Args:
        name: Task name to sanitize

    Returns:
        Sanitized name suitable for git branch names

    Example:
        >>> sanitize_name("Backend API Implementation")
        'backend-api-implementation'
        >>> sanitize_name("Fix Bug #123 (Critical!)")
        'fix-bug-123-critical'
    """
    # Remove special characters, keep alphanumeric, spaces, and hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9\s-]", "", name)
    # Replace whitespace with hyphens
    sanitized = re.sub(r"\s+", "-", sanitized)
    # Remove consecutive hyphens
    sanitized = re.sub(r"-+", "-", sanitized)
    # Strip leading/trailing hyphens
    sanitized = sanitized.strip("-")
    # Lowercase
    return sanitized.lower()


def load_metadata_from_file(metadata_file: Path) -> WorktreeMetadata:
    """Load WorktreeMetadata from JSON file.

    Args:
        metadata_file: Path to metadata JSON file

    Returns:
        WorktreeMetadata instance

    Raises:
        ValueError: If file cannot be parsed
    """
    with open(metadata_file, "r") as f:
        data = json.load(f)

    # Convert string paths back to Path objects
    if "path" in data and isinstance(data["path"], str):
        data["path"] = Path(data["path"])

    # Convert ISO datetime strings back to datetime objects
    for datetime_field in ["created_at", "assigned_at", "completed_at", "merged_at", "cleaned_at"]:
        if datetime_field in data and data[datetime_field]:
            if isinstance(data[datetime_field], str):
                data[datetime_field] = datetime.fromisoformat(data[datetime_field].replace("Z", "+00:00"))

    return WorktreeMetadata(**data)


def worktree_exists(worktree_name: str) -> bool:
    """Check if worktree directory and metadata both exist.

    Args:
        worktree_name: Worktree name

    Returns:
        True if worktree exists and is valid
    """
    metadata = get_worktree_metadata(worktree_name)
    if not metadata:
        return False

    return metadata.path.exists()


def get_all_git_worktrees() -> List[dict]:
    """Get list of all git worktrees from git directly.

    Returns:
        List of dicts with keys: path, branch, commit

    Example:
        >>> worktrees = get_all_git_worktrees()
        >>> for wt in worktrees:
        ...     print(f"{wt['path']} -> {wt['branch']}")
    """
    try:
        result = subprocess.run(["git", "worktree", "list", "--porcelain"], check=True, capture_output=True, text=True)

        worktrees = []
        current = {}
        for line in result.stdout.strip().split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
            elif line.startswith("HEAD "):
                current["commit"] = line.split(" ", 1)[1]

        if current:
            worktrees.append(current)

        return worktrees

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list git worktrees: {e.stderr}")
        return []
