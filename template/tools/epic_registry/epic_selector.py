"""
Smart epic selection - choose next epic to implement.
"""

from typing import List, Optional
from .models import Epic, EpicStatus, EpicRegistryData


def select_next_epic(registry_data: EpicRegistryData) -> Optional[Epic]:
    """
    Select next epic to implement based on:
    1. Status = "ready"
    2. Not blocked by unimplemented dependencies
    3. Priority (critical > high > medium > low)
    4. Creation date (oldest first)

    Returns:
        Next epic to implement, or None if none available
    """
    # Filter: status = "ready"
    ready_epics = [e for e in registry_data.epics if e.status == EpicStatus.READY]

    if not ready_epics:
        return None

    # Filter: not blocked
    unblocked = [e for e in ready_epics if not is_blocked(e, registry_data)]

    if not unblocked:
        return None

    # Sort by priority and creation date
    priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    def get_priority(epic: Epic) -> int:
        for tag in epic.tags:
            if tag in priority_map:
                return priority_map[tag]
        return 2  # default medium

    def sort_key(epic: Epic):
        return (get_priority(epic), epic.created_date)

    unblocked.sort(key=sort_key)

    return unblocked[0]


def is_blocked(epic: Epic, registry_data: EpicRegistryData) -> bool:
    """
    Check if epic is blocked by unimplemented dependencies.

    Returns:
        True if any blocking epic is not implemented
    """
    blocked_by = epic.dependencies.blocked_by

    if not blocked_by:
        return False

    # Check if all blocking epics are implemented
    for block_id in blocked_by:
        blocker = next((e for e in registry_data.epics if e.epic_id == block_id), None)
        if blocker and blocker.status != EpicStatus.IMPLEMENTED:
            return True

    return False


def get_blocked_epics(registry_data: EpicRegistryData) -> List[Epic]:
    """Get all epics that are blocked by dependencies."""
    return [e for e in registry_data.epics if is_blocked(e, registry_data)]


def get_ready_unblocked_epics(registry_data: EpicRegistryData) -> List[Epic]:
    """Get all ready epics that are not blocked."""
    ready = [e for e in registry_data.epics if e.status == EpicStatus.READY]
    return [e for e in ready if not is_blocked(e, registry_data)]
