"""
Master specification coverage analysis.
"""

import re
from pathlib import Path
from typing import List, Set
from .models import EpicRegistryData, MasterSpecCoverage


def parse_master_spec_requirements(master_spec_path: Path) -> List[str]:
    """
    Parse requirements from master spec.

    Expected format:
    - REQ-001: Description
    - REQ-002: Another requirement

    Returns:
        List of requirement IDs (e.g., ["REQ-001", "REQ-002"])
    """
    if not master_spec_path.exists():
        return []

    content = master_spec_path.read_text()

    # Match: - REQ-XXX: or ## REQ-XXX or **REQ-XXX**
    pattern = r'[-#\*\s]+(REQ-\d+)'
    matches = re.findall(pattern, content)

    # Deduplicate and sort
    requirements = sorted(set(matches))

    return requirements


def find_requirements_in_epic(epic_spec_path: Path) -> Set[str]:
    """
    Find requirement references in epic spec.

    Returns:
        Set of requirement IDs mentioned
    """
    if not epic_spec_path.exists():
        return set()

    content = epic_spec_path.read_text()

    # Match: REQ-XXX anywhere in text
    pattern = r'REQ-\d+'
    matches = re.findall(pattern, content)

    return set(matches)


def calculate_coverage(registry_data: EpicRegistryData, project_dir: Path) -> MasterSpecCoverage:
    """
    Calculate master spec coverage.

    Returns:
        MasterSpecCoverage with statistics
    """
    master_spec_path = project_dir / registry_data.master_spec_path

    # Parse all requirements from master spec
    all_requirements = parse_master_spec_requirements(master_spec_path)

    if not all_requirements:
        return MasterSpecCoverage(
            total_requirements=0,
            covered_by_epics=0,
            coverage_percentage=0.0,
            uncovered_requirements=[],
        )

    # Find which requirements are covered by epics
    covered = set()

    for epic in registry_data.epics:
        if epic.status in ["defined", "prepared", "ready", "implemented"]:
            epic_spec_path = project_dir / epic.directory / "spec.md"
            requirements = find_requirements_in_epic(epic_spec_path)
            covered.update(requirements)

    # Calculate uncovered
    uncovered = [req for req in all_requirements if req not in covered]

    coverage_pct = (len(covered) / len(all_requirements)) * 100 if all_requirements else 0.0

    return MasterSpecCoverage(
        total_requirements=len(all_requirements),
        covered_by_epics=len(covered),
        coverage_percentage=round(coverage_pct, 1),
        uncovered_requirements=uncovered,
    )


def suggest_next_epic_from_coverage(coverage: MasterSpecCoverage) -> List[str]:
    """
    Suggest which requirements should be addressed next.

    Returns:
        List of requirement IDs prioritized for next epic
    """
    # Return first 3 uncovered requirements
    return coverage.uncovered_requirements[:3]
