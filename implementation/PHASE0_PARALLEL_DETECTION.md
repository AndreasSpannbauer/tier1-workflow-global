# Phase 0: Preflight Checks (Enhanced with Parallel Detection)

This document contains the enhanced Phase 0 section for execute-workflow.md with integrated parallel detection logic.

---

## PHASE 0: PREFLIGHT CHECKS

Verify the epic is ready for execution and analyze parallel execution opportunities before deploying any agents.

### Step 0.1: Find Epic Directory

```bash
EPIC_DIR=$(find .tasks -name "${ARGUMENTS}-*" -type d | head -1)
```

If not found:
```
❌ Epic directory not found for: ${ARGUMENTS}
Check: .tasks/backlog/${ARGUMENTS}-*/
Run: /task-list to view available epics
```

### Step 0.2: Verify Required Files

Check the following files exist and are complete:

```bash
# Required files
[ -f "${EPIC_DIR}/spec.md" ] || echo "MISSING: spec.md"
[ -f "${EPIC_DIR}/architecture.md" ] || echo "MISSING: architecture.md"
[ -f "${EPIC_DIR}/implementation-details/file-tasks.md" ] || echo "MISSING: file-tasks.md"
```

**Expected files:**
- ✅ `spec.md` - Epic specification with problem statement and requirements
- ✅ `architecture.md` - Architecture decisions and design
- ✅ `implementation-details/file-tasks.md` - Prescriptive implementation plan

If any files are missing:
```
❌ Epic not ready for execution

Missing files:
- [list missing files]

Run: /refine-epic ${ARGUMENTS}
```

### Step 0.3: Verify Git Working Directory

Check that the working directory is clean before starting:

```bash
git status --porcelain
```

If output is not empty:
```
❌ Git working directory not clean

Uncommitted changes detected:
[show git status output]

Commit or stash changes before running workflow:
git add .
git commit -m "Your commit message"

OR

git stash
```

### Step 0.4: Check Dependencies

Verify required tools are available:

```bash
# Check jq (required for parallel detection)
if ! command -v jq &> /dev/null; then
  echo "⚠️ jq not installed (required for parallel detection)"
  echo "   Install: sudo apt-get install jq"
  echo "   Defaulting to sequential execution"
  JQ_AVAILABLE="false"
else
  JQ_AVAILABLE="true"
fi

# Check parallel detection script
if [ ! -f ~/tier1_workflow_global/implementation/parallel_detection.py ]; then
  echo "⚠️ Parallel detection script not found"
  echo "   Expected: ~/tier1_workflow_global/implementation/parallel_detection.py"
  echo "   Defaulting to sequential execution"
  PARALLEL_SCRIPT_AVAILABLE="false"
else
  PARALLEL_SCRIPT_AVAILABLE="true"
fi
```

### Step 0.5: Analyze for Parallel Execution Opportunities

Determine if the epic is suitable for parallel execution based on domain separation and file overlap.

```bash
# Initialize defaults
EXECUTION_MODE="sequential"
PARALLEL_VIABLE="false"
FILE_COUNT=0
DOMAIN_COUNT=0
FILE_OVERLAP=0

# Only run parallel detection if dependencies are available
if [ "$JQ_AVAILABLE" = "true" ] && [ "$PARALLEL_SCRIPT_AVAILABLE" = "true" ]; then
  echo ""
  echo "🔍 Analyzing for parallel execution opportunities..."
  echo ""

  # Create output directory
  mkdir -p .workflow/outputs/${ARGUMENTS}

  # Run parallel detection
  PARALLEL_RESULT=$(python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
    "${EPIC_DIR}/implementation-details/file-tasks.md" 2>&1)

  # Check if parallel detection succeeded
  if [ $? -eq 0 ]; then
    # Parse result
    PARALLEL_VIABLE=$(echo "$PARALLEL_RESULT" | jq -r '.viable')
    PARALLEL_REASON=$(echo "$PARALLEL_RESULT" | jq -r '.reason')
    FILE_COUNT=$(echo "$PARALLEL_RESULT" | jq -r '.file_count')
    DOMAIN_COUNT=$(echo "$PARALLEL_RESULT" | jq -r '.domain_count')
    FILE_OVERLAP=$(echo "$PARALLEL_RESULT" | jq -r '.file_overlap_percentage')
    EXECUTION_MODE=$(echo "$PARALLEL_RESULT" | jq -r '.recommendation')

    # Store results for later phases
    echo "$PARALLEL_RESULT" > .workflow/outputs/${ARGUMENTS}/parallel_analysis.json

    # Display analysis results
    echo "📊 Parallel Execution Analysis:"
    echo "  Files to modify: ${FILE_COUNT}"
    echo "  Domains involved: ${DOMAIN_COUNT}"
    echo "  File overlap: ${FILE_OVERLAP}%"
    echo "  Recommendation: ${EXECUTION_MODE}"
    echo ""

    if [ "$PARALLEL_VIABLE" = "true" ]; then
      echo "✅ Parallel execution VIABLE"
      echo "   ${PARALLEL_REASON}"
      echo ""
      echo "   Domains:"
      echo "$PARALLEL_RESULT" | jq -r '.domains | to_entries[] | "     - \(.key): \(.value | length) files"'
      echo ""
    else
      echo "➡️ Sequential execution recommended"
      echo "   ${PARALLEL_REASON}"
      echo ""
    fi
  else
    # Parallel detection failed
    echo "⚠️ Parallel detection failed with error:"
    echo "$PARALLEL_RESULT"
    echo ""
    echo "Defaulting to sequential execution"
    EXECUTION_MODE="sequential"
    PARALLEL_VIABLE="false"
  fi
else
  echo ""
  echo "➡️ Sequential execution (parallel detection unavailable)"
  echo ""
fi
```

### Step 0.6: Store Execution Plan

Save the execution mode decision for Phase 1:

```bash
# Store execution mode decision
cat > .workflow/outputs/${ARGUMENTS}/execution_plan.json << EOF
{
  "execution_mode": "${EXECUTION_MODE}",
  "parallel_viable": ${PARALLEL_VIABLE},
  "reason": "${PARALLEL_REASON:-Sequential execution (default)}",
  "file_count": ${FILE_COUNT},
  "domain_count": ${DOMAIN_COUNT},
  "file_overlap_percentage": ${FILE_OVERLAP},
  "parallel_analysis_file": ".workflow/outputs/${ARGUMENTS}/parallel_analysis.json"
}
EOF
```

### Step 0.7: Display Epic Summary

Read and display epic information:

```bash
# Extract epic title
EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

# Display summary
echo "========================================="
echo "✅ Preflight Complete"
echo "========================================="
echo "Epic: ${ARGUMENTS}"
echo "Title: ${EPIC_TITLE}"
echo "Files: ${FILE_COUNT}"
echo "Execution mode: ${EXECUTION_MODE}"
echo "========================================="
echo ""
```

**If all checks pass, proceed to Phase 1.**

---

## Integration Notes

### Dependencies
- **jq**: Required for JSON parsing (install: `sudo apt-get install jq`)
- **parallel_detection.py**: Script location: `~/tier1_workflow_global/implementation/parallel_detection.py`

### Execution Flow
1. **Verify dependencies** (jq, parallel_detection.py)
2. **Run parallel detection** (after file verification)
3. **Parse results** (viability, domain breakdown, file overlap)
4. **Store execution plan** (for Phase 1 to read)
5. **Display summary** (includes execution mode)

### Graceful Degradation
- If jq missing → Sequential execution
- If parallel_detection.py missing → Sequential execution
- If parallel detection fails → Sequential execution
- Non-blocking: Missing dependencies don't halt workflow

### Parallel Detection Criteria
From `tier1_enhancement_assessment.md` section 1.2:
- **Minimum scope**: 5+ files changed across 2+ domains
- **File overlap threshold**: <30% shared files between tasks
- **Domain separation**: Backend, frontend, database, tests, docs
- **Dependency awareness**: Respects task dependencies

### Output Files
- `.workflow/outputs/${ARGUMENTS}/parallel_analysis.json` - Full parallel detection results
- `.workflow/outputs/${ARGUMENTS}/execution_plan.json` - Execution mode decision for Phase 1

### Visual Indicators
- ✅ Parallel execution viable
- ➡️ Sequential execution recommended
- ⚠️ Warning (missing dependencies, detection failure)
- 🔍 Analysis in progress
- 📊 Analysis results

### Error Handling
All parallel detection errors are caught and logged:
- Script execution errors → Sequential fallback
- JSON parsing errors → Sequential fallback
- Missing output → Sequential fallback

Workflow continues regardless of parallel detection status.

---

## Next Steps

After Phase 0 completes:
1. **Phase 1 reads execution plan** from `.workflow/outputs/${ARGUMENTS}/execution_plan.json`
2. **If sequential**: Deploy single implementation agent
3. **If parallel**: Create worktrees and deploy parallel agents
4. **Phase 2+**: Validation, post-mortem, commit, cleanup

---

## Testing Checklist

Before integrating this Phase 0 section into execute-workflow.md:

- [ ] Parallel detection script invocation works
- [ ] JSON parsing with jq succeeds
- [ ] Results display with clear formatting
- [ ] Execution mode stored correctly for Phase 1
- [ ] Dependency checks (jq, parallel_detection.py) working
- [ ] Graceful degradation on missing jq
- [ ] Graceful degradation on missing script
- [ ] Graceful degradation on script errors
- [ ] Updated Phase 0 summary includes execution mode
- [ ] Integration notes documented

---

## Example Output

### Parallel Execution Viable

```
🔍 Analyzing for parallel execution opportunities...

📊 Parallel Execution Analysis:
  Files to modify: 12
  Domains involved: 3
  File overlap: 15%
  Recommendation: parallel

✅ Parallel execution VIABLE
   12 files across 3 domains with 15% overlap

   Domains:
     - backend: 5 files
     - frontend: 5 files
     - docs: 2 files

=========================================
✅ Preflight Complete
=========================================
Epic: EPIC-007
Title: Semantic Email Search
Files: 12
Execution mode: parallel
=========================================
```

### Sequential Execution Recommended

```
🔍 Analyzing for parallel execution opportunities...

📊 Parallel Execution Analysis:
  Files to modify: 3
  Domains involved: 1
  File overlap: 0%
  Recommendation: sequential

➡️ Sequential execution recommended
   Not viable: too few files (3 < 5)

=========================================
✅ Preflight Complete
=========================================
Epic: EPIC-007
Title: Small Feature Update
Files: 3
Execution mode: sequential
=========================================
```

### Dependencies Missing

```
⚠️ jq not installed (required for parallel detection)
   Install: sudo apt-get install jq
   Defaulting to sequential execution

➡️ Sequential execution (parallel detection unavailable)

=========================================
✅ Preflight Complete
=========================================
Epic: EPIC-007
Title: Feature Implementation
Files: 0
Execution mode: sequential
=========================================
```

---

## Implementation Priority

This Phase 0 enhancement is part of **Week 1** of the Tier 1 Enhancement Roadmap:

**Week 1: Agent/Briefing System + Worktree Manager**
- [x] Parallel detection logic (parallel_detection.py) ✅ Created
- [ ] Integrate detection into Phase 0 ⬅️ THIS DOCUMENT
- [ ] Create worktree manager
- [ ] Create agent definitions
- [ ] Create domain briefings

**Status**: Ready for integration into execute-workflow.md
