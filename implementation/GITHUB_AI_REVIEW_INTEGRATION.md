# GitHub AI Review Integration for Tier1 Workflow

**Status:** ✅ Implemented in template
**Version:** 1.0.0
**Date:** 2025-10-29

---

## Overview

Tier1 workflow now includes automatic GitHub integration with @claude and @codex AI review:

1. **Epic → GitHub Issue:** Epics automatically create GitHub issues
2. **Feature Branches:** Workflow creates feature branches automatically
3. **Pull Requests:** PRs created with AI review tags (@claude, @codex)
4. **AI Review:** Both Claude (GitHub Actions) and Codex (optional) review every PR

---

## What Was Added

### 1. @claude Mention Trigger (GitHub Actions)

**File:** `.github/workflows/claude.yml`

**Triggers on:**
- Issue comments containing `@claude`
- PR comments containing `@claude`
- PR reviews containing `@claude`
- New issues with `@claude` in title/body

**How it works:**
1. User mentions `@claude` in issue/PR
2. GitHub Actions workflow triggers
3. Claude Code CLI invoked with context
4. Response posted as comment
5. Total time: 30-60 seconds

### 2. PR Creation with AI Review Tags

**File:** `tools/github_integration/pr_with_ai_review.py`

**Automatically:**
- Creates feature branch: `feature/EPIC-XXX-slug`
- Opens PR to `main` (or specified base branch)
- Posts comment with @claude and @codex review requests
- Saves PR info for workflow tracking

### 3. Execute-Workflow Integration

**Updated:** `.claude/commands/execute-workflow.md`

**New Phase 5.3:**
- After creating commit
- Creates feature branch from current work
- Opens PR with implementation summary
- Posts AI review request comment
- Continues with epic completion

### 4. Documentation

**Created:**
- `.github/workflows/QUICK_REFERENCE.md` - TL;DR usage guide
- `.github/workflows/MENTION_TRIGGERS_SETUP.md` - Complete setup instructions
- `.github/workflows/scripts/verify-mention-triggers.sh` - Setup verification

---

## Setup Requirements

### For @claude (GitHub Actions)

**One-time setup per repository:**

1. **Generate OAuth token:**
   ```bash
   claude /token
   ```

2. **Add to GitHub secrets:**
   - Go to repo Settings → Secrets → Actions
   - Create secret: `CLAUDE_CODE_OAUTH_TOKEN`
   - Paste token value

3. **Verify workflow file exists:**
   ```bash
   ls .github/workflows/claude.yml
   ```

**That's it!** @claude will respond to mentions in 30-60 seconds.

### For @codex (Optional - Codex Cloud)

1. Sign up at https://developers.openai.com/codex/cloud
2. Connect GitHub repository
3. Enable Code Review feature
4. Test with `@codex review` in PR

---

## How It Works (Full Flow)

### Epic Creation (`/spec-epic`)

1. User creates epic specification
2. GitHub issue created automatically
3. Issue labeled: `epic`, `status:planned`, domain labels
4. Users can mention `@claude` in issue for spec review

### Epic Execution (`/execute-workflow EPIC-XXX`)

1. **Phase 0:** Preflight checks (including GitHub verification)
2. **Phase 1:** Implementation (sequential or parallel)
3. **Phase 2:** Validation (build, lint, type checks)
4. **Phase 5:**
   - **Step 5.1:** Generate commit message
   - **Step 5.2:** Create commit
   - **Step 5.3:** ✨ NEW - Create feature branch and PR with AI review
   - **Step 5.4:** Move epic to completed
   - **Step 5.5:** Close GitHub epic issue

5. **Phase 6:** Post-mortem analysis

### PR Creation (Automatic in Phase 5.3)

```python
# Automatically creates:
feature_branch = "feature/epic-007-add-semantic-search"
pr_title = "EPIC-007: Add Semantic Search"
pr_body = """
## Summary
Sequential implementation completed with 8 new files and 12 modified files.

## Epic Details
- **Epic ID:** EPIC-007
- **Branch:** `feature/epic-007-add-semantic-search`
- **Base:** `main`

## Checklist
- [ ] Code quality verified
- [ ] Tests passing
- [ ] Documentation updated
- [ ] AI review addressed
"""

# Then posts review comment:
"""
## 🤖 AI Review Requested

@claude Please review this PR for:
- Code quality and best practices
- Type safety and error handling
- Architecture compliance
- Security considerations

@codex review

---
*Epic: EPIC-007*
*Automated review request from tier1 workflow*
"""
```

### AI Review Process

**@claude reviews:**
1. User sees review comment posted automatically
2. Claude analyzes PR context (files, diffs, CLAUDE.md)
3. Posts review with findings in ~30-60 seconds
4. User addresses feedback
5. Can ask follow-up: `@claude Please clarify the type safety concern`

**@codex reviews (if configured):**
1. Codex Cloud detects `@codex review`
2. Analyzes PR diffs
3. Posts inline comments on specific lines
4. Identifies potential bugs, style issues

---

## Usage Examples

### In GitHub Issues

**Spec review:**
```
@claude Review .tasks/backlog/EPIC-007/spec.md and suggest improvements
```

**Architecture questions:**
```
@claude Based on our architecture, should this be a new service or added to EmailService?
```

### In Pull Requests

**Code review:**
```
@claude Review this PR focusing on:
- Type safety
- Error handling
- Architecture compliance
```

**Follow-up:**
```
@claude The type error on line 45 is confusing. Can you explain what's wrong?
```

**Codex review:**
```
@codex review
```

---

## Benefits

### For Development

1. **Automatic PR creation:** No manual branch/PR setup
2. **AI review by default:** Every PR gets reviewed
3. **Fast feedback:** 30-60 seconds for @claude response
4. **Continuous improvement:** AI identifies patterns across PRs

### For Code Quality

1. **Catch issues early:** Type errors, security concerns before human review
2. **Architecture compliance:** AI knows project patterns from CLAUDE.md
3. **Best practices:** Identifies anti-patterns and suggests improvements
4. **Documentation:** AI can review specs, docs, and suggest clarity improvements

### For Workflow

1. **Zero manual setup:** Workflow handles branch/PR/review automatically
2. **Observable:** All AI interactions in GitHub comments (audit trail)
3. **Non-blocking:** AI review failures don't stop workflow
4. **Optional:** Can disable @claude mentions if not needed

---

## Configuration Options

### Customize PR Base Branch

Edit `tools/github_integration/pr_with_ai_review.py`:

```python
# Default: main
base_branch = "main"

# Change to:
base_branch = "dev"  # or "master", etc.
```

### Customize AI Review Request

Edit `tools/github_integration/pr_with_ai_review.py`:

```python
review_comment = f"""## 🤖 AI Review Requested

@claude Please review this PR for:
- YOUR CUSTOM REVIEW CRITERIA HERE

@codex review
"""
```

### Disable PR Creation

Comment out Phase 5.3 in `.claude/commands/execute-workflow.md`:

```bash
# ### Step 5.3: Create Feature Branch and Pull Request with AI Review
# (commented out - no PR creation)
```

### Disable @claude Mentions

Delete `.github/workflows/claude.yml` or disable workflow in GitHub Settings.

---

## Troubleshooting

### @claude not responding

**Check:**
1. Workflow run in Actions tab
2. `CLAUDE_CODE_OAUTH_TOKEN` secret exists
3. Claude Code CLI version (`claude --version`)
4. Exact mention format: `@claude` (no space)

**Fix:**
```bash
# Regenerate token
claude /token

# Update GitHub secret
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

### PR creation fails

**Check:**
1. Git working directory clean before workflow
2. `gh` CLI authenticated (`gh auth status`)
3. Commit created successfully (Phase 5.2)
4. Python script has execute permissions

**Fix:**
```bash
# Authenticate gh CLI
gh auth login

# Verify Python script
python3 tools/github_integration/pr_with_ai_review.py --help
```

### Branch already exists

**Error:** `fatal: A branch named 'feature/epic-007-...' already exists`

**Fix:** Workflow checks out new branch from committed state. If branch exists:
```bash
# Delete old branch
git branch -D feature/epic-007-...

# Re-run workflow
```

---

## Deployment to Projects

### For New Projects

Tier1 deployment automatically includes:
```bash
/tier1-deploy ~/my-new-project
```

This installs:
- `.github/workflows/claude.yml`
- `tools/github_integration/pr_with_ai_review.py`
- Updated `/execute-workflow` command
- Documentation files

**Then:**
1. Set `CLAUDE_CODE_OAUTH_TOKEN` secret
2. Test `@claude` mention in any issue

### For Existing Tier1 Projects

**Option A: Full tier1 update (recommended):**
```bash
# From tier1_workflow_global
./tools/sync_tier1_to_projects.sh ~/my-project
```

**Option B: Manual file copy:**
```bash
# Copy workflow file
cp ~/tier1_workflow_global/template/.github/workflows/claude.yml \
   ~/my-project/.github/workflows/

# Copy PR helper
cp ~/tier1_workflow_global/template/tools/github_integration/pr_with_ai_review.py \
   ~/my-project/tools/github_integration/

# Copy updated execute-workflow command
cp ~/tier1_workflow_global/template/.claude/commands/execute-workflow.md \
   ~/my-project/.claude/commands/

# Copy documentation
cp ~/tier1_workflow_global/template/.github/workflows/*.md \
   ~/my-project/.github/workflows/
```

---

## Security Considerations

### OAuth Token Security

- **Storage:** Encrypted GitHub secret (not in code)
- **Scope:** Token only used for Claude Code CLI
- **Rotation:** Generate new token every 90 days
- **Revocation:** `claude /logout` revokes immediately

### Workflow Permissions

```yaml
permissions:
  issues: write          # Post comments
  pull-requests: write   # Post PR comments
  contents: read         # Read repository code
```

**Does NOT have:**
- `contents: write` - Cannot push code
- `admin` - Cannot change settings

### Data Privacy

**@claude (GitHub Actions):**
- Code analyzed in GitHub Actions runner
- Claude Code CLI processes locally in runner
- No code stored by Anthropic
- Audit trail in Actions logs

**@codex (Codex Cloud):**
- Code sent to OpenAI servers
- Subject to OpenAI data policies
- Optional (can disable)

---

## Metrics & Monitoring

### Track @claude Usage

```bash
# Count @claude mentions in last 30 days
gh api repos/:owner/:repo/issues \
  --jq '[.[] | select(.created_at > (now - 30*86400) and (.body | contains("@claude")))] | length'
```

### Workflow Success Rate

```bash
# Check claude.yml workflow runs
gh run list --workflow=claude.yml --limit 20 --json conclusion
```

### PR Creation Rate

```bash
# Count PRs with AI review tags
gh pr list --search "AI Review Requested" --state all --json number | jq 'length'
```

---

## Future Enhancements

**Potential additions:**

1. **@claude auto-review:** Trigger on every PR (not just when mentioned)
2. **AI review checklist:** Auto-generate review checklist from CLAUDE.md
3. **Review quality scoring:** Track AI suggestions accepted/rejected
4. **Custom review templates:** Per-domain review focus areas
5. **Integration with code coverage:** AI reviews untested code first

---

## Summary

✅ **@claude:** GitHub Actions workflow, 30-60s response time
✅ **@codex:** Optional Codex Cloud integration
✅ **Automatic:** PR creation with AI review tags
✅ **Secure:** OAuth tokens, scoped permissions
✅ **Non-blocking:** Failures don't stop workflow
✅ **Observable:** All interactions logged

**Deployment status:** Ready for use in all tier1 projects

**Next steps:**
1. Deploy to existing projects
2. Set CLAUDE_CODE_OAUTH_TOKEN secrets
3. Test @claude mentions
4. Monitor usage and feedback

---

**Version:** 1.0.0
**Date:** 2025-10-29
**Author:** Tier1 Workflow Team
