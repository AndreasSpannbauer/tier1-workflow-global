"""
Utility functions for GitHub integration.

Provides project-agnostic path detection and file location helpers.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Detect project root from current working directory.

    Looks for .git or .tasks directory by traversing up from cwd.
    Falls back to current working directory if not found.

    Returns:
        Path to project root

    Example:
        >>> root = get_project_root()
        >>> print(root)
        /home/user/my-project
    """
    cwd = Path.cwd()
    current = cwd

    while current != current.parent:
        if (current / ".git").exists() or (current / ".tasks").exists():
            logger.debug(f"Found project root: {current}")
            return current
        current = current.parent

    logger.warning(f"No project root found, using cwd: {cwd}")
    return cwd


def find_epic_dir(epic_id: str) -> Path:
    """
    Find epic directory by ID.

    Searches in .tasks/backlog, .tasks/current, .tasks/completed
    directories for a folder starting with the given epic_id.

    Args:
        epic_id: Epic identifier (e.g., "EPIC-007")

    Returns:
        Path to epic directory

    Raises:
        FileNotFoundError: If epic directory not found

    Example:
        >>> epic_dir = find_epic_dir("EPIC-007")
        >>> print(epic_dir)
        /home/user/my-project/.tasks/backlog/EPIC-007
    """
    project_root = get_project_root()

    search_dirs = [
        project_root / ".tasks" / "backlog",
        project_root / ".tasks" / "current",
        project_root / ".tasks" / "completed",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            logger.debug(f"Search directory does not exist: {search_dir}")
            continue

        # Look for directory starting with epic_id
        for item in search_dir.iterdir():
            if item.is_dir() and item.name.startswith(epic_id):
                logger.info(f"Found epic directory: {item}")
                return item

    raise FileNotFoundError(
        f"Epic {epic_id} not found in .tasks/ subdirectories. "
        f"Searched: {', '.join(str(d) for d in search_dirs if d.exists())}"
    )


def find_task_file(task_id: str) -> Path:
    """
    Find task file by ID.

    Searches for task.md files starting with the given task_id
    in .tasks/backlog, .tasks/current, and .tasks/completed.

    Args:
        task_id: Task identifier (e.g., "FEATURE-001", "TASK-001")

    Returns:
        Path to task file

    Raises:
        FileNotFoundError: If task file not found

    Example:
        >>> task_file = find_task_file("FEATURE-001")
        >>> print(task_file)
        /home/user/my-project/.tasks/current/FEATURE-001-implement-search.task.md
    """
    project_root = get_project_root()

    search_dirs = [
        project_root / ".tasks" / "backlog",
        project_root / ".tasks" / "current",
        project_root / ".tasks" / "completed",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            logger.debug(f"Search directory does not exist: {search_dir}")
            continue

        # Look for file starting with task_id
        for item in search_dir.glob(f"{task_id}*.task.md"):
            logger.info(f"Found task file: {item}")
            return item

    raise FileNotFoundError(
        f"Task {task_id} not found in .tasks/ subdirectories. "
        f"Searched: {', '.join(str(d) for d in search_dirs if d.exists())}"
    )


def ensure_tasks_directory() -> Path:
    """
    Ensure .tasks directory structure exists.

    Creates .tasks/backlog, .tasks/current, and .tasks/completed
    directories if they don't exist.

    Returns:
        Path to .tasks directory

    Example:
        >>> tasks_dir = ensure_tasks_directory()
        >>> print(tasks_dir)
        /home/user/my-project/.tasks
    """
    project_root = get_project_root()
    tasks_dir = project_root / ".tasks"

    # Create subdirectories
    for subdir in ["backlog", "current", "completed"]:
        subdir_path = tasks_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {subdir_path}")

    return tasks_dir
