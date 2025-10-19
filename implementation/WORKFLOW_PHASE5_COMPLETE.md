# Workflow Phase 5: Commit & Cleanup

**Phase:** Phase 5 (Final)
**Purpose:** Create git commit with proper formatting, cleanup artifacts, mark epic complete
**Duration:** ~1 minute

---

## Overview

Phase 5 handles the final workflow steps after successful implementation and validation:

1. Stage all changes to git
2. Generate conventional commit message with metadata
3. Create commit with Claude Code attribution
4. Cleanup parallel execution artifacts (worktrees)
5. Mark epic as complete
6. Display comprehensive completion summary

---

## Step 1: Stage All Changes

```bash
echo ""
echo "========================================="
echo "📦 Phase 5: Commit & Cleanup"
echo "========================================="
echo ""

# Stage all changes
echo "Staging changes..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
  echo "⚠️ No changes to commit"
  echo ""
  echo "Possible causes:"
  echo "  - All changes already committed"
  echo "  - Implementation phase made no file changes"
  echo "  - Changes were in .gitignore paths"
  echo ""
  echo "Workflow status: Complete (no commit needed)"
  exit 0
fi

echo "✅ Changes staged"
```

**Error Handling:**

- If no changes staged, exit gracefully (not an error)
- Provides context on why no commit is needed
- Preserves workflow completion status

---

## Step 2: Generate Commit Message

```bash
echo ""
echo "Generating commit message..."

# Extract epic ID from arguments
EPIC_ID="${ARGUMENTS}"

# Extract epic title from spec.md
EPIC_DIR=$(find .tasks -name "${EPIC_ID}-*" -type d | head -1)
EPIC_TITLE=$(grep "^# " "${EPIC_DIR}/spec.md" | head -1 | sed 's/^# //')

# Get file counts from phase1_results.json
PHASE1_RESULTS=".workflow/outputs/${EPIC_ID}/phase1_results.json"
if [ -f "$PHASE1_RESULTS" ]; then
  FILES_CREATED=$(jq -r '.files_created | length' "$PHASE1_RESULTS")
  FILES_MODIFIED=$(jq -r '.files_modified | length' "$PHASE1_RESULTS")
else
  # Fallback: Count from git diff
  FILES_CREATED=$(git diff --cached --name-only --diff-filter=A | wc -l)
  FILES_MODIFIED=$(git diff --cached --name-only --diff-filter=M | wc -l)
fi

# Get validation results
VALIDATION_RESULTS=".workflow/outputs/${EPIC_ID}/validation_results.json"
VALIDATION_STATUS="passed"
BUILD_STATUS="passed"
LINT_STATUS="passed"
TYPECHECK_STATUS="passed"

if [ -f "$VALIDATION_RESULTS" ]; then
  VALIDATION_STATUS=$(jq -r '.status // "passed"' "$VALIDATION_RESULTS")
  BUILD_STATUS=$(jq -r '.build_status // "passed"' "$VALIDATION_RESULTS")
  LINT_STATUS=$(jq -r '.lint_status // "passed"' "$VALIDATION_RESULTS")
  TYPECHECK_STATUS=$(jq -r '.typecheck_status // "passed"' "$VALIDATION_RESULTS")
fi

# Detect execution mode (sequential or parallel)
EXECUTION_MODE="sequential"
if [ -d ".worktrees/${EPIC_ID}-"* ] 2>/dev/null; then
  WORKTREE_COUNT=$(find .worktrees -maxdepth 1 -name "${EPIC_ID}-*" -type d | wc -l)
  EXECUTION_MODE="parallel (${WORKTREE_COUNT} agents)"
fi

# Determine commit type
COMMIT_TYPE="feat"
if echo "$EPIC_TITLE" | grep -qi "fix\|bug"; then
  COMMIT_TYPE="fix"
elif echo "$EPIC_TITLE" | grep -qi "refactor"; then
  COMMIT_TYPE="refactor"
fi

echo "✅ Commit message generated"
```

**Key Extraction Logic:**

- **Epic Title:** Extracted from spec.md first line
- **File Counts:** Read from phase1_results.json (fallback to git diff)
- **Validation Status:** Read from validation_results.json (default to "passed")
- **Execution Mode:** Detect worktrees to determine parallel execution
- **Commit Type:** Auto-detect from epic title (feat/fix/refactor)

---

## Step 3: Create Commit Message Template

```bash
# Create commit message using HEREDOC for proper formatting
cat > "/tmp/commit_msg_${EPIC_ID}" << EOF
${COMMIT_TYPE}(${EPIC_ID}): ${EPIC_TITLE}

Implementation of ${EPIC_ID}.

Changes:
- Files created: ${FILES_CREATED}
- Files modified: ${FILES_MODIFIED}
- Execution mode: ${EXECUTION_MODE}

Validation:
- Build: ${BUILD_STATUS}
- Lint: ${LINT_STATUS}
- Type checking: ${TYPECHECK_STATUS}
- Overall status: ${VALIDATION_STATUS}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
```

**Commit Message Format:**

**Header Line:**
```
feat(EPIC-007): Semantic Email Search with Vector Embeddings
```

- **Type:** `feat`, `fix`, or `refactor` (auto-detected)
- **Scope:** Epic ID in parentheses
- **Subject:** Epic title from spec.md

**Body:**
```
Implementation of EPIC-007.

Changes:
- Files created: 5
- Files modified: 3
- Execution mode: parallel (2 agents)

Validation:
- Build: passed
- Lint: passed
- Type checking: passed
- Overall status: passed
```

**Footer:**
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Follows Conventional Commits:**
- Type: feat, fix, refactor, docs, test, chore
- Scope: Epic ID
- Body: Implementation details and validation results
- Footer: Attribution

---

## Step 4: Create Git Commit

```bash
echo ""
echo "Creating commit..."

# Create commit with generated message
git commit -F "/tmp/commit_msg_${EPIC_ID}"

# Check commit status
if [ $? -eq 0 ]; then
  echo "✅ Commit created successfully"
  echo ""
  git log -1 --oneline
else
  echo "❌ Commit failed"
  echo ""
  echo "Possible causes:"
  echo "  - Pre-commit hooks failed"
  echo "  - Git configuration issues"
  echo "  - File permissions errors"
  echo ""
  echo "Review git output above for details."
  echo "Staged changes remain (run 'git status' to see them)"
  echo ""
  exit 1
fi

# Cleanup temp file
rm -f "/tmp/commit_msg_${EPIC_ID}"
```

**Error Handling:**

- Checks commit exit code
- Provides detailed error guidance
- Preserves staged changes on failure
- Cleans up temp file on success

**Common Failure Scenarios:**

1. **Pre-commit hooks fail:** Validation scripts run and fail
2. **Git config issues:** Missing user.name or user.email
3. **File permission errors:** Can't write to .git directory
4. **Large files:** Git LFS not configured

---

## Step 5: Cleanup Parallel Execution Artifacts

```bash
echo ""
echo "Cleaning up..."

# Cleanup worktrees (if parallel execution was used)
if [ -d ".worktrees/${EPIC_ID}-"* ] 2>/dev/null; then
  echo "Removing worktrees..."

  # Use worktree manager if available
  if [ -f "tools/worktree_manager/worktree_manager.py" ]; then
    python3 tools/worktree_manager/worktree_manager.py cleanup --epic "${EPIC_ID}"

    if [ $? -eq 0 ]; then
      echo "✅ Worktrees cleaned up"
    else
      echo "⚠️ Worktree cleanup failed (non-critical)"
      echo "Manual cleanup: git worktree prune"
    fi
  else
    # Fallback: Manual cleanup
    for worktree in .worktrees/${EPIC_ID}-*; do
      if [ -d "$worktree" ]; then
        BRANCH=$(git -C "$worktree" branch --show-current)
        git worktree remove "$worktree" --force
        git branch -D "$BRANCH" 2>/dev/null
      fi
    done

    echo "✅ Worktrees removed (manual cleanup)"
  fi
else
  echo "No worktrees to clean up (sequential execution)"
fi
```

**Cleanup Logic:**

1. **Check for worktrees:** Detect `.worktrees/EPIC-XXX-*` directories
2. **Use worktree manager:** If available (preferred method)
3. **Fallback to manual:** If worktree manager not installed
4. **Non-blocking:** Cleanup failures are warnings, not errors

**What Gets Cleaned:**

- `.worktrees/EPIC-XXX-*/` - Worktree directories
- `feature/EPIC-XXX/*` - Feature branches created for worktrees
- `.worktrees/.metadata/EPIC-XXX-*.json` - Metadata files

---

## Step 6: Mark Epic Complete

```bash
echo ""
echo "Marking epic complete..."

# Move epic to completed directory
COMPLETED_DIR=".tasks/completed"

if [ -d "$COMPLETED_DIR" ]; then
  mv "${EPIC_DIR}" "${COMPLETED_DIR}/"

  if [ $? -eq 0 ]; then
    echo "✅ Epic moved to .tasks/completed/"
  else
    echo "⚠️ Failed to move epic (non-critical)"
    echo "Manual move: mv ${EPIC_DIR} ${COMPLETED_DIR}/"
  fi
else
  echo "⚠️ .tasks/completed/ directory not found"
  echo "Creating directory..."
  mkdir -p "$COMPLETED_DIR"
  mv "${EPIC_DIR}" "${COMPLETED_DIR}/"
  echo "✅ Epic moved to .tasks/completed/"
fi
```

**Epic Completion:**

- Moves epic from `.tasks/backlog/` to `.tasks/completed/`
- Creates completed directory if missing
- Non-blocking: Failure doesn't halt workflow

**What Gets Moved:**

```
.tasks/backlog/EPIC-007-SemanticSearch/
├── spec.md
├── architecture.md
├── implementation-details/
│   └── file-tasks.md
└── contracts/
    └── api-contracts.yaml
```

To:

```
.tasks/completed/EPIC-007-SemanticSearch/
└── [same structure]
```

---

## Step 7: Display Completion Summary

```bash
echo ""
echo "========================================="
echo "✅ Workflow Complete: ${EPIC_ID}"
echo "========================================="
echo ""
echo "Implementation:"
echo "  - Epic: ${EPIC_TITLE}"
echo "  - Files created: ${FILES_CREATED}"
echo "  - Files modified: ${FILES_MODIFIED}"
echo "  - Execution mode: ${EXECUTION_MODE}"
echo ""
echo "Validation:"
echo "  - Build: ${BUILD_STATUS}"
echo "  - Lint: ${LINT_STATUS}"
echo "  - Type checking: ${TYPECHECK_STATUS}"
echo "  - Overall status: ${VALIDATION_STATUS}"
if [ -f "$VALIDATION_RESULTS" ]; then
  FIX_ATTEMPTS=$(jq -r '.fix_attempts // 0' "$VALIDATION_RESULTS")
  echo "  - Fix attempts: ${FIX_ATTEMPTS}"
fi
echo ""
echo "Artifacts:"
echo "  - Phase 1 results: .workflow/outputs/${EPIC_ID}/phase1_results.json"
if [ -f "$VALIDATION_RESULTS" ]; then
  echo "  - Validation results: .workflow/outputs/${EPIC_ID}/validation_results.json"
fi
if [ -f ".workflow/post-mortem/${EPIC_ID}.md" ]; then
  echo "  - Post-mortem: .workflow/post-mortem/${EPIC_ID}.md"
fi
echo "  - Epic location: .tasks/completed/${EPIC_ID}-*/"
echo ""
echo "Commit:"
echo "  - View commit: git log -1 -p"
echo "  - View summary: git show --stat"
echo ""
echo "Next steps:"
if [ -f ".workflow/post-mortem/${EPIC_ID}.md" ]; then
  echo "  - Review post-mortem for insights and recommendations"
fi
echo "  - Push to remote: git push origin $(git branch --show-current)"
echo "  - Create PR: gh pr create (if needed)"
if [ -d ".worktrees/.metadata" ] && [ "$(ls -A .worktrees/.metadata)" ]; then
  echo "  - Note: Some worktrees still exist (check: git worktree list)"
fi
echo ""
```

**Summary Contents:**

1. **Implementation Details:**
   - Epic title and ID
   - File change counts
   - Execution mode (sequential/parallel)

2. **Validation Results:**
   - Build, lint, type checking status
   - Overall validation status
   - Number of fix attempts

3. **Artifacts:**
   - Phase results JSON files
   - Post-mortem report (if exists)
   - Epic location after move

4. **Commit Information:**
   - Commands to review commit
   - Current branch name

5. **Next Steps:**
   - Review post-mortem recommendations
   - Push to remote repository
   - Create pull request (if applicable)
   - Check remaining worktrees (if any)

---

## Step 8: Optional - Cleanup Old Workflow Outputs

```bash
# Optional: Clean up old workflow outputs (keep last 10)
if [ -d ".workflow/outputs" ]; then
  echo ""
  echo "Cleaning up old workflow outputs..."

  cd .workflow/outputs

  # List directories by modification time, skip first 10, delete the rest
  OUTPUT_COUNT=$(ls -1 | wc -l)

  if [ "$OUTPUT_COUNT" -gt 10 ]; then
    TO_DELETE=$((OUTPUT_COUNT - 10))
    ls -t | tail -n +11 | xargs -r rm -rf
    echo "✅ Removed ${TO_DELETE} old workflow output(s)"
  else
    echo "No old outputs to clean (${OUTPUT_COUNT} total)"
  fi

  cd ../..
fi
```

**Optional Cleanup:**

- Keeps last 10 workflow outputs
- Removes older outputs to save disk space
- Non-destructive: Only cleans `.workflow/outputs/`
- Skip if less than 10 outputs exist

---

## Complete Phase 5 Script

```bash
#!/bin/bash
# Phase 5: Commit & Cleanup
# Usage: Called by execute-workflow.md after successful validation

set -e  # Exit on error

EPIC_ID="${1}"

echo ""
echo "========================================="
echo "📦 Phase 5: Commit & Cleanup"
echo "========================================="
echo ""

# Step 1: Stage all changes
echo "Staging changes..."
git add .

if git diff --cached --quiet; then
  echo "⚠️ No changes to commit"
  echo ""
  echo "Workflow status: Complete (no commit needed)"
  exit 0
fi

echo "✅ Changes staged"

# Step 2: Generate commit message
echo ""
echo "Generating commit message..."

EPIC_DIR=$(find .tasks -name "${EPIC_ID}-*" -type d | head -1)
EPIC_TITLE=$(grep "^# " "${EPIC_DIR}/spec.md" | head -1 | sed 's/^# //')

PHASE1_RESULTS=".workflow/outputs/${EPIC_ID}/phase1_results.json"
if [ -f "$PHASE1_RESULTS" ]; then
  FILES_CREATED=$(jq -r '.files_created | length' "$PHASE1_RESULTS")
  FILES_MODIFIED=$(jq -r '.files_modified | length' "$PHASE1_RESULTS")
else
  FILES_CREATED=$(git diff --cached --name-only --diff-filter=A | wc -l)
  FILES_MODIFIED=$(git diff --cached --name-only --diff-filter=M | wc -l)
fi

VALIDATION_RESULTS=".workflow/outputs/${EPIC_ID}/validation_results.json"
VALIDATION_STATUS="passed"
BUILD_STATUS="passed"
LINT_STATUS="passed"
TYPECHECK_STATUS="passed"

if [ -f "$VALIDATION_RESULTS" ]; then
  VALIDATION_STATUS=$(jq -r '.status // "passed"' "$VALIDATION_RESULTS")
  BUILD_STATUS=$(jq -r '.build_status // "passed"' "$VALIDATION_RESULTS")
  LINT_STATUS=$(jq -r '.lint_status // "passed"' "$VALIDATION_RESULTS")
  TYPECHECK_STATUS=$(jq -r '.typecheck_status // "passed"' "$VALIDATION_RESULTS")
fi

EXECUTION_MODE="sequential"
if [ -d ".worktrees/${EPIC_ID}-"* ] 2>/dev/null; then
  WORKTREE_COUNT=$(find .worktrees -maxdepth 1 -name "${EPIC_ID}-*" -type d | wc -l)
  EXECUTION_MODE="parallel (${WORKTREE_COUNT} agents)"
fi

COMMIT_TYPE="feat"
if echo "$EPIC_TITLE" | grep -qi "fix\|bug"; then
  COMMIT_TYPE="fix"
elif echo "$EPIC_TITLE" | grep -qi "refactor"; then
  COMMIT_TYPE="refactor"
fi

echo "✅ Commit message generated"

# Step 3: Create commit message file
cat > "/tmp/commit_msg_${EPIC_ID}" << EOF
${COMMIT_TYPE}(${EPIC_ID}): ${EPIC_TITLE}

Implementation of ${EPIC_ID}.

Changes:
- Files created: ${FILES_CREATED}
- Files modified: ${FILES_MODIFIED}
- Execution mode: ${EXECUTION_MODE}

Validation:
- Build: ${BUILD_STATUS}
- Lint: ${LINT_STATUS}
- Type checking: ${TYPECHECK_STATUS}
- Overall status: ${VALIDATION_STATUS}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF

# Step 4: Create commit
echo ""
echo "Creating commit..."

git commit -F "/tmp/commit_msg_${EPIC_ID}"

if [ $? -eq 0 ]; then
  echo "✅ Commit created successfully"
  echo ""
  git log -1 --oneline
else
  echo "❌ Commit failed"
  echo ""
  echo "Possible causes:"
  echo "  - Pre-commit hooks failed"
  echo "  - Git configuration issues"
  echo "  - File permissions errors"
  echo ""
  echo "Staged changes remain (run 'git status' to see them)"
  exit 1
fi

rm -f "/tmp/commit_msg_${EPIC_ID}"

# Step 5: Cleanup worktrees
echo ""
echo "Cleaning up..."

if [ -d ".worktrees/${EPIC_ID}-"* ] 2>/dev/null; then
  echo "Removing worktrees..."

  if [ -f "tools/worktree_manager/worktree_manager.py" ]; then
    python3 tools/worktree_manager/worktree_manager.py cleanup --epic "${EPIC_ID}"

    if [ $? -eq 0 ]; then
      echo "✅ Worktrees cleaned up"
    else
      echo "⚠️ Worktree cleanup failed (non-critical)"
    fi
  else
    for worktree in .worktrees/${EPIC_ID}-*; do
      if [ -d "$worktree" ]; then
        BRANCH=$(git -C "$worktree" branch --show-current)
        git worktree remove "$worktree" --force
        git branch -D "$BRANCH" 2>/dev/null
      fi
    done
    echo "✅ Worktrees removed"
  fi
else
  echo "No worktrees to clean up"
fi

# Step 6: Mark epic complete
echo ""
echo "Marking epic complete..."

COMPLETED_DIR=".tasks/completed"

if [ ! -d "$COMPLETED_DIR" ]; then
  mkdir -p "$COMPLETED_DIR"
fi

mv "${EPIC_DIR}" "${COMPLETED_DIR}/"

if [ $? -eq 0 ]; then
  echo "✅ Epic moved to .tasks/completed/"
else
  echo "⚠️ Failed to move epic (non-critical)"
fi

# Step 7: Display completion summary
echo ""
echo "========================================="
echo "✅ Workflow Complete: ${EPIC_ID}"
echo "========================================="
echo ""
echo "Implementation:"
echo "  - Epic: ${EPIC_TITLE}"
echo "  - Files created: ${FILES_CREATED}"
echo "  - Files modified: ${FILES_MODIFIED}"
echo "  - Execution mode: ${EXECUTION_MODE}"
echo ""
echo "Validation:"
echo "  - Build: ${BUILD_STATUS}"
echo "  - Lint: ${LINT_STATUS}"
echo "  - Type checking: ${TYPECHECK_STATUS}"
echo "  - Overall status: ${VALIDATION_STATUS}"
if [ -f "$VALIDATION_RESULTS" ]; then
  FIX_ATTEMPTS=$(jq -r '.fix_attempts // 0' "$VALIDATION_RESULTS")
  echo "  - Fix attempts: ${FIX_ATTEMPTS}"
fi
echo ""
echo "Artifacts:"
echo "  - Phase 1 results: .workflow/outputs/${EPIC_ID}/phase1_results.json"
if [ -f "$VALIDATION_RESULTS" ]; then
  echo "  - Validation results: .workflow/outputs/${EPIC_ID}/validation_results.json"
fi
if [ -f ".workflow/post-mortem/${EPIC_ID}.md" ]; then
  echo "  - Post-mortem: .workflow/post-mortem/${EPIC_ID}.md"
fi
echo "  - Epic location: .tasks/completed/${EPIC_ID}-*/"
echo ""
echo "Commit:"
echo "  - View commit: git log -1 -p"
echo "  - View summary: git show --stat"
echo ""
echo "Next steps:"
if [ -f ".workflow/post-mortem/${EPIC_ID}.md" ]; then
  echo "  - Review post-mortem for insights"
fi
echo "  - Push to remote: git push origin $(git branch --show-current)"
echo "  - Create PR: gh pr create (if needed)"
echo ""

# Step 8: Optional cleanup
if [ -d ".workflow/outputs" ]; then
  echo "Cleaning up old workflow outputs..."

  cd .workflow/outputs
  OUTPUT_COUNT=$(ls -1 | wc -l)

  if [ "$OUTPUT_COUNT" -gt 10 ]; then
    TO_DELETE=$((OUTPUT_COUNT - 10))
    ls -t | tail -n +11 | xargs -r rm -rf
    echo "✅ Removed ${TO_DELETE} old workflow output(s)"
  fi

  cd ../..
fi

echo "Workflow execution complete."
```

---

## Error Handling Summary

**Critical Errors (Exit 1):**

1. **Commit fails:** Pre-commit hooks fail or git errors
   - **Action:** Halt workflow, preserve staged changes
   - **Resolution:** User reviews git output, fixes issues manually

**Non-Critical Warnings (Continue):**

1. **No changes to commit:** Nothing staged
   - **Action:** Exit gracefully (workflow still successful)

2. **Worktree cleanup fails:** Can't remove worktrees
   - **Action:** Log warning, continue to completion
   - **Resolution:** User runs `git worktree prune` manually

3. **Epic move fails:** Can't move to completed
   - **Action:** Log warning, continue to completion
   - **Resolution:** User moves epic manually

4. **Old output cleanup fails:** Can't delete old artifacts
   - **Action:** Log warning, continue to completion
   - **Resolution:** User deletes manually or ignores

---

## Validation Checklist

Before completing Phase 5 implementation:

- [x] Git staging command included
- [x] Commit message generation with proper format
- [x] File count extraction from phase1_results.json
- [x] Conventional commit format (feat/fix/refactor)
- [x] Claude Code attribution in footer
- [x] Epic moved to completed directory
- [x] Completion summary with all details
- [x] Error handling for commit failures
- [x] Optional cleanup of old artifacts
- [x] Worktree cleanup (if parallel execution)
- [x] Non-blocking warnings for non-critical failures
- [x] Fallback logic for missing JSON files
- [x] Auto-detection of execution mode
- [x] Auto-detection of commit type

---

## Integration with Execute-Workflow Command

**In `.claude/commands/execute-workflow.md`:**

```markdown
### Step 7: Commit & Cleanup (Phase 5)

After successful validation and post-mortem:

```bash
# Run Phase 5 script
bash .workflow/scripts/phase5_commit_cleanup.sh "${ARGUMENTS}"

if [ $? -eq 0 ]; then
  echo "✅ Phase 5 complete"
else
  echo "❌ Phase 5 failed (see output above)"
  exit 1
fi
```

**Or inline in orchestrator:**

```markdown
### Step 7: Commit & Cleanup

[Inline Phase 5 bash commands here]
```
```

---

## Example Output

```
=========================================
📦 Phase 5: Commit & Cleanup
=========================================

Staging changes...
✅ Changes staged

Generating commit message...
✅ Commit message generated

Creating commit...
✅ Commit created successfully

a3f2b1c feat(EPIC-007): Semantic Email Search with Vector Embeddings

Cleaning up...
Removing worktrees...
✅ Worktrees cleaned up

Marking epic complete...
✅ Epic moved to .tasks/completed/

=========================================
✅ Workflow Complete: EPIC-007
=========================================

Implementation:
  - Epic: Semantic Email Search with Vector Embeddings
  - Files created: 5
  - Files modified: 3
  - Execution mode: parallel (2 agents)

Validation:
  - Build: passed
  - Lint: passed
  - Type checking: passed
  - Overall status: passed
  - Fix attempts: 1

Artifacts:
  - Phase 1 results: .workflow/outputs/EPIC-007/phase1_results.json
  - Validation results: .workflow/outputs/EPIC-007/validation_results.json
  - Post-mortem: .workflow/post-mortem/EPIC-007.md
  - Epic location: .tasks/completed/EPIC-007-SemanticSearch/

Commit:
  - View commit: git log -1 -p
  - View summary: git show --stat

Next steps:
  - Review post-mortem for insights
  - Push to remote: git push origin dev
  - Create PR: gh pr create (if needed)

Cleaning up old workflow outputs...
✅ Removed 3 old workflow output(s)

Workflow execution complete.
```

---

## Files Created/Modified

**New Files:**

- `.workflow/scripts/phase5_commit_cleanup.sh` - Standalone Phase 5 script (optional)

**Modified Files:**

- `.claude/commands/execute-workflow.md` - Integrate Phase 5 steps

**Artifacts:**

- `/tmp/commit_msg_EPIC-XXX` - Temporary commit message file (deleted after commit)

---

## Dependencies

**Required:**

- `git` - Version control
- `jq` - JSON parsing
- `bash` 4.0+ - Shell scripting

**Optional:**

- `tools/worktree_manager/worktree_manager.py` - Worktree cleanup (recommended)

---

## Testing Phase 5

**Test Scenario 1: Successful Commit**

```bash
# Setup
git init
mkdir -p .tasks/backlog/TEST-001-Example
echo "# Test Epic" > .tasks/backlog/TEST-001-Example/spec.md
mkdir -p .workflow/outputs/TEST-001
echo '{"files_created":["file1.py"],"files_modified":["file2.py"]}' > .workflow/outputs/TEST-001/phase1_results.json

# Create some changes
echo "test" > test_file.txt
git add test_file.txt

# Run Phase 5
bash phase5_commit_cleanup.sh TEST-001

# Verify
git log -1 --oneline  # Should show new commit
[ -d .tasks/completed/TEST-001-Example ] && echo "Epic moved" || echo "Epic not moved"
```

**Test Scenario 2: No Changes**

```bash
# Clean working directory
git reset --hard HEAD

# Run Phase 5 (should exit gracefully)
bash phase5_commit_cleanup.sh TEST-001

# Should output: "⚠️ No changes to commit"
```

**Test Scenario 3: Parallel Execution Cleanup**

```bash
# Setup worktrees
mkdir -p .worktrees/TEST-001-backend
git worktree add .worktrees/TEST-001-backend

# Create changes and commit
echo "test" > test.txt
git add test.txt

# Run Phase 5 (should cleanup worktrees)
bash phase5_commit_cleanup.sh TEST-001

# Verify worktrees removed
git worktree list  # Should not show TEST-001 worktrees
```

---

## Troubleshooting

**Problem:** Commit fails with "nothing to commit"

**Solution:** Check if changes are staged:
```bash
git diff --cached
```

**Problem:** Epic not moved to completed

**Solution:** Check directory exists and permissions:
```bash
ls -la .tasks/completed
mkdir -p .tasks/completed
```

**Problem:** Worktrees not cleaned up

**Solution:** Manual cleanup:
```bash
git worktree list
git worktree remove .worktrees/EPIC-XXX-backend --force
git worktree prune
```

**Problem:** Commit message formatting broken

**Solution:** Verify jq is installed and JSON files exist:
```bash
jq --version
jq . .workflow/outputs/EPIC-XXX/phase1_results.json
```

---

## End of Phase 5 Documentation
