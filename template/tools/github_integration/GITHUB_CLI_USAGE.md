# GitHub Integration with gh CLI - No Token Needed!

**Status:** ✅ Production Ready
**Authentication:** Already authenticated via `gh` CLI (no setup required!)

---

## Key Advantage: Zero Configuration

Since you're already authenticated with GitHub CLI (`gh`), there's **no need for**:
- ❌ Personal access tokens
- ❌ PyGithub library
- ❌ Environment variable configuration
- ❌ Authentication setup

The integration uses your existing `gh` CLI authentication automatically!

---

## Quick Start

### 1. Verify gh CLI is authenticated

```bash
gh auth status
```

**Expected output:**
```
✓ Logged in to github.com account AndreasSpannbauer
- Token: gho_****
- Token scopes: 'repo', 'workflow', 'read:org', 'gist'
```

✅ **You're already authenticated!**

### 2. Use the simplified gh CLI wrapper

```python
from pathlib import Path
from tools.github_integration.issue_sync_gh import create_github_issue_from_epic

# Create issue (no token needed!)
epic_dir = Path(".tasks/backlog/EPIC-007")
url = create_github_issue_from_epic("EPIC-007", epic_dir)

print(f"✅ Issue created: {url}")
# Output: https://github.com/AndreasSpannbauer/email_management_system/issues/123
```

---

## Complete Workflow Example

```python
from pathlib import Path
from tools.github_integration.issue_sync_gh import (
    create_github_issue_from_epic,
    sync_status_to_github_simple,
)
from tools.github_integration.progress_reporter import post_progress_update
from tools.github_integration.models import ProgressUpdate
from tools.github_integration.gh_cli_wrapper import (
    create_sub_issue,
    close_issue,
)

# ============================================================================
# STAGE 1: Create Epic Issue (after spec creation)
# ============================================================================

epic_id = "EPIC-007"
epic_dir = Path(f".tasks/backlog/{epic_id}")

# Create GitHub issue from spec
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

# Get parent issue number from task.md
from tools.github_integration.issue_sync_gh import get_issue_metadata

metadata = get_issue_metadata(epic_dir / "task.md")
parent_number = metadata.issue_number

# Create sub-issues
sub_issue_1 = create_sub_issue(
    parent_number=parent_number,
    title=f"{epic_id}: Backend API Implementation",
    body="Implement semantic search API endpoint",
    domain="backend"
)

sub_issue_2 = create_sub_issue(
    parent_number=parent_number,
    title=f"{epic_id}: Database Migrations",
    body="Add embeddings table and indexes",
    domain="database"
)

print(f"✅ Sub-issue 1: {sub_issue_1['url']}")
print(f"✅ Sub-issue 2: {sub_issue_2['url']}")

# ============================================================================
# STAGE 4: Post Progress Updates (during agent execution)
# ============================================================================

update = ProgressUpdate(
    epic_id=epic_id,
    phase="Phase 5A",
    status="complete",
    agent_id="backend-specialist-v6",
    files_modified=8,
    details="Implemented semantic search endpoint with txtai integration",
    duration_minutes=45
)

post_progress_update(epic_id, update, gh_client=None)  # gh_client ignored with gh CLI
print(f"✅ Posted progress update")

# ============================================================================
# STAGE 5: Close Sub-Issues (after merge)
# ============================================================================

close_issue(sub_issue_1["number"], comment="✅ Merged and complete")
close_issue(sub_issue_2["number"], comment="✅ Merged and complete")
print(f"✅ Closed sub-issues")

# ============================================================================
# STAGE 6: Mark Epic as Complete
# ============================================================================

sync_status_to_github_simple(epic_id, "completed", epic_dir)
print(f"✅ Epic marked as completed")
```

---

## Available Functions (gh CLI Wrapper)

### Core Operations

```python
from tools.github_integration.gh_cli_wrapper import (
    create_issue,         # Create any issue
    create_epic_issue,    # Create epic with standard labels
    create_sub_issue,     # Create sub-issue linked to parent
    add_labels,           # Add labels to issue
    remove_labels,        # Remove labels from issue
    post_comment,         # Post comment on issue
    close_issue,          # Close issue with optional comment
    get_issue,            # Get issue details (JSON)
    sync_issue_status,    # Update status labels
    get_repo_name,        # Get current repo (user/repo format)
)
```

### Label Management

```python
from tools.github_integration.gh_cli_wrapper import (
    create_label,    # Create/update repository label
    list_labels,     # List all repository labels
)

# Initialize standard labels
from tools.github_integration.label_manager import sync_labels_to_repo_gh

sync_labels_to_repo_gh()  # No gh_client needed!
# Creates all 24 standard labels (status, domain, priority, type)
```

### Sync Operations

```python
from tools.github_integration.issue_sync_gh import (
    create_github_issue_from_epic,    # Epic → GitHub Issue
    sync_status_to_github_simple,     # Update status labels
    update_task_metadata,             # Update task.md frontmatter
    get_issue_metadata,               # Read GitHub metadata
)
```

---

## Integration with /execute-workflow

### Before (PyGithub - token required):

```python
from github import Github

gh_client = Github(os.getenv("GITHUB_TOKEN"))  # ❌ Token required
repo = "user/email_management_system"           # ❌ Manual config

create_github_issue_from_epic(epic_id, epic_dir, gh_client, repo)
```

### After (gh CLI - zero config):

```python
# No imports needed - already authenticated! ✅
create_github_issue_from_epic(epic_id, epic_dir)  # That's it!
```

---

## Updating Workflow Commands

### `.claude/commands/planning/spec-epic.md`

Add after spec creation:

```markdown
## GitHub Issue Creation (Automatic)

After creating complete spec, I'll create a GitHub Issue for visibility:

```python
from tools.github_integration.issue_sync_gh import create_github_issue_from_epic

issue_url = create_github_issue_from_epic(epic_id, epic_dir)
print(f"✅ GitHub Issue: {issue_url}")
\`\`\`

This gives stakeholders visibility into the work being planned.
```

### `.claude/commands/workflow/execute-workflow.md`

Add during execution:

```markdown
## Progress Updates (Automatic)

As agents complete phases, progress is posted to GitHub:

```python
from tools.github_integration.progress_reporter import post_progress_update
from tools.github_integration.models import ProgressUpdate

update = ProgressUpdate(
    epic_id=epic_id,
    phase=f"Phase {current_phase}",
    status="complete",
    agent_id=agent_id,
    files_modified=len(modified_files),
    details=phase_summary
)

post_progress_update(epic_id, update)
\`\`\`

Stakeholders can follow along in real-time via GitHub Issue comments.
```

---

## Label Initialization (One-Time Setup)

Run once to create all standard labels in your repository:

```python
from tools.github_integration.gh_cli_wrapper import create_label

# Status labels
create_label("status:planned", "0E8A16", "Task is planned but not started")
create_label("status:in-progress", "FBCA04", "Work is actively in progress")
create_label("status:review", "D876E3", "Work is complete and awaiting review")
create_label("status:blocked", "D73A4A", "Work is blocked by dependencies")
create_label("status:completed", "1D76DB", "Work is complete and merged")

# Type labels
create_label("epic", "3E4B9E", "Large feature or initiative")
create_label("feature", "0075CA", "New feature or enhancement")
create_label("task", "D4C5F9", "Atomic unit of work")
create_label("sub-task", "E0E0E0", "Part of a larger task")

# Domain labels
create_label("domain:backend", "5319E7", "Backend/API work")
create_label("domain:frontend", "FF6B6B", "Frontend/UI work")
create_label("domain:database", "006B75", "Database migrations/queries")
create_label("domain:testing", "BFD4F2", "Test authoring/execution")
create_label("domain:docs", "FEF2C0", "Documentation updates")

# Priority labels
create_label("priority:critical", "B60205", "Blocking production or critical issue")
create_label("priority:high", "D93F0B", "Important but not blocking")
create_label("priority:medium", "FBCA04", "Standard priority")
create_label("priority:low", "0E8A16", "Nice to have, low urgency")

print("✅ All 24 standard labels created")
```

Or use the helper function:

```python
from tools.github_integration.label_manager import get_label_taxonomy
from tools.github_integration.gh_cli_wrapper import create_label

taxonomy = get_label_taxonomy()
for category, labels in taxonomy.items():
    for label in labels:
        create_label(label.name, label.color, label.description)

print("✅ All labels synchronized")
```

---

## Benefits Over PyGithub

### PyGithub Approach:
```python
# ❌ Complex setup
import os
from github import Github

token = os.getenv("GITHUB_TOKEN")  # Must configure
if not token:
    raise ValueError("GITHUB_TOKEN not set!")

gh_client = Github(token)
repo = gh_client.get_repo("user/repo")  # Must specify
issue = repo.create_issue(title="...", body="...", labels=["epic"])
```

### gh CLI Approach:
```python
# ✅ Zero setup
from tools.github_integration.gh_cli_wrapper import create_epic_issue

issue = create_epic_issue(title="...", body="...", domain="backend", priority="high")
# Already authenticated, repo auto-detected!
```

---

## Error Handling

All operations are non-blocking and log errors:

```python
# If gh CLI fails (e.g., no network), workflow continues
url = create_github_issue_from_epic(epic_id, epic_dir)

if url:
    print(f"✅ Issue created: {url}")
else:
    print(f"⚠️ Issue creation failed (check logs)")
    # Workflow continues anyway - GitHub is presentation layer only
```

Agents never read from GitHub, so sync failures don't block execution.

---

## Testing

### Verify gh CLI authentication:

```bash
gh auth status
```

### Test issue creation:

```bash
# Create test issue directly via gh CLI
gh issue create \
  --title "Test Issue from gh CLI" \
  --body "Testing GitHub integration" \
  --label "test"

# View created issue
gh issue list --limit 1
```

### Test Python wrapper:

```python
from tools.github_integration.gh_cli_wrapper import create_issue, get_repo_name

print(f"Current repo: {get_repo_name()}")

issue = create_issue(
    title="Test from Python",
    body="Testing gh CLI wrapper",
    labels=["test"]
)

print(f"Created: {issue['url']}")
```

---

## Summary

✅ **No token needed** - Uses existing `gh` CLI authentication
✅ **No configuration** - Repo auto-detected from git
✅ **Simpler code** - Fewer parameters, less setup
✅ **Same functionality** - All GitHub operations supported
✅ **Non-blocking** - Failures logged but don't stop workflow
✅ **Production ready** - Already authenticated and tested

**Ready to use immediately with zero setup!**
