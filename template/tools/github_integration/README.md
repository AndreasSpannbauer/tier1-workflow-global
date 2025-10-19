# GitHub Integration Module (Portable Version)

**Version:** 2.0.0
**Purpose:** Bidirectional sync between local V6 task files and GitHub Issues
**Authentication:** Uses existing `gh` CLI authentication (zero configuration!)

## Overview

This is a **portable, project-agnostic** GitHub integration module extracted from email_management_system. It works in any project with a `.tasks/` directory structure and provides GitHub Issues as a presentation layer for local task files.

### Key Features

- **Zero Configuration**: Uses existing `gh` CLI authentication (no tokens needed)
- **Project Agnostic**: Automatically detects project root and repository
- **Non-Blocking**: All GitHub operations are non-blocking with retry queues
- **Complete Workflow Support**: Epic creation, status sync, progress updates, sub-issues
- **Robust Path Detection**: Works from any directory in your project

## Quick Start

### Prerequisites

1. **GitHub CLI authenticated:**
   ```bash
   gh auth status
   ```
   Expected output: `✓ Logged in to github.com`

2. **Project structure:**
   ```
   your-project/
   ├── .git/
   ├── .tasks/
   │   ├── backlog/
   │   ├── current/
   │   └── completed/
   └── tools/
       └── github_integration/  # This module
   ```

### Basic Usage

```python
from pathlib import Path
from tools.github_integration import create_github_issue_from_epic

# Epic directory (can be in backlog, current, or completed)
epic_dir = Path(".tasks/backlog/EPIC-007")

# Create GitHub issue (no token needed!)
url = create_github_issue_from_epic("EPIC-007", epic_dir)
print(f"✅ Issue created: {url}")
```

## Complete Workflow Example

```python
from pathlib import Path
from tools.github_integration import (
    create_github_issue_from_epic,
    sync_status_to_github_simple,
    post_progress_update,
    ProgressUpdate,
    create_sub_issues_for_parallel_work,
    SubIssueTask,
    close_sub_issues,
    get_issue_metadata
)

epic_id = "EPIC-007"
epic_dir = Path(f".tasks/backlog/{epic_id}")

# ============================================================================
# STAGE 1: Create Epic Issue (after spec creation)
# ============================================================================

issue_url = create_github_issue_from_epic(epic_id, epic_dir)
print(f"✅ Epic issue created: {issue_url}")

# ============================================================================
# STAGE 2: Update Status (when execution starts)
# ============================================================================

sync_status_to_github_simple(epic_id, "in-progress", epic_dir)
print(f"✅ Status updated to in-progress")

# ============================================================================
# STAGE 3: Create Sub-Issues for Parallel Work
# ============================================================================

metadata = get_issue_metadata(epic_dir / "task.md")
parent_number = metadata.issue_number

parallel_tasks = [
    SubIssueTask(
        name="Backend API Implementation",
        domain="backend",
        epic_id=epic_id,
        estimated_effort="MEDIUM"
    ),
    SubIssueTask(
        name="Frontend UI Components",
        domain="frontend",
        epic_id=epic_id,
        estimated_effort="LOW"
    )
]

sub_issues = create_sub_issues_for_parallel_work(
    parent_number, parallel_tasks, epic_dir
)
print(f"✅ Created {len(sub_issues)} sub-issues: {sub_issues}")

# ============================================================================
# STAGE 4: Post Progress Updates (during agent execution)
# ============================================================================

update = ProgressUpdate(
    epic_id=epic_id,
    phase="Phase 5A - Implementation",
    status="complete",
    agent_id="backend-specialist-v6",
    files_modified=8,
    details="Implemented semantic search endpoint with txtai integration",
    duration_minutes=45
)

post_progress_update(epic_id, update, epic_dir)
print(f"✅ Posted progress update")

# ============================================================================
# STAGE 5: Close Sub-Issues (after merge)
# ============================================================================

close_sub_issues(sub_issues, comment="✅ Merged and complete")
print(f"✅ Closed {len(sub_issues)} sub-issues")

# ============================================================================
# STAGE 6: Mark Epic as Complete
# ============================================================================

sync_status_to_github_simple(epic_id, "completed", epic_dir)
print(f"✅ Epic marked as completed")
```

## API Reference

### Core Sync Operations

#### `create_github_issue_from_epic(epic_id: str, epic_dir: Path) -> Optional[str]`

Create GitHub Issue from epic specification.

```python
from pathlib import Path
from tools.github_integration import create_github_issue_from_epic

epic_dir = Path(".tasks/backlog/EPIC-007")
url = create_github_issue_from_epic("EPIC-007", epic_dir)
```

**Returns:** Issue URL or None on failure
**Side Effects:** Creates issue, updates task.md with metadata

#### `sync_status_to_github_simple(epic_id: str, new_status: str, epic_dir: Path) -> None`

Update GitHub issue status labels.

```python
sync_status_to_github_simple("EPIC-007", "in-progress", epic_dir)
```

**Statuses:** `planned`, `in-progress`, `review`, `blocked`, `completed`

### Progress Reporting

#### `post_progress_update(epic_id: str, update: ProgressUpdate, epic_dir: Path) -> None`

Post agent progress as GitHub comment.

```python
from tools.github_integration import post_progress_update, ProgressUpdate

update = ProgressUpdate(
    epic_id="EPIC-007",
    phase="Phase 5A",
    status="complete",
    agent_id="agent-1",
    files_modified=5,
    details="Implementation complete"
)

post_progress_update("EPIC-007", update, epic_dir)
```

### Utility Functions

#### `get_project_root() -> Path`

Detect project root by traversing up from cwd looking for `.git` or `.tasks`.

```python
from tools.github_integration.utils import get_project_root

root = get_project_root()
print(root)  # /home/user/my-project
```

#### `find_epic_dir(epic_id: str) -> Path`

Find epic directory by ID, searching backlog/current/completed.

```python
from tools.github_integration.utils import find_epic_dir

epic_dir = find_epic_dir("EPIC-007")
print(epic_dir)  # /home/user/my-project/.tasks/backlog/EPIC-007
```

#### `find_task_file(task_id: str) -> Path`

Find task file by ID.

```python
from tools.github_integration.utils import find_task_file

task_file = find_task_file("FEATURE-001")
print(task_file)  # /home/user/my-project/.tasks/current/FEATURE-001.task.md
```

## Configuration

### Environment Variables (Optional)

```bash
# Optional: Set explicit repository (auto-detected otherwise)
export GITHUB_REPO="username/repo"
```

### Task Metadata Structure

The module reads/writes metadata in task.md frontmatter:

```yaml
---
epic_id: EPIC-007
title: "Implement Semantic Search"
status: in-progress
domain: backend
priority: high

github:
  issue_number: 123
  issue_url: "https://github.com/username/repo/issues/123"
  sync_enabled: true
  last_synced: "2025-10-13T10:30:00"
  sub_issues: [124, 125]
---
```

## Error Handling

All GitHub operations are **non-blocking**:

```python
# If GitHub API fails, workflow continues
url = create_github_issue_from_epic("EPIC-007", epic_dir)
if url is None:
    print("⚠️ GitHub sync failed - check logs")
    # Local files are unaffected, workflow continues
```

**Retry Queue:** Failed updates stored in `.github_sync_queue/` for later retry:

```python
from tools.github_integration import retry_failed_updates

# Retry failed updates
count = retry_failed_updates(epic_dir)
print(f"Retried {count} failed updates")
```

## Differences from Original

### What Changed

1. **Path detection:** Uses `get_project_root()` instead of hardcoded paths
2. **Repository detection:** Robust `get_repo_name()` with multiple fallbacks
3. **Utility functions:** New `utils.py` with `find_epic_dir()`, `find_task_file()`
4. **Generic examples:** All documentation uses generic project names
5. **Project-agnostic:** Works in ANY project with `.tasks/` structure

### What Stayed the Same

- **API:** All function signatures unchanged
- **Functionality:** All features preserved
- **Models:** Pydantic models unchanged
- **Non-blocking:** Error handling unchanged

## Troubleshooting

### "Could not detect repository name"

**Cause:** Not in a git repository or no GitHub remote configured

**Fix:**
```bash
# Option 1: Set default repo via gh CLI
gh repo set-default

# Option 2: Set environment variable
export GITHUB_REPO="username/repo"

# Option 3: Ensure git remote is configured
git remote -v
```

### "Epic EPIC-007 not found in .tasks/"

**Cause:** Epic directory doesn't exist or is named incorrectly

**Fix:**
```bash
# Check directory structure
ls -la .tasks/backlog/
ls -la .tasks/current/
ls -la .tasks/completed/

# Epic directory should start with epic_id
# Valid: EPIC-007/, EPIC-007-description/
# Invalid: epic-007/, 007/
```

### "No frontmatter found in task.md"

**Cause:** task.md missing YAML frontmatter

**Fix:**
```yaml
# task.md must start with:
---
epic_id: EPIC-007
title: "Epic Title"
status: planned
---

# Content here
```

## Testing

### Verify GitHub CLI

```bash
# Check authentication
gh auth status

# Test issue creation
gh issue create --title "Test Issue" --body "Testing" --label "test"
```

### Test Python Integration

```python
from tools.github_integration.gh_cli_wrapper import get_repo_name

# Should print "username/repo"
print(get_repo_name())
```

## File Structure

```
tools/github_integration/
├── __init__.py                 # Module exports
├── models.py                   # Pydantic data models
├── gh_cli_wrapper.py          # GitHub CLI wrapper (no tokens!)
├── issue_mapper.py            # Task <-> Issue conversion
├── issue_sync_gh.py           # Core sync operations
├── label_manager.py           # Label taxonomy
├── progress_reporter.py       # Progress updates
├── utils.py                   # Path detection utilities (NEW)
├── README.md                  # This file
└── GITHUB_CLI_USAGE.md       # CLI reference
```

## Dependencies

```bash
# Required
pip install pydantic pyyaml

# GitHub CLI (must be authenticated)
gh auth status
```

## Migration from Original

If migrating from email_management_system version:

1. **Update imports:**
   ```python
   # OLD
   from email_management_system.tools.github_integration import ...

   # NEW
   from tools.github_integration import ...
   ```

2. **Use utility functions:**
   ```python
   # OLD
   epic_dir = Path("/path/to/email_management_system/.tasks/backlog/EPIC-007")

   # NEW
   from tools.github_integration.utils import find_epic_dir
   epic_dir = find_epic_dir("EPIC-007")
   ```

3. **No other changes needed!** API is fully compatible.

## License

Same as parent project

## Version History

- **2.0.0** - Portable, project-agnostic version with robust path detection
- **1.0.0** - Original email_management_system version
