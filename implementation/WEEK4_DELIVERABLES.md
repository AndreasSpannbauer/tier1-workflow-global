# Week 4 Deliverables Reference

**Week:** 4 of 6
**Status:** COMPLETE
**Date:** 2025-10-19

---

## Overview

Week 4 delivers a complete validation and post-mortem system for the Tier 1 workflow. This document provides a detailed reference for all deliverables, their locations, purposes, and usage instructions.

---

## Deliverables Summary

### Documentation Files (4)

1. **VALIDATION_SYSTEM.md** (26KB)
2. **VALIDATION_RETRY_WORKFLOW.md** (22KB)
3. **POST_MORTEM_SYSTEM.md** (27KB)
4. **validation_scripts/README.md** (15KB)

**Total:** 90KB of new documentation

### Agent Definitions (2)

1. **build_fixer_agent_v1.md** (integrated in Week 4)
2. **post_mortem_agent_v1.md** (integrated in Week 4)

### Template Scripts (3)

1. **validate_architecture.py** (template)
2. **validate_contracts.py** (template)
3. **README.md** (customization guide)

### Workflow Integration

- **Phase 3:** Validation with retry loop
- **Phase 6:** Post-mortem analysis

---

## Detailed Deliverables

### 1. VALIDATION_SYSTEM.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/VALIDATION_SYSTEM.md`

**Size:** 26KB

**Purpose:** Complete validation architecture documentation

**Contents:**
- Validation system overview
- Architecture diagrams (retry loop, state machine)
- Validation types (mandatory vs optional)
- Build fixer agent integration
- Validation script templates
- Integration with package.json
- Output artifacts format
- Non-blocking philosophy
- GitHub integration
- Common validation patterns (Python, TypeScript, Go, Polyglot)
- Error messages and troubleshooting

**When to Use:**
- Understanding validation system architecture
- Configuring validation for a project
- Troubleshooting validation failures
- Customizing validation rules

**Key Sections:**
- Phase 3 Flow (validation retry loop diagram)
- Validation Types (mandatory: build/lint/format/typecheck; optional: architecture/contracts)
- Build Fixer Agent (deployment and results format)
- Integration with package.json (consistent interface)
- Non-Blocking Philosophy (why failures don't halt workflow)

---

### 2. VALIDATION_RETRY_WORKFLOW.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/VALIDATION_RETRY_WORKFLOW.md`

**Size:** 22KB

**Purpose:** Deep dive into validation retry loop mechanics

**Contents:**
- Retry loop state machine
- Detailed workflow (initialization, loop entry, validation execution)
- Decision points (pass vs fail)
- Build fixer deployment
- Max attempts handling
- Example execution traces (pass on first attempt, fail-fix-pass, max attempts reached)
- File artifacts structure
- Agent communication protocol
- Common patterns (auto-fixable errors, mixed errors, unfixable errors)
- Best practices
- Troubleshooting

**When to Use:**
- Understanding retry loop internals
- Debugging validation retry issues
- Customizing retry behavior
- Analyzing validation logs

**Key Sections:**
- Retry Loop State Machine (visual diagram)
- Detailed Workflow (step-by-step execution)
- Example Execution Traces (3 real-world scenarios)
- Agent Communication Protocol (orchestrator ↔ build fixer)
- Common Patterns (auto-fixable, mixed, unfixable)

---

### 3. POST_MORTEM_SYSTEM.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/POST_MORTEM_SYSTEM.md`

**Size:** 27KB

**Purpose:** Post-mortem analysis architecture and knowledge capture workflow

**Contents:**
- Post-mortem system overview
- Single-agent design (Tier 1 philosophy)
- Workflow integration (Phase 6)
- Post-mortem agent responsibilities
- 4 post-mortem questions framework
- Output format (structured markdown report)
- Knowledge capture workflow (agent → human → application)
- Tier 1 vs V6 comparison
- Integration points
- Metrics and analysis
- Example use cases
- Best practices
- Limitations and trade-offs
- Future enhancements (Tier 2/3)

**When to Use:**
- Understanding post-mortem system
- Reviewing post-mortem reports
- Applying recommendations to briefings
- Analyzing workflow effectiveness

**Key Sections:**
- 4 Post-Mortem Questions (framework for analysis)
- Output Format (structured markdown report template)
- Knowledge Capture Workflow (agent generates → human reviews → human applies)
- Tier 1 vs V6 Comparison (design choices)
- Best Practices (for agents and humans)

---

### 4. validation_scripts/README.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/validation_scripts/README.md`

**Size:** 15KB

**Purpose:** Comprehensive customization guide for validation scripts

**Contents:**
- Overview (copy-and-customize philosophy)
- Validation categories (architecture, contracts, build/lint)
- Integration with package.json scripts
- Integration with workflow (Phase 3)
- Customization steps (5-step process)
- Examples:
  - Python project setup
  - TypeScript project setup
  - Polyglot project setup (Python + TypeScript)
- Validation script examples:
  - Architecture validator (Python)
  - Contract validator (Python + OpenAPI)
- Non-blocking failures
- Testing validation setup
- Summary and next steps

**When to Use:**
- Setting up validation for a new project
- Customizing validation templates
- Adding architecture validation
- Adding contract validation
- Integrating with package.json

**Key Sections:**
- Customization Steps (5-step process)
- Example Setups (Python, TypeScript, Polyglot)
- Validation Script Examples (working code snippets)
- Integration with package.json (consistent interface)

---

### 5. build_fixer_agent_v1.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md`

**Status:** Integrated in Week 4 (created earlier)

**Purpose:** Agent definition for fixing validation errors

**Responsibilities:**
1. Read validation error log
2. Apply auto-fixes (ruff check --fix, ruff format)
3. Fix manual errors (type hints, imports)
4. Re-run validation to verify
5. Document blockers
6. Write structured results JSON

**Capabilities:**
- Auto-fix linting violations
- Auto-format code
- Add missing type hints
- Fix import order
- Fix line length violations
- Document unfixable issues

**When to Use:**
- Automatically deployed on validation failures
- Triggered by orchestrator (Phase 3)
- Up to 3 deployment attempts per epic

**Results Format:**
```json
{
  "status": "passed|failed",
  "validation_results": { ... },
  "fixes_applied": [ ... ],
  "remaining_issues": [ ... ]
}
```

---

### 6. post_mortem_agent_v1.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/agent_definitions/post_mortem_agent_v1.md`

**Status:** Integrated in Week 4 (created earlier)

**Purpose:** Agent definition for workflow analysis and recommendations

**Responsibilities:**
1. Review workflow artifacts
2. Analyze git changes
3. Answer 4 post-mortem questions
4. Generate recommendations
5. Write structured markdown report

**Analysis Scope:**
- Implementation quality
- Prescriptive plan clarity
- Validation effectiveness
- Briefing helpfulness
- Parallel execution (if applicable)
- Merge smoothness (if parallel)

**When to Use:**
- Automatically deployed in Phase 6 (after commit)
- Runs for every completed epic
- Always non-blocking

**Output Format:** Structured markdown report (see POST_MORTEM_SYSTEM.md)

---

### 7. validate_architecture.py (Template)

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/validation_scripts/validate_architecture.py`

**Size:** ~150 lines (example template)

**Purpose:** Template for architecture boundary validation

**Example Validation:**
- Domain layer should not import infrastructure layer
- Frontend should not import backend
- Shared utilities should not depend on features

**Customization Required:**
- Update layer definitions for your project
- Update file paths
- Update import patterns
- Add project-specific rules

**Integration:**
```json
{
  "scripts": {
    "validate-architecture": "python3 tools/validate_architecture.py"
  }
}
```

**Exit Codes:**
- `0` - Architecture valid
- `1` - Violations detected

---

### 8. validate_contracts.py (Template)

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/validation_scripts/validate_contracts.py`

**Size:** ~150 lines (example template)

**Purpose:** Template for API contract validation

**Example Validation:**
- API endpoints match OpenAPI spec
- Database models match schema
- Frontend types match backend contracts

**Customization Required:**
- Update schema file paths
- Update contract validation logic
- Add project-specific checks

**Integration:**
```json
{
  "scripts": {
    "validate-contracts": "python3 tools/validate_contracts.py"
  }
}
```

**Exit Codes:**
- `0` - Contracts valid
- `1` - Mismatches detected

---

### 9. Phase 3: Validation (execute-workflow.md)

**Location:** Updated in `template/.claude/commands/execute-workflow.md`

**Integration Point:** After Phase 1 (Implementation) or Phase 1C (Sequential Merge)

**Flow:**
1. Initialize validation state (attempt = 0, max = 3, passed = false)
2. While attempts < 3 && not passed:
   - Run validation (npm run validate-all or fallback)
   - If passed → exit loop
   - If failed && attempts < 3 → deploy build fixer agent → retry
   - If failed && attempts >= 3 → mark failed → continue workflow
3. Write validation results
4. Continue to Phase 5 (Commit)

**Artifacts Created:**
- `.workflow/outputs/${EPIC_ID}/validation/attempt_N.log`
- `.workflow/outputs/${EPIC_ID}/validation/result.json`
- `.workflow/outputs/${EPIC_ID}/fix_attempt_N.json`

**Non-Blocking:** Workflow continues even if validation fails after 3 attempts

---

### 10. Phase 6: Post-Mortem (execute-workflow.md)

**Location:** Updated in `template/.claude/commands/execute-workflow.md`

**Integration Point:** After Phase 5 (Commit & Cleanup)

**Flow:**
1. Read all workflow artifacts
2. Read git changes (git diff HEAD~1)
3. Deploy post-mortem agent via Task tool
4. Agent generates structured report
5. Write report to `.workflow/post-mortem/${EPIC_ID}.md`
6. Display summary to user

**Artifacts Created:**
- `.workflow/post-mortem/${EPIC_ID}.md`

**Non-Blocking:** Always succeeds (never fails workflow)

---

## File Structure Reference

### Runtime Artifacts

**Validation Artifacts:**
```
.workflow/outputs/${EPIC_ID}/
├── validation/
│   ├── attempt_1.log           # First validation attempt
│   ├── attempt_2.log           # Second attempt (if needed)
│   ├── attempt_3.log           # Third attempt (if needed)
│   └── result.json             # Final validation result
├── fix_attempt_1.json          # Build fixer results (attempt 1)
├── fix_attempt_2.json          # Build fixer results (attempt 2)
└── fix_attempt_3.json          # Build fixer results (attempt 3)
```

**Post-Mortem Artifacts:**
```
.workflow/post-mortem/
├── EPIC-001.md                 # Sequential execution example
├── EPIC-002.md                 # Parallel execution example
├── EPIC-003.md                 # Validation failure example
└── TEMPLATE.md                 # Template for manual creation
```

### Template Files (Project Setup)

**Validation Templates:**
```
tools/
├── validate_architecture.py    # Architecture validation (copy from template)
├── validate_contracts.py       # Contract validation (copy from template)
└── README.md                   # Customization guide reference
```

**package.json Scripts:**
```json
{
  "scripts": {
    "validate-all": "npm run lint && npm run typecheck && npm run validate-architecture"
  }
}
```

---

## Quick Reference: How to Use

### Setting Up Validation for a Project

1. **Copy validation templates:**
   ```bash
   cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/
   ```

2. **Customize validation scripts:**
   ```bash
   # Edit tools/validate_architecture.py
   # - Update layer definitions
   # - Update file paths
   # - Update validation logic
   ```

3. **Add package.json scripts:**
   ```json
   {
     "scripts": {
       "lint:py": "ruff check .",
       "typecheck:py": "mypy src/ --strict",
       "validate-architecture": "python3 tools/validate_architecture.py",
       "validate-all": "npm run lint:py && npm run typecheck:py && npm run validate-architecture"
     }
   }
   ```

4. **Test validation:**
   ```bash
   npm run validate-all
   ```

5. **Run workflow:**
   ```bash
   /execute-workflow EPIC-001
   ```

### Reviewing Post-Mortem Reports

1. **View report:**
   ```bash
   cat .workflow/post-mortem/EPIC-001.md
   ```

2. **Extract recommendations:**
   ```bash
   grep -A 20 "Recommendations" .workflow/post-mortem/EPIC-001.md
   ```

3. **Apply valuable recommendations:**
   ```bash
   # Update agent briefings
   nano .claude/agent_briefings/backend_implementation.md

   # Add recommended pattern

   # Commit changes
   git add .claude/agent_briefings/
   git commit -m "refine: add async error handling pattern (EPIC-001 post-mortem)"
   ```

### Debugging Validation Failures

1. **Check validation logs:**
   ```bash
   cat .workflow/outputs/EPIC-001/validation/attempt_1.log
   ```

2. **Check build fixer results:**
   ```bash
   jq . .workflow/outputs/EPIC-001/fix_attempt_1.json
   ```

3. **Check remaining issues:**
   ```bash
   jq -r '.remaining_issues[] | "- \(.issue)"' .workflow/outputs/EPIC-001/fix_attempt_1.json
   ```

4. **Fix manually:**
   ```bash
   # Apply fixes based on remaining_issues

   # Re-run validation
   npm run validate-all
   ```

---

## Dependencies

### Required Tools

**For Validation:**
- Python validation: `ruff`, `mypy` (install via `pip install ruff mypy`)
- TypeScript validation: `eslint`, `prettier`, `typescript` (install via `npm install --save-dev`)
- Go validation: `golangci-lint`, `gofmt` (install via package manager)

**For Workflow:**
- `jq` - JSON processing (validation results)
- `git` - Version control (git worktrees, diffs)
- `gh` - GitHub CLI (optional, for GitHub integration)

**For Post-Mortem:**
- No additional dependencies (uses Claude Code Task tool)

### Optional Tools

- `pytest` - Python testing (for test coverage validation)
- `jest` - TypeScript testing (for test coverage validation)
- Custom architecture validators (project-specific)

---

## Troubleshooting Reference

### Issue: Validation Retry Loop Not Working

**Symptoms:**
- Validation runs only once
- No retry attempts

**Causes:**
- Loop condition incorrect
- VALIDATION_PASSED not being set

**Solutions:**
1. Check execute-workflow.md Phase 3 loop condition
2. Verify VALIDATION_PASSED=1 is set on success
3. Add debug logging

**Related Documentation:** VALIDATION_RETRY_WORKFLOW.md

---

### Issue: Build Fixer Agent Doesn't Fix Anything

**Symptoms:**
- Fix results show `status: "failed"`
- All errors remain

**Causes:**
- Errors not auto-fixable
- Agent can't parse error messages

**Solutions:**
1. Check error message format
2. Add auto-fix tools (ruff, prettier)
3. Update build fixer agent definition

**Related Documentation:** VALIDATION_SYSTEM.md (Build Fixer Agent section)

---

### Issue: Post-Mortem Report Not Generated

**Symptoms:**
- No .workflow/post-mortem/${EPIC_ID}.md file

**Causes:**
- Phase 6 not running
- Agent deployment failed

**Solutions:**
1. Check execute-workflow.md Phase 6 exists
2. Verify Task tool available
3. Check agent definition file exists

**Related Documentation:** POST_MORTEM_SYSTEM.md

---

### Issue: Validation Scripts Not Found

**Symptoms:**
- npm run validate-all fails with "command not found"

**Causes:**
- Validation scripts not copied to project
- package.json scripts not configured

**Solutions:**
1. Copy templates: `cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/`
2. Add package.json scripts
3. Make scripts executable: `chmod +x tools/*.py`

**Related Documentation:** validation_scripts/README.md (Customization Steps)

---

## Summary

Week 4 delivers:

**4 Documentation Files (90KB):**
- VALIDATION_SYSTEM.md (26KB) - Architecture
- VALIDATION_RETRY_WORKFLOW.md (22KB) - Deep dive
- POST_MORTEM_SYSTEM.md (27KB) - Knowledge capture
- validation_scripts/README.md (15KB) - Customization

**2 Agent Definitions:**
- build_fixer_agent_v1.md - Validation error fixing
- post_mortem_agent_v1.md - Workflow analysis

**3 Template Scripts:**
- validate_architecture.py - Architecture boundaries
- validate_contracts.py - API contracts
- README.md - Customization guide

**2 Workflow Phases:**
- Phase 3: Validation with retry loop
- Phase 6: Post-mortem analysis

**All deliverables production-ready and documented.**

---

**Generated:** 2025-10-19
**Author:** Claude Code (Tier 1 Workflow Implementation)
**Document Version:** 1.0
