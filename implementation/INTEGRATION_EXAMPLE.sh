#!/bin/bash
# Integration Example: Using Parallel Detection in Workflow
#
# This script demonstrates how the parallel detection logic would be
# integrated into the Tier 1 workflow command.

set -e

# Configuration
EPIC_ID="${1:-EPIC-007}"
TASKS_DIR="${HOME}/.tasks"

# Find epic directory
EPIC_DIR=$(find "$TASKS_DIR" -name "${EPIC_ID}-*" -type d | head -1)

if [ -z "$EPIC_DIR" ]; then
    echo "❌ Epic not found: $EPIC_ID"
    exit 1
fi

echo "📁 Epic directory: $EPIC_DIR"
echo ""

# Locate file-tasks.md
FILE_TASKS="${EPIC_DIR}/implementation-details/file-tasks.md"

if [ ! -f "$FILE_TASKS" ]; then
    echo "❌ file-tasks.md not found at: $FILE_TASKS"
    exit 1
fi

echo "📄 Analyzing: $FILE_TASKS"
echo ""

# Run parallel detection
PARALLEL_RESULT=$(python3 "$(dirname "$0")/parallel_detection.py" "$FILE_TASKS")

# Parse result
VIABLE=$(echo "$PARALLEL_RESULT" | jq -r '.viable')
REASON=$(echo "$PARALLEL_RESULT" | jq -r '.reason')
FILE_COUNT=$(echo "$PARALLEL_RESULT" | jq -r '.file_count')
DOMAIN_COUNT=$(echo "$PARALLEL_RESULT" | jq -r '.domain_count')
OVERLAP=$(echo "$PARALLEL_RESULT" | jq -r '.file_overlap_percentage')
RECOMMENDATION=$(echo "$PARALLEL_RESULT" | jq -r '.recommendation')

# Display results
echo "═══════════════════════════════════════════════════"
echo "  Parallel Execution Analysis: $EPIC_ID"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📊 Statistics:"
echo "   - Files to modify/create: $FILE_COUNT"
echo "   - Domains involved: $DOMAIN_COUNT"
echo "   - File overlap: $OVERLAP%"
echo ""

if [ "$VIABLE" = "true" ]; then
    echo "✅ VIABLE FOR PARALLEL EXECUTION"
    echo ""
    echo "📝 Reason: $REASON"
    echo ""
    echo "🔀 Parallel Execution Plan:"
    echo ""

    # Extract domains
    DOMAINS=$(echo "$PARALLEL_RESULT" | jq -r '.parallel_plan | keys[]')

    for DOMAIN in $DOMAINS; do
        TASK_DESC=$(echo "$PARALLEL_RESULT" | jq -r ".parallel_plan.${DOMAIN}.task_description")
        FILES=$(echo "$PARALLEL_RESULT" | jq -r ".parallel_plan.${DOMAIN}.files[]")
        FILE_COUNT_DOMAIN=$(echo "$FILES" | wc -l)

        echo "   🏷️  Domain: $DOMAIN"
        echo "      Task: $TASK_DESC"
        echo "      Files:"
        echo "$FILES" | sed 's/^/         - /'
        echo ""
    done

    echo "═══════════════════════════════════════════════════"
    echo "  Next Steps"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "1. Create worktrees for each domain:"
    echo ""
    for DOMAIN in $DOMAINS; do
        echo "   python3 tools/worktree_manager/worktree_manager.py create \\"
        echo "     --epic $EPIC_ID \\"
        echo "     --task-name $DOMAIN \\"
        echo "     --base-branch dev"
        echo ""
    done

    echo "2. Deploy agents in parallel (single message with multiple Task calls)"
    echo ""
    echo "3. Merge results sequentially after all agents complete"
    echo ""
    echo "4. Cleanup worktrees"

else
    echo "➡️  SEQUENTIAL EXECUTION RECOMMENDED"
    echo ""
    echo "📝 Reason: $REASON"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Next Steps"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "1. Deploy single implementation agent"
    echo ""
    echo "2. Agent follows file-tasks.md sequentially"
    echo ""
    echo "3. No worktree creation needed"
fi

echo ""
echo "💾 Full JSON output saved to: parallel_plan.json"
echo "$PARALLEL_RESULT" | jq '.' > parallel_plan.json

exit 0
