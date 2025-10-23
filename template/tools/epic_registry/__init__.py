"""
Epic Registry - Centralized epic lifecycle tracking system.

Provides:
- Epic state management (defined → prepared → ready → implemented)
- Unique epic ID generation
- Dependency tracking
- Master spec coverage analysis
"""

from .registry_manager import (
    EpicRegistry,
    create_registry,
    load_registry,
    save_registry,
)
from .models import Epic, EpicStatus, EpicDependencies, MasterSpecCoverage
from .epic_selector import select_next_epic, is_blocked, get_ready_unblocked_epics
from .dependency_resolver import get_dependency_graph, find_dependency_cycle, topological_sort
from .coverage_analyzer import (
    calculate_coverage,
    suggest_next_epic_from_coverage,
    parse_master_spec_requirements,
)

__all__ = [
    "EpicRegistry",
    "create_registry",
    "load_registry",
    "save_registry",
    "Epic",
    "EpicStatus",
    "EpicDependencies",
    "MasterSpecCoverage",
    "select_next_epic",
    "is_blocked",
    "get_ready_unblocked_epics",
    "get_dependency_graph",
    "find_dependency_cycle",
    "topological_sort",
    "calculate_coverage",
    "suggest_next_epic_from_coverage",
    "parse_master_spec_requirements",
]
