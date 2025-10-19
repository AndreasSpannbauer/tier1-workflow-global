"""
GitHub issue label management.

Manages the standard label taxonomy for status, type, domain, and priority.
"""

import logging
from typing import Any, Dict, List

from .models import IssueLabel

logger = logging.getLogger(__name__)


def get_label_taxonomy() -> Dict[str, List[IssueLabel]]:
    """
    Return standard label taxonomy for GitHub issues.

    Categories:
    - status: Workflow state tracking
    - type: Issue hierarchy (epic, feature, task, sub-task)
    - domain: Technical domain or layer
    - priority: Urgency and importance

    Returns:
        Dict mapping category to list of IssueLabel
    """
    return {
        "status": [
            IssueLabel(name="status:planned", color="d4c5f9", description="Planning phase - spec not yet complete"),
            IssueLabel(name="status:ready", color="0e8a16", description="Ready for implementation - spec complete"),
            IssueLabel(name="status:in-progress", color="fbca04", description="Currently being implemented"),
            IssueLabel(name="status:review", color="006b75", description="Under review or validation"),
            IssueLabel(name="status:blocked", color="d93f0b", description="Blocked by dependencies or issues"),
            IssueLabel(name="status:completed", color="5319e7", description="Implementation complete"),
        ],
        "type": [
            IssueLabel(name="type:epic", color="3e4b9e", description="Large feature requiring multiple tasks"),
            IssueLabel(name="type:feature", color="84b6eb", description="Single feature implementation"),
            IssueLabel(name="type:task", color="c5def5", description="Individual work item"),
            IssueLabel(name="type:sub-task", color="e4e4e4", description="Part of parallel work breakdown"),
        ],
        "domain": [
            IssueLabel(name="domain:backend", color="d4c5f9", description="Backend services and APIs"),
            IssueLabel(name="domain:frontend", color="bfdadc", description="Frontend UI and components"),
            IssueLabel(name="domain:database", color="5319e7", description="Database schema and migrations"),
            IssueLabel(name="domain:testing", color="c2e0c6", description="Test infrastructure and cases"),
            IssueLabel(name="domain:docs", color="d1f0ff", description="Documentation"),
            IssueLabel(name="domain:workflow", color="fbca04", description="Workflow orchestration"),
            IssueLabel(name="domain:infra", color="0e8a16", description="Infrastructure and DevOps"),
        ],
        "priority": [
            IssueLabel(name="priority:critical", color="d93f0b", description="Must be done immediately"),
            IssueLabel(name="priority:high", color="ff9800", description="High priority"),
            IssueLabel(name="priority:medium", color="fbca04", description="Medium priority"),
            IssueLabel(name="priority:low", color="c5def5", description="Low priority"),
        ],
    }


def sync_labels_to_repo(gh_client: Any) -> None:
    """
    Ensure all standard labels exist in GitHub repository.

    Creates missing labels and updates existing ones to match the taxonomy.
    Non-blocking: logs warnings on failure but doesn't raise exceptions.

    Args:
        gh_client: PyGithub Repository object
    """
    taxonomy = get_label_taxonomy()
    all_labels = []
    for category_labels in taxonomy.values():
        all_labels.extend(category_labels)

    try:
        existing_labels = {label.name: label for label in gh_client.get_labels()}

        for label_def in all_labels:
            try:
                if label_def.name in existing_labels:
                    # Update existing label
                    existing_label = existing_labels[label_def.name]
                    existing_label.edit(
                        name=label_def.name, color=label_def.color, description=label_def.description or ""
                    )
                    logger.info(f"Updated label: {label_def.name}")
                else:
                    # Create new label
                    gh_client.create_label(
                        name=label_def.name, color=label_def.color, description=label_def.description or ""
                    )
                    logger.info(f"Created label: {label_def.name}")
            except Exception as e:
                logger.warning(f"Failed to sync label {label_def.name}: {e}")

        logger.info(f"Label sync complete: {len(all_labels)} labels processed")

    except Exception as e:
        logger.error(f"Failed to sync labels to repository: {e}")


def get_labels_for_task(task_metadata: Dict[str, Any]) -> List[str]:
    """
    Determine appropriate labels for a task based on metadata.

    Analyzes task.md frontmatter to select relevant labels from the taxonomy.

    Args:
        task_metadata: Dict containing task.md frontmatter fields

    Returns:
        List of label names to apply to the GitHub issue
    """
    labels = []

    # Status label
    status = task_metadata.get("status", "planned").lower()
    if status in ["planned", "ready", "in-progress", "review", "blocked", "completed"]:
        labels.append(f"status:{status}")
    else:
        labels.append("status:planned")

    # Type label (determine from hierarchy)
    epic_id = task_metadata.get("epic_id", "")
    if epic_id.startswith("EPIC-"):
        labels.append("type:epic")
    elif "parent_epic" in task_metadata:
        labels.append("type:task")
    else:
        labels.append("type:feature")

    # Domain label
    domain = task_metadata.get("domain", "").lower()
    if domain:
        labels.append(f"domain:{domain}")

    # Priority label
    priority = task_metadata.get("priority", "medium").lower()
    if priority in ["critical", "high", "medium", "low"]:
        labels.append(f"priority:{priority}")
    else:
        labels.append("priority:medium")

    return labels


def get_status_labels() -> List[str]:
    """
    Get list of all status label names.

    Used for label cleanup when updating status.

    Returns:
        List of status label names (e.g., ["status:planned", "status:in-progress", ...])
    """
    taxonomy = get_label_taxonomy()
    return [label.name for label in taxonomy["status"]]
