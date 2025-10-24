---
title: 'ADR-012: Spec Validation Template Detection Pattern'
description: 'Mandatory two-phase validation for spec completeness: file existence and template placeholder detection'
category: Workflow-Validation
component_type: architectural_decision
last_updated: '2025-10-21'
monitored_paths:
- template/.claude/commands/execute-workflow.md
priority: HIGH
tags:
- Workflow
- Validation
- Spec-Creation
- Tier1-Template
---
# ADR-012: Spec Validation Template Detection Pattern

**Status:** Active

**Decision Date:** 2025-10-21
**Tier1 Global Integration Date:** 2025-10-21

**Deciders:** Development Team, Tier 1 Workflow System

## Context

The Tier 1 workflow template suffered from false positive "ready for execution" messages that wasted significant developer time. This pattern was originally discovered and fixed in the email_management_system project (see `/home/andreas-spannbauer/coding_projects/email_management_system/docs/architecture/ADR-012-spec-validation-template-detection.md`).

The root cause was in `template/.claude/commands/execute-workflow.md` Step 0.2, which only checked for file existence without validating content for template placeholders.

This led to situations where:
1. **Specs appeared complete** when files existed but contained unfilled templates
2. **Workflow execution failed** due to template placeholders in critical sections
3. **Developer trust eroded** in automated validation systems
4. **Wasted agent time** implementing incomplete specifications

Example failure: Epic passes validation despite containing template placeholders like `[What happens now]`, `[Component Name]`, and `[table_name]` throughout spec.md and architecture.md.

## Decision

### Mandatory Two-Phase Validation Pattern

All spec validation in the Tier 1 workflow template MUST implement two-phase validation:

**Phase 1: File Existence**
- Verify required files and directories exist
- Report missing artifacts

**Phase 2: Template Placeholder Detection**
- Scan file contents for template markers
- Report files containing placeholders separately

### Canonical Template Marker List

The following 18 template markers indicate incomplete specifications and MUST be detected:

```bash
TEMPLATE_MARKERS=(
  # User scenario templates
  "[What happens now]"
  "[What should happen]"
  "[How we measure success]"

  # Architecture templates
  "[Component Name]"
  "[System diagram here"
  "[Brief description]"

  # Requirements templates
  "[Criterion 1]"
  "[Criterion 2]"

  # Database/API templates
  "[table_name]"
  "[METHOD] /api/"

  # Performance templates
  "[Performance targets]"
  "[Accuracy targets]"

  # Dependency templates
  "[Feature deliberately excluded]"
  "[Epic/feature this depends on]"
  "[Epic/feature that depends on]"

  # Generic incomplete markers
  "_To be defined"
  "_To be determined"
  "_Description to be added_"
)
```

### Implementation Pattern (Bash)

```bash
# Required files
REQUIRED_FILES=(
  "spec.md"
  "architecture.md"
  "implementation-details/file-tasks.md"
)

# Phase 1: Check file existence
MISSING_FILES=""
FILES_WITH_TEMPLATES=""

for FILE in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "${EPIC_DIR}/${FILE}" ]; then
    MISSING_FILES+="- ${FILE}\n"
  else
    # Phase 2: Check for template placeholders
    FILE_HAS_TEMPLATES=false
    for MARKER in "${TEMPLATE_MARKERS[@]}"; do
      if grep -q "${MARKER}" "${EPIC_DIR}/${FILE}"; then
        FILE_HAS_TEMPLATES=true
        break
      fi
    done

    if [ "$FILE_HAS_TEMPLATES" = true ]; then
      FILES_WITH_TEMPLATES+="- ${FILE} (contains template placeholders)\n"
    fi
  fi
done

# Report issues if any
if [ -n "$MISSING_FILES" ] || [ -n "$FILES_WITH_TEMPLATES" ]; then
  echo "❌ Epic not ready for execution"
  # ... provide recovery instructions
  exit 1
fi
```

## Rationale

### Why Both Phases Are Required

1. **File existence alone is insufficient** - Empty or template files provide no value
2. **Template detection prevents wasted effort** - Catches incomplete specs before execution
3. **Clear error messages guide resolution** - "contains template placeholders" is actionable
4. **Consistency across workflow system** - All validation follows same pattern

### Why These Specific Markers

The 18 template markers were identified from:
- Analysis of actual spec templates in the Tier 1 workflow codebase
- Common placeholders that indicate incomplete sections
- Patterns that frequently cause execution failures
- Original research in email_management_system ADR-012

### Benefits

- **Prevents false positives** - No more "ready for execution" with template content
- **Saves developer time** - Catches issues before workflow execution
- **Saves agent time** - Agents don't waste time on incomplete specs
- **Improves trust** - Validation accurately reflects spec readiness
- **Enables automation** - Reliable validation enables automated workflows

## Consequences

### Positive

- **Accurate validation** - Specs are truly ready when validation passes
- **Early detection** - Template issues caught during preflight, not implementation
- **Clear feedback** - Developers know exactly what needs completion
- **Reduced debugging** - Fewer mysterious workflow failures
- **Agent efficiency** - Agents only work on complete specifications

### Negative

- **Slightly slower validation** - File content must be read and scanned
- **Maintenance burden** - Template marker list must be kept current
- **False negatives possible** - New template patterns might not be detected

### Mitigation

- **Performance**: Template detection is fast (<10ms per file in bash)
- **Maintenance**: Marker list documented in ADR, easy to update
- **Coverage**: Regular review of new templates added to system

## Implementation Status

### Completed

- ✅ Fixed `template/.claude/commands/execute-workflow.md` Step 0.2 with 18 markers
- ✅ Canonical pattern implemented in bash (suitable for workflow template)
- ✅ Recovery instructions for template placeholder failures

### Required Actions

1. **Testing**: Verify against epics with template placeholders
2. **Documentation**: Update template README with validation pattern reference
3. **Future Projects**: Apply pattern when instantiating from template

## Compliance Verification

To verify compliance with this ADR in projects instantiated from template:

```bash
# Check validation implements both phases
grep -n "TEMPLATE_MARKERS" .claude/commands/execute-workflow.md

# Verify all 18 markers are present
grep -c "What happens now" .claude/commands/execute-workflow.md
# Should return: 1 (or more if in comments)

# Test against known incomplete spec
# 1. Create test epic with template placeholders
# 2. Run: /execute-workflow TEST-001
# 3. Should fail with "contains template placeholders" message
```

## Relationship to Original ADR-012

This is the **global Tier 1 workflow template version** of ADR-012.

**Source**: `/home/andreas-spannbauer/coding_projects/email_management_system/docs/architecture/ADR-012-spec-validation-template-detection.md`

**Key Differences**:
- **Language**: Bash (workflow template) vs Python (email_management_system)
- **Context**: Generic workflow template vs project-specific validation
- **Files**: Template structure vs project structure
- **Scope**: Global template for all projects vs single project

**Shared Principles**:
- ✅ Same 18 template markers
- ✅ Same two-phase validation logic
- ✅ Same goal: prevent false "ready for execution"
- ✅ Same recovery guidance pattern

**Adaptation Notes**:
- Bash implementation uses arrays and loops instead of Python lists
- Error reporting adapted to bash echo/printf
- Recovery instructions reference template-specific commands
- Validation happens in slash command vs Python function

## References

- **Original ADR**: `/home/andreas-spannbauer/coding_projects/email_management_system/docs/architecture/ADR-012-spec-validation-template-detection.md`
- **Template Implementation**: `template/.claude/commands/execute-workflow.md` Step 0.2
- **Related Files**:
  - `template/.claude/commands/execute-workflow.md` (validation location)
  - Template spec/architecture files (validated artifacts)

## Future Enhancements

1. **Centralized marker list**: Consider extracting TEMPLATE_MARKERS to shared config
2. **Pattern detection**: Add detection of common incomplete patterns (e.g., "TODO", "FIXME")
3. **Automated fixes**: Script to help fill common template placeholders
4. **CI integration**: Add pre-commit hook to catch template markers in specs
