"""
Task to GitHub Issue mapping functionality.

Converts between local task file artifacts and GitHub issue format.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

from .models import IssueSummary, ProgressUpdate

logger = logging.getLogger(__name__)


def extract_issue_summary(epic_dir: Path) -> IssueSummary:
    """
    Extract summary data from epic artifacts for GitHub issue.

    Reads multiple artifact files to build a comprehensive summary:
    - spec.md: Problem statement and requirements
    - architecture.md: Services and components
    - analysis/impact_report.md: Impact analysis
    - task.md: Metadata

    Args:
        epic_dir: Path to epic directory (e.g., .tasks/backlog/EPIC-XXX/)

    Returns:
        IssueSummary with ~500-1000 word summary

    Raises:
        FileNotFoundError: If required artifacts are missing
        ValueError: If artifact parsing fails

    Example:
        >>> from pathlib import Path
        >>> epic_dir = Path(".tasks/backlog/EPIC-007")
        >>> summary = extract_issue_summary(epic_dir)
        >>> print(summary.title)
        "Implement Semantic Search"
    """
    logger.info(f"Extracting issue summary from {epic_dir}")

    # Load task.md for metadata
    task_file = epic_dir / "task.md"
    if not task_file.exists():
        raise FileNotFoundError(f"task.md not found in {epic_dir}")

    task_metadata = _parse_task_frontmatter(task_file)

    # Load spec.md for problem statement and requirements
    spec_file = epic_dir / "spec.md"
    problem_statement = ""
    requirements = []
    if spec_file.exists():
        spec_content = spec_file.read_text()
        problem_statement = _extract_section(spec_content, "Problem Statement")
        requirements = _extract_requirements(spec_content)
    else:
        logger.warning(f"spec.md not found in {epic_dir}")

    # Load architecture.md for services
    architecture_file = epic_dir / "architecture.md"
    services = []
    if architecture_file.exists():
        arch_content = architecture_file.read_text()
        services = _extract_services(arch_content)
    else:
        logger.warning(f"architecture.md not found in {epic_dir}")

    # Load impact analysis
    impact_report = epic_dir / "analysis" / "impact_report.md"
    impact_summary = ""
    if impact_report.exists():
        impact_content = impact_report.read_text()
        impact_summary = _extract_impact_summary(impact_content)
    else:
        logger.warning(f"impact_report.md not found in {epic_dir / 'analysis'}")

    # Collect artifact links (relative to epic directory)
    artifact_links = []
    for artifact in ["spec.md", "architecture.md", "implementation_plan.md"]:
        artifact_path = epic_dir / artifact
        if artifact_path.exists():
            # Use relative path from epic_dir for portability
            artifact_links.append(f".tasks/{epic_dir.parent.name}/{epic_dir.name}/{artifact}")

    return IssueSummary(
        title=task_metadata.get("title", task_metadata.get("epic_id", "Unknown Epic")),
        epic_id=task_metadata.get("epic_id", ""),
        status=task_metadata.get("status", "planned"),
        domain=task_metadata.get("domain", "unknown"),
        effort=task_metadata.get("estimated_effort", "MEDIUM").upper(),
        complexity=task_metadata.get("complexity", "MEDIUM").upper(),
        problem_statement=_truncate_text(problem_statement, 200),
        requirements=requirements[:10],  # Limit to 10 requirements
        services=services,
        impact_summary=_truncate_text(impact_summary, 150),
        artifact_links=artifact_links,
    )


def format_issue_body(summary: IssueSummary) -> str:
    """
    Format GitHub issue body markdown from summary data.

    Creates a human-readable presentation of the epic specification.
    Includes clear disclaimer that agents read local files, not GitHub.

    Args:
        summary: IssueSummary object with epic data

    Returns:
        Markdown string for GitHub issue body
    """
    body_parts = [
        "## 🎯 Overview",
        "",
        f"**Epic ID:** `{summary.epic_id}`",
        f"**Status:** {summary.status}",
        f"**Domain:** {summary.domain}",
        f"**Effort:** {summary.effort} | **Complexity:** {summary.complexity}",
        "",
        "---",
        "",
        "## 📋 Problem Statement",
        "",
        summary.problem_statement,
        "",
    ]

    if summary.requirements:
        body_parts.extend(
            [
                "## ✅ Key Requirements",
                "",
            ]
        )
        for i, req in enumerate(summary.requirements, 1):
            body_parts.append(f"{i}. {req}")
        body_parts.append("")

    if summary.services:
        body_parts.extend(
            [
                "## 🏗️ Architecture",
                "",
                "**Services/Components:**",
                "",
            ]
        )
        for service in summary.services:
            body_parts.append(f"- {service}")
        body_parts.append("")

    if summary.impact_summary:
        body_parts.extend(
            [
                "## 📊 Impact Analysis",
                "",
                summary.impact_summary,
                "",
            ]
        )

    if summary.artifact_links:
        body_parts.extend(
            [
                "## 📁 Full Specification",
                "",
                "**Complete artifacts in local repository:**",
                "",
            ]
        )
        for link in summary.artifact_links:
            body_parts.append(f"- `{link}`")
        body_parts.append("")

    body_parts.extend(
        [
            "---",
            "",
            "### 🤖 Agent Integration",
            "",
            "> **Note:** V6 agents read local task files in `.tasks/`, NOT this GitHub issue.",
            "> This issue is a presentation layer for human visibility and collaboration.",
            "> All authoritative data is stored in local repository files.",
            "",
            f"_Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_",
        ]
    )

    return "\n".join(body_parts)


def format_progress_comment(update: ProgressUpdate) -> str:
    """
    Format progress update as GitHub issue comment.

    Creates a formatted comment showing agent progress during workflow execution.

    Args:
        update: ProgressUpdate object with agent execution data

    Returns:
        Markdown string for GitHub comment
    """
    status_emoji = {"started": "🚀", "in_progress": "⚙️", "complete": "✅", "failed": "❌", "blocked": "🚧"}

    emoji = status_emoji.get(update.status, "📝")

    comment_parts = [
        f"## {emoji} Phase: {update.phase}",
        "",
        f"**Status:** {update.status}",
        f"**Agent:** `{update.agent_id}`",
    ]

    if update.duration_minutes is not None:
        comment_parts.append(f"**Duration:** {update.duration_minutes} minutes")

    if update.files_modified > 0:
        comment_parts.append(f"**Files Modified:** {update.files_modified}")

    comment_parts.extend(
        [
            "",
            "### Details",
            "",
            _truncate_text(update.details, 500),
            "",
            "---",
            "",
            f"_🤖 Posted by V6 Agent at {update.timestamp.strftime('%Y-%m-%d %H:%M UTC')}_",
        ]
    )

    return "\n".join(comment_parts)


# ============================================================================
# Helper Functions
# ============================================================================


def _parse_task_frontmatter(task_file: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter from task.md."""
    content = task_file.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML frontmatter: {e}")
                return {}
    return {}


def _extract_section(content: str, section_name: str) -> str:
    """Extract text under a markdown heading."""
    lines = content.split("\n")
    section_lines = []
    in_section = False

    for line in lines:
        if line.startswith("#"):
            if section_name.lower() in line.lower():
                in_section = True
                continue
            elif in_section:
                break
        elif in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def _extract_requirements(spec_content: str) -> list[str]:
    """Extract requirements from spec.md."""
    requirements = []
    lines = spec_content.split("\n")
    in_requirements = False

    for line in lines:
        if "requirement" in line.lower() and line.startswith("#"):
            in_requirements = True
            continue
        if in_requirements:
            if line.startswith("#"):
                break
            if line.strip().startswith("-") or line.strip().startswith("*"):
                req = line.strip().lstrip("-*").strip()
                if req:
                    requirements.append(req)

    return requirements


def _extract_services(architecture_content: str) -> list[str]:
    """Extract service names from architecture.md."""
    services = []
    lines = architecture_content.split("\n")

    for line in lines:
        line_lower = line.lower()
        if ("service" in line_lower or "component" in line_lower) and ":" in line:
            if line.strip().startswith("-") or line.strip().startswith("*"):
                service = line.strip().lstrip("-*").strip()
                if service:
                    services.append(service)

    return services


def _extract_impact_summary(impact_content: str) -> str:
    """Extract 1-2 sentence summary from impact report."""
    summary_section = _extract_section(impact_content, "Summary")
    if summary_section:
        sentences = summary_section.split(".")
        return ". ".join(sentences[:2]).strip() + "."
    return ""


def _truncate_text(text: str, max_words: int) -> str:
    """Truncate text to maximum number of words."""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."
