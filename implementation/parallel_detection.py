#!/usr/bin/env python3
"""
Parallel Detection Logic for Tier 1 Workflow System

Analyzes implementation-details/file-tasks.md to determine if parallel execution
is viable based on domain separation and file overlap.

Parallelization Criteria (from tier1_enhancement_assessment.md):
- Minimum scope: 5+ files changed across 2+ domains
- File overlap threshold: <30% shared files between tasks
- Domain separation: Backend, frontend, database, tests, docs
- Dependency awareness: Respect task dependencies

Usage:
    python3 parallel_detection.py <path-to-file-tasks.md>

Output:
    JSON to stdout with viability analysis and parallel plan
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set, Optional


# Domain classification rules
DOMAIN_RULES = {
    "backend": [
        r"^src/backend/",
        r"^src/api/",
        r"^src/services/",
        r"^src/models/",
        r"^backend/",
        r"^api/",
        r"^services/",
        r"^models/",
        r"\.service\.py$",
        r"\.controller\.py$",
        r"\.router\.py$",
    ],
    "frontend": [
        r"^src/frontend/",
        r"^src/components/",
        r"^src/pages/",
        r"^src/ui/",
        r"^frontend/",
        r"^components/",
        r"^pages/",
        r"^ui/",
        r"\.tsx?$",
        r"\.jsx?$",
        r"\.vue$",
        r"\.svelte$",
    ],
    "database": [
        r"^migrations/",
        r"^alembic/",
        r"^src/database/",
        r"^src/schemas/",
        r"^database/",
        r"^schemas/",
        r"migration.*\.py$",
        r"\.sql$",
    ],
    "tests": [
        r"^tests/",
        r"^test/",
        r"test_.*\.py$",
        r".*_test\.py$",
        r"\.test\.ts$",
        r"\.spec\.ts$",
    ],
    "docs": [
        r"^docs/",
        r"^documentation/",
        r"README.*\.md$",
        r"\.md$",
        r"\.rst$",
    ],
}


@dataclass
class ParallelTask:
    """Represents a task within a parallel execution plan."""
    files: List[str] = field(default_factory=list)
    task_description: str = ""


@dataclass
class ParallelPlan:
    """
    Parallel execution plan with domain-separated tasks.

    Attributes:
        viable: Whether parallel execution is viable
        reason: Explanation for viability decision
        file_count: Total number of files to create/modify
        domain_count: Number of domains involved
        domains: Mapping of domain to list of files
        file_overlap_percentage: Percentage of files shared between domains
        recommendation: "parallel" or "sequential"
        parallel_plan: Domain-specific task definitions (if viable)
    """
    viable: bool
    reason: str
    file_count: int
    domain_count: int
    domains: Dict[str, List[str]]
    file_overlap_percentage: float
    recommendation: str
    parallel_plan: Optional[Dict[str, ParallelTask]] = None


def parse_file_tasks(file_path: Path) -> List[str]:
    """
    Parse file-tasks.md to extract list of files to create/modify.

    Args:
        file_path: Path to file-tasks.md

    Returns:
        List of file paths mentioned in the document

    Raises:
        FileNotFoundError: If file_path does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text()
    files = set()

    # Pattern 1: "- `path/to/file.py` - Description"
    pattern1 = r'-\s+`([^`]+)`\s*-'
    files.update(re.findall(pattern1, content))

    # Pattern 2: "- path/to/file.py"
    pattern2 = r'-\s+([^\s`]+\.[a-zA-Z0-9]+)'
    files.update(re.findall(pattern2, content))

    # Pattern 3: Code blocks with file paths
    # Look for ```python or similar followed by file paths
    code_block_pattern = r'```[a-z]*\n([^`]+)```'
    code_blocks = re.findall(code_block_pattern, content, re.MULTILINE)
    for block in code_blocks:
        # Extract file paths from code blocks
        file_pattern = r'([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)'
        potential_files = re.findall(file_pattern, block)
        # Filter out non-file-path matches (e.g., function.call())
        for pf in potential_files:
            if '/' in pf or pf.count('.') == 1:
                files.add(pf)

    # Pattern 4: Headers like "### src/backend/service.py"
    header_pattern = r'^#{1,4}\s+([^\s`#]+\.[a-zA-Z0-9]+)'
    files.update(re.findall(header_pattern, content, re.MULTILINE))

    # Pattern 5: Bold file mentions like "**src/api/routes.py**"
    bold_pattern = r'\*\*([^\s*]+\.[a-zA-Z0-9]+)\*\*'
    files.update(re.findall(bold_pattern, content))

    # Filter out invalid paths (too short, no extension, etc.)
    valid_files = []
    for f in files:
        f = f.strip()
        # Must have at least one character before extension
        # Must have a valid file extension
        if len(f) > 3 and '.' in f and not f.startswith('.'):
            valid_files.append(f)

    return sorted(valid_files)


def classify_file(file_path: str) -> str:
    """
    Classify a file into a domain based on path patterns.

    Args:
        file_path: Path to the file

    Returns:
        Domain name ("backend", "frontend", "database", "tests", "docs", "other")
    """
    for domain, patterns in DOMAIN_RULES.items():
        for pattern in patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return domain

    return "other"


def classify_files(files: List[str]) -> Dict[str, List[str]]:
    """
    Classify a list of files into domains.

    Args:
        files: List of file paths

    Returns:
        Dictionary mapping domain names to lists of files
    """
    domains: Dict[str, List[str]] = {}

    for file in files:
        domain = classify_file(file)
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(file)

    return domains


def calculate_file_overlap(domains: Dict[str, List[str]]) -> float:
    """
    Calculate percentage of files that appear in multiple domains.

    Note: In the current implementation, files are assigned to a single domain,
    so overlap is based on files that could logically belong to multiple domains
    or are shared infrastructure (e.g., models used by both backend and frontend).

    For simplicity, we consider files as shared if they match multiple domain patterns.

    Args:
        domains: Dictionary mapping domain names to lists of files

    Returns:
        Percentage of overlapping files (0-100)
    """
    all_files = []
    for files in domains.values():
        all_files.extend(files)

    if not all_files:
        return 0.0

    # Check how many files match multiple domain patterns
    shared_count = 0
    for file in all_files:
        matching_domains = 0
        for domain_patterns in DOMAIN_RULES.values():
            for pattern in domain_patterns:
                if re.search(pattern, file, re.IGNORECASE):
                    matching_domains += 1
                    break  # Count each domain only once per file

        if matching_domains > 1:
            shared_count += 1

    overlap_percentage = (shared_count / len(all_files)) * 100
    return round(overlap_percentage, 1)


def generate_task_description(domain: str, files: List[str]) -> str:
    """
    Generate a human-readable task description for a domain.

    Args:
        domain: Domain name
        files: List of files in this domain

    Returns:
        Task description string
    """
    descriptions = {
        "backend": "Backend API implementation",
        "frontend": "Frontend UI implementation",
        "database": "Database schema and migrations",
        "tests": "Test suite implementation",
        "docs": "Documentation updates",
        "other": "Additional implementation tasks",
    }

    base_desc = descriptions.get(domain, "Implementation tasks")
    file_count = len(files)

    return f"{base_desc} ({file_count} file{'s' if file_count != 1 else ''})"


def analyze_parallel_viability(
    file_tasks_path: Path,
    min_files: int = 5,
    min_domains: int = 2,
    max_overlap_percentage: float = 30.0
) -> ParallelPlan:
    """
    Analyze file-tasks.md to determine if parallel execution is viable.

    Args:
        file_tasks_path: Path to file-tasks.md
        min_files: Minimum number of files required for parallel execution
        min_domains: Minimum number of domains required
        max_overlap_percentage: Maximum allowed file overlap percentage

    Returns:
        ParallelPlan object with viability analysis
    """
    try:
        files = parse_file_tasks(file_tasks_path)
    except FileNotFoundError as e:
        return ParallelPlan(
            viable=False,
            reason=f"File not found: {file_tasks_path}",
            file_count=0,
            domain_count=0,
            domains={},
            file_overlap_percentage=0.0,
            recommendation="sequential",
        )
    except Exception as e:
        return ParallelPlan(
            viable=False,
            reason=f"Error parsing file-tasks.md: {str(e)}",
            file_count=0,
            domain_count=0,
            domains={},
            file_overlap_percentage=0.0,
            recommendation="sequential",
        )

    # Classify files by domain
    domains = classify_files(files)

    # Remove "other" domain for analysis purposes
    analysis_domains = {k: v for k, v in domains.items() if k != "other"}

    file_count = len(files)
    domain_count = len(analysis_domains)
    file_overlap = calculate_file_overlap(domains)

    # Check viability criteria
    criteria = []
    viable = True

    if file_count < min_files:
        criteria.append(f"too few files ({file_count} < {min_files})")
        viable = False

    if domain_count < min_domains:
        criteria.append(f"too few domains ({domain_count} < {min_domains})")
        viable = False

    if file_overlap > max_overlap_percentage:
        criteria.append(f"high overlap ({file_overlap}% > {max_overlap_percentage}%)")
        viable = False

    # Generate reason string
    if viable:
        reason = f"{file_count} files across {domain_count} domains with {file_overlap}% overlap"
    else:
        reason = "Not viable: " + ", ".join(criteria)

    # Generate parallel plan if viable
    parallel_plan = None
    if viable:
        parallel_plan = {}
        for domain, domain_files in analysis_domains.items():
            parallel_plan[domain] = ParallelTask(
                files=domain_files,
                task_description=generate_task_description(domain, domain_files)
            )

    recommendation = "parallel" if viable else "sequential"

    return ParallelPlan(
        viable=viable,
        reason=reason,
        file_count=file_count,
        domain_count=domain_count,
        domains=domains,
        file_overlap_percentage=file_overlap,
        recommendation=recommendation,
        parallel_plan=parallel_plan,
    )


def dataclass_to_dict(obj):
    """Convert dataclass to dict recursively, handling nested dataclasses."""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_value in asdict(obj).items():
            if isinstance(field_value, dict):
                result[field_name] = {
                    k: dataclass_to_dict(v) if hasattr(v, '__dataclass_fields__') else v
                    for k, v in field_value.items()
                }
            else:
                result[field_name] = field_value
        return result
    return obj


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Analyze file-tasks.md for parallel execution opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze file-tasks.md
    python3 parallel_detection.py ~/.tasks/backlog/EPIC-007/implementation-details/file-tasks.md

    # Save output to file
    python3 parallel_detection.py file-tasks.md > parallel_plan.json

    # Custom thresholds
    python3 parallel_detection.py file-tasks.md --min-files 10 --max-overlap 20
        """
    )

    parser.add_argument(
        "file_tasks_path",
        type=Path,
        help="Path to file-tasks.md"
    )

    parser.add_argument(
        "--min-files",
        type=int,
        default=5,
        help="Minimum number of files required for parallel execution (default: 5)"
    )

    parser.add_argument(
        "--min-domains",
        type=int,
        default=2,
        help="Minimum number of domains required (default: 2)"
    )

    parser.add_argument(
        "--max-overlap",
        type=float,
        default=30.0,
        help="Maximum allowed file overlap percentage (default: 30.0)"
    )

    args = parser.parse_args()

    # Analyze parallel viability
    result = analyze_parallel_viability(
        args.file_tasks_path,
        min_files=args.min_files,
        min_domains=args.min_domains,
        max_overlap_percentage=args.max_overlap
    )

    # Convert to dictionary for JSON serialization
    result_dict = dataclass_to_dict(result)

    # Handle nested ParallelTask objects in parallel_plan
    if result_dict.get('parallel_plan'):
        result_dict['parallel_plan'] = {
            domain: {
                'files': task.files,
                'task_description': task.task_description
            }
            for domain, task in result.parallel_plan.items()
        }

    # Output JSON to stdout
    print(json.dumps(result_dict, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.viable else 1)


if __name__ == "__main__":
    main()
