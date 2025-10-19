# Parallel Progress Tracking Guide

GitHub integration for real-time parallel workflow progress reporting.

## Overview

The parallel progress reporter tracks multiple parallel agents simultaneously and posts real-time updates to GitHub issues as formatted progress tables.

**Key Features:**
- Multi-agent progress tracking with live status updates
- Beautiful progress table in GitHub issue comments
- Per-agent file counts and completion percentages
- Overall parallel execution progress
- Offline queue support (never blocks workflow)
- Non-blocking design (failures are warnings)

## How It Works

### 1. Initialization (Phase 1B)

When parallel execution starts, the reporter:

1. Reads `task.md` to get GitHub issue number
2. Creates tracking state for all parallel agents
3. Posts initial progress table to GitHub issue:

```markdown
## 🔄 Parallel Execution Progress

**Parallel execution initialized**

**Mode:** Parallel (3 domains)
**Started:** 2025-10-19 16:30:00

| Domain | Agent | Status | Files | Progress |
|--------|-------|--------|-------|----------|
| backend | impl-bac-163000 | ⏳ Pending | 0/0 | 0% |
| frontend | impl-fro-163000 | ⏳ Pending | 0/0 | 0% |
| tests | impl-tes-163000 | ⏳ Pending | 0/0 | 0% |

**Overall:** 0% (0/0 files)
```

### 2. Real-Time Updates (Phase 1C)

As agents execute, progress updates are posted:

```markdown
## 🔄 Parallel Execution Progress

**Agent impl-bac-163000 progress updated**

**Mode:** Parallel (3 domains)
**Started:** 2025-10-19 16:30:00

| Domain | Agent | Status | Files | Progress |
|--------|-------|--------|-------|----------|
| backend | impl-bac-163000 | 🔄 In Progress | 3/7 | 43% |
| frontend | impl-fro-163000 | ⏳ Pending | 0/5 | 0% |
| tests | impl-tes-163000 | ⏳ Pending | 0/4 | 0% |

**Overall:** 19% (3/16 files)
```

### 3. Completion Updates (Phase 1C)

When agents complete:

```markdown
## 🔄 Parallel Execution Progress

**Agent impl-bac-163000 completed**

**Mode:** Parallel (3 domains)
**Started:** 2025-10-19 16:30:00

| Domain | Agent | Status | Files | Progress |
|--------|-------|--------|-------|----------|
| backend | impl-bac-163000 | ✅ Completed | 7/7 | 100% |
| frontend | impl-fro-163000 | 🔄 In Progress | 3/5 | 60% |
| tests | impl-tes-163000 | ⏳ Pending | 0/4 | 0% |

**Overall:** 62% (10/16 files)
```

### 4. Final Summary (Phase 2)

After all agents complete and changes are merged:

```markdown
## 🔄 Parallel Execution Progress

**Parallel execution completed**

**Mode:** Parallel (3 domains)
**Started:** 2025-10-19 16:30:00

| Domain | Agent | Status | Files | Progress |
|--------|-------|--------|-------|----------|
| backend | impl-bac-163000 | ✅ Completed | 7/7 | 100% |
| frontend | impl-fro-163000 | ✅ Completed | 5/5 | 100% |
| tests | impl-tes-163000 | ✅ Completed | 4/4 | 100% |

**Overall:** 100% (16/16 files)

## 🎉 Final Summary

**Total Duration:** 12 minutes
**Total Files:** 16/16

### Merge Results

All parallel worktrees merged successfully.
- backend: 7 files integrated
- frontend: 5 files integrated
- tests: 4 files integrated

Conflict resolution: 0 conflicts
Integration tests: PASSED
```

## Integration with execute-workflow.md

### Phase 1B: Parallel Initialization

After creating worktrees and generating implementation plans:

```python
from tools.github_integration.parallel_progress_reporter import create_parallel_reporter

# Initialize parallel tracking
reporter = create_parallel_reporter(epic_dir)
domains = ["backend", "frontend", "tests"]
reporter.initialize_parallel_tracking(epic_id, domains, epic_dir)
```

### Phase 1C: Agent Execution Loop

During parallel agent execution:

```python
# Start agent execution
reporter.update_agent_progress(
    agent_id="agent-abc",
    status="in_progress",
    files_completed=0,
    files_total=7
)

# Update progress periodically
reporter.update_agent_progress(
    agent_id="agent-abc",
    status="in_progress",
    files_completed=3,
    files_total=7
)

# Mark complete on success
reporter.mark_agent_complete(
    agent_id="agent-abc",
    result_summary="Implemented all backend features"
)

# Or mark failed on error
reporter.mark_agent_failed(
    agent_id="agent-abc",
    error_message="Compilation error in main.py"
)
```

### Phase 2: Merge and Finalization

After merging all parallel worktrees:

```python
# Finalize execution
merge_summary = """
All parallel worktrees merged successfully.
- backend: 7 files integrated
- frontend: 5 files integrated
- tests: 4 files integrated

Conflict resolution: 0 conflicts
Integration tests: PASSED
"""

reporter.finalize_parallel_execution(merge_summary)
```

## Configuration

### GitHub Sync Settings

Progress reporting respects `task.md` frontmatter settings:

```yaml
---
github:
  issue_number: 123
  sync_enabled: true  # Set to false to disable progress updates
  last_synced: 2025-10-19T16:30:00
---
```

### Offline Queue

Failed GitHub updates are queued in `.github_parallel_queue/`:

```
.tasks/backlog/EPIC-007/
└── .github_parallel_queue/
    ├── comment_20251019_163045_123456.json
    └── comment_20251019_163047_234567.json
```

Queue files are automatically retried when `finalize_parallel_execution()` is called.

## Status Indicators

| Status | Emoji | Meaning |
|--------|-------|---------|
| pending | ⏳ | Agent not yet started |
| in_progress | 🔄 | Agent actively executing |
| completed | ✅ | Agent finished successfully |
| failed | ❌ | Agent encountered error |

## API Reference

### ParallelProgressReporter

```python
class ParallelProgressReporter:
    """Reporter for parallel workflow progress to GitHub Issues."""

    def __init__(self, metadata_dir: Optional[Path] = None):
        """Initialize reporter with optional metadata directory."""

    def initialize_parallel_tracking(
        self, epic_id: str, domains: List[str], epic_dir: Path
    ) -> None:
        """Initialize parallel execution tracking."""

    def update_agent_progress(
        self,
        agent_id: str,
        status: AgentStatus,
        files_completed: int,
        files_total: int,
    ) -> None:
        """Update progress for specific agent."""

    def mark_agent_complete(self, agent_id: str, result_summary: str) -> None:
        """Mark agent as completed."""

    def mark_agent_failed(self, agent_id: str, error_message: str) -> None:
        """Mark agent as failed."""

    def finalize_parallel_execution(self, merge_summary: str) -> None:
        """Finalize parallel execution after all agents complete."""
```

### Convenience Functions

```python
def create_parallel_reporter(epic_dir: Path) -> ParallelProgressReporter:
    """Create a parallel progress reporter for an epic."""
```

## Troubleshooting

### Issue: Progress updates not appearing on GitHub

**Check:**

1. Verify `issue_number` exists in `task.md`:
   ```bash
   head -20 .tasks/backlog/EPIC-007/task.md
   ```

2. Check sync is enabled:
   ```yaml
   github:
     sync_enabled: true
   ```

3. Verify GitHub CLI authentication:
   ```bash
   gh auth status
   ```

4. Check logs for errors:
   ```bash
   tail -100 .logs/workflow_execution.log | grep "parallel_progress"
   ```

### Issue: Offline queue growing

**Symptom:** Many `.json` files in `.github_parallel_queue/`

**Causes:**
- Network connectivity issues
- GitHub API rate limiting
- Authentication problems

**Solution:**
1. Fix underlying issue (network, auth, etc.)
2. Run `finalize_parallel_execution()` to retry queued updates
3. Or manually retry with `_retry_offline_queue()`

### Issue: Agent not showing in progress table

**Check:**

1. Verify agent was initialized:
   ```python
   print(reporter.execution_state.agents.keys())
   ```

2. Ensure agent ID matches:
   ```python
   # Agent IDs are auto-generated as: impl-{domain[:3]}-{timestamp}
   # Example: impl-bac-163000 for "backend"
   ```

3. Check domain was included in `initialize_parallel_tracking()` call

### Issue: Progress percentages incorrect

**Common causes:**
- `files_total` changed after initialization
- `files_completed` exceeds `files_total`

**Solution:** Update with correct totals:
```python
reporter.update_agent_progress(
    agent_id="agent-abc",
    status="in_progress",
    files_completed=3,
    files_total=10  # Updated total
)
```

## Offline Mode Behavior

The parallel progress reporter is **fully non-blocking**:

### Network Failure Handling

1. **Initialization failure:**
   - Warning logged
   - Workflow continues normally
   - No progress updates posted

2. **Update failure:**
   - Comment queued to `.github_parallel_queue/`
   - Warning logged
   - Workflow continues without delay

3. **Retry on finalization:**
   - All queued comments retried
   - Successfully posted updates removed from queue
   - Failed updates remain for manual retry

### Guaranteed Workflow Execution

**The workflow NEVER stops due to GitHub failures:**

- All exceptions caught and logged as warnings
- No blocking network calls
- Queue ensures updates are not lost
- Human can review queued updates manually

### Manual Queue Processing

If automatic retry fails, process queue manually:

```python
from pathlib import Path
from tools.github_integration.parallel_progress_reporter import ParallelProgressReporter

epic_dir = Path(".tasks/backlog/EPIC-007")
reporter = ParallelProgressReporter(metadata_dir=epic_dir / ".github_parallel_queue")
retry_count = reporter._retry_offline_queue()
print(f"Retried {retry_count} queued updates")
```

## Examples

### Basic Usage

```python
from pathlib import Path
from tools.github_integration.parallel_progress_reporter import create_parallel_reporter

# Setup
epic_dir = Path(".tasks/backlog/EPIC-007")
reporter = create_parallel_reporter(epic_dir)

# Initialize (Phase 1B)
domains = ["backend", "frontend", "tests"]
reporter.initialize_parallel_tracking("EPIC-007", domains, epic_dir)

# Execute agents (Phase 1C)
for agent_id, domain in zip(reporter.execution_state.agents.keys(), domains):
    # Start
    reporter.update_agent_progress(agent_id, "in_progress", 0, 5)

    # Progress
    for i in range(1, 6):
        # ... agent does work ...
        reporter.update_agent_progress(agent_id, "in_progress", i, 5)

    # Complete
    reporter.mark_agent_complete(agent_id, f"{domain.title()} implementation complete")

# Finalize (Phase 2)
reporter.finalize_parallel_execution("All changes merged successfully")
```

### Error Handling

```python
# Mark agent as failed
try:
    # ... agent execution ...
    raise Exception("Compilation error")
except Exception as e:
    reporter.mark_agent_failed(agent_id, str(e))
```

### Dynamic File Counts

```python
# Update file counts as they change
initial_files = scan_files_to_modify()
reporter.update_agent_progress(agent_id, "in_progress", 0, len(initial_files))

# Later, if more files discovered
additional_files = discover_more_files()
total_files = len(initial_files) + len(additional_files)
reporter.update_agent_progress(agent_id, "in_progress", 5, total_files)
```

## Best Practices

### 1. Initialize Early

Call `initialize_parallel_tracking()` **immediately after** creating worktrees, before starting agents.

### 2. Update Frequently

Update progress **at least** after each file is completed:
```python
for file in files:
    process_file(file)
    files_done += 1
    reporter.update_agent_progress(agent_id, "in_progress", files_done, total)
```

### 3. Accurate File Counts

Ensure `files_total` is accurate:
```python
# Good: Count files before starting
files = list(files_to_modify.glob("**/*.py"))
reporter.update_agent_progress(agent_id, "in_progress", 0, len(files))

# Bad: Hardcoded or guessed
reporter.update_agent_progress(agent_id, "in_progress", 0, 10)  # ❌
```

### 4. Always Finalize

Always call `finalize_parallel_execution()` even if agents failed:
```python
try:
    # ... parallel execution ...
    merge_summary = "Success"
except Exception as e:
    merge_summary = f"Failed: {e}"
finally:
    reporter.finalize_parallel_execution(merge_summary)
```

### 5. Check Sync Enabled

Respect user's sync settings:
```python
if not github_metadata.get("sync_enabled", True):
    # Skip GitHub integration
    return
```

## See Also

- **Sequential Progress:** `progress_reporter.py` for non-parallel workflows
- **GitHub Integration:** `gh_cli_wrapper.py` for GitHub CLI operations
- **Issue Sync:** `issue_sync_gh.py` for bidirectional sync
- **Workflow Execution:** `execute-workflow.md` Phases 1B, 1C, 2
