# Tier 1 Workflow - Quick Reference Troubleshooting

**Last Updated:** 2025-10-19
**Quick lookup cheat sheet for common issues**

---

## Epic Not Found

```bash
# Problem: Epic directory not found for EPIC-042
# Fix:
ls .tasks/backlog/ | grep 042
find .tasks -name "*042*" -type d
```

---

## Missing Epic Files

```bash
# Problem: Missing spec.md, architecture.md, or file-tasks.md
# Fix:
/refine-epic EPIC-042

# Verify:
ls .tasks/backlog/EPIC-042-*/
ls .tasks/backlog/EPIC-042-*/implementation-details/
```

---

## Git Not Clean

```bash
# Problem: Uncommitted changes detected
# Fix Option 1 (commit):
git add . && git commit -m "WIP: Prepare for workflow"

# Fix Option 2 (stash):
git stash push -m "Before EPIC-042"

# Verify:
git status  # Should show "nothing to commit"
```

---

## Missing Dependencies

```bash
# Problem: ruff, mypy, or other tools not found
# Fix (Python):
pip install ruff mypy

# Fix (TypeScript):
npm install --save-dev eslint typescript prettier

# Verify:
ruff --version
mypy --version
```

---

## Parallel Detection Fails

```bash
# Problem: python3 not found or parallel_detection.py errors
# Fix:
which python3  # Check if installed
python3 --version  # Should be 3.8+

# Test script:
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md
```

---

## Worktree Creation Fails

```bash
# Problem: Cannot create worktree (permission denied)
# Fix:
mkdir -p .workflow/worktrees/
chmod -R u+w .workflow/

# Clean up existing:
git worktree prune
rm -rf .workflow/worktrees/*

# Check disk space:
df -h .
```

---

## Worktree Won't Remove

```bash
# Problem: Worktree locked or in use
# Fix:
git worktree unlock .workflow/worktrees/backend
git worktree remove --force .workflow/worktrees/backend
git worktree prune

# Nuclear option:
rm -rf .workflow/worktrees/*
git worktree prune
git branch -D $(git branch | grep "epic/042/")
```

---

## Validation Commands Not Found

```bash
# Problem: npm run validate - script not found
# Fix (add to package.json):
{
  "scripts": {
    "validate": "ruff check . && mypy src/"
  }
}

# Or for TypeScript:
{
  "scripts": {
    "validate": "eslint src/ && tsc --noEmit"
  }
}

# Test:
npm run validate
```

---

## Validation Fails (Max Attempts)

```bash
# Problem: Validation failed 3 times
# Fix:
# 1. Review errors:
cat .workflow/outputs/EPIC-042/validation/attempt_3.log

# 2. Check what fixer tried:
cat .workflow/outputs/EPIC-042/fix_attempt_3.json | jq .

# 3. Run validation manually:
npm run validate

# 4. Fix errors one by one:
ruff check .  # Python lint
mypy src/     # Type check

# 5. Commit fixes:
git add . && git commit -m "fix(EPIC-042): Fix validation errors"
```

---

## Build Fixer Does Nothing

```bash
# Problem: Build fixer can't fix any errors
# Fix:
# 1. Test auto-fix manually:
ruff check --fix .
ruff format .

# 2. Check if errors reduced:
npm run validate

# 3. Update agent definition:
nano ~/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md
```

---

## GitHub Not Authenticated

```bash
# Problem: GitHub CLI not authenticated
# Fix:
gh auth login  # Follow prompts

# Verify:
gh auth status

# Test:
gh repo view
```

---

## GitHub API Rate Limit

```bash
# Problem: Rate limit exceeded
# Fix:
# Check limit:
gh api rate_limit

# Wait for reset (workflow continues anyway)
# GitHub integration is optional

# Manual issue creation after reset:
gh issue create --title "EPIC-042: ..." --body "..."
```

---

## Agent Timeout

```bash
# Problem: Agent timed out after 30 minutes
# Fix:
# 1. Check partial results:
git status
cat .workflow/outputs/EPIC-042/phase1_results.json

# 2. Split epic into smaller chunks:
/spec-epic  # Create EPIC-042-A (smaller scope)
/spec-epic  # Create EPIC-042-B (smaller scope)

# 3. Run smaller epics:
/execute-workflow EPIC-042-A
/execute-workflow EPIC-042-B
```

---

## Agent Invalid Results

```bash
# Problem: Results JSON is invalid
# Fix:
# Try to parse:
jq . .workflow/outputs/EPIC-042/phase1_results.json

# Fix manually or create minimal:
cat > .workflow/outputs/EPIC-042/phase1_results.json << 'EOF'
{
  "status": "partial",
  "epic_id": "EPIC-042",
  "files_created": [],
  "files_modified": [],
  "issues_encountered": [{"description": "Manual results"}]
}
EOF
```

---

## Commit Fails (No Identity)

```bash
# Problem: Git author identity unknown
# Fix:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Verify:
git config user.name
git config user.email

# Retry commit:
git commit -m "feat(EPIC-042): ..."
```

---

## Push Rejected

```bash
# Problem: Remote rejected push (protected branch)
# Fix:
# Create feature branch:
git checkout -b feat/epic-042-email-validation
git push -u origin feat/epic-042-email-validation

# Create PR:
gh pr create --title "feat(EPIC-042): ..." --body "..."
```

---

## Merge Conflicts

```bash
# Problem: Merge conflict during worktree merge
# Fix:
# 1. View conflict:
git status
cat <conflicted-file>

# 2. Edit file, remove markers:
# <<<<<<< HEAD
# =======
# >>>>>>> branch

# 3. Stage and continue:
git add <conflicted-file>
git merge --continue

# Or abort:
git merge --abort
```

---

## Emergency: Abort Workflow

```bash
# Stop workflow mid-execution
# Option 1 (keep changes):
git add .
git commit -m "chore: Partial work from EPIC-042"

# Option 2 (discard changes):
git reset --hard HEAD
git clean -fd

# Clean up worktrees:
for wt in .workflow/worktrees/*; do
  git worktree remove --force "$wt" 2>/dev/null
done
git worktree prune

# Restart:
/execute-workflow EPIC-042
```

---

## Emergency: Rollback Workflow

```bash
# Undo workflow commit
# Find commit:
git log --oneline | grep -i "epic-042"

# Revert (safe for pushed commits):
git revert <commit-hash>

# Or reset (local only):
git reset --hard HEAD~1

# Clean up:
rm -rf .workflow/outputs/EPIC-042/
```

---

## Common Error Messages

### ❌ Epic directory not found
→ Run: `ls .tasks/backlog/` or create epic with `/spec-epic`

### ❌ Git working directory not clean
→ Run: `git add . && git commit -m "WIP"` or `git stash`

### ❌ Missing script: "validate"
→ Add to package.json: `"validate": "ruff check . && mypy src/"`

### ❌ Validation failed after 3 attempts
→ Fix errors manually: `npm run validate` then fix issues

### ❌ Worktree creation failed
→ Run: `git worktree prune` and `rm -rf .workflow/worktrees/*`

### ❌ GitHub CLI not authenticated
→ Run: `gh auth login`

### ❌ Agent timeout
→ Split epic into smaller chunks

### ❌ Permission denied
→ Run: `chmod -R u+w .` or `sudo chown -R $USER:$USER .`

### ⚠️  Parallel detection failed
→ Check: `which python3` and test script manually

### ⚠️  Maximum validation attempts reached
→ Continue workflow, fix manually: `npm run validate`

---

## Diagnostic One-Liner

```bash
# Full system check (copy-paste this)
echo "=== Git ===" && git status --short && \
echo "=== Worktrees ===" && git worktree list && \
echo "=== Tools ===" && which python3 ruff mypy gh git && \
echo "=== Epic Files ===" && ls .tasks/backlog/EPIC-042-*/ && \
echo "=== Outputs ===" && ls -la .workflow/outputs/EPIC-042/ 2>/dev/null && \
echo "=== Package Scripts ===" && cat package.json | jq -r '.scripts | keys[]'
```

---

## Quick Recovery Commands

```bash
# Clean git state:
git reset --hard HEAD && git clean -fd

# Clean worktrees:
git worktree prune && rm -rf .workflow/worktrees/*

# Clean outputs:
rm -rf .workflow/outputs/EPIC-042/

# Reset git user:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Reinstall validation tools:
pip install ruff mypy && npm install --save-dev eslint typescript

# Re-authenticate GitHub:
gh auth login
```

---

## Severity Indicators

- 🔴 **CRITICAL** - Workflow cannot proceed
- ⚠️ **WARNING** - Workflow continues but may produce incomplete results
- ℹ️ **INFO** - Non-blocking, informational only

---

## Phase-Specific Quick Fixes

### Phase 0 (Preflight)
```bash
# Epic not found → /refine-epic EPIC-042
# Git not clean → git stash or git add . && git commit
# Python not found → Install Python 3.8+
```

### Phase 1 (Implementation)
```bash
# Agent timeout → Split epic into smaller chunks
# Invalid results → Check JSON syntax or create minimal results
# Permission denied → chmod -R u+w . or sudo chown
```

### Phase 1B (Parallel)
```bash
# Worktree fails → git worktree prune && rm -rf .workflow/worktrees/*
# Merge conflicts → Edit files, remove markers, git add && git merge --continue
# Overlap too high → Lower max-overlap threshold
```

### Phase 2 (Validation)
```bash
# Commands not found → Add "validate" script to package.json
# Max attempts → Fix errors manually: npm run validate
# Build fixer fails → Run ruff check --fix . manually
```

### Phase 5 (Commit/Push)
```bash
# No identity → git config --global user.name/email
# Push rejected → Use feature branch: git checkout -b feat/epic-042
# GitHub fails → Skip GitHub (non-blocking), create issue manually later
```

---

## When to Check Comprehensive Guide

Reference [TROUBLESHOOTING_COMPREHENSIVE.md](./TROUBLESHOOTING_COMPREHENSIVE.md) for:
- Detailed root cause analysis
- Step-by-step resolution procedures
- Prevention strategies
- Recovery procedures
- Related issues and cross-references

---

## Testing Checklist (Before First Workflow)

```bash
# ✅ Git configured
git config user.name && git config user.email

# ✅ Dependencies installed
ruff --version && mypy --version

# ✅ Package.json has validate script
cat package.json | jq '.scripts.validate'

# ✅ Parallel detection works
python3 ~/tier1_workflow_global/implementation/parallel_detection.py --help

# ✅ GitHub authenticated (optional)
gh auth status

# ✅ Epic files exist
ls .tasks/backlog/EPIC-042-*/spec.md
ls .tasks/backlog/EPIC-042-*/architecture.md
ls .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md

# ✅ Git clean
git status  # Should show "nothing to commit"
```

---

**For detailed troubleshooting, see [TROUBLESHOOTING_COMPREHENSIVE.md](./TROUBLESHOOTING_COMPREHENSIVE.md)**
