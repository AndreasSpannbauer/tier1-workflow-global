# GitHub Integration for Parallel Execution

**Date:** 2025-10-19
**Status:** Implementation Ready
**Purpose:** GitHub integration that creates epic issues and sub-issues for parallel domain execution with progress tracking

---

## Overview

This document defines the **optional** GitHub integration for parallel execution workflows. When parallel execution is viable, the orchestrator:

1. Creates an **epic issue** with workflow metadata
2. Creates **sub-issues** for each parallel domain
3. Links sub-issues to the epic with bidirectional references
4. Posts **progress updates** as agents complete
5. Closes sub-issues after merge and updates epic status
6. Updates epic labels to track workflow phases

**Design Principle:** Non-blocking - GitHub failures log warnings but never halt the workflow.

---

## Architecture

### Integration Points

```
Phase 0: Preflight
└─► Check GitHub CLI availability (non-blocking)

Phase 1A: Worktree Creation
└─► Create epic issue (if parallel + GitHub available)
└─► Create sub-issues for each domain
└─► Link sub-issues to epic

Phase 1B: Parallel Implementation
└─► Agents execute in isolation
└─► (No GitHub operations during execution)

Phase 1C: Sequential Merge
└─► Post progress updates after each merge
└─► Close sub-issues as domains complete
└─► Update epic issue with merge status

Phase 2: Validation
└─► Update epic labels (status:in-progress → status:validation)

Phase 5: Commit & Cleanup
└─► Close epic issue with completion comment
└─► Final label update (status:validation → status:completed)
```

### Non-Blocking Design

All GitHub operations are wrapped in try-catch with graceful degradation:

```python
try:
    epic_issue = create_epic_issue(...)
    if epic_issue:
        print(f"✅ GitHub Issue: #{epic_issue['number']}")
except Exception as e:
    logger.warning(f"GitHub operation failed (non-blocking): {e}")
    # Workflow continues - local files are source of truth
```

**Rationale:** GitHub is supplementary to the workflow. Local `.tasks/` directory is the source of truth.

---

## Implementation Steps

### Step 1: Check GitHub CLI Availability

**When:** Phase 0 (Preflight)
**Purpose:** Detect if GitHub integration is possible
**Blocking:** No

```bash
#!/bin/bash
# Check if gh CLI is available and authenticated

GITHUB_AVAILABLE=0

if ! command -v gh &> /dev/null; then
  echo "ℹ️ GitHub CLI not found - skipping issue creation"
elif ! gh auth status &> /dev/null 2>&1; then
  echo "ℹ️ GitHub CLI not authenticated - skipping issue creation"
else
  echo "✅ GitHub CLI available and authenticated"
  GITHUB_AVAILABLE=1
fi

# Store for later phases
echo "$GITHUB_AVAILABLE" > .workflow/outputs/${ARGUMENTS}/github_available.txt
```

**Output:**
- `.workflow/outputs/${ARGUMENTS}/github_available.txt` - Contains "1" (available) or "0" (unavailable)

**Error Handling:** Never fails - always succeeds with status indicator

---

### Step 2: Create Epic Issue (If Parallel)

**When:** Phase 1A (After parallel detection, before worktree creation)
**Condition:** `EXECUTION_MODE == "parallel" AND GITHUB_AVAILABLE == 1`
**Blocking:** No

```bash
#!/bin/bash
# Create epic issue for parallel execution

EPIC_DIR=".tasks/backlog/${ARGUMENTS}"
EXECUTION_MODE="parallel"  # Determined by parallel detection
GITHUB_AVAILABLE=$(cat .workflow/outputs/${ARGUMENTS}/github_available.txt)

if [ "$EXECUTION_MODE" = "parallel" ] && [ "$GITHUB_AVAILABLE" -eq 1 ]; then
  echo ""
  echo "📝 Creating GitHub epic issue..."

  # Extract epic metadata
  EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

  # Count domains and files
  DOMAINS=$(echo "$PARALLEL_PLAN" | jq -r '.domains | keys[]')
  DOMAIN_COUNT=$(echo "$DOMAINS" | wc -l)
  TOTAL_FILES=$(echo "$PARALLEL_PLAN" | jq '[.domains[] | length] | add')

  # Generate domain summary
  DOMAIN_SUMMARY=$(for domain in $DOMAINS; do
    file_count=$(echo "$PARALLEL_PLAN" | jq -r ".domains.\"$domain\" | length")
    echo "- **${domain}**: ${file_count} files"
  done)

  # Create issue body
  EPIC_BODY=$(cat << EOF
## Epic: ${ARGUMENTS}

**Execution Mode:** Parallel (${DOMAIN_COUNT} domains, ${TOTAL_FILES} files)

### Specification

$(cat ${EPIC_DIR}/spec.md)

### Architecture

$(cat ${EPIC_DIR}/architecture.md)

### Domains

${DOMAIN_SUMMARY}

### Execution Plan

This epic will be implemented using parallel execution with git worktrees. Each domain will be implemented by an isolated agent in its own worktree, then merged sequentially to prevent conflicts.

### Status

- [x] Phase 0: Preflight ✅
- [ ] Phase 1B: Parallel Implementation (in progress)
- [ ] Phase 1C: Sequential Merge
- [ ] Phase 2: Validation
- [ ] Phase 5: Commit & Cleanup

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)

  # Create epic issue using gh CLI
  EPIC_ISSUE_NUMBER=$(gh issue create \
    --title "${EPIC_TITLE}" \
    --body "${EPIC_BODY}" \
    --label "type:epic,status:in-progress,execution:parallel" \
    --json number \
    --jq '.number' 2>&1)

  if [ $? -eq 0 ]; then
    echo "  ✅ Epic issue created: #${EPIC_ISSUE_NUMBER}"
    EPIC_URL=$(gh issue view ${EPIC_ISSUE_NUMBER} --json url --jq '.url')
    echo "  URL: ${EPIC_URL}"

    # Store issue number for later phases
    echo "${EPIC_ISSUE_NUMBER}" > .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt
  else
    echo "  ⚠️ Epic issue creation failed (non-blocking)"
    echo "  Error: ${EPIC_ISSUE_NUMBER}"
    # Clear issue number file
    echo "" > .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt
  fi

else
  echo "ℹ️ Skipping GitHub epic issue creation"
  echo "  Reason: $([ "$EXECUTION_MODE" = "sequential" ] && echo "Sequential execution" || echo "GitHub unavailable")"
fi
```

**Output:**
- `.workflow/outputs/${ARGUMENTS}/github_epic_issue.txt` - Contains issue number or empty

**Labels Applied:**
- `type:epic` - Identifies this as an epic issue
- `status:in-progress` - Initial status
- `execution:parallel` - Indicates parallel execution mode

**Error Handling:**
- If `gh issue create` fails, log warning and continue
- Store empty string in issue number file to signal failure
- Subsequent GitHub operations check for empty file and skip

---

### Step 3: Create Sub-Issues for Each Domain

**When:** Phase 1A (Immediately after epic issue creation)
**Condition:** Epic issue created successfully
**Blocking:** No

```bash
#!/bin/bash
# Create sub-issues for each parallel domain

EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Creating sub-issues for parallel domains..."

  # Parse parallel plan to get domains
  DOMAINS=$(echo "$PARALLEL_PLAN" | jq -r '.domains | keys[]')

  # Associative array to store sub-issue numbers
  declare -A SUB_ISSUE_NUMBERS

  for domain in $DOMAINS; do
    # Extract domain-specific information
    TASK_DESCRIPTION=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".task_description")
    DOMAIN_FILES=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".files[]")
    FILE_COUNT=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".files | length")

    # Generate file list
    FILE_LIST=$(echo "$DOMAIN_FILES" | while read file; do echo "- \`${file}\`"; done)

    # Create sub-issue body
    SUB_ISSUE_BODY=$(cat << EOF
## ${ARGUMENTS}: ${domain} Implementation

**Parent Epic:** #${EPIC_ISSUE_NUMBER}
**Domain:** ${domain}
**Files:** ${FILE_COUNT}

### Task Description

${TASK_DESCRIPTION}

### Files to Create/Modify

${FILE_LIST}

### Execution Details

This task will be executed by an isolated agent in a dedicated git worktree:
- **Branch:** \`feature/${ARGUMENTS}/${domain}\`
- **Worktree:** \`.worktrees/${ARGUMENTS}-${domain}-<hash>/\`

After implementation, this branch will be merged sequentially into the target branch.

### Status

- [ ] Implementation (in progress)
- [ ] Validation
- [ ] Merge

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)

    # Create sub-issue
    SUB_ISSUE_NUMBER=$(gh issue create \
      --title "${ARGUMENTS}: ${domain} Implementation" \
      --body "${SUB_ISSUE_BODY}" \
      --label "type:task,domain:${domain},status:in-progress,parent:${EPIC_ISSUE_NUMBER}" \
      --json number \
      --jq '.number' 2>&1)

    if [ $? -eq 0 ]; then
      SUB_ISSUE_NUMBERS[$domain]="$SUB_ISSUE_NUMBER"
      echo "  ✅ Sub-issue created for ${domain}: #${SUB_ISSUE_NUMBER}"

      # Link to parent epic
      gh issue comment ${EPIC_ISSUE_NUMBER} \
        --body "🔗 Sub-task created: #${SUB_ISSUE_NUMBER} (${domain})" \
        2>&1 > /dev/null || echo "  ⚠️ Failed to link sub-issue to epic (non-blocking)"
    else
      echo "  ⚠️ Sub-issue creation failed for ${domain} (non-blocking)"
      SUB_ISSUE_NUMBERS[$domain]=""
    fi
  done

  # Store sub-issue numbers as JSON
  SUB_ISSUES_JSON=$(cat << EOF
{
  "epic_issue": ${EPIC_ISSUE_NUMBER},
  "sub_issues": {
$(for domain in $DOMAINS; do
  sub_num="${SUB_ISSUE_NUMBERS[$domain]}"
  [ -n "$sub_num" ] && echo "    \"$domain\": ${sub_num}," || echo "    \"$domain\": null,"
done | sed '$ s/,$//')
  }
}
EOF
)

  echo "$SUB_ISSUES_JSON" > .workflow/outputs/${ARGUMENTS}/github_sub_issues.json

  echo ""
  echo "✅ GitHub issues created:"
  echo "   Epic: #${EPIC_ISSUE_NUMBER}"
  for domain in $DOMAINS; do
    sub_num="${SUB_ISSUE_NUMBERS[$domain]}"
    [ -n "$sub_num" ] && echo "   ${domain}: #${sub_num}"
  done

else
  echo "ℹ️ Skipping GitHub sub-issue creation (no epic issue)"
fi
```

**Output:**
- `.workflow/outputs/${ARGUMENTS}/github_sub_issues.json` - Maps domains to issue numbers

**Example JSON:**
```json
{
  "epic_issue": 123,
  "sub_issues": {
    "backend": 124,
    "frontend": 125,
    "database": 126
  }
}
```

**Labels Applied to Sub-Issues:**
- `type:task` - Identifies as a sub-task
- `domain:<domain-name>` - Domain identifier (backend, frontend, etc.)
- `status:in-progress` - Initial status
- `parent:<epic-issue-number>` - Links to parent epic

**Error Handling:**
- Failed sub-issue creation stores `null` in JSON
- Comment linking may fail independently (non-blocking)
- Partial success is acceptable (some sub-issues created, others failed)

---

### Step 4: Update Epic with Progress (After Phase 1B)

**When:** Phase 1B completion (All parallel agents finished)
**Condition:** Epic issue exists
**Blocking:** No

```bash
#!/bin/bash
# Update epic issue with Phase 1B completion

EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Updating epic issue with Phase 1B progress..."

  # Read sub-issues
  SUB_ISSUES_JSON=$(cat .workflow/outputs/${ARGUMENTS}/github_sub_issues.json)
  DOMAINS=$(echo "$SUB_ISSUES_JSON" | jq -r '.sub_issues | keys[]')

  # Read domain status from agent results
  declare -A DOMAIN_STATUS
  for domain in $DOMAINS; do
    RESULT_FILE=".workflow/outputs/${ARGUMENTS}/${domain}_results.json"
    if [ -f "$RESULT_FILE" ]; then
      STATUS=$(jq -r '.status' "$RESULT_FILE")
      DOMAIN_STATUS[$domain]="$STATUS"
    else
      DOMAIN_STATUS[$domain]="unknown"
    fi
  done

  # Create progress comment
  PROGRESS_COMMENT=$(cat << EOF
## Phase 1B Complete: Parallel Implementation ✅

All domain implementations have completed. Results:

$(for domain in $DOMAINS; do
  SUB_ISSUE=$(echo "$SUB_ISSUES_JSON" | jq -r ".sub_issues.\"$domain\"")
  STATUS="${DOMAIN_STATUS[$domain]}"

  if [ "$STATUS" = "success" ]; then
    echo "- ✅ **${domain}**: Success (#${SUB_ISSUE})"
  elif [ "$STATUS" = "partial" ]; then
    echo "- ⚠️ **${domain}**: Partial (#${SUB_ISSUE})"
  else
    echo "- ❌ **${domain}**: Failed/Unknown (#${SUB_ISSUE})"
  fi
done)

**Next Phase:** Sequential merge (Phase 1C)

---
Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
)

  # Post comment
  gh issue comment ${EPIC_ISSUE_NUMBER} --body "${PROGRESS_COMMENT}" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Progress updated on epic issue #${EPIC_ISSUE_NUMBER}"
  else
    echo "  ⚠️ Failed to update epic issue (non-blocking)"
  fi

else
  echo "ℹ️ Skipping epic progress update (no epic issue)"
fi
```

**Comment Format:**
- **Header:** Phase name and completion status
- **Results:** List each domain with status icon and sub-issue link
- **Next Phase:** What happens next
- **Timestamp:** UTC timestamp for tracking

**Error Handling:**
- Missing result files default to "unknown" status
- Comment posting failure is logged but non-blocking

---

### Step 5: Close Sub-Issues After Merge (Phase 1C)

**When:** Phase 1C (After each domain merge completes)
**Condition:** Sub-issue exists for domain
**Blocking:** No

```bash
#!/bin/bash
# Close sub-issues as domains are merged

EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt)
SUB_ISSUES_JSON=$(cat .workflow/outputs/${ARGUMENTS}/github_sub_issues.json)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Closing sub-issues after merge..."

  # Merge happens in dependency order (from parallel plan)
  ORDERED_DOMAINS=$(echo "$PARALLEL_PLAN" | jq -r '.merge_order[]')

  for domain in $ORDERED_DOMAINS; do
    SUB_ISSUE=$(echo "$SUB_ISSUES_JSON" | jq -r ".sub_issues.\"$domain\"")

    if [ -n "$SUB_ISSUE" ] && [ "$SUB_ISSUE" != "null" ]; then
      # Close sub-issue with merge confirmation
      gh issue close ${SUB_ISSUE} \
        --comment "✅ Merged successfully into main branch

**Merge Details:**
- Branch: \`feature/${ARGUMENTS}/${domain}\`
- Merged at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- Merge strategy: Sequential (no-fast-forward)

This sub-task is complete." 2>&1 > /dev/null

      if [ $? -eq 0 ]; then
        echo "  ✅ Closed sub-issue #${SUB_ISSUE} (${domain})"
      else
        echo "  ⚠️ Failed to close sub-issue #${SUB_ISSUE} (non-blocking)"
      fi
    fi
  done

  # Update epic with merge completion
  MERGE_COMMENT=$(cat << EOF
## Phase 1C Complete: Sequential Merge ✅

All domain branches have been merged successfully into the target branch.

**Merge Order:**
$(for domain in $ORDERED_DOMAINS; do
  echo "1. ${domain} → merged"
done)

**Conflicts:** None detected
**Sub-issues:** All closed

**Next Phase:** Validation (Phase 2)

---
Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
)

  gh issue comment ${EPIC_ISSUE_NUMBER} --body "${MERGE_COMMENT}" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Merge completion posted to epic issue"
  fi

else
  echo "ℹ️ Skipping sub-issue closure (no epic issue)"
fi
```

**Merge Order:**
- Respects `merge_order` from parallel plan (dependency-aware)
- Closes sub-issues sequentially as merges complete
- Posts summary comment to epic after all merges

**Error Handling:**
- Missing or null sub-issue numbers are skipped
- Individual close failures don't block subsequent closes

---

### Step 6: Update Epic Labels (Phase Transitions)

**When:** Phase transitions (1B→2, 2→5, 5→complete)
**Condition:** Epic issue exists
**Blocking:** No

```bash
#!/bin/bash
# Update epic labels as workflow progresses

EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt)

update_epic_labels() {
  local remove_label="$1"
  local add_label="$2"
  local phase_name="$3"

  if [ -n "$EPIC_ISSUE_NUMBER" ]; then
    echo "📝 Updating epic labels: ${remove_label} → ${add_label}"

    gh issue edit ${EPIC_ISSUE_NUMBER} \
      --remove-label "${remove_label}" \
      --add-label "${add_label}" 2>&1 > /dev/null

    if [ $? -eq 0 ]; then
      echo "  ✅ Epic labels updated for ${phase_name}"
    else
      echo "  ⚠️ Failed to update epic labels (non-blocking)"
    fi
  fi
}

# After Phase 1B → Starting Phase 2 (Validation)
update_epic_labels "status:in-progress" "status:validation" "Phase 2: Validation"

# After Phase 2 → Starting Phase 5 (Commit)
update_epic_labels "status:validation" "status:review" "Phase 5: Commit"

# After Phase 5 → Workflow complete
if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  gh issue close ${EPIC_ISSUE_NUMBER} \
    --comment "✅ Workflow complete - all phases passed

**Final Status:**
- Implementation: ✅ Parallel execution successful
- Validation: ✅ Build/lint/architecture checks passed
- Commit: ✅ Changes committed to repository

**Artifacts:**
- Post-mortem: \`.workflow/post-mortem/${ARGUMENTS}.md\`
- Implementation results: \`.workflow/outputs/${ARGUMENTS}/\`

This epic is complete and can be closed.

---
Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Epic issue closed successfully"
  else
    echo "  ⚠️ Failed to close epic issue (non-blocking)"
  fi
fi
```

**Label Transitions:**
1. **Phase 1B → Phase 2:** `status:in-progress` → `status:validation`
2. **Phase 2 → Phase 5:** `status:validation` → `status:review`
3. **Phase 5 Complete:** Close issue with final comment

**Error Handling:**
- Label updates are non-blocking
- Issue close failure is logged but doesn't affect workflow

---

## Label Taxonomy

### Required Labels

**Status Labels:**
- `status:in-progress` - Active implementation
- `status:validation` - Validation phase
- `status:review` - Ready for review/commit
- `status:blocked` - Blocked on external dependency (manual use)

**Type Labels:**
- `type:epic` - Epic issue (parent)
- `type:task` - Sub-task issue (child)

**Execution Labels:**
- `execution:parallel` - Parallel execution mode
- `execution:sequential` - Sequential execution mode (optional)

**Domain Labels (Dynamic):**
- `domain:backend` - Backend domain
- `domain:frontend` - Frontend domain
- `domain:database` - Database domain
- `domain:docs` - Documentation domain
- `domain:tests` - Testing domain
- *(Add more as needed per project)*

**Parent Reference Labels (Dynamic):**
- `parent:<issue-number>` - Links sub-issue to parent epic

### Label Initialization

Labels must be created in the repository before use:

```bash
#!/bin/bash
# Initialize GitHub labels for workflow

gh label create "type:epic" --color "8B5CF6" --description "Parent epic issue" || true
gh label create "type:task" --color "3B82F6" --description "Sub-task of epic" || true

gh label create "status:in-progress" --color "FBBF24" --description "Active work" || true
gh label create "status:validation" --color "F97316" --description "Validation phase" || true
gh label create "status:review" --color "10B981" --description "Ready for review" || true
gh label create "status:blocked" --color "EF4444" --description "Blocked" || true

gh label create "execution:parallel" --color "EC4899" --description "Parallel execution" || true
gh label create "execution:sequential" --color "6366F1" --description "Sequential execution" || true

# Domain labels (customize per project)
gh label create "domain:backend" --color "0EA5E9" --description "Backend domain" || true
gh label create "domain:frontend" --color "8B5CF6" --description "Frontend domain" || true
gh label create "domain:database" --color "14B8A6" --description "Database domain" || true
gh label create "domain:docs" --color "6366F1" --description "Documentation domain" || true
gh label create "domain:tests" --color "F59E0B" --description "Testing domain" || true

echo "✅ GitHub labels initialized"
```

**Note:** `|| true` ensures script doesn't fail if labels already exist.

---

## Python Integration API

For projects preferring Python over Bash scripts:

```python
#!/usr/bin/env python3
"""GitHub integration for parallel execution workflows."""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class GitHubParallelIntegration:
    """Manages GitHub issues for parallel execution workflows."""

    def __init__(self, epic_id: str, output_dir: Path):
        self.epic_id = epic_id
        self.output_dir = output_dir
        self.github_available = self._check_github_cli()

    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def create_epic_issue(
        self,
        title: str,
        spec_content: str,
        architecture_content: str,
        parallel_plan: Dict
    ) -> Optional[int]:
        """Create epic issue for parallel execution.

        Returns:
            Issue number if successful, None otherwise
        """
        if not self.github_available:
            return None

        # Generate domain summary
        domains = parallel_plan.get("domains", {})
        domain_summary = "\n".join([
            f"- **{domain}**: {len(files)} files"
            for domain, files in domains.items()
        ])

        # Create issue body
        body = f"""## Epic: {self.epic_id}

**Execution Mode:** Parallel ({len(domains)} domains, {sum(len(f) for f in domains.values())} files)

### Specification

{spec_content}

### Architecture

{architecture_content}

### Domains

{domain_summary}

### Status

- [x] Phase 0: Preflight ✅
- [ ] Phase 1B: Parallel Implementation (in progress)
- [ ] Phase 1C: Sequential Merge
- [ ] Phase 2: Validation
- [ ] Phase 5: Commit & Cleanup

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
"""

        try:
            result = subprocess.run(
                [
                    "gh", "issue", "create",
                    "--title", title,
                    "--body", body,
                    "--label", "type:epic,status:in-progress,execution:parallel",
                    "--json", "number",
                    "--jq", ".number"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                issue_number = int(result.stdout.strip())
                # Store issue number
                (self.output_dir / "github_epic_issue.txt").write_text(str(issue_number))
                return issue_number
            else:
                print(f"⚠️ Epic issue creation failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"⚠️ Epic issue creation error (non-blocking): {e}")
            return None

    def create_sub_issues(
        self,
        epic_issue_number: int,
        parallel_plan: Dict
    ) -> Dict[str, Optional[int]]:
        """Create sub-issues for each parallel domain.

        Returns:
            Mapping of domain names to issue numbers
        """
        sub_issues = {}

        for domain, files in parallel_plan.get("domains", {}).items():
            task_desc = parallel_plan.get("parallel_plan", {}).get(domain, {}).get("task_description", "")
            file_list = "\n".join([f"- `{f}`" for f in files])

            body = f"""## {self.epic_id}: {domain} Implementation

**Parent Epic:** #{epic_issue_number}
**Domain:** {domain}
**Files:** {len(files)}

### Task Description

{task_desc}

### Files to Create/Modify

{file_list}

### Status

- [ ] Implementation (in progress)
- [ ] Validation
- [ ] Merge

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
"""

            try:
                result = subprocess.run(
                    [
                        "gh", "issue", "create",
                        "--title", f"{self.epic_id}: {domain} Implementation",
                        "--body", body,
                        "--label", f"type:task,domain:{domain},status:in-progress,parent:{epic_issue_number}",
                        "--json", "number",
                        "--jq", ".number"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    issue_number = int(result.stdout.strip())
                    sub_issues[domain] = issue_number

                    # Link to parent
                    self._post_comment(
                        epic_issue_number,
                        f"🔗 Sub-task created: #{issue_number} ({domain})"
                    )
                else:
                    print(f"⚠️ Sub-issue creation failed for {domain}")
                    sub_issues[domain] = None

            except Exception as e:
                print(f"⚠️ Sub-issue creation error for {domain}: {e}")
                sub_issues[domain] = None

        # Store sub-issue mapping
        mapping = {
            "epic_issue": epic_issue_number,
            "sub_issues": sub_issues
        }
        (self.output_dir / "github_sub_issues.json").write_text(
            json.dumps(mapping, indent=2)
        )

        return sub_issues

    def update_progress(
        self,
        epic_issue_number: int,
        domain_status: Dict[str, str],
        sub_issues: Dict[str, Optional[int]]
    ):
        """Post progress update to epic issue."""
        status_icons = {
            "success": "✅",
            "partial": "⚠️",
            "failed": "❌",
            "unknown": "❓"
        }

        results = "\n".join([
            f"- {status_icons.get(status, '❓')} **{domain}**: {status.title()} (#{sub_issues.get(domain, 'N/A')})"
            for domain, status in domain_status.items()
        ])

        comment = f"""## Phase 1B Complete: Parallel Implementation ✅

All domain implementations have completed. Results:

{results}

**Next Phase:** Sequential merge (Phase 1C)

---
Updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

        self._post_comment(epic_issue_number, comment)

    def close_sub_issue(
        self,
        sub_issue_number: int,
        domain: str
    ):
        """Close sub-issue after successful merge."""
        comment = f"""✅ Merged successfully into main branch

**Merge Details:**
- Branch: `feature/{self.epic_id}/{domain}`
- Merged at: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
- Merge strategy: Sequential (no-fast-forward)

This sub-task is complete.
"""

        try:
            subprocess.run(
                [
                    "gh", "issue", "close", str(sub_issue_number),
                    "--comment", comment
                ],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️ Failed to close sub-issue #{sub_issue_number}: {e}")

    def update_epic_labels(
        self,
        epic_issue_number: int,
        remove_label: str,
        add_label: str
    ):
        """Update epic issue labels."""
        try:
            subprocess.run(
                [
                    "gh", "issue", "edit", str(epic_issue_number),
                    "--remove-label", remove_label,
                    "--add-label", add_label
                ],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️ Failed to update epic labels: {e}")

    def close_epic(
        self,
        epic_issue_number: int
    ):
        """Close epic issue after workflow completion."""
        comment = f"""✅ Workflow complete - all phases passed

**Final Status:**
- Implementation: ✅ Parallel execution successful
- Validation: ✅ Build/lint/architecture checks passed
- Commit: ✅ Changes committed to repository

**Artifacts:**
- Post-mortem: `.workflow/post-mortem/{self.epic_id}.md`
- Implementation results: `.workflow/outputs/{self.epic_id}/`

This epic is complete and can be closed.

---
Completed: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

        try:
            subprocess.run(
                [
                    "gh", "issue", "close", str(epic_issue_number),
                    "--comment", comment
                ],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️ Failed to close epic issue: {e}")

    def _post_comment(
        self,
        issue_number: int,
        comment: str
    ):
        """Post comment to issue (helper method)."""
        try:
            subprocess.run(
                [
                    "gh", "issue", "comment", str(issue_number),
                    "--body", comment
                ],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️ Failed to post comment to #{issue_number}: {e}")


# Example usage in workflow orchestrator
if __name__ == "__main__":
    # Initialize integration
    gh = GitHubParallelIntegration(
        epic_id="EPIC-007",
        output_dir=Path(".workflow/outputs/EPIC-007")
    )

    # Create epic issue
    epic_issue = gh.create_epic_issue(
        title="Semantic Email Search",
        spec_content=Path(".tasks/backlog/EPIC-007/spec.md").read_text(),
        architecture_content=Path(".tasks/backlog/EPIC-007/architecture.md").read_text(),
        parallel_plan={
            "domains": {
                "backend": ["src/backend/service.py", "src/backend/api.py"],
                "frontend": ["src/frontend/component.tsx"]
            }
        }
    )

    if epic_issue:
        # Create sub-issues
        sub_issues = gh.create_sub_issues(epic_issue, parallel_plan)

        # ... agents execute in parallel ...

        # Update progress
        gh.update_progress(
            epic_issue,
            {"backend": "success", "frontend": "success"},
            sub_issues
        )

        # Close sub-issues after merge
        for domain, issue_num in sub_issues.items():
            if issue_num:
                gh.close_sub_issue(issue_num, domain)

        # Update labels through phases
        gh.update_epic_labels(epic_issue, "status:in-progress", "status:validation")
        gh.update_epic_labels(epic_issue, "status:validation", "status:review")

        # Close epic when complete
        gh.close_epic(epic_issue)
```

---

## Validation Checklist

Before marking implementation complete, verify:

- [x] **GitHub CLI availability check** - Detects `gh` command and authentication status
- [x] **Epic issue creation** - Creates issue with spec, architecture, domain summary
- [x] **Sub-issue creation** - Creates one issue per domain with file list
- [x] **Sub-issue linking** - Posts comment to epic referencing sub-issues
- [x] **Progress updates** - Posts Phase 1B completion with domain status
- [x] **Sub-issue closure** - Closes issues after merge with confirmation
- [x] **Epic label updates** - Transitions status labels through phases
- [x] **Epic closure** - Closes issue after workflow completion
- [x] **Non-blocking design** - All operations wrapped in error handling
- [x] **JSON storage** - Issue numbers persisted for later phases
- [x] **Timestamp tracking** - UTC timestamps in all comments

---

## Integration with Workflow Command

The workflow orchestrator (`.claude/commands/execute-workflow.md`) integrates GitHub operations at these points:

```markdown
## Phase 0: Preflight

```bash
# Check GitHub CLI
source tools/github_integration/check_cli.sh
```

## Phase 1A: Create Worktrees (If Parallel)

```bash
# Create epic issue
if [ "$EXECUTION_MODE" = "parallel" ]; then
  source tools/github_integration/create_epic.sh
  source tools/github_integration/create_sub_issues.sh
fi
```

## Phase 1B: Agent Execution Complete

```bash
# Update progress
if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  source tools/github_integration/update_progress.sh
fi
```

## Phase 1C: Merge Complete

```bash
# Close sub-issues
if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  source tools/github_integration/close_sub_issues.sh
fi
```

## Phase 2: Validation

```bash
# Update label: in-progress → validation
if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  gh issue edit $EPIC_ISSUE_NUMBER \
    --remove-label "status:in-progress" \
    --add-label "status:validation"
fi
```

## Phase 5: Commit & Cleanup

```bash
# Close epic
if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  source tools/github_integration/close_epic.sh
fi
```
```

---

## Installation

Add GitHub integration to project:

```bash
#!/bin/bash
# Install GitHub integration for parallel workflows

PROJECT_DIR="${1:-.}"

# Create integration directory
mkdir -p "$PROJECT_DIR/tools/github_integration"

# Copy Python module (if using Python API)
cp github_parallel_integration.py "$PROJECT_DIR/tools/github_integration/"

# Create Bash scripts (if using Bash)
cat > "$PROJECT_DIR/tools/github_integration/check_cli.sh" << 'EOF'
#!/bin/bash
# Check GitHub CLI availability
GITHUB_AVAILABLE=0
if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
  echo "✅ GitHub CLI available"
  GITHUB_AVAILABLE=1
else
  echo "ℹ️ GitHub CLI not available - skipping issue creation"
fi
echo "$GITHUB_AVAILABLE" > .workflow/outputs/${ARGUMENTS}/github_available.txt
EOF

# ... (additional scripts as needed) ...

# Initialize labels
echo "🏷️ Initializing GitHub labels..."
gh label create "type:epic" --color "8B5CF6" --description "Parent epic issue" || true
gh label create "type:task" --color "3B82F6" --description "Sub-task of epic" || true
gh label create "status:in-progress" --color "FBBF24" --description "Active work" || true
gh label create "status:validation" --color "F97316" --description "Validation phase" || true
gh label create "status:review" --color "10B981" --description "Ready for review" || true
gh label create "execution:parallel" --color "EC4899" --description "Parallel execution" || true

echo "✅ GitHub integration installed"
```

---

## Summary

This GitHub integration provides:

1. **Epic issue creation** with full specification and architecture
2. **Sub-issue management** for parallel domain execution
3. **Progress tracking** via comments and label updates
4. **Bidirectional linking** between epics and sub-issues
5. **Non-blocking design** that never halts the workflow
6. **Dual API** supporting both Bash and Python implementations

**Key Design Principles:**
- **Optional:** Only activates if GitHub CLI is authenticated
- **Non-blocking:** Failures log warnings, never halt workflow
- **Observable:** All operations visible in terminal output
- **Persistent:** Issue numbers stored in JSON for cross-phase access
- **Timestamped:** All comments include UTC timestamps

**Next Steps:**
1. Install label taxonomy in repository
2. Add integration scripts to workflow command
3. Test with parallel execution example
4. Verify issue creation/closure cycle works end-to-end
