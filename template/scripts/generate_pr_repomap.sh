#!/bin/bash
#
# Generate scoped repomap for PR changed files
# Usage: ./scripts/generate_pr_repomap.sh <PR_NUMBER> [output_file]
#

set -e

PR_NUM="$1"
OUTPUT_FILE="${2:-workspace/pr-exports/PR-${PR_NUM}-repomap.txt}"

if [ -z "$PR_NUM" ]; then
    echo "Usage: $0 <PR_NUMBER> [output_file]"
    exit 1
fi

echo "Generating scoped repomap for PR #${PR_NUM}..."

# Create output directory
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Get list of changed files in the PR
CHANGED_FILES=$(gh pr view "$PR_NUM" --json files --jq '.files[].path' | tr '\n' ' ')

if [ -z "$CHANGED_FILES" ]; then
    echo "Error: No changed files found in PR #${PR_NUM}"
    exit 1
fi

echo "Changed files: $CHANGED_FILES"

# Generate repomap focusing on changed files and their dependencies
cat > "$OUTPUT_FILE" <<EOF
# Scoped Repository Map for PR #${PR_NUM}

## Changed Files
$(gh pr view "$PR_NUM" --json files --jq '.files[] | "- \(.path) (+\(.additions)/-\(.deletions))"')

## File Structure

EOF

# For each changed file, show its location in the tree
for file in $CHANGED_FILES; do
    if [ -f "$file" ]; then
        echo "### $file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"

        # Show file tree context (3 levels up and down)
        FILE_DIR=$(dirname "$file")
        FILE_NAME=$(basename "$file")

        # Tree structure
        tree -L 2 -I '__pycache__|*.pyc|node_modules|.git' "$FILE_DIR" 2>/dev/null >> "$OUTPUT_FILE" || true
        echo "" >> "$OUTPUT_FILE"

        # Show imports/dependencies if it's a code file
        if [[ "$file" =~ \.(py|ts|tsx|js|jsx)$ ]]; then
            echo "#### Imports/Dependencies:" >> "$OUTPUT_FILE"

            if [[ "$file" =~ \.py$ ]]; then
                # Python imports
                grep -E "^(from|import) " "$file" 2>/dev/null | head -20 >> "$OUTPUT_FILE" || echo "No imports found" >> "$OUTPUT_FILE"
            elif [[ "$file" =~ \.(ts|tsx|js|jsx)$ ]]; then
                # TypeScript/JavaScript imports
                grep -E "^import " "$file" 2>/dev/null | head -20 >> "$OUTPUT_FILE" || echo "No imports found" >> "$OUTPUT_FILE"
            fi

            echo "" >> "$OUTPUT_FILE"
        fi

        # Show function/class definitions
        if [[ "$file" =~ \.py$ ]]; then
            echo "#### Structure (Python):" >> "$OUTPUT_FILE"
            grep -E "^(class|def|async def) " "$file" 2>/dev/null >> "$OUTPUT_FILE" || echo "No classes/functions found" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        elif [[ "$file" =~ \.(ts|tsx)$ ]]; then
            echo "#### Structure (TypeScript):" >> "$OUTPUT_FILE"
            grep -E "^(export )?(class|interface|type|function|const|async function) " "$file" 2>/dev/null | head -20 >> "$OUTPUT_FILE" || echo "No definitions found" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    fi
done

# Add related files that import changed files (reverse dependencies)
cat >> "$OUTPUT_FILE" <<EOF

## Reverse Dependencies (files that import changed files)

EOF

for file in $CHANGED_FILES; do
    if [[ "$file" =~ \.(py|ts|tsx|js|jsx)$ ]]; then
        FILE_BASE=$(basename "$file" | sed 's/\.[^.]*$//')
        echo "### Files importing $file:" >> "$OUTPUT_FILE"

        # Search for imports of this file
        if [[ "$file" =~ \.py$ ]]; then
            # Python - search for imports
            grep -r "from.*${FILE_BASE}\|import.*${FILE_BASE}" --include="*.py" . 2>/dev/null | grep -v "__pycache__" | head -10 >> "$OUTPUT_FILE" || echo "No reverse dependencies found" >> "$OUTPUT_FILE"
        elif [[ "$file" =~ \.(ts|tsx|js|jsx)$ ]]; then
            # TypeScript/JavaScript - search for imports
            grep -r "from.*${FILE_BASE}\|import.*${FILE_BASE}" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null | grep -v "node_modules" | head -10 >> "$OUTPUT_FILE" || echo "No reverse dependencies found" >> "$OUTPUT_FILE"
        fi

        echo "" >> "$OUTPUT_FILE"
    fi
done

# Add summary statistics
cat >> "$OUTPUT_FILE" <<EOF

## Summary

- Total changed files: $(echo "$CHANGED_FILES" | wc -w)
- PR URL: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pull/${PR_NUM}
- Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

EOF

echo "✓ Repomap generated: $OUTPUT_FILE"
echo "  Size: $(wc -l < "$OUTPUT_FILE") lines"
