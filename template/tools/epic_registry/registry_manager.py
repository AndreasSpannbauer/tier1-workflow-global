"""
Epic Registry Manager - CRUD operations for epic lifecycle tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import Epic, EpicRegistryData, EpicStatus, RegistryStatistics

logger = logging.getLogger(__name__)


class EpicRegistry:
    """
    Epic Registry manager for project-level epic tracking.

    Usage:
        registry = EpicRegistry.load(Path(".tasks/epic_registry.json"))
        epic = registry.get_epic("EPIC-001")
        registry.update_epic_status("EPIC-001", EpicStatus.IMPLEMENTED)
        registry.save()
    """

    def __init__(self, data: EpicRegistryData, file_path: Path):
        self.data = data
        self.file_path = file_path

    @classmethod
    def load(cls, file_path: Path) -> "EpicRegistry":
        """Load registry from JSON file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Registry not found: {file_path}")

        with open(file_path) as f:
            data_dict = json.load(f)

        data = EpicRegistryData(**data_dict)
        return cls(data, file_path)

    @classmethod
    def create(cls, project_name: str, file_path: Path, github_repo: Optional[str] = None) -> "EpicRegistry":
        """Create new epic registry."""
        now = datetime.utcnow().isoformat() + "Z"

        data = EpicRegistryData(
            project_name=project_name,
            created=now,
            last_updated=now,
            github_repo=github_repo,
        )

        registry = cls(data, file_path)
        registry.save()
        return registry

    def save(self) -> None:
        """Save registry to JSON file."""
        # Update statistics before saving
        self._recalculate_statistics()

        # Update last_updated timestamp
        self.data.last_updated = datetime.utcnow().isoformat() + "Z"

        # Write JSON
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.data.model_dump(), f, indent=2)

        logger.info(f"Registry saved: {self.file_path}")

    def _recalculate_statistics(self) -> None:
        """Recalculate epic statistics."""
        stats = RegistryStatistics()
        stats.total_epics = len(self.data.epics)

        for epic in self.data.epics:
            if epic.status == EpicStatus.DEFINED:
                stats.defined += 1
            elif epic.status == EpicStatus.PREPARED:
                stats.prepared += 1
            elif epic.status == EpicStatus.READY:
                stats.ready += 1
            elif epic.status == EpicStatus.IMPLEMENTED:
                stats.implemented += 1
            elif epic.status == EpicStatus.ARCHIVED:
                stats.archived += 1

        self.data.statistics = stats

    def add_epic(self, epic: Epic) -> None:
        """Add new epic to registry."""
        # Verify epic_id is unique
        if self.get_epic(epic.epic_id):
            raise ValueError(f"Epic {epic.epic_id} already exists in registry")

        # Verify epic_number matches next_epic_number
        if epic.epic_number != self.data.next_epic_number:
            raise ValueError(
                f"Epic number mismatch: expected {self.data.next_epic_number}, got {epic.epic_number}"
            )

        self.data.epics.append(epic)
        self.data.next_epic_number += 1
        logger.info(f"Added epic: {epic.epic_id}")

    def get_epic(self, epic_id: str) -> Optional[Epic]:
        """Get epic by ID."""
        for epic in self.data.epics:
            if epic.epic_id == epic_id:
                return epic
        return None

    def update_epic_status(self, epic_id: str, status: EpicStatus) -> None:
        """Update epic status with automatic timestamp updates."""
        epic = self.get_epic(epic_id)
        if not epic:
            raise ValueError(f"Epic not found: {epic_id}")

        old_status = epic.status
        epic.status = status

        # Update timestamps based on status transitions
        today = datetime.utcnow().date().isoformat()

        if status == EpicStatus.PREPARED and not epic.prepared_date:
            epic.prepared_date = today
        elif status == EpicStatus.IMPLEMENTED and not epic.implemented_date:
            epic.implemented_date = today

        logger.info(f"Updated {epic_id} status: {old_status} → {status}")

    def update_epic_github(self, epic_id: str, issue_number: int, issue_url: str) -> None:
        """Update epic GitHub metadata."""
        epic = self.get_epic(epic_id)
        if not epic:
            raise ValueError(f"Epic not found: {epic_id}")

        epic.github_issue = issue_number
        epic.github_url = issue_url
        logger.info(f"Updated {epic_id} GitHub issue: #{issue_number}")

    def get_epics_by_status(self, status: EpicStatus) -> List[Epic]:
        """Get all epics with given status."""
        return [e for e in self.data.epics if e.status == status]

    def get_next_epic_number(self) -> int:
        """Get next epic number to assign."""
        return self.data.next_epic_number

    def generate_epic_id(self) -> str:
        """Generate next epic ID."""
        return f"EPIC-{self.data.next_epic_number:03d}"


# Convenience functions for quick access

def load_registry(project_dir: Optional[Path] = None) -> EpicRegistry:
    """Load registry from project directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    registry_file = project_dir / ".tasks" / "epic_registry.json"
    return EpicRegistry.load(registry_file)


def create_registry(project_name: str, project_dir: Optional[Path] = None, github_repo: Optional[str] = None) -> EpicRegistry:
    """Create new registry in project directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    registry_file = project_dir / ".tasks" / "epic_registry.json"
    return EpicRegistry.create(project_name, registry_file, github_repo)


def save_registry(registry: EpicRegistry) -> None:
    """Save registry."""
    registry.save()
