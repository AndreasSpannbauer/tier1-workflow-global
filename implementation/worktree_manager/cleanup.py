"""Worktree cleanup and archival operations."""

import logging
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import Optional

from .models import WorktreeMetadata
from .worktree_manager import METADATA_DIR, get_worktree_metadata, list_worktrees, load_metadata_from_file

logger = logging.getLogger(__name__)

# Archive directory for historical metadata
ARCHIVE_DIR = METADATA_DIR / "archived"


def cleanup_worktree(worktree_name: str, delete_branch: bool = False, force: bool = False) -> None:
    """Remove worktree and optionally delete branch.

    Args:
        worktree_name: Worktree name
        delete_branch: Delete feature branch after removing worktree
        force: Force removal even if worktree has uncommitted changes

    Raises:
        ValueError: If worktree not in terminal state and force=False

    Example:
        >>> # Normal cleanup after successful merge
        >>> cleanup_worktree("EPIC-007-api-a3f2b1", delete_branch=True)
        >>>
        >>> # Force cleanup of failed worktree
        >>> cleanup_worktree("EPIC-007-broken-a3f2b1", force=True)
    """
    metadata = get_worktree_metadata(worktree_name)
    if not metadata:
        logger.warning(f"Metadata not found for {worktree_name}")
        return

    # Check if worktree is in terminal state
    terminal_states = ["completed", "merged", "failed", "cleaned"]
    if metadata.status not in terminal_states and not force:
        raise ValueError(
            f"Worktree {worktree_name} is in state '{metadata.status}'. Use force=True to cleanup non-terminal state."
        )

    logger.info(f"Cleaning up worktree: {worktree_name}")

    # Remove worktree directory
    if metadata.path.exists():
        try:
            force_flag = ["--force"] if force else []
            subprocess.run(
                ["git", "worktree", "remove", str(metadata.path)] + force_flag,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"✅ Removed worktree directory: {metadata.path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove worktree: {e.stderr}")
            if not force:
                raise
            # If force=True, try manual directory removal
            logger.warning("Attempting manual directory removal...")
            try:
                shutil.rmtree(metadata.path)
                logger.info(f"✅ Manually removed directory: {metadata.path}")
            except Exception as rm_error:
                logger.error(f"Failed to manually remove directory: {rm_error}")
                raise
    else:
        logger.warning(f"Worktree directory does not exist: {metadata.path}")

    # Delete feature branch if requested
    if delete_branch:
        try:
            force_flag = "-D" if force else "-d"
            subprocess.run(["git", "branch", force_flag, metadata.branch], check=True, capture_output=True, text=True)
            logger.info(f"✅ Deleted branch: {metadata.branch}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete branch: {e.stderr}")
            if not force:
                raise

    # Archive metadata
    metadata.status = "cleaned"  # type: ignore
    metadata.cleaned_at = datetime.utcnow()
    archive_worktree_metadata(metadata)

    # Remove active metadata file
    metadata_file = METADATA_DIR / f"{worktree_name}.json"
    if metadata_file.exists():
        metadata_file.unlink()
        logger.info(f"✅ Removed metadata file: {metadata_file}")

    logger.info(f"✅ Cleanup complete for {worktree_name}")


def cleanup_epic_worktrees(epic_id: str, delete_branches: bool = False) -> int:
    """Cleanup all worktrees for an epic.

    Args:
        epic_id: Epic identifier
        delete_branches: Delete all feature branches

    Returns:
        Number of worktrees cleaned up

    Example:
        >>> # Cleanup all completed worktrees for EPIC-007
        >>> count = cleanup_epic_worktrees("EPIC-007", delete_branches=True)
        >>> print(f"Cleaned up {count} worktrees")
    """
    logger.info(f"Cleaning up all worktrees for {epic_id}")

    # Get all worktrees in terminal states
    all_worktrees = list_worktrees(epic_id=epic_id)
    terminal_states = ["completed", "merged", "failed"]

    cleanable_worktrees = [wt for wt in all_worktrees if wt.status in terminal_states]

    if not cleanable_worktrees:
        logger.info(f"No worktrees to cleanup for {epic_id}")
        return 0

    logger.info(f"Found {len(cleanable_worktrees)} worktrees to cleanup")

    cleaned_count = 0
    for worktree in cleanable_worktrees:
        try:
            cleanup_worktree(worktree.name, delete_branch=delete_branches)
            cleaned_count += 1
        except Exception as e:
            logger.error(f"Failed to cleanup {worktree.name}: {e}")
            continue

    logger.info(f"✅ Cleaned up {cleaned_count}/{len(cleanable_worktrees)} worktrees")
    return cleaned_count


def archive_worktree_metadata(metadata: WorktreeMetadata) -> None:
    """Move metadata to archived directory for historical record.

    Creates .worktrees/.metadata/archived/{name}.json

    Args:
        metadata: WorktreeMetadata to archive

    Example:
        >>> metadata = get_worktree_metadata("EPIC-007-api-a3f2b1")
        >>> archive_worktree_metadata(metadata)
    """
    # Ensure archive directory exists
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Create archive filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    archive_filename = f"{metadata.name}-{timestamp}.json"
    archive_path = ARCHIVE_DIR / archive_filename

    # Save to archive
    import json

    try:
        with open(archive_path, "w") as f:
            json.dump(metadata.model_dump(mode="json"), f, indent=2, default=str)
        logger.info(f"✅ Archived metadata: {archive_path}")
    except Exception as e:
        logger.error(f"Failed to archive metadata: {e}")
        raise


def cleanup_abandoned_worktrees(max_age_days: int = 7) -> int:
    """Cleanup worktrees that have been inactive for > max_age_days.

    Args:
        max_age_days: Maximum age before cleanup (default: 7)

    Returns:
        Number of abandoned worktrees cleaned up

    Example:
        >>> # Cleanup worktrees older than 7 days
        >>> count = cleanup_abandoned_worktrees(max_age_days=7)
        >>> print(f"Cleaned up {count} abandoned worktrees")
    """
    logger.info(f"Checking for abandoned worktrees (max age: {max_age_days} days)")

    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

    # Get all worktrees in non-terminal states
    all_worktrees = list_worktrees()
    non_terminal_states = ["created", "assigned", "in_progress"]

    abandoned_worktrees = []
    for wt in all_worktrees:
        if wt.status not in non_terminal_states:
            continue

        # Check age based on created_at or last updated timestamp
        check_date = wt.completed_at or wt.assigned_at or wt.created_at

        if check_date < cutoff_date:
            abandoned_worktrees.append(wt)

    if not abandoned_worktrees:
        logger.info("No abandoned worktrees found")
        return 0

    logger.warning(f"Found {len(abandoned_worktrees)} abandoned worktrees")

    cleaned_count = 0
    for worktree in abandoned_worktrees:
        logger.warning(
            f"Cleaning abandoned worktree: {worktree.name} (age: {(datetime.utcnow() - worktree.created_at).days} days)"
        )
        try:
            cleanup_worktree(worktree.name, delete_branch=True, force=True)
            cleaned_count += 1
        except Exception as e:
            logger.error(f"Failed to cleanup abandoned worktree {worktree.name}: {e}")
            continue

    logger.info(f"✅ Cleaned up {cleaned_count}/{len(abandoned_worktrees)} abandoned worktrees")
    return cleaned_count


def list_archived_worktrees(epic_id: Optional[str] = None) -> list:
    """List archived worktree metadata.

    Args:
        epic_id: Filter by epic (optional)

    Returns:
        List of WorktreeMetadata from archived files

    Example:
        >>> archived = list_archived_worktrees(epic_id="EPIC-007")
        >>> print(f"Found {len(archived)} archived worktrees")
    """
    if not ARCHIVE_DIR.exists():
        return []

    archived_worktrees = []

    for archive_file in ARCHIVE_DIR.glob("*.json"):
        try:
            metadata = load_metadata_from_file(archive_file)

            # Apply filter
            if epic_id and metadata.epic_id != epic_id:
                continue

            archived_worktrees.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to load archived metadata from {archive_file}: {e}")
            continue

    # Sort by archived date (most recent first)
    archived_worktrees.sort(key=lambda w: w.cleaned_at or w.completed_at or w.created_at, reverse=True)

    return archived_worktrees


def cleanup_all_worktrees(include_active: bool = False, delete_branches: bool = False) -> dict:
    """Cleanup all worktrees in the system.

    Args:
        include_active: Also cleanup active (non-terminal) worktrees
        delete_branches: Delete feature branches

    Returns:
        Dict with cleanup statistics

    Example:
        >>> stats = cleanup_all_worktrees(include_active=False, delete_branches=True)
        >>> print(f"Cleaned: {stats['cleaned']}, Failed: {stats['failed']}")
    """
    logger.info("Starting full worktree cleanup")

    all_worktrees = list_worktrees()

    if not include_active:
        terminal_states = ["completed", "merged", "failed"]
        worktrees_to_clean = [wt for wt in all_worktrees if wt.status in terminal_states]
    else:
        worktrees_to_clean = all_worktrees

    logger.info(f"Cleaning {len(worktrees_to_clean)} worktrees")

    cleaned = 0
    failed = 0

    for worktree in worktrees_to_clean:
        try:
            cleanup_worktree(worktree.name, delete_branch=delete_branches, force=include_active)
            cleaned += 1
        except Exception as e:
            logger.error(f"Failed to cleanup {worktree.name}: {e}")
            failed += 1

    stats = {"total": len(worktrees_to_clean), "cleaned": cleaned, "failed": failed}

    logger.info(f"✅ Cleanup complete: {cleaned} cleaned, {failed} failed")
    return stats
