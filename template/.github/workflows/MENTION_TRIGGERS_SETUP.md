# @claude and @codex Mention Triggers Setup

**Status:** Template file (configure during tier1 deployment)

This document explains how to set up @claude and @codex mention triggers in your GitHub repository.

---

## Overview

**@claude trigger:** Responds to mentions in issues and PRs using Claude Code CLI
**@codex trigger:** (Optional) Uses Codex Cloud's built-in code review feature

---

## Part 1: @claude Setup (GitHub Actions)

### Step 1: Get Claude Code OAuth Token

```bash
# Generate OAuth token
claude /token

# Copy the output token (starts with "claude_...")
```

### Step 2: Add Secret to GitHub Repository

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CLAUDE_CODE_OAUTH_TOKEN`
5. Value: Paste the token from Step 1
6. Click **Add secret**

### Step 3: Verify Workflow File

The workflow file `.github/workflows/claude.yml` should already be present (installed by tier1). Verify it exists:

```bash
ls -la .github/workflows/claude.yml
```

### Step 4: Test @claude Trigger

1. Open any GitHub issue in your repository
2. Add a comment: `@claude Hello! Can you read CLAUDE.md and summarize the project?`
3. Wait 30-60 seconds
4. Check for Claude's response comment

**Verify in Actions tab:**
- Go to **Actions** tab in GitHub
- Look for "Claude Code Mention Trigger" workflow runs
- Check logs if no response appears

---

## Part 2: @codex Setup (Optional - Codex Cloud)

@codex uses OpenAI's Codex Cloud service, which is separate from our GitHub Actions setup.

### Requirements

- Codex Cloud account (https://developers.openai.com/codex/cloud)
- Repository added to Codex Cloud
- Code Review feature enabled

### Setup Steps

1. **Sign up for Codex Cloud**
   - Visit https://developers.openai.com/codex/cloud
   - Create account or sign in

2. **Add Repository**
   - Connect your GitHub account
   - Select this repository
   - Grant necessary permissions

3. **Enable Code Review**
   - In Codex Cloud dashboard, go to repository settings
   - Enable "Code Review" feature
   - Configure review triggers (@codex mentions)

4. **Test @codex**
   - Open a PR
   - Comment: `@codex review`
   - Codex will analyze the PR and post review comments

---

## Part 3: Automatic PR Review Tags

When tier1 workflow creates PRs (via `/execute-workflow`), it automatically adds review request comments:

```markdown
## Review Requests

@claude Please review this PR for:
- Code quality and best practices
- Type safety and error handling
- Architecture compliance

@codex review
```

This happens automatically in the workflow command.

---

## Part 4: Verification

### Verify @claude Setup

Run the verification script:

```bash
./.github/workflows/scripts/verify-mention-triggers.sh
```

Expected output:
```
✅ claude.yml exists with correct triggers
✅ Workflow checks for @claude mentions
✅ CLAUDE_CODE_OAUTH_TOKEN secret exists
✅ Claude Code CLI installed
```

### Verify @codex Setup (Optional)

1. Check Codex Cloud dashboard
2. Verify repository is connected
3. Test with `@codex review` in a PR

---

## Usage Examples

### @claude: Code Review

```
@claude Review this PR for:
- Security vulnerabilities
- Type safety issues
- Best practices violations
```

### @claude: Architecture Questions

```
@claude Based on our service layer architecture, should this new feature be a separate service or added to EmailService?
```

### @claude: Spec Review

```
@claude Review .tasks/backlog/EPIC-007/spec.md and suggest improvements for the acceptance criteria
```

### @codex: Automated Code Review

```
@codex review
```

---

## Troubleshooting

### @claude not responding

**Check workflow runs:**
```bash
# View recent workflow runs
gh run list --workflow=claude.yml --limit 5

# View logs for specific run
gh run view <run-id> --log
```

**Common issues:**
1. **Secret not set:** Verify `CLAUDE_CODE_OAUTH_TOKEN` in repo settings
2. **Token expired:** Generate new token with `claude /token`
3. **Workflow disabled:** Check Settings → Actions → Enable workflows
4. **Mention not detected:** Use exact format `@claude` (no space)

### @codex not responding

**Codex Cloud issues:**
1. **Repository not connected:** Check Codex Cloud dashboard
2. **Feature disabled:** Enable Code Review in repository settings
3. **Permissions:** Grant Codex read access to repository

---

## Security Considerations

### @claude (GitHub Actions)

- **Token security:** OAuth token stored as GitHub secret (encrypted)
- **Permissions:** Workflow has read access to code, write access to comments
- **Audit:** All workflow runs logged in Actions tab
- **Revocation:** Revoke token anytime with `claude /logout`

### @codex (Codex Cloud)

- **Data sharing:** Code sent to OpenAI's Codex Cloud for analysis
- **Privacy:** Review OpenAI's data usage policies
- **Opt-out:** Remove repository from Codex Cloud anytime

---

## Maintenance

### Rotate Claude OAuth Token (Every 90 Days)

```bash
# Generate new token
claude /token

# Update GitHub secret
# Go to Settings → Secrets → CLAUDE_CODE_OAUTH_TOKEN → Update

# Old token automatically revoked after update
```

### Monitor Workflow Health

```bash
# Check recent workflow success rate
gh run list --workflow=claude.yml --limit 10 --json conclusion
```

### Update Workflow File

If `.github/workflows/claude.yml` needs updates from tier1_workflow_global:

```bash
# Copy latest version from tier1_workflow_global template
cp ~/tier1_workflow_global/template/.github/workflows/claude.yml .github/workflows/

# Commit update
git add .github/workflows/claude.yml
git commit -m "Update @claude mention trigger workflow"
git push
```

---

## Integration with Tier1 Workflow

### Automatic PR Creation with Review Tags

The `/execute-workflow` command automatically:

1. Creates feature branch: `feature/EPIC-XXX-slug`
2. Opens PR with title: `EPIC-XXX: Title`
3. Adds PR description with summary
4. **Posts review request comment:**
   ```
   @claude Review this PR for code quality, type safety, and architecture compliance
   @codex review
   ```

This ensures every PR gets AI review by default.

### Epic → Issue Sync

When creating epics with `/spec-epic`:

1. Epic created in `.tasks/backlog/EPIC-XXX/`
2. GitHub issue created automatically
3. Issue labeled with: `epic`, `status:planned`, domain labels
4. @claude can be mentioned in issue for spec review

---

## Summary

✅ **@claude:** GitHub Actions workflow, responds to mentions in 30-60 seconds
✅ **@codex:** Optional Codex Cloud integration for code review
✅ **Automatic:** PR creation includes review tags by default
✅ **Secure:** OAuth tokens stored as GitHub secrets
✅ **Auditable:** All interactions logged in GitHub Actions

**Ready to use after secret configuration!**
