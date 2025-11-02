# 🚀 Quick Reference: @claude & @codex

## ⚡ TL;DR

**@claude:** ✅ Configured (needs CLAUDE_CODE_OAUTH_TOKEN secret)
**@codex:** ⏳ Optional (requires separate Codex Cloud setup)

## 🎯 Usage

### @claude (GitHub Actions)

Mention @claude in any issue or PR comment:

```
@claude Please review this code for security issues
```

**Expected behavior:**
1. Workflow triggers (~5 seconds)
2. Claude analyzes context (~30 seconds)
3. Response posted as comment
4. Total: 30-60 seconds

### @codex (Codex Cloud - Optional)

If you've set up Codex Cloud:

```
@codex review
```

This triggers Codex's built-in code review feature.

## 📋 Setup Checklist

- [ ] `CLAUDE_CODE_OAUTH_TOKEN` secret configured in GitHub repo
- [ ] `.github/workflows/claude.yml` workflow file present
- [ ] Claude Code CLI authentication working
- [ ] (Optional) Codex Cloud configured for @codex

## 🎓 Quick Examples

**Code Review:**
```
@claude Review this PR for type safety and error handling
```

**Architecture Advice:**
```
@claude Based on our architecture, what's the best way to add real-time notifications?
```

**Security Analysis:**
```
@claude Security review focusing on authentication and input validation
```

**Spec Review:**
```
@claude Review .tasks/backlog/EPIC-XXX/spec.md and suggest improvements
```

## 🔧 Troubleshooting

**@claude not responding?**
1. Check Actions tab for workflow run
2. Verify `CLAUDE_CODE_OAUTH_TOKEN` secret exists
3. Check workflow logs for errors
4. Ensure you used `@claude` (not `@ claude`)

**Want faster responses?**
- Use specific, focused questions
- Reference specific files or line numbers
- Provide context about what you're trying to achieve

## 📖 Full Documentation

- Complete setup guide: `.github/workflows/MENTION_TRIGGERS_SETUP.md`
- Usage examples: `.github/workflows/USAGE_GUIDE.md`
- Setup verification: `.github/workflows/scripts/verify-mention-triggers.sh`
