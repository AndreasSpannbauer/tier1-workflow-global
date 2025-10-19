# GitHub Integration Quick Start

**5-Minute Setup Guide**

## Prerequisites Check

```bash
# 1. Verify GitHub CLI is authenticated
gh auth status
# Expected: ✓ Logged in to github.com

# 2. Verify you're in a git repository
git remote -v
# Should show GitHub remote URL

# 3. Verify .tasks directory exists
ls -la .tasks/
# Should show: backlog/, current/, completed/
```

## Installation

**Copy this directory to your project:**

```bash
# From v6-tier1-template
cp -r tools/github_integration /path/to/your-project/tools/

# Install dependencies
pip install pydantic pyyaml
```

## Basic Usage

### 1. Create Epic Issue

```python
from pathlib import Path
from tools.github_integration import create_github_issue_from_epic

epic_dir = Path(".tasks/backlog/EPIC-007")
url = create_github_issue_from_epic("EPIC-007", epic_dir)
print(f"Created: {url}")
```

### 2. Update Status

```python
from tools.github_integration import sync_status_to_github_simple

sync_status_to_github_simple("EPIC-007", "in-progress", epic_dir)
```

### 3. Post Progress

```python
from tools.github_integration import post_progress_update, ProgressUpdate

update = ProgressUpdate(
    epic_id="EPIC-007",
    phase="Phase 5A",
    status="complete",
    agent_id="agent-1",
    details="Implementation complete"
)

post_progress_update("EPIC-007", update, epic_dir)
```

## With Auto-Detection

```python
from tools.github_integration import create_github_issue_from_epic
from tools.github_integration.utils import find_epic_dir

# Find epic automatically (searches backlog, current, completed)
epic_dir = find_epic_dir("EPIC-007")
url = create_github_issue_from_epic("EPIC-007", epic_dir)
```

## Directory Structure Required

Your epic directory should contain:

```
.tasks/backlog/EPIC-007/
├── task.md           # REQUIRED: Contains frontmatter with metadata
├── spec.md           # Recommended: Problem statement and requirements
├── architecture.md   # Optional: Services and components
└── analysis/
    └── impact_report.md  # Optional: Impact analysis
```

**Minimal task.md:**

```yaml
---
epic_id: EPIC-007
title: "Implement Semantic Search"
status: planned
domain: backend
priority: high
---

# Epic content here
```

## Troubleshooting

### "Could not detect repository name"

```bash
# Fix: Set default repo
gh repo set-default
```

### "Epic EPIC-007 not found"

```bash
# Fix: Check directory naming (must start with epic_id)
ls .tasks/backlog/
# Correct: EPIC-007/, EPIC-007-description/
# Wrong: epic-007/, 007/
```

### "No frontmatter found in task.md"

**Fix:** Add YAML frontmatter to task.md:

```yaml
---
epic_id: EPIC-007
title: "Epic Title"
status: planned
---
```

## Testing

```bash
# Run test suite
cd tools/github_integration
python3 test_portable_integration.py
```

## Next Steps

- Read full documentation: `README.md`
- View GitHub CLI reference: `GITHUB_CLI_USAGE.md`
- Check porting notes: `PORTING_NOTES.md`

## Common Patterns

### Create Issue + Sync Status

```python
from pathlib import Path
from tools.github_integration import (
    create_github_issue_from_epic,
    sync_status_to_github_simple
)

epic_dir = Path(".tasks/backlog/EPIC-007")

# Create issue
url = create_github_issue_from_epic("EPIC-007", epic_dir)

# Update status
sync_status_to_github_simple("EPIC-007", "in-progress", epic_dir)
```

### Create Sub-Issues

```python
from tools.github_integration import (
    get_issue_metadata,
    create_sub_issues_for_parallel_work,
    SubIssueTask
)

# Get parent issue number
metadata = get_issue_metadata(epic_dir / "task.md")

# Create sub-issues
tasks = [
    SubIssueTask(
        name="Backend Implementation",
        domain="backend",
        epic_id="EPIC-007",
        estimated_effort="MEDIUM"
    )
]

sub_issues = create_sub_issues_for_parallel_work(
    metadata.issue_number, tasks, epic_dir
)
```

### Retry Failed Updates

```python
from tools.github_integration import retry_failed_updates

# Retry any failed progress updates
count = retry_failed_updates(epic_dir)
print(f"Retried {count} updates")
```

## API Quick Reference

**Core Functions:**
- `create_github_issue_from_epic(epic_id, epic_dir)` - Create issue
- `sync_status_to_github_simple(epic_id, status, epic_dir)` - Update status
- `post_progress_update(epic_id, update, epic_dir)` - Post progress
- `get_issue_metadata(task_file)` - Get GitHub metadata

**Utilities:**
- `get_project_root()` - Find project root
- `find_epic_dir(epic_id)` - Find epic directory
- `find_task_file(task_id)` - Find task file

**Models:**
- `GitHubIssueMetadata` - GitHub sync metadata
- `ProgressUpdate` - Progress update data
- `SubIssueTask` - Sub-issue definition
- `IssueSummary` - Issue body data

## Success Criteria

✅ `gh auth status` shows authenticated
✅ `git remote -v` shows GitHub URL
✅ `.tasks/` directory exists
✅ Epic has `task.md` with YAML frontmatter
✅ Python imports work: `from tools.github_integration import create_github_issue_from_epic`

**You're ready to go!**
