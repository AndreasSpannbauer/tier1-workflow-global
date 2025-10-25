#!/bin/bash
#
# Tier1 Workflow Pre-Commit Hook
#
# Validates constitutional compliance before allowing commits.
# - Article III (simulation code): BLOCKS commit
# - Other articles: WARNS only
#
# Installation:
#   cp tools/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#

set -e

echo "🔍 Running Tier1 constitutional validation..."

# Change to project root (hook runs from .git/hooks/)
cd "$(git rev-parse --show-toplevel)"

# CRITICAL: Detect simulation code (BLOCKS on failure)
if [ -f "tools/detect_simulation_code.py" ]; then
    echo "  → Checking Article III (No Simulation Code)..."
    if ! python3 tools/detect_simulation_code.py src/ 2>&1; then
        echo ""
        echo "❌ COMMIT BLOCKED: Simulation code detected (Article III violation)"
        echo ""
        echo "Constitutional Article III requires REAL implementations only."
        echo "Agents must report blockers instead of creating fake/mock code."
        echo ""
        echo "Action required:"
        echo "1. Review violations above"
        echo "2. Replace simulations with real implementations"
        echo "3. OR report blocker using Agent Failure Reporting Protocol"
        echo ""
        exit 1
    fi
fi

# OPTIONAL: Other constitutional checks (WARNS, doesn't block)
if [ -f "tools/validate_constitutional_compliance.py" ]; then
    echo "  → Checking Articles II, IV, VI (warnings only)..."
    python3 tools/validate_constitutional_compliance.py 2>&1 || true  # Don't block
fi

# OPTIONAL: Architecture validation (if exists)
if [ -f "tools/validate_architecture.py" ]; then
    echo "  → Checking architecture boundaries..."
    python3 tools/validate_architecture.py 2>&1 || true  # Don't block
fi

echo ""
echo "✅ Validation complete - commit allowed"
echo ""

exit 0
