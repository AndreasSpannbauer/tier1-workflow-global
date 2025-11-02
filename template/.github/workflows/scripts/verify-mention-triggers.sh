#!/bin/bash
# Verify @claude and @codex mention triggers setup

set -e

echo "🔍 Verifying @claude and @codex mention triggers setup..."
echo ""

ERRORS=0

# Check 1: Workflow file exists
echo "1. Checking workflow file..."
if [ -f ".github/workflows/claude.yml" ]; then
    echo "   ✅ claude.yml exists"
else
    echo "   ❌ claude.yml not found"
    ((ERRORS++))
fi
echo ""

# Check 2: Workflow has correct triggers
echo "2. Checking workflow triggers..."
if grep -q "issue_comment" .github/workflows/claude.yml && \
   grep -q "pull_request_review" .github/workflows/claude.yml && \
   grep -q "@claude" .github/workflows/claude.yml; then
    echo "   ✅ Workflow configured for @claude mentions"
else
    echo "   ❌ Workflow missing required triggers"
    ((ERRORS++))
fi
echo ""

# Check 3: GitHub secret exists (can't verify content, only presence)
echo "3. Checking GitHub secrets..."
if gh secret list 2>/dev/null | grep -q "CLAUDE_CODE_OAUTH_TOKEN"; then
    echo "   ✅ CLAUDE_CODE_OAUTH_TOKEN secret exists"
else
    echo "   ⚠️  CLAUDE_CODE_OAUTH_TOKEN secret not found (or gh CLI not authenticated)"
    echo "   Run: gh auth login"
    echo "   Then add secret: gh secret set CLAUDE_CODE_OAUTH_TOKEN"
    ((ERRORS++))
fi
echo ""

# Check 4: Claude Code CLI installed
echo "4. Checking Claude Code CLI..."
if command -v claude &> /dev/null; then
    VERSION=$(claude --version 2>&1 || echo "unknown")
    echo "   ✅ Claude Code CLI installed ($VERSION)"
else
    echo "   ⚠️  Claude Code CLI not installed"
    echo "   Install: npm install -g @anthropic-ai/claude-code"
fi
echo ""

# Check 5: Documentation present
echo "5. Checking documentation..."
if [ -f ".github/workflows/QUICK_REFERENCE.md" ] && \
   [ -f ".github/workflows/MENTION_TRIGGERS_SETUP.md" ]; then
    echo "   ✅ Documentation files present"
else
    echo "   ⚠️  Documentation files missing"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! @claude mention trigger is ready."
    echo ""
    echo "Test it now:"
    echo "1. Open any issue in this repository"
    echo "2. Comment: @claude Hello! Can you summarize this project?"
    echo "3. Wait 30-60 seconds for response"
else
    echo "⚠️  Found $ERRORS issue(s). Review output above."
    echo ""
    echo "Setup guide: .github/workflows/MENTION_TRIGGERS_SETUP.md"
fi
echo "═══════════════════════════════════════════════"

exit $ERRORS
