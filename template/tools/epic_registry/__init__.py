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
from .models import Epic, EpicStatus, EpicDependencies

__all__ = [
    "EpicRegistry",
    "create_registry",
    "load_registry",
    "save_registry",
    "Epic",
    "EpicStatus",
    "EpicDependencies",
]
