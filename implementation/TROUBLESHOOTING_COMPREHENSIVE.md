# Tier 1 Workflow - Comprehensive Troubleshooting Guide

**Last Updated:** 2025-10-19
**Status:** Production Ready
**Version:** 1.0

---

## Table of Contents

1. [Epic Creation Issues](#1-epic-creation-issues)
2. [Preflight Check Failures](#2-preflight-check-failures)
3. [Parallel Execution Issues](#3-parallel-execution-issues)
4. [Validation Issues](#4-validation-issues)
5. [GitHub Integration Issues](#5-github-integration-issues)
6. [Agent Failures](#6-agent-failures)
7. [Git Issues](#7-git-issues)
8. [Recovery Procedures](#8-recovery-procedures)

---

## 1. Epic Creation Issues

### 1.1 Epic Directory Not Found

**Symptom:**
```
❌ Epic directory not found for: EPIC-042
Check: .tasks/backlog/EPIC-042-*/
Run: /task-list to view available epics
```

**Root Cause:**
- Epic was never created
- Epic ID is incorrect
- Epic is in wrong directory (in-progress vs backlog)

**Resolution:**

**Step 1: List all epics**
```bash
# Check backlog
ls -la .tasks/backlog/

# Check in-progress
ls -la .tasks/in-progress/

# Search by number only
find .tasks -name "*042*" -type d
```

**Step 2: Verify epic ID**
```bash
# If found in in-progress, move it back to backlog
# (workflow expects epics in backlog/)
mv .tasks/in-progress/EPIC-042-* .tasks/backlog/

# Or use correct path
EPIC_DIR=$(find .tasks -name "EPIC-042-*" -type d | head -1)
```

**Step 3: Create epic if missing**
```bash
# Create new epic
/spec-epic

# This will prompt you for requirements and create:
# .tasks/backlog/EPIC-XXX-<description>/
```

**Prevention:**
- Always use `/spec-epic` to create epics
- Don't manually rename epic directories
- Don't move epics between backlog/in-progress manually (workflow handles this)

---

### 1.2 Missing Required Files

**Symptom:**
```
❌ Epic not ready for execution

Missing files:
- spec.md ❌
- architecture.md ❌
- implementation-details/file-tasks.md ❌

Run: /refine-epic EPIC-042
```

**Root Cause:**
- Epic was created but not refined
- Refinement failed partway through
- Files were deleted or moved

**Resolution:**

**Step 1: Check what exists**
```bash
ls -la .tasks/backlog/EPIC-042-*/
ls -la .tasks/backlog/EPIC-042-*/implementation-details/
```

**Step 2: Run refinement**
```bash
# Generate all missing files
/refine-epic EPIC-042
```

This will:
1. Read existing spec.md (or create if missing)
2. Generate architecture.md with design decisions
3. Generate implementation-details/file-tasks.md with prescriptive plan

**Step 3: Verify files created**
```bash
# Should show all three files
ls .tasks/backlog/EPIC-042-*/
# - spec.md ✅
# - architecture.md ✅
# - implementation-details/ ✅

ls .tasks/backlog/EPIC-042-*/implementation-details/
# - file-tasks.md ✅
```

**Step 4: Review generated files**
```bash
# Check that file-tasks.md has clear, specific instructions
cat .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md
```

Look for:
- Absolute file paths (not relative)
- Specific instructions (not vague "add stuff")
- Clear requirements for each file

**Prevention:**
- Always run `/refine-epic` after `/spec-epic`
- Verify file-tasks.md quality before running workflow
- Don't delete generated files manually

---

### 1.3 Invalid Prescriptive Plan Format

**Symptom:**
```
❌ Phase 1: Implementation FAILED

Error: Cannot parse file-tasks.md
Line 42: File path unclear: "update service.py"

Implementation aborted.
```

**Root Cause:**
- file-tasks.md has ambiguous file paths
- Instructions are too vague
- Missing context for implementation

**Resolution:**

**Step 1: Review file-tasks.md**
```bash
cat .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md
```

**Step 2: Identify issues**

❌ **WRONG FORMAT:**
```markdown
## Implementation Tasks

- Update service.py (add validation)
- Modify routes.py (add endpoint)
- Create email stuff
```

✅ **CORRECT FORMAT:**
```markdown
## Files to Create

### `src/backend/services/email_service.py`

**Purpose:** Email business logic service

**Requirements:**
- Create EmailService class
- Implement create_email(email_data: EmailCreate) -> Email method
- Add error handling (EmailNotFoundError, DatabaseError)
- Use dependency injection for database session

**Dependencies:**
- SQLAlchemy AsyncSession
- Email model from models/email.py
- EmailCreate schema from schemas/email.py

## Files to Modify

### `src/backend/api/routes.py`

**Changes:**
- Add POST /emails endpoint
- Integrate with EmailService
- Add error handling for 404 and 500 errors

**Location:** After line 15 (after existing route definitions)

**Example:**
```python
@router.post("/emails", response_model=EmailResponse)
async def create_email(
    email: EmailCreate,
    service: EmailService = Depends(get_email_service)
):
    return await service.create_email(email)
```
```

**Step 3: Fix or regenerate**

**Option 1: Fix manually**
```bash
nano .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md

# Update to use correct format (see above)
```

**Option 2: Regenerate with better context**
```bash
# First, improve spec.md with more details
nano .tasks/backlog/EPIC-042-*/spec.md

# Then regenerate
/refine-epic EPIC-042
```

**Prevention:**
- Provide detailed requirements in spec.md
- Review file-tasks.md before running workflow
- Use template from existing successful epics
- Include specific file paths, not generic names

---

## 2. Preflight Check Failures

### 2.1 Git Working Directory Not Clean

**Symptom:**
```
❌ Git working directory not clean

Uncommitted changes detected:
 M src/backend/service.py
 M src/frontend/component.tsx
?? new_file.py

Commit or stash changes before running workflow.
```

**Root Cause:**
The workflow requires a clean git state to:
- Ensure all changes come from workflow execution
- Enable clean rollback if workflow fails
- Create atomic commits per epic

**Resolution:**

**Option 1: Commit changes**
```bash
# Review changes
git status
git diff

# Stage all changes
git add .

# Commit
git commit -m "feat: Prepare for EPIC-042 workflow"

# Verify clean
git status
# Should show: "nothing to commit, working tree clean"

# Run workflow
/execute-workflow EPIC-042
```

**Option 2: Stash changes (temporary)**
```bash
# Stash with description
git stash push -m "Before EPIC-042 workflow"

# Verify clean
git status

# Run workflow
/execute-workflow EPIC-042

# After workflow completes, restore
git stash pop
```

**Option 3: Create temporary branch**
```bash
# Save current work to branch
git checkout -b temp-work
git add .
git commit -m "Temporary work"

# Return to main branch
git checkout main

# Verify clean
git status

# Run workflow
/execute-workflow EPIC-042

# After workflow, merge or discard temp branch
git branch -D temp-work  # Delete if not needed
# OR
git merge temp-work  # Merge if needed
```

**Prevention:**
- Commit frequently during manual work
- Use feature branches for experiments
- Run workflow on clean main/develop branch
- Keep separate terminal for workflow vs manual work

---

### 2.2 Missing Dependencies

**Symptom:**
```
❌ Preflight FAILED

Missing dependencies:
- ruff (Python linter)
- mypy (Type checker)

Install with: pip install ruff mypy
```

**Root Cause:**
Validation tools not installed in environment.

**Resolution:**

**Step 1: Check current environment**
```bash
# Check Python version
python3 --version

# Check if in virtual environment
which python3

# List installed packages
pip list | grep -E "(ruff|mypy)"
```

**Step 2: Install missing tools**

**For Python projects:**
```bash
# Install in current environment
pip install ruff mypy

# Or install in project venv
source venv/bin/activate
pip install ruff mypy

# Or install globally
pip install --user ruff mypy
```

**For TypeScript projects:**
```bash
# Install dev dependencies
npm install --save-dev \
  eslint \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin \
  typescript \
  prettier
```

**For polyglot projects:**
```bash
# Python
pip install ruff mypy

# TypeScript
npm install --save-dev eslint typescript prettier
```

**Step 3: Verify installation**
```bash
# Test Python tools
ruff --version
mypy --version

# Test TypeScript tools
npx eslint --version
npx tsc --version
```

**Step 4: Add to package.json**
```json
{
  "name": "my-project",
  "scripts": {
    "validate": "ruff check . && mypy src/"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

**Prevention:**
- Document required dependencies in README.md
- Use requirements.txt (Python) or package.json (TypeScript)
- Include setup script in project
- Use virtual environments for Python projects

---

### 2.3 Parallel Detection Fails

**Symptom:**
```
❌ Parallel detection failed

Error: python3: command not found

Falling back to sequential execution.
```

**Root Cause:**
- Python 3 not in PATH
- parallel_detection.py not found
- Syntax errors in parallel_detection.py

**Resolution:**

**Step 1: Check Python**
```bash
# Check Python availability
which python3
python3 --version

# If not found, install
# Ubuntu/Debian:
sudo apt install python3

# macOS:
brew install python3

# Windows (WSL):
sudo apt update && sudo apt install python3
```

**Step 2: Verify script location**
```bash
# Check script exists
ls -la ~/tier1_workflow_global/implementation/parallel_detection.py

# If not found, verify tier1_workflow_global location
ls -la ~/tier1_workflow_global/
```

**Step 3: Test parallel detection manually**
```bash
# Run directly
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md

# Should output JSON with viability analysis
```

**Step 4: Check for syntax errors**
```bash
# Validate Python syntax
python3 -m py_compile ~/tier1_workflow_global/implementation/parallel_detection.py

# If errors, reinstall tier1_workflow_global
```

**Prevention:**
- Ensure Python 3.8+ installed globally
- Add Python to PATH in shell profile
- Test parallel detection before running workflow

---

## 3. Parallel Execution Issues

### 3.1 Worktree Creation Fails

**Symptom:**
```
❌ Phase 1B: Parallel Implementation FAILED

Worktree creation failed for domain: backend

Error: fatal: cannot create directory '.workflow/worktrees/backend': Permission denied
```

**Root Cause:**
- Permission issues on .workflow directory
- Disk space exhausted
- Existing worktree conflicts
- Git configuration issues

**Resolution:**

**Step 1: Check permissions**
```bash
# Verify write access
ls -la .workflow/

# Create directory if missing
mkdir -p .workflow/worktrees/

# Fix permissions if needed
chmod -R u+w .workflow/
```

**Step 2: Check disk space**
```bash
# Check available space
df -h .

# Should have at least 1GB free for worktrees
```

**Step 3: Clean up existing worktrees**
```bash
# List all worktrees
git worktree list

# Output example:
# /home/user/project        abc1234 [main]
# /home/user/project/.workflow/worktrees/backend  def5678 [epic/042/backend]

# Remove stale worktrees
git worktree prune

# Force remove if needed
rm -rf .workflow/worktrees/*

# Verify cleanup
git worktree list
# Should only show main directory
```

**Step 4: Test worktree creation manually**
```bash
# Try creating a test worktree
git worktree add .workflow/worktrees/test-backend -b test-branch

# If successful, remove
git worktree remove .workflow/worktrees/test-backend
git branch -D test-branch
```

**Step 5: Check git configuration**
```bash
# Verify git version (needs 2.5+)
git --version

# Check worktree config
git config --list | grep worktree
```

**Prevention:**
- Ensure sufficient disk space before running workflow
- Clean up worktrees after failed runs
- Use git 2.5 or newer
- Don't manually delete worktree directories (use git worktree remove)

---

### 3.2 False Positive Parallel Detection

**Symptom:**
```
✅ Parallel execution enabled

Parallel Analysis:
  Files: 6
  Domains: 2
  Viable: true
  Reason: 6 files across 2 domains with 50% overlap

[Later: Merge conflicts due to shared files]
```

**Root Cause:**
- File overlap threshold too high (default 30%)
- Files incorrectly classified into different domains
- Shared infrastructure files (models, types) not detected

**Resolution:**

**Step 1: Review parallel analysis**
```bash
# Check detailed analysis
cat .workflow/outputs/EPIC-042/parallel_analysis.json | jq .

# Look for:
# - file_overlap_percentage (should be < 30%)
# - domains (check file classifications)
```

**Step 2: Adjust thresholds**

Edit execute-workflow.md to use stricter thresholds:

```bash
# More conservative settings
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  "${EPIC_DIR}/implementation-details/file-tasks.md" \
  --min-files 10 \        # Higher minimum (default: 5)
  --min-domains 3 \       # More domains required (default: 2)
  --max-overlap 20.0      # Lower overlap tolerance (default: 30.0)
```

**Step 3: Force sequential execution**

If parallel keeps causing issues:

```bash
# Option 1: Set in workflow
EXECUTION_MODE="sequential"
echo "➡️ Forcing sequential execution"

# Option 2: Reduce file count in file-tasks.md
# (Split epic into smaller chunks)
```

**Step 4: Review domain classification**

Check if files are classified correctly:

```python
# Test classification manually
python3 << EOF
from parallel_detection import classify_file

# Test your file paths
print(classify_file("src/backend/api/routes.py"))  # Should be "backend"
print(classify_file("src/frontend/components/Email.tsx"))  # Should be "frontend"
print(classify_file("src/models/email.py"))  # Might be "backend" or "other"
EOF
```

**Prevention:**
- Use conservative thresholds (min 10 files, max 20% overlap)
- Review parallel analysis before executing
- Separate shared infrastructure into dedicated domain
- Keep shared files (models, types) in one domain

---

### 3.3 Worktree Merge Conflicts

**Symptom:**
```
❌ Phase 1C: Sequential Merge FAILED

Cannot merge worktree changes back to main.

Error: Merge conflict in src/backend/api/__init__.py
```

**Root Cause:**
Multiple agents modified overlapping files despite parallel detection passing.

**Resolution:**

**Step 1: Identify conflict**
```bash
# View conflict markers
cat src/backend/api/__init__.py

# Should show:
# <<<<<<< HEAD
# [main branch version]
# =======
# [worktree version]
# >>>>>>> epic/042/backend
```

**Step 2: Navigate to worktree (if merge in progress)**
```bash
# List worktrees
git worktree list

# Navigate to problematic worktree
cd .workflow/worktrees/backend

# Check status
git status
```

**Step 3: Resolve conflict manually**

**Option A: Accept worktree changes**
```bash
# Edit file to remove conflict markers
nano src/backend/api/__init__.py

# Keep the changes you want, remove markers:
# <<<<<<< HEAD
# =======
# >>>>>>> epic/042/backend

# Stage resolved file
git add src/backend/api/__init__.py

# Complete merge (if in progress)
git merge --continue
```

**Option B: Use merge tool**
```bash
# Configure merge tool (optional)
git config merge.tool vimdiff

# Launch merge tool
git mergetool src/backend/api/__init__.py

# Resolve conflicts interactively
```

**Step 4: Return to main directory**
```bash
# Back to project root
cd ../../..

# Verify merge completed
git status
```

**Step 5: Clean up worktree**
```bash
# Remove merged worktree
git worktree remove .workflow/worktrees/backend

# Prune references
git worktree prune
```

**Prevention:**
- Lower overlap threshold (--max-overlap 10)
- Review parallel plan for implicit dependencies
- Ensure agents don't modify shared files
- Use sequential execution for highly coupled changes

---

### 3.4 Agent Fails in Worktree

**Symptom:**
```
❌ Domain: backend implementation FAILED

Agent in worktree .workflow/worktrees/backend encountered errors.

Results file not created.
```

**Root Cause:**
- Agent crashed or timed out
- File permissions in worktree
- Missing dependencies in worktree
- Agent tried to access files outside worktree scope

**Resolution:**

**Step 1: Navigate to worktree**
```bash
cd .workflow/worktrees/backend

# Check git status
git status

# Check what files were modified
git diff
```

**Step 2: Check for partial work**
```bash
# List created files
git status --short | grep "^??"

# List modified files
git status --short | grep "^ M"

# Check agent output location
ls -la .workflow/outputs/EPIC-042/
```

**Step 3: Review error logs**
```bash
# Check if results file exists
cat .workflow/outputs/EPIC-042/backend_results.json

# Or check for error messages
find .workflow/outputs/EPIC-042/ -name "*error*"
```

**Step 4: Clean up failed worktree**
```bash
# Return to main directory
cd ../../..

# Remove worktree
git worktree remove --force .workflow/worktrees/backend

# Delete orphaned branch
git branch -D epic/042/backend

# Prune worktree list
git worktree prune
```

**Step 5: Retry with sequential execution**
```bash
# Force sequential mode
/execute-workflow EPIC-042
# (Parallel detection will fail due to cleanup, forcing sequential)
```

**Prevention:**
- Ensure all dependencies available in clean git checkout
- Don't rely on uncommitted files
- Keep agents focused on their assigned files only
- Test implementation agents in isolation first

---

## 4. Validation Issues

### 4.1 Validation Commands Not Found

**Symptom:**
```
❌ Phase 2: Validation FAILED

Validation command not found: npm run validate

Error: Missing script: "validate"
```

**Root Cause:**
package.json doesn't have required validation scripts.

**Resolution:**

**Step 1: Check existing scripts**
```bash
# View current scripts
cat package.json | jq '.scripts'

# Or manually
grep -A 10 '"scripts"' package.json
```

**Step 2: Add validation scripts**

**For Python projects:**
```json
{
  "name": "your-project",
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",
    "typecheck:py": "mypy src/ --strict",
    "validate": "npm run lint:py && npm run format:py:check && npm run typecheck:py"
  }
}
```

**For TypeScript projects:**
```json
{
  "name": "your-project",
  "scripts": {
    "lint": "eslint src/ --ext .ts,.tsx",
    "lint:fix": "eslint src/ --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write src/",
    "format:check": "prettier --check src/",
    "validate": "npm run lint && npm run type-check && npm run format:check"
  }
}
```

**For polyglot (Python + TypeScript) projects:**
```json
{
  "name": "your-project",
  "scripts": {
    "validate:python": "ruff check src/backend/ && mypy src/backend/",
    "validate:typescript": "eslint src/frontend/ && tsc --noEmit",
    "validate": "npm run validate:python && npm run validate:typescript"
  }
}
```

**Step 3: Install dependencies**

**Python:**
```bash
pip install ruff mypy
```

**TypeScript:**
```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin typescript prettier
```

**Step 4: Test validation**
```bash
# Run validation manually
npm run validate

# Should execute all checks
```

**Prevention:**
- Add validation scripts during project setup
- Document required dependencies in README
- Include in project template/boilerplate
- Test validation before first workflow run

---

### 4.2 Validation Fails Repeatedly (Max 3 Attempts)

**Symptom:**
```
❌ Validation failed on attempt 3

⚠️  Maximum validation attempts (3) reached

Validation failed after 3 attempts.
Logs: .workflow/outputs/EPIC-042/validation/

Manual intervention recommended but workflow will continue.
```

**Root Cause:**
Build fixer agent cannot automatically fix complex errors:
- Type incompatibility issues
- Missing data structures
- Architectural mismatches
- Logic errors requiring spec clarification

**Resolution:**

**Step 1: Review all attempt logs**
```bash
# Check all validation attempts
cat .workflow/outputs/EPIC-042/validation/attempt_1.log
cat .workflow/outputs/EPIC-042/validation/attempt_2.log
cat .workflow/outputs/EPIC-042/validation/attempt_3.log

# Compare to see if errors reduced
diff .workflow/outputs/EPIC-042/validation/attempt_1.log \
     .workflow/outputs/EPIC-042/validation/attempt_3.log
```

**Step 2: Review fixer results**
```bash
# Check what fixer attempted
cat .workflow/outputs/EPIC-042/fix_attempt_1.json | jq .
cat .workflow/outputs/EPIC-042/fix_attempt_2.json | jq .
cat .workflow/outputs/EPIC-042/fix_attempt_3.json | jq .

# Look for remaining_issues
jq -r '.remaining_issues[]' .workflow/outputs/EPIC-042/fix_attempt_3.json
```

**Step 3: Categorize remaining errors**

**Type hint errors:**
```bash
# Example error:
# src/backend/service.py:42: Missing type hint for 'db' parameter

# Fix manually:
nano src/backend/service.py

# Add type hints:
from sqlalchemy.ext.asyncio import AsyncSession

async def get_email(email_id: int, db: AsyncSession) -> Email:
    ...
```

**Type compatibility errors:**
```bash
# Example error:
# src/backend/api.py:25: Incompatible return type: expected Email, got Optional[Email]

# Fix manually:
nano src/backend/api.py

# Handle None case:
async def get_email(email_id: int) -> Email:
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email  # Now guaranteed to be Email, not None
```

**Import errors:**
```bash
# Example error:
# src/backend/routes.py:5: Unused import 'HTTPException'

# Fix manually:
nano src/backend/routes.py

# Remove or use the import
# from fastapi import HTTPException  # ❌ Remove if unused
```

**Step 4: Run validation manually**
```bash
# Test your fixes
npm run validate

# Or run specific checks
ruff check .
mypy src/
```

**Step 5: Commit fixes**
```bash
git add .
git commit -m "fix(EPIC-042): Fix remaining validation errors after workflow"
```

**Prevention:**
- Improve prescriptive plan with type hints examples
- Add validation requirements to agent briefings
- Include validation in implementation agent's checklist
- Run validation during implementation phase (not just after)

---

### 4.3 Build Fixer Agent Doesn't Fix Anything

**Symptom:**
```
🔧 Deploying build fixer agent (attempt 1)...

Build fixer result: failed
  ⚠️  Build fixer could not fix all issues
    - All errors remain unfixed
```

**Root Cause:**
- Agent can't parse error messages
- Errors require manual intervention
- Auto-fix tools not installed
- Agent definition outdated

**Resolution:**

**Step 1: Check error message format**
```bash
# View raw validation output
cat .workflow/outputs/EPIC-042/validation/attempt_1.log

# Errors should have file:line:column format:
# ✅ GOOD: src/api.py:15:5: error: Missing type hint
# ❌ BAD: Type checking failed (no location)
```

**Step 2: Test auto-fix tools manually**
```bash
# Test ruff auto-fix
ruff check --fix .

# Test ruff format
ruff format .

# Check if errors reduced
npm run validate
```

**Step 3: Update build fixer agent definition**

Edit `~/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md`:

```markdown
## Auto-Fix Strategy

1. **Run ruff auto-fixes:**
   ```bash
   ruff check --fix .
   ruff format .
   ```

2. **Parse mypy errors:**
   ```bash
   mypy src/ 2>&1 | grep "error:"
   ```

3. **Add type hints for common patterns:**
   - Missing parameter types: Add `: Type` after parameter
   - Missing return types: Add `-> ReturnType:` after function signature
   - Optional types: Use `Optional[Type]` or `Type | None`

4. **Document unfixable errors in remaining_issues**
```

**Step 4: Verify agent has access to tools**

Check that build fixer agent can execute:
```bash
# In agent definition, ensure these commands work:
which ruff
which mypy
ruff --version
mypy --version
```

**Prevention:**
- Install auto-fix tools globally
- Test build fixer agent independently
- Update agent definition with new error patterns
- Add examples of common fixes to agent briefing

---

### 4.4 Custom Validation Scripts Fail

**Symptom:**
```
❌ Validation FAILED

Error: python3 tools/validate_architecture.py failed with exit code 1

Architecture validation errors:
- Backend imports frontend modules (src/backend/api.py imports src/frontend/types.py)
```

**Root Cause:**
Custom validation script (validate_architecture.py or validate_contracts.py) detected issues.

**Resolution:**

**Step 1: Review custom validation output**
```bash
# Run validation manually for details
python3 tools/validate_architecture.py

# Or
python3 tools/validate_contracts.py
```

**Step 2: Understand the violation**

**Architecture violations:**
- Layer boundary violations (backend importing frontend)
- Circular dependencies
- Unauthorized imports

**Contract violations:**
- API response doesn't match OpenAPI schema
- Missing required fields
- Type mismatches

**Step 3: Fix violations**

**For architecture violations:**
```bash
# Example: Backend imports frontend
# src/backend/api.py:
# from src.frontend.types import EmailType  # ❌ WRONG

# Fix: Move shared types to common module
mkdir -p src/common/types/
mv src/frontend/types.py src/common/types/email_types.py

# Update imports:
# src/backend/api.py:
from src.common.types.email_types import EmailType  # ✅ CORRECT

# src/frontend/components.tsx:
import { EmailType } from '../common/types/email_types'  # ✅ CORRECT
```

**For contract violations:**
```bash
# Example: Response missing required field
# OpenAPI schema requires 'created_at' field

# Fix: Add missing field to response model
# src/backend/models/email.py:
class Email(Base):
    id: int
    subject: str
    created_at: datetime  # ✅ Add missing field
```

**Step 4: Re-run custom validation**
```bash
python3 tools/validate_architecture.py
# Should pass now

python3 tools/validate_contracts.py
# Should pass now
```

**Step 5: Update validation rules (if too strict)**

If validation rules are too strict:

```python
# tools/validate_architecture.py

# Adjust layer definitions
ALLOWED_IMPORTS = {
    "backend": ["backend", "common", "models"],  # Add "common"
    "frontend": ["frontend", "common"],           # Add "common"
}
```

**Prevention:**
- Run custom validations during implementation
- Include architecture rules in agent briefings
- Document layer boundaries clearly
- Add examples of allowed/disallowed imports

---

## 5. GitHub Integration Issues

### 5.1 GitHub CLI Not Authenticated

**Symptom:**
```
ℹ️ GitHub CLI not authenticated - skipping issue creation

Run: gh auth login
```

**Root Cause:**
`gh` CLI is installed but not authenticated with GitHub.

**Resolution:**

**Step 1: Authenticate**
```bash
# Start authentication flow
gh auth login

# Follow prompts:
# 1. Select GitHub.com
# 2. Choose HTTPS or SSH
# 3. Authenticate via web browser or token
```

**Step 2: Verify authentication**
```bash
# Check status
gh auth status

# Should show:
# ✓ Logged in to github.com as <username>
# ✓ Token: *******************
```

**Step 3: Test GitHub access**
```bash
# List your repos
gh repo list

# View current repo
gh repo view
```

**Step 4: Re-run workflow**
```bash
# GitHub integration will now work
/execute-workflow EPIC-042
```

**Prevention:**
- Authenticate gh CLI during initial setup
- Add to documentation/README
- Include in project setup checklist

---

### 5.2 GitHub API Rate Limit

**Symptom:**
```
⚠️ GitHub API rate limit exceeded

Issue creation failed. Continuing workflow without GitHub integration.
```

**Root Cause:**
Exceeded GitHub API rate limits (5000 requests/hour for authenticated users).

**Resolution:**

**Step 1: Check rate limit status**
```bash
# View current rate limit
gh api rate_limit

# Output shows:
# {
#   "rate": {
#     "limit": 5000,
#     "remaining": 0,
#     "reset": 1729347600
#   }
# }
```

**Step 2: Wait for reset**
```bash
# Calculate reset time
date -d @1729347600

# Wait until reset time, then retry
```

**Step 3: Continue workflow without GitHub**
```bash
# Workflow continues automatically (GitHub is non-blocking)
# Issues won't be created, but work completes
```

**Step 4: Create issue manually (optional)**
```bash
# After rate limit resets, create issue manually
gh issue create \
  --title "EPIC-042: Add Email Validation" \
  --body "$(cat .tasks/backlog/EPIC-042-*/spec.md)" \
  --label "type:epic"
```

**Prevention:**
- Use GitHub integration sparingly
- Batch issue creation
- Monitor rate limit usage
- Consider GitHub Enterprise for higher limits

---

### 5.3 GitHub Issue Creation Fails

**Symptom:**
```
❌ Failed to create GitHub epic issue

Error: GraphQL: Resource not found

Continuing workflow without GitHub integration.
```

**Root Cause:**
- Repository not found
- No remote configured
- Insufficient permissions
- Private repo without access

**Resolution:**

**Step 1: Check repository configuration**
```bash
# View remotes
git remote -v

# Should show:
# origin  git@github.com:user/repo.git (fetch)
# origin  git@github.com:user/repo.git (push)
```

**Step 2: Verify repository exists**
```bash
# Check repo exists
gh repo view

# If not found, create or link:
gh repo create my-repo --private
# OR
git remote add origin git@github.com:user/repo.git
```

**Step 3: Check permissions**
```bash
# Test permissions
gh issue create --title "Test" --body "Test issue"

# If fails with permission error:
# - Check you have write access to repo
# - Check repo allows issues (Settings > Features > Issues)
```

**Step 4: Test issue creation manually**
```bash
# Try creating simple issue
echo "Test content" | gh issue create --title "Test" --body-file -

# If successful, workflow should work next time
gh issue close <issue-number>
```

**Prevention:**
- Verify GitHub repo setup before first workflow run
- Test `gh` CLI manually first
- Ensure repository has Issues enabled
- Check user permissions (write access required)

---

### 5.4 Sub-Issue Linking Fails

**Symptom:**
```
✅ Created epic issue #42
❌ Failed to create sub-issue for domain: backend

Error: Unable to post comment to epic

Sub-issues will not be linked.
```

**Root Cause:**
- Epic issue number not saved correctly
- Comment creation fails
- Network issues

**Resolution:**

**Step 1: Check if epic issue exists**
```bash
# List recent issues
gh issue list --limit 20

# Find epic issue
gh issue view 42
```

**Step 2: Manually link sub-issues**
```bash
# Create sub-issue
SUB_ISSUE=$(gh issue create \
  --title "EPIC-042: Backend Implementation" \
  --body "Domain: backend\n\nParent Epic: #42" \
  --label "type:task,domain:backend")

# Link to epic with comment
gh issue comment 42 --body "🔗 Sub-task: #${SUB_ISSUE} (backend)"
```

**Step 3: Verify linking**
```bash
# View epic issue
gh issue view 42

# Should show comment with sub-issue link
```

**Prevention:**
- Test GitHub integration with simple epic first
- Check network connectivity before workflow
- Ensure API token has full repo permissions

---

## 6. Agent Failures

### 6.1 Agent Timeout

**Symptom:**
```
❌ Phase 1: Implementation FAILED

Agent timeout after 30 minutes.

Partial results may be available.
```

**Root Cause:**
- Epic too large (too many files)
- Agent stuck in loop
- Complex implementation requirements
- Agent waiting for user input

**Resolution:**

**Step 1: Check for partial results**
```bash
# Look for any created files
git status

# Check results file (may be partial)
cat .workflow/outputs/EPIC-042/phase1_results.json
```

**Step 2: Review agent output**
```bash
# Check what agent accomplished
git diff

# List new files
git status --short | grep "^??"
```

**Step 3: Split epic into smaller chunks**
```bash
# Create multiple smaller epics
/spec-epic
# Epic 1: Create models only
# Epic 2: Create API routes only
# Epic 3: Add validation only

# Run workflows sequentially
/execute-workflow EPIC-042-A
/execute-workflow EPIC-042-B
/execute-workflow EPIC-042-C
```

**Step 4: Increase timeout (if needed)**

Edit `execute-workflow.md`:

```markdown
# Increase Task tool timeout
Task(
    subagent_type="general-purpose",
    description="Implementation for EPIC-042",
    prompt="...",
    timeout_minutes=60  # Increase from default 30
)
```

**Prevention:**
- Keep epics small (<10 files)
- Break large features into multiple epics
- Use parallel execution for large epics
- Set realistic timeouts based on epic size

---

### 6.2 Agent Produces Invalid Results

**Symptom:**
```
❌ Phase 1: Implementation FAILED

Results file is invalid:

Error: JSON parse error at line 15
Expected '}', got ','
```

**Root Cause:**
- Agent didn't follow results format
- JSON syntax error
- Incomplete results file

**Resolution:**

**Step 1: Check results file**
```bash
# View raw results
cat .workflow/outputs/EPIC-042/phase1_results.json

# Try to pretty-print (will show error location)
jq . .workflow/outputs/EPIC-042/phase1_results.json
```

**Step 2: Fix JSON manually**
```bash
# Common issues:
# - Trailing comma: {"key": "value",}  # ❌
# - Missing quotes: {key: value}        # ❌
# - Unclosed brackets: {"key": "value"  # ❌

# Fix manually
nano .workflow/outputs/EPIC-042/phase1_results.json

# Validate
jq . .workflow/outputs/EPIC-042/phase1_results.json
```

**Step 3: If results missing entirely**

Create minimal valid results:

```bash
cat > .workflow/outputs/EPIC-042/phase1_results.json << 'EOF'
{
  "status": "partial",
  "epic_id": "EPIC-042",
  "agent_type": "implementation-agent-v1",
  "execution_mode": "sequential",
  "files_created": [],
  "files_modified": [],
  "issues_encountered": [
    {
      "description": "Agent failed to produce valid results",
      "resolution": "Manual results file created"
    }
  ],
  "completion_timestamp": "2025-10-19T14:30:00Z"
}
EOF
```

**Step 4: Continue workflow**
```bash
# Workflow will proceed with partial results
# Manual implementation required
```

**Prevention:**
- Update agent definition with clear JSON format
- Add JSON validation to agent checklist
- Include example results in agent definition
- Test agents with simple epics first

---

### 6.3 Agent Doesn't Follow Prescriptive Plan

**Symptom:**
```
✅ Phase 1: Implementation Complete

Files created: 3
Expected files: 8

Agent created subset of required files.
```

**Root Cause:**
- Agent ignored some tasks from file-tasks.md
- Agent misinterpreted instructions
- Agent encountered errors and stopped early

**Resolution:**

**Step 1: Compare expected vs actual**
```bash
# Extract expected files from file-tasks.md
grep -E "^###\s+\`" .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md

# Compare with created files
git status --short

# Or from results
jq -r '.files_created[]' .workflow/outputs/EPIC-042/phase1_results.json
```

**Step 2: Check agent reasoning**
```bash
# Look for issues_encountered in results
jq -r '.issues_encountered[]' .workflow/outputs/EPIC-042/phase1_results.json

# Check if agent explained why files were skipped
```

**Step 3: Complete missing files manually**
```bash
# Identify missing files
# Example: models/email.py not created

# Create manually
nano src/backend/models/email.py

# Implement according to file-tasks.md
```

**Step 4: Update agent briefing**

Edit `~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md`:

```markdown
## CRITICAL: Complete ALL Tasks

You MUST create/modify EVERY file listed in file-tasks.md.

Before finishing:
1. Read file-tasks.md completely
2. Create checklist of all files
3. Verify each file created/modified
4. Don't skip files due to complexity
5. Document issues but still attempt implementation
```

**Prevention:**
- Make file-tasks.md extremely explicit
- Number each task (1. Create X, 2. Create Y)
- Add verification checklist to agent definition
- Review agent results before proceeding to validation

---

## 7. Git Issues

### 7.1 Commit Fails

**Symptom:**
```
❌ Phase 5: Commit FAILED

Error: Author identity unknown

fatal: unable to auto-detect email address
```

**Root Cause:**
Git user.name and user.email not configured.

**Resolution:**

**Step 1: Check git configuration**
```bash
# Check current config
git config user.name
git config user.email

# If empty, configure
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Step 2: Verify configuration**
```bash
git config --list | grep user
# Should show:
# user.name=Your Name
# user.email=your.email@example.com
```

**Step 3: Retry commit**
```bash
# Workflow should have changes staged
git status

# Commit manually if needed
git commit -m "feat(EPIC-042): Add email validation"
```

**Prevention:**
- Configure git during initial setup
- Add to project README/setup instructions
- Include in onboarding checklist

---

### 7.2 Push Fails (Remote Rejection)

**Symptom:**
```
❌ Git push failed

Error: remote rejected
! [remote rejected] main -> main (pre-receive hook declined)
```

**Root Cause:**
- Remote branch protected
- Pre-receive hook failure
- Insufficient permissions
- Network issues

**Resolution:**

**Step 1: Check remote status**
```bash
# View remote configuration
git remote -v

# Test connection
git fetch origin
```

**Step 2: Check branch protection**
```bash
# If pushing to protected branch (main/master)
# Create feature branch instead:
git checkout -b feat/epic-042-email-validation

# Push feature branch
git push -u origin feat/epic-042-email-validation

# Create PR on GitHub
gh pr create --title "feat(EPIC-042): Add email validation" --body "..."
```

**Step 3: Check pre-receive hooks**
```bash
# Hook might require:
# - Specific commit message format
# - Tests passing
# - No merge commits

# View commit message
git log -1

# Amend if needed
git commit --amend -m "feat(EPIC-042): add email validation\n\nImplements email validation with regex pattern."
```

**Step 4: Force push (use with caution)**
```bash
# Only if you're sure and have permissions
git push --force-with-lease origin feat/epic-042-email-validation
```

**Prevention:**
- Always push to feature branches, not main
- Check branch protection rules before workflow
- Follow commit message conventions
- Test push access before running workflow

---

### 7.3 Worktree Conflicts Persist

**Symptom:**
```
❌ Cannot remove worktree

Error: worktree 'epic/042/backend' is locked
```

**Root Cause:**
- Worktree in use by another process
- Git lock files present
- Worktree directory deleted manually

**Resolution:**

**Step 1: Check worktree status**
```bash
# List all worktrees
git worktree list

# Check if directory exists
ls -la .workflow/worktrees/backend/
```

**Step 2: Unlock worktree**
```bash
# Remove lock file
rm -f .workflow/worktrees/backend/.git/worktrees/backend/gitdir.lock

# Or force unlock
git worktree unlock .workflow/worktrees/backend
```

**Step 3: Force remove**
```bash
# Force remove worktree
git worktree remove --force .workflow/worktrees/backend

# Or manually
rm -rf .workflow/worktrees/backend/
git worktree prune
```

**Step 4: Clean up branches**
```bash
# Delete associated branch
git branch -D epic/042/backend

# Verify cleanup
git worktree list
git branch -a
```

**Prevention:**
- Never delete worktree directories manually
- Always use `git worktree remove`
- Clean up after failed workflows
- Don't interrupt workflow during worktree operations

---

## 8. Recovery Procedures

### 8.1 Abort Workflow Mid-Execution

**When to use:** Workflow is stuck, producing errors, or needs to be stopped.

**Procedure:**

**Step 1: Stop current agent**
```bash
# If agent is running, interrupt:
Ctrl+C

# Agent may finish current task before stopping
```

**Step 2: Check workflow state**
```bash
# Check git status
git status

# Check worktrees
git worktree list

# Check outputs
ls -la .workflow/outputs/EPIC-042/
```

**Step 3: Clean up partial work**

**If changes are good (keep them):**
```bash
# Commit partial work
git add .
git commit -m "chore: Partial implementation from EPIC-042 workflow"
```

**If changes are bad (discard them):**
```bash
# Discard all changes
git reset --hard HEAD
git clean -fd

# Remove untracked files
rm -rf .workflow/outputs/EPIC-042/
```

**Step 4: Clean up worktrees**
```bash
# Remove all worktrees
for wt in .workflow/worktrees/*; do
  git worktree remove --force "$wt"
done

# Prune
git worktree prune

# Delete worktree branches
git branch -D $(git branch | grep "epic/042/")
```

**Step 5: Restart workflow**
```bash
# Re-run from beginning
/execute-workflow EPIC-042
```

---

### 8.2 Recover from Failed Validation

**When to use:** Validation failed 3 times, workflow continued, you need to fix errors.

**Procedure:**

**Step 1: Review validation logs**
```bash
# Check final validation attempt
cat .workflow/outputs/EPIC-042/validation/attempt_3.log

# Review fixer attempts
cat .workflow/outputs/EPIC-042/fix_attempt_3.json
```

**Step 2: Run validation manually**
```bash
# See current errors
npm run validate

# Or run specific checks
ruff check .
mypy src/
```

**Step 3: Fix errors systematically**

Create checklist:
```bash
# List all errors
npm run validate 2>&1 | grep "error:" > errors.txt

# Fix one by one
# Edit files, re-run validation after each fix
```

**Step 4: Commit fixes**
```bash
# Once validation passes
git add .
git commit -m "fix(EPIC-042): Fix validation errors after workflow"
```

**Step 5: Update workflow artifacts**
```bash
# Update validation results (optional)
cat > .workflow/outputs/EPIC-042/validation/result.json << EOF
{
  "status": "passed",
  "attempts": 4,
  "manual_fixes": true,
  "timestamp": "$(date -Iseconds)"
}
EOF
```

---

### 8.3 Rollback Workflow Changes

**When to use:** Workflow completed but changes are wrong, need to undo everything.

**Procedure:**

**Step 1: Identify workflow commit**
```bash
# Find workflow commit (should have "Generated with Claude Code" in message)
git log --oneline | grep -i "epic-042"

# Or check recent commits
git log --oneline -10
```

**Step 2: Review changes**
```bash
# View diff for commit
git show <commit-hash>

# Check if this is the right commit to revert
```

**Step 3: Revert commit**

**Option A: Soft revert (keep files, undo commit)**
```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Files still modified, can edit and recommit
git status
```

**Option B: Hard revert (discard everything)**
```bash
# Undo commit and discard all changes
git reset --hard HEAD~1

# All files reverted to previous state
```

**Option C: Create revert commit (safe for pushed commits)**
```bash
# Create new commit that undoes changes
git revert <commit-hash>

# This is safe for shared branches
```

**Step 4: Clean up artifacts**
```bash
# Remove workflow outputs
rm -rf .workflow/outputs/EPIC-042/

# Remove worktrees if any
git worktree prune
```

**Step 5: Push revert (if already pushed)**
```bash
# Push revert commit
git push origin main

# Or force push reset (dangerous!)
git push --force-with-lease origin main
```

---

### 8.4 Resume After Network Failure

**When to use:** Workflow interrupted by network issues, especially during GitHub operations.

**Procedure:**

**Step 1: Check workflow state**
```bash
# Determine which phase was running
ls -la .workflow/outputs/EPIC-042/

# Files present:
# - parallel_analysis.json → Phase 0 complete
# - phase1_results.json → Phase 1 complete
# - validation/result.json → Phase 2 complete
```

**Step 2: Check git state**
```bash
git status
git log -1
```

**Step 3: Resume based on phase**

**If interrupted during Phase 1 (Implementation):**
```bash
# Check for partial results
cat .workflow/outputs/EPIC-042/phase1_results.json

# If results exist but incomplete, re-run implementation
/execute-workflow EPIC-042
```

**If interrupted during Phase 2 (Validation):**
```bash
# Re-run validation manually
npm run validate

# If passes, continue to commit
git add .
git commit -m "feat(EPIC-042): ..."
```

**If interrupted during GitHub operations:**
```bash
# Check network
ping github.com

# Verify gh CLI
gh auth status

# Manually create issue if needed
gh issue create --title "EPIC-042: ..." --body "..."
```

**Step 4: Complete workflow manually**
```bash
# If workflow can't resume, finish manually:

# 1. Verify implementation complete
git status

# 2. Run validation
npm run validate

# 3. Commit
git add .
git commit -m "feat(EPIC-042): Add email validation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push
git push origin main

# 5. Create GitHub issue manually (optional)
gh issue create --title "EPIC-042: Email Validation" --body "$(cat .tasks/backlog/EPIC-042-*/spec.md)"
```

---

## Getting Help

If issues persist after troubleshooting:

**1. Check documentation:**
- [WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md) - Setup and integration
- [WORKFLOW_EXAMPLE.md](./WORKFLOW_EXAMPLE.md) - Complete example walkthrough
- [VALIDATION_SYSTEM.md](./VALIDATION_SYSTEM.md) - Validation details
- [PARALLEL_DETECTION_COMPLETE.md](./PARALLEL_DETECTION_COMPLETE.md) - Parallel execution

**2. Review artifacts:**
```bash
# Check all workflow outputs
find .workflow/outputs/EPIC-042/ -type f -exec echo "=== {} ===" \; -exec cat {} \;
```

**3. Check logs:**
```bash
# Implementation results
cat .workflow/outputs/EPIC-042/phase1_results.json | jq .

# Validation logs
cat .workflow/outputs/EPIC-042/validation/attempt_*.log

# Build fixer results
cat .workflow/outputs/EPIC-042/fix_attempt_*.json | jq .
```

**4. Validate setup:**
```bash
# Check dependencies
which python3 ruff mypy gh git

# Check git configuration
git config --list

# Check file structure
tree .tasks/ -L 3
```

**5. Test components independently:**
```bash
# Test parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md

# Test validation
npm run validate

# Test GitHub CLI
gh issue list
```

---

## Quick Diagnostic Commands

```bash
# Full system check
echo "=== Git Status ==="
git status
echo ""

echo "=== Git Config ==="
git config user.name
git config user.email
echo ""

echo "=== Worktrees ==="
git worktree list
echo ""

echo "=== Dependencies ==="
which python3 ruff mypy gh git
echo ""

echo "=== Workflow Outputs ==="
ls -la .workflow/outputs/EPIC-042/
echo ""

echo "=== Package.json Scripts ==="
cat package.json | jq '.scripts'
echo ""

echo "=== Epic Files ==="
find .tasks/backlog/EPIC-042-* -type f
```

Save as `.workflow/diagnose.sh` and run: `bash .workflow/diagnose.sh`

---

**End of Comprehensive Troubleshooting Guide**
