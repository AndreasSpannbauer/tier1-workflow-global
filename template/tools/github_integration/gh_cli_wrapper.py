"""GitHub CLI (gh) wrapper for GitHub API operations.

Uses the already-authenticated `gh` CLI tool instead of PyGithub,
eliminating the need for separate tokens or authentication setup.

All functions return structured data parsed from gh CLI JSON output.
"""

import json
import logging
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GitHubCLIError(Exception):
    """Raised when gh CLI command fails."""

    pass


def get_current_repo() -> Dict[str, str]:
    """
    Get current repository information.

    Returns:
        Dict with keys: nameWithOwner, url, defaultBranch

    Example:
        {"nameWithOwner": "user/repo", "url": "https://...", "defaultBranch": "main"}
    """
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner,url,defaultBranchRef"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        return {
            "nameWithOwner": data["nameWithOwner"],
            "url": data["url"],
            "defaultBranch": data["defaultBranchRef"]["name"],
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repo info: {e.stderr}")
        raise GitHubCLIError(f"gh repo view failed: {e.stderr}")
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse repo info: {e}")
        raise GitHubCLIError(f"Failed to parse repo info: {e}")


def create_issue(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new GitHub issue.

    Args:
        title: Issue title
        body: Issue body (markdown)
        labels: Optional list of label names
        assignee: Optional assignee username

    Returns:
        Dict with keys: number, url, title

    Example:
        {"number": 123, "url": "https://github.com/user/repo/issues/123", "title": "..."}
    """
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]

    if labels:
        cmd.extend(["--label", ",".join(labels)])

    if assignee:
        cmd.extend(["--assignee", assignee])

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        # gh issue create returns URL on stdout
        issue_url = result.stdout.strip()

        # Extract issue number from URL
        issue_number = int(issue_url.split("/")[-1])

        logger.info(f"✅ Created issue #{issue_number}: {issue_url}")
        return {"number": issue_number, "url": issue_url, "title": title}

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create issue: {e.stderr}")
        raise GitHubCLIError(f"gh issue create failed: {e.stderr}")


def add_labels(issue_number: int, labels: List[str]) -> None:
    """
    Add labels to an existing issue.

    Args:
        issue_number: Issue number
        labels: List of label names to add
    """
    if not labels:
        return

    cmd = ["gh", "issue", "edit", str(issue_number), "--add-label", ",".join(labels)]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ Added labels to issue #{issue_number}: {', '.join(labels)}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to add labels to issue #{issue_number}: {e.stderr}")
        # Non-blocking: log warning but don't raise


def remove_labels(issue_number: int, labels: List[str]) -> None:
    """
    Remove labels from an existing issue.

    Args:
        issue_number: Issue number
        labels: List of label names to remove
    """
    if not labels:
        return

    cmd = [
        "gh",
        "issue",
        "edit",
        str(issue_number),
        "--remove-label",
        ",".join(labels),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(
            f"✅ Removed labels from issue #{issue_number}: {', '.join(labels)}"
        )
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"Failed to remove labels from issue #{issue_number}: {e.stderr}"
        )
        # Non-blocking: log warning but don't raise


def post_comment(issue_number: int, comment: str) -> None:
    """
    Post a comment on an issue.

    Args:
        issue_number: Issue number
        comment: Comment body (markdown)
    """
    cmd = ["gh", "issue", "comment", str(issue_number), "--body", comment]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ Posted comment to issue #{issue_number}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to post comment to issue #{issue_number}: {e.stderr}")
        # Non-blocking: log warning but don't raise


def close_issue(issue_number: int, comment: Optional[str] = None) -> None:
    """
    Close an issue with optional comment.

    Args:
        issue_number: Issue number
        comment: Optional closing comment
    """
    cmd = ["gh", "issue", "close", str(issue_number)]

    if comment:
        cmd.extend(["--comment", comment])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ Closed issue #{issue_number}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to close issue #{issue_number}: {e.stderr}")
        # Non-blocking: log warning but don't raise


def get_issue(issue_number: int) -> Dict[str, Any]:
    """
    Get issue details.

    Args:
        issue_number: Issue number

    Returns:
        Dict with keys: number, title, body, state, labels, assignees, url

    Example:
        {
            "number": 123,
            "title": "Issue title",
            "body": "Issue body",
            "state": "OPEN",
            "labels": [{"name": "bug"}],
            "assignees": [{"login": "username"}],
            "url": "https://..."
        }
    """
    cmd = [
        "gh",
        "issue",
        "view",
        str(issue_number),
        "--json",
        "number,title,body,state,labels,assignees,url",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get issue #{issue_number}: {e.stderr}")
        raise GitHubCLIError(f"gh issue view failed: {e.stderr}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse issue data: {e}")
        raise GitHubCLIError(f"Failed to parse issue data: {e}")


def create_label(name: str, color: str, description: Optional[str] = None) -> None:
    """
    Create a repository label.

    Args:
        name: Label name
        color: Label color (hex without #)
        description: Optional label description
    """
    cmd = ["gh", "label", "create", name, "--color", color]

    if description:
        cmd.extend(["--description", description])

    # Add --force to update if exists
    cmd.append("--force")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ Created/updated label: {name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to create label '{name}': {e.stderr}")
        # Non-blocking: log warning but don't raise


def list_labels() -> List[Dict[str, str]]:
    """
    List all repository labels.

    Returns:
        List of dicts with keys: name, color, description

    Example:
        [
            {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
            ...
        ]
    """
    cmd = ["gh", "label", "list", "--json", "name,color,description"]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list labels: {e.stderr}")
        raise GitHubCLIError(f"gh label list failed: {e.stderr}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse label data: {e}")
        raise GitHubCLIError(f"Failed to parse label data: {e}")


def link_sub_issue(parent_number: int, child_number: int) -> None:
    """
    Link a sub-issue to parent by posting a comment.

    Note: GitHub doesn't have native sub-issue support, so we create
    a link via comment on the parent issue.

    Args:
        parent_number: Parent issue number
        child_number: Sub-issue number
    """
    comment = f"Sub-issue: #{child_number}"
    post_comment(parent_number, comment)
    logger.info(f"✅ Linked sub-issue #{child_number} to parent #{parent_number}")


def get_repo_name() -> str:
    """
    Get repository name in 'owner/repo' format.

    Attempts multiple methods:
    1. Use gh CLI to detect repo (most reliable)
    2. Parse from git remote URL
    3. Fall back to environment variable

    Returns:
        Repository name (e.g., "user/repo")

    Raises:
        GitHubCLIError: If repo cannot be detected
    """
    # Method 1: Use gh CLI (most reliable)
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_name = result.stdout.strip()
        if repo_name:
            logger.debug(f"Detected repo via gh CLI: {repo_name}")
            return repo_name
    except subprocess.CalledProcessError as e:
        logger.debug(f"gh CLI repo detection failed: {e.stderr}")

    # Method 2: Parse git remote URL
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()

        # Parse GitHub URL (supports HTTPS and SSH)
        match = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
        if match:
            repo_name = match.group(1)
            logger.debug(f"Detected repo from git remote: {repo_name}")
            return repo_name
    except subprocess.CalledProcessError as e:
        logger.debug(f"git remote parsing failed: {e.stderr}")

    # Method 3: Environment variable fallback
    if "GITHUB_REPO" in os.environ:
        repo_name = os.environ["GITHUB_REPO"]
        logger.debug(f"Using repo from GITHUB_REPO env var: {repo_name}")
        return repo_name

    # All methods failed
    raise GitHubCLIError(
        "Could not detect repository name. "
        "Ensure you're in a git repository with GitHub remote, "
        "or run 'gh repo set-default', "
        "or set GITHUB_REPO environment variable"
    )


# Convenience functions for common operations


def sync_issue_status(
    issue_number: int, new_status: str, old_statuses: Optional[List[str]] = None
) -> None:
    """
    Update issue status by swapping labels.

    Args:
        issue_number: Issue number
        new_status: New status (e.g., "in-progress")
        old_statuses: Optional list of old status labels to remove
                     (default: all status:* labels)
    """
    if old_statuses is None:
        old_statuses = ["planned", "in-progress", "review", "blocked", "completed"]

    # Remove old status labels
    old_labels = [f"status:{s}" for s in old_statuses]
    remove_labels(issue_number, old_labels)

    # Add new status label
    add_labels(issue_number, [f"status:{new_status}"])

    # Post comment
    post_comment(issue_number, f"Status changed to **{new_status}**")


def create_epic_issue(
    title: str, body: str, domain: str, priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create an epic issue with standard labels.

    Args:
        title: Epic title
        body: Epic body (markdown)
        domain: Domain (backend, frontend, database, etc.)
        priority: Priority (critical, high, medium, low)

    Returns:
        Dict with keys: number, url, title
    """
    labels = ["epic", "status:planned", f"domain:{domain}", f"priority:{priority}"]
    return create_issue(title, body, labels=labels)


def create_sub_issue(
    parent_number: int, title: str, body: str, domain: str
) -> Dict[str, Any]:
    """
    Create a sub-issue and link to parent.

    Args:
        parent_number: Parent issue number
        title: Sub-issue title
        body: Sub-issue body (markdown)
        domain: Domain (backend, frontend, etc.)

    Returns:
        Dict with keys: number, url, title
    """
    labels = ["sub-task", "status:planned", f"domain:{domain}"]
    issue = create_issue(title, body, labels=labels)

    # Link to parent
    link_sub_issue(parent_number, issue["number"])

    return issue
