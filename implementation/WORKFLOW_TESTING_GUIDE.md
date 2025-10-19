# Workflow Testing Guide

**Date:** 2025-10-19
**Purpose:** Comprehensive testing documentation for parallel execution workflow validation
**Location:** `~/tier1_workflow_global/implementation/`

---

## Overview

This guide provides complete test scenarios, mock data, and validation procedures to test the parallel execution workflow from end-to-end. Each test scenario validates specific workflow capabilities and failure modes.

**Test Coverage:**
- Sequential execution mode (baseline)
- Parallel execution with clean merge
- Parallel execution with merge conflicts
- Validation failure and retry loops
- GitHub integration (epic and sub-issues)

---

## Prerequisites

Before running tests:

```bash
# 1. Install dependencies
pip install -r ~/tier1_workflow_global/requirements.txt

# 2. Verify worktree manager
python3 -c "import sys; sys.path.insert(0, '$HOME/tier1_workflow_global/implementation/worktree_manager'); from worktree_manager import create_worktree_for_agent; print('✅ Worktree manager OK')"

# 3. Verify parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py --help

# 4. Create test directory
mkdir -p ~/workflow_test_project
cd ~/workflow_test_project
git init
git config user.email "test@example.com"
git config user.name "Test User"
echo "# Test Project" > README.md
git add README.md
git commit -m "Initial commit"

# 5. Create workflow directories
mkdir -p .workflow/outputs
mkdir -p .tasks/{backlog,in_progress,completed}
```

---

## Test Scenario 1: Sequential Execution Test

**Purpose:** Validate baseline sequential execution path with single agent.

**Expected Behavior:**
- Parallel detection determines sequential mode
- Single agent deploys
- Standard validation path
- No worktrees created

### Test Epic: SEQUENTIAL-001

**Files to Create:**

``.tasks/backlog/SEQUENTIAL-001/spec.md``:
```markdown
---
epic_id: SEQUENTIAL-001
title: Add user email validation
type: enhancement
priority: medium
---

# SEQUENTIAL-001: Add user email validation

## Requirements

- FR-1: Validate email format using regex
- FR-2: Return clear error messages for invalid emails
- FR-3: Support multiple email providers

## Acceptance Criteria

- [ ] Email validation function created
- [ ] Unit tests pass
- [ ] Integration with user routes
```

`.tasks/backlog/SEQUENTIAL-001/file-tasks.md`:
```markdown
# File Tasks: SEQUENTIAL-001

## Files to Create

1. **src/validators/email_validator.py** (50 lines)
   - EmailValidator class with validate() method
   - Regex pattern for standard email formats
   - Error message generation

## Files to Modify

1. **src/api/user_routes.py** (10 lines added)
   - Import EmailValidator
   - Add validation to POST /users endpoint
   - Return 400 on validation failure

Total: 1 file to create, 1 file to modify (2 files, 1 domain)
```

`.tasks/backlog/SEQUENTIAL-001/architecture.md`:
```markdown
# Architecture: SEQUENTIAL-001

## Changes

### Backend Layer
- New validator module: `src/validators/email_validator.py`
- Modified: `src/api/user_routes.py`

### Dependencies
- No new dependencies required
- Uses standard library `re` module

## Domain: backend
All changes in single domain (backend)
```

### Expected Parallel Detection Output

```json
{
  "viable": false,
  "reason": "Too few files (2 < 8 minimum)",
  "execution_mode": "sequential",
  "file_count": 2,
  "domain_count": 1,
  "domains": {
    "backend": ["src/validators/email_validator.py", "src/api/user_routes.py"]
  }
}
```

### Run Test

```bash
cd ~/workflow_test_project

# Run parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/SEQUENTIAL-001 \
  --output .workflow/outputs/SEQUENTIAL-001/parallel_analysis.json

# Verify sequential mode
jq -r '.execution_mode' .workflow/outputs/SEQUENTIAL-001/parallel_analysis.json
# Expected: "sequential"

# Check file count
jq -r '.file_count' .workflow/outputs/SEQUENTIAL-001/parallel_analysis.json
# Expected: 2
```

### Validation Checklist

- [ ] Parallel detection runs successfully
- [ ] `execution_mode = "sequential"`
- [ ] Reason: "Too few files"
- [ ] File count: 2
- [ ] Domain count: 1
- [ ] Output JSON written correctly

---

## Test Scenario 2: Parallel Execution Test (Clean Merge)

**Purpose:** Validate parallel execution with no conflicts.

**Expected Behavior:**
- Parallel detection determines parallel mode
- 3 worktrees created
- 3 agents deploy in parallel
- Sequential merge succeeds
- Worktrees cleaned up

### Test Epic: PARALLEL-CLEAN-001

**Files to Create:**

`.tasks/backlog/PARALLEL-CLEAN-001/spec.md`:
```markdown
---
epic_id: PARALLEL-CLEAN-001
title: Complete user management system
type: feature
priority: high
---

# PARALLEL-CLEAN-001: Complete user management system

## Requirements

- FR-1: Backend API for user CRUD operations
- FR-2: Frontend UI for user management
- FR-3: Database schema and migrations
- FR-4: Comprehensive test coverage

## Acceptance Criteria

- [ ] Backend API endpoints implemented
- [ ] Frontend components created
- [ ] Database migrations applied
- [ ] All tests passing
```

`.tasks/backlog/PARALLEL-CLEAN-001/file-tasks.md`:
```markdown
# File Tasks: PARALLEL-CLEAN-001

## Files to Create

### Backend (5 files)
1. **src/backend/api/users.py** (100 lines)
2. **src/backend/api/auth.py** (80 lines)
3. **src/backend/models/user.py** (60 lines)
4. **src/backend/services/user_service.py** (90 lines)
5. **src/backend/utils/password_hash.py** (40 lines)

### Frontend (6 files)
1. **src/frontend/components/UserList.tsx** (120 lines)
2. **src/frontend/components/UserForm.tsx** (100 lines)
3. **src/frontend/components/UserProfile.tsx** (80 lines)
4. **src/frontend/api/userClient.ts** (70 lines)
5. **src/frontend/hooks/useUsers.ts** (60 lines)
6. **src/frontend/pages/UsersPage.tsx** (90 lines)

### Database (3 files)
1. **src/migrations/001_create_users_table.sql** (30 lines)
2. **src/migrations/002_add_user_indexes.sql** (20 lines)
3. **src/database/seeds/users.sql** (40 lines)

Total: 14 files to create (3 domains)
```

`.tasks/backlog/PARALLEL-CLEAN-001/architecture.md`:
```markdown
# Architecture: PARALLEL-CLEAN-001

## Domains

### backend
- API layer: RESTful endpoints
- Service layer: Business logic
- Model layer: Data structures
- Files: 5

### frontend
- Components: React/TypeScript
- API client: Fetch wrapper
- Hooks: Custom React hooks
- Files: 6

### database
- Migrations: SQL DDL
- Seeds: Test data
- Files: 3

No file overlap between domains.
```

### Expected Parallel Detection Output

```json
{
  "viable": true,
  "reason": "14 files across 3 domains (meets thresholds)",
  "execution_mode": "parallel",
  "file_count": 14,
  "domain_count": 3,
  "domains": {
    "backend": [
      "src/backend/api/users.py",
      "src/backend/api/auth.py",
      "src/backend/models/user.py",
      "src/backend/services/user_service.py",
      "src/backend/utils/password_hash.py"
    ],
    "frontend": [
      "src/frontend/components/UserList.tsx",
      "src/frontend/components/UserForm.tsx",
      "src/frontend/components/UserProfile.tsx",
      "src/frontend/api/userClient.ts",
      "src/frontend/hooks/useUsers.ts",
      "src/frontend/pages/UsersPage.tsx"
    ],
    "database": [
      "src/migrations/001_create_users_table.sql",
      "src/migrations/002_add_user_indexes.sql",
      "src/database/seeds/users.sql"
    ]
  },
  "parallel_plan": {
    "backend": {
      "files": [...],
      "task_description": "Implement backend API endpoints, services, and models..."
    },
    "frontend": {
      "files": [...],
      "task_description": "Create frontend UI components and API client..."
    },
    "database": {
      "files": [...],
      "task_description": "Add database migrations and seed data..."
    }
  }
}
```

### Run Test

```bash
cd ~/workflow_test_project

# Run parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/PARALLEL-CLEAN-001 \
  --output .workflow/outputs/PARALLEL-CLEAN-001/parallel_analysis.json

# Verify parallel mode
jq -r '.execution_mode' .workflow/outputs/PARALLEL-CLEAN-001/parallel_analysis.json
# Expected: "parallel"

# Check domains
jq -r '.domain_count' .workflow/outputs/PARALLEL-CLEAN-001/parallel_analysis.json
# Expected: 3

# List domains
jq -r '.domains | keys[]' .workflow/outputs/PARALLEL-CLEAN-001/parallel_analysis.json
# Expected: backend, database, frontend
```

### Validation Checklist

- [ ] Parallel detection runs successfully
- [ ] `execution_mode = "parallel"`
- [ ] Reason contains "meets thresholds"
- [ ] File count: 14
- [ ] Domain count: 3
- [ ] All 3 domains present in output
- [ ] Parallel plan generated for each domain

---

## Test Scenario 3: Parallel with Conflicts Test

**Purpose:** Validate conflict detection and graceful failure.

**Expected Behavior:**
- Parallel detection determines parallel mode
- Worktrees created
- Agents deploy
- Sequential merge detects conflicts
- Clear resolution instructions provided
- Workflow aborts safely

### Test Epic: PARALLEL-CONFLICT-001

**Files to Create:**

`.tasks/backlog/PARALLEL-CONFLICT-001/spec.md`:
```markdown
---
epic_id: PARALLEL-CONFLICT-001
title: Refactor shared configuration
type: refactor
priority: medium
---

# PARALLEL-CONFLICT-001: Refactor shared configuration

## Requirements

- FR-1: Split monolithic config into modules
- FR-2: Update backend to use new config
- FR-3: Update frontend to use new config

## Acceptance Criteria

- [ ] Config module created
- [ ] Backend updated
- [ ] Frontend updated
```

`.tasks/backlog/PARALLEL-CONFLICT-001/file-tasks.md`:
```markdown
# File Tasks: PARALLEL-CONFLICT-001

## Files to Create

### config (3 files)
1. **src/config/database.py** (40 lines)
2. **src/config/api.py** (30 lines)
3. **src/config/frontend.ts** (35 lines)

### Backend (4 files)
1. **src/backend/app.py** (MODIFIED - uses config.database)
2. **src/backend/api/base.py** (MODIFIED - uses config.api)
3. **src/backend/services/db_connection.py** (50 lines)
4. **src/config/__init__.py** (MODIFIED - imports all)

### Frontend (3 files)
1. **src/frontend/config.ts** (MODIFIED - uses config.frontend)
2. **src/frontend/api/client.ts** (MODIFIED - uses config.api)
3. **src/config/__init__.py** (MODIFIED - imports all)

**CONFLICT:** Both backend and frontend modify `src/config/__init__.py`
```

`.tasks/backlog/PARALLEL-CONFLICT-001/architecture.md`:
```markdown
# Architecture: PARALLEL-CONFLICT-001

## Domains

### backend
- Modifies: src/config/__init__.py (adds backend imports)
- Files: 4

### frontend
- Modifies: src/config/__init__.py (adds frontend imports)
- Files: 3

**INTENTIONAL CONFLICT:** Both domains modify same file (src/config/__init__.py)
```

### Expected Behavior

**Parallel Detection:** Should detect parallel mode (10 files, 2 domains)

**Merge Conflict:** Sequential merge should detect conflict on `src/config/__init__.py`

**Output:**
```
Merging: frontend
  Branch: feature/PARALLEL-CONFLICT-001/frontend
  Merging into: main
  ❌ Merge conflict detected
  Conflicted files:
    - src/config/__init__.py

⚠️ Merge conflicts detected in:
  - frontend

=========================================
MANUAL CONFLICT RESOLUTION REQUIRED
=========================================

Steps to resolve:
  1. Review conflicted domains above
  2. Merge manually:
     git merge feature/PARALLEL-CONFLICT-001/frontend
     # Resolve conflicts in editor
     git add .
     git commit

  3. Run validation: npm run validate-all
  4. Complete workflow: /execute-workflow PARALLEL-CONFLICT-001 --resume
```

### Validation Checklist

- [ ] Parallel detection succeeds
- [ ] Worktrees created
- [ ] First merge (backend) succeeds
- [ ] Second merge (frontend) detects conflict
- [ ] Conflicted file listed correctly
- [ ] Merge aborted cleanly
- [ ] Resolution instructions displayed
- [ ] Conflict state JSON written

---

## Test Scenario 4: Validation Failure Test

**Purpose:** Validate retry loop and fixer agent deployment.

**Expected Behavior:**
- Implementation completes
- Validation detects lint/type errors
- Fixer agent deployed
- Max 3 retry attempts
- Workflow blocks on persistent failures

### Test Setup

Create a test epic with intentional lint errors:

`.tasks/backlog/VALIDATION-FAIL-001/spec.md`:
```markdown
---
epic_id: VALIDATION-FAIL-001
title: Add utility functions with linting issues
type: test
priority: low
---

# VALIDATION-FAIL-001: Test validation failure

Add utility functions with intentional linting errors to test validation retry loop.
```

`.tasks/backlog/VALIDATION-FAIL-001/file-tasks.md`:
```markdown
# File Tasks: VALIDATION-FAIL-001

## Files to Create

1. **src/utils/math.py** (30 lines - intentional lint errors)
2. **src/utils/string.py** (25 lines - intentional type errors)

Total: 2 files (sequential mode)
```

**Create test file with errors:**

`src/utils/math.py`:
```python
# Intentional lint errors
def add(a,b):  # Missing spaces around parameters
    return a+b  # Missing spaces around operator

def subtract( a, b ):  # Extra spaces
    result=a-b  # Missing spaces
    return result

unused_variable = 42  # Unused variable (linting error)
```

### Expected Validation Output

**First Attempt:**
```
❌ Validation Failed (Attempt 1/3)
  Lint errors: 5
  Type errors: 0

Deploying fixer agent...
```

**After Max Retries:**
```
❌ Validation Failed (Attempt 3/3)
  Maximum retry attempts reached

⚠️ WORKFLOW BLOCKED
  Manual intervention required
  Review errors: .workflow/outputs/VALIDATION-FAIL-001/validation_errors.log
```

### Validation Checklist

- [ ] Implementation completes
- [ ] Validation runs automatically
- [ ] Lint/type errors detected
- [ ] Fixer agent deploys
- [ ] Retry counter increments
- [ ] Max 3 attempts enforced
- [ ] Workflow blocks after max retries
- [ ] Error log written

---

## Test Scenario 5: GitHub Integration Test

**Purpose:** Validate GitHub issue creation and updates.

**Prerequisites:**
- GitHub CLI installed: `gh --version`
- Authenticated: `gh auth status`
- Repository has remote: `git remote get-url origin`

### Test Epic: GITHUB-INT-001

Use **Test Scenario 2** epic (PARALLEL-CLEAN-001) for GitHub integration.

### Expected Behavior

**Phase 0 (Preflight):**
```
✅ GitHub CLI available and authenticated
```

**Phase 1A (Worktree Creation):**
```
📝 Creating GitHub epic issue...
  ✅ Epic issue created: #42
  URL: https://github.com/user/repo/issues/42

📝 Creating sub-issues for parallel domains...
  ✅ Sub-issue created for backend: #43
  ✅ Sub-issue created for frontend: #44
  ✅ Sub-issue created for database: #45
```

**Phase 1C (Sequential Merge):**
```
Merging: database
  ✅ Merged successfully
  📝 Updated sub-issue #45 (closed)

Merging: backend
  ✅ Merged successfully
  📝 Updated sub-issue #43 (closed)

Merging: frontend
  ✅ Merged successfully
  📝 Updated sub-issue #44 (closed)
```

**Phase 5 (Commit & Cleanup):**
```
📝 Closing epic issue #42
  ✅ Epic closed with completion comment
  Labels updated: status:completed
```

### Verify GitHub Issues

```bash
# Check epic issue
gh issue view 42

# Check sub-issues
gh issue list --label "parent:42"

# Verify all closed
gh issue list --label "type:epic" --state closed
```

### Validation Checklist

- [ ] GitHub CLI detection works
- [ ] Epic issue created with correct labels
- [ ] Epic body includes spec and architecture
- [ ] Sub-issues created for each domain
- [ ] Sub-issues linked to epic
- [ ] Progress updates posted during merge
- [ ] Sub-issues closed after merge
- [ ] Epic issue closed after workflow
- [ ] Final labels updated

---

## Mock Data Directory Structure

Create complete mock epics for easy testing:

```bash
# Create mock data directory
mkdir -p ~/tier1_workflow_global/test_epics

# Sequential test
mkdir -p ~/tier1_workflow_global/test_epics/sequential
cp .tasks/backlog/SEQUENTIAL-001/* ~/tier1_workflow_global/test_epics/sequential/

# Parallel clean test
mkdir -p ~/tier1_workflow_global/test_epics/parallel_clean
cp .tasks/backlog/PARALLEL-CLEAN-001/* ~/tier1_workflow_global/test_epics/parallel_clean/

# Parallel conflicts test
mkdir -p ~/tier1_workflow_global/test_epics/parallel_conflicts
cp .tasks/backlog/PARALLEL-CONFLICT-001/* ~/tier1_workflow_global/test_epics/parallel_conflicts/
```

**Usage:**
```bash
# Quick test from mock data
cp -r ~/tier1_workflow_global/test_epics/parallel_clean .tasks/backlog/TEST-001
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/TEST-001
```

---

## Troubleshooting

### Parallel Detection Fails

**Symptom:** Script exits with error

**Solutions:**
```bash
# Check file exists
ls -la ~/tier1_workflow_global/implementation/parallel_detection.py

# Check Python path
python3 --version

# Run with verbose output
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/EPIC-001 \
  --output /tmp/test.json 2>&1 | tee /tmp/debug.log
```

### Worktree Creation Fails

**Symptom:** "Failed to create worktree" error

**Solutions:**
```bash
# Check git working directory is clean
git status

# Check no existing worktrees
git worktree list

# Verify worktree manager
python3 -c "
import sys
sys.path.insert(0, '$HOME/tier1_workflow_global/implementation/worktree_manager')
from worktree_manager import create_worktree_for_agent
print('OK')
"
```

### Agent Can't Find Worktree

**Symptom:** Agent reports "directory not found"

**Solutions:**
```bash
# Check worktree exists
ls -la .worktrees/

# Verify absolute paths used
grep -r "cd .worktrees" .workflow/  # Should be ABSOLUTE paths

# Check agent prompt includes CD command
# Agent prompt MUST start with: cd /absolute/path/to/worktree
```

### Merge Conflicts Not Detected

**Symptom:** Workflow completes despite conflicts

**Solutions:**
```bash
# Check git merge exit code handling
# Script should check: if [ $? -ne 0 ]; then

# Verify git diff command
git diff --name-only --diff-filter=U

# Ensure merge abort is called
git merge --abort
```

### GitHub Issue Creation Fails

**Symptom:** "GitHub operation failed" warning

**Solutions:**
```bash
# Check gh CLI
gh --version

# Check authentication
gh auth status

# Test issue creation manually
gh issue create --title "Test" --body "Test" --repo user/repo

# Check repository has remote
git remote get-url origin
```

### Validation Scripts Missing

**Symptom:** "npm run validate-all not found"

**Solutions:**
```bash
# Add validation scripts to package.json
{
  "scripts": {
    "lint": "eslint src/",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "validate-all": "npm run lint && npm run type-check && npm run test"
  }
}

# Or use Python validation
python -m pylint src/
python -m mypy src/
python -m pytest tests/
```

---

## Validation Metrics

Track test execution metrics:

```bash
# Create metrics file
cat > .workflow/test_metrics.json << EOF
{
  "test_runs": [],
  "total_tests": 5,
  "passed": 0,
  "failed": 0
}
EOF

# After each test, append result
jq '.test_runs += [{
  "scenario": "sequential",
  "status": "passed",
  "duration_seconds": 45,
  "timestamp": "'$(date -Iseconds)'"
}]' .workflow/test_metrics.json > /tmp/metrics.json && mv /tmp/metrics.json .workflow/test_metrics.json
```

**Expected Performance:**

| Scenario | Expected Duration | Success Rate |
|----------|------------------|--------------|
| Sequential | 30-60s | 100% |
| Parallel Clean | 60-120s | 95%+ |
| Parallel Conflicts | 60-120s (abort) | 100% (detects) |
| Validation Failure | 90-180s (retries) | 100% (blocks) |
| GitHub Integration | 90-180s | 90%+ |

---

## Complete Test Suite Script

**Create automated test runner:**

`~/tier1_workflow_global/test_runner.sh`:
```bash
#!/bin/bash
set -e

echo "=================================="
echo "Tier 1 Workflow Test Suite"
echo "=================================="
echo ""

# Setup
TEST_PROJECT=~/workflow_test_project_$(date +%s)
mkdir -p "$TEST_PROJECT"
cd "$TEST_PROJECT"
git init
git config user.email "test@example.com"
git config user.name "Test User"
echo "# Test" > README.md
git add README.md
git commit -m "Initial"

# Test 1: Sequential
echo "Test 1: Sequential Execution"
cp -r ~/tier1_workflow_global/test_epics/sequential .tasks/backlog/SEQ-001
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/SEQ-001 \
  --output .workflow/outputs/SEQ-001/parallel_analysis.json

MODE=$(jq -r '.execution_mode' .workflow/outputs/SEQ-001/parallel_analysis.json)
if [ "$MODE" = "sequential" ]; then
  echo "✅ PASSED: Sequential mode detected"
else
  echo "❌ FAILED: Expected sequential, got $MODE"
  exit 1
fi

# Test 2: Parallel Clean
echo ""
echo "Test 2: Parallel Execution (Clean)"
cp -r ~/tier1_workflow_global/test_epics/parallel_clean .tasks/backlog/PAR-001
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/PAR-001 \
  --output .workflow/outputs/PAR-001/parallel_analysis.json

MODE=$(jq -r '.execution_mode' .workflow/outputs/PAR-001/parallel_analysis.json)
DOMAINS=$(jq -r '.domain_count' .workflow/outputs/PAR-001/parallel_analysis.json)
if [ "$MODE" = "parallel" ] && [ "$DOMAINS" -eq 3 ]; then
  echo "✅ PASSED: Parallel mode with 3 domains"
else
  echo "❌ FAILED: Expected parallel with 3 domains, got $MODE / $DOMAINS"
  exit 1
fi

# Cleanup
echo ""
echo "Cleaning up test project: $TEST_PROJECT"
rm -rf "$TEST_PROJECT"

echo ""
echo "=================================="
echo "All tests passed!"
echo "=================================="
```

**Run all tests:**
```bash
chmod +x ~/tier1_workflow_global/test_runner.sh
~/tier1_workflow_global/test_runner.sh
```

---

## Summary

This testing guide provides:

- ✅ **5 comprehensive test scenarios** covering all execution paths
- ✅ **Complete mock data** ready to use
- ✅ **Validation checklists** for each scenario
- ✅ **Troubleshooting guide** for common failures
- ✅ **Automated test runner** for regression testing
- ✅ **Performance metrics** for benchmarking

**Next Steps:**
1. Run Test Scenario 1 (Sequential) to validate baseline
2. Run Test Scenario 2 (Parallel Clean) to validate worktrees
3. Run Test Scenario 3 (Conflicts) to validate error handling
4. Run Test Scenario 4 (Validation) to validate retry loop
5. Run Test Scenario 5 (GitHub) to validate integration

**Files Created:**
- Test epics in: `~/tier1_workflow_global/test_epics/`
- Test runner: `~/tier1_workflow_global/test_runner.sh`
- This guide: `~/tier1_workflow_global/implementation/WORKFLOW_TESTING_GUIDE.md`
