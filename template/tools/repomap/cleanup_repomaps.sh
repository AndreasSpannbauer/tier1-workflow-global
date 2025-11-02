#!/bin/bash
# Cleanup script for repository map files
# These files are auto-generated and can be safely removed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🧹 Repository Map Cleanup Script"
echo "================================"
echo ""

cd "$PROJECT_ROOT"

# Count files before cleanup
REPOMAP_DIR_COUNT=$(find . -type d -name "repomaps" 2>/dev/null | wc -l)
REPOMAP_TXT_COUNT=$(find . -name "repomap-*.txt" 2>/dev/null | wc -l)
REPOMAP_PDF_COUNT=$(find . -name "repomap-*.pdf" 2>/dev/null | wc -l)
TOTAL_COUNT=$((REPOMAP_TXT_COUNT + REPOMAP_PDF_COUNT))

if [ "$TOTAL_COUNT" -eq 0 ] && [ "$REPOMAP_DIR_COUNT" -eq 0 ]; then
    echo "✅ No repomap files or directories found. Nothing to clean up."
    exit 0
fi

echo "Found repomap files:"
echo "  - Text files: $REPOMAP_TXT_COUNT"
echo "  - PDF files: $REPOMAP_PDF_COUNT"
echo "  - Directories: $REPOMAP_DIR_COUNT"
echo "  - Total: $TOTAL_COUNT"
echo ""

# Calculate total size
if [ "$TOTAL_COUNT" -gt 0 ]; then
    TOTAL_SIZE=$(find . -name "repomap-*.txt" -o -name "repomap-*.pdf" 2>/dev/null | xargs du -ch 2>/dev/null | tail -1 | cut -f1 || echo "0")
    echo "Total size: $TOTAL_SIZE"
    echo ""
fi

# Show files to be deleted
echo "Files to be deleted:"
find . -name "repomap-*.txt" -o -name "repomap-*.pdf" 2>/dev/null | sort

if [ "$REPOMAP_DIR_COUNT" -gt 0 ]; then
    echo ""
    echo "Directories to be deleted:"
    find . -type d -name "repomaps" 2>/dev/null | sort
fi
echo ""

# Ask for confirmation unless --force is provided
if [ "$1" != "--force" ] && [ "$1" != "-f" ]; then
    read -p "Delete these files and directories? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled."
        exit 1
    fi
fi

# Delete files
echo "Deleting files..."
find . -name "repomap-*.txt" -delete 2>/dev/null || true
find . -name "repomap-*.pdf" -delete 2>/dev/null || true

# Delete directories (only if empty or contain only timestamped subdirs)
if [ "$REPOMAP_DIR_COUNT" -gt 0 ]; then
    echo "Deleting directories..."
    find . -type d -name "repomaps" -exec rm -rf {} + 2>/dev/null || true
fi

echo ""
echo "✅ Cleanup complete! Deleted $TOTAL_COUNT files"
echo ""
echo "💡 Tip: Repomap files are typically ignored by git (.gitignore)"
echo "💡 Use generate_repomap.py to create new repomaps when needed"
