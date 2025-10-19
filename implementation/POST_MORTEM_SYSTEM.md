# Post-Mortem System - Tier 1 Architecture

**Date:** 2025-10-19
**Status:** COMPLETE
**Week:** 4 of 6

---

## Executive Summary

The Post-Mortem System provides lightweight workflow analysis and knowledge capture for the Tier 1 workflow. After each epic completion, a single post-mortem agent analyzes execution results, identifies what worked and what didn't, and generates actionable recommendations for improving agent briefings and processes.

**Key Design:** Simplified vs V6 (single agent, markdown reports, manual knowledge capture)

---

## Overview

### Purpose

Extract learnings from completed workflows to continuously improve:
- Agent briefing quality (more examples, clearer patterns)
- Prescriptive plan clarity (reduce ambiguity)
- Validation effectiveness (catch issues early)
- Parallel execution efficiency (better domain detection)
- Overall workflow reliability (fewer failures)

### Philosophy

**Human-in-the-loop knowledge capture:**
- Post-mortem agent **suggests** improvements
- Human **reviews** recommendations
- Human **applies** valuable suggestions to briefings
- Briefings evolve incrementally based on real experience

**Not automated semantic indexing** (that's V6 complexity - Tier 1 keeps it simple)

---

## Architecture

### Single-Agent Design

**Unlike V6's 3-agent system**, Tier 1 uses a single post-mortem agent:

```
Post-Mortem Agent
    │
    ├─► Reviews workflow artifacts (.workflow/outputs/)
    ├─► Analyzes git changes (git diff)
    ├─► Identifies patterns (what worked)
    ├─► Documents challenges (what didn't)
    ├─► Generates recommendations (what to improve)
    │
    └─► Writes markdown report (.workflow/post-mortem/EPIC-ID.md)
```

**No complex orchestration** - one agent, one report, clear output.

### Workflow Integration

Post-mortem runs as **Phase 6** (after commit):

```
Phase 0: Preflight
Phase 1A/1B: Implementation (sequential or parallel)
Phase 1C: Sequential Merge (if parallel)
Phase 2: Validation
Phase 5: Commit & Cleanup
Phase 6: Post-Mortem ← NEW
```

**Why after commit?**
- All artifacts available (implementation, validation, merge, commit)
- Git changes finalized (diff shows actual changes)
- Epic complete (no partial analysis)
- No blocking workflow (analysis happens post-success)

---

## Post-Mortem Agent V1

### Responsibilities

**MUST DO:**
1. Review all workflow artifacts (JSON results, git changes)
2. Answer 4 post-mortem questions
3. Provide specific, actionable recommendations
4. Write structured markdown report

**MUST NOT:**
- Make code changes (analysis only)
- Skip recommendations (always suggest improvements)
- Provide generic feedback (be specific: file names, patterns, issues)
- Ignore failures (document what went wrong and why)

### 4 Post-Mortem Questions

**1. What worked well?**
- Which prescriptive plans were clear?
- Which validation steps caught real issues?
- Which agent briefings were helpful?
- Which architectural patterns worked?

**2. What challenges occurred?**
- What problems did implementation agent face?
- What validation errors occurred?
- What required multiple fix attempts?
- What was unclear in specifications?

**3. How were challenges resolved?**
- What strategies worked for fixing issues?
- What architectural decisions helped?
- What could have been prevented?
- What workarounds were needed?

**4. What should improve next time?**
- Which briefings need clarification?
- Which prescriptive plans were unclear?
- Which validation steps should be added/removed?
- Which patterns should be documented?

### Analysis Scope

**Sequential Execution:**
- Implementation quality (code, patterns, architecture)
- Prescriptive plan clarity (was it followed exactly?)
- Validation effectiveness (did it catch real issues?)
- Briefing helpfulness (did examples apply?)

**Parallel Execution (Additional):**
- Worktree management (creation, isolation, cleanup)
- Domain separation quality (file overlap, boundaries)
- Parallel effectiveness (actual speedup vs expected)
- Merge smoothness (conflicts, order, timing)

---

## Output Format

### Structured Markdown Report

**Location:** `.workflow/post-mortem/EPIC-ID.md`

**Sections:**

1. **Frontmatter** (metadata)
   ```yaml
   ---
   epic_id: EPIC-XXX
   title: [Epic Title]
   completed_at: 2025-10-19T14:40:00Z
   execution_mode: sequential|parallel
   parallel_agents: 0|2|3
   ---
   ```

2. **Summary** (1-2 sentences)
   - High-level overview
   - Key outcome (success/partial/failed)
   - Major achievements or issues

3. **Execution Details**
   - Files created/modified
   - Execution mode
   - Duration (estimated)
   - Validation attempts
   - Final status

4. **What Worked Well** (3-5 items)
   - Specific successes with examples
   - File names, patterns, decisions

5. **Challenges Encountered** (2-4 items)
   - Description of issue
   - Impact on workflow
   - Root cause analysis
   - Resolution approach
   - Lesson learned

6. **Recommendations**
   - **Briefing Updates:** Specific files, specific additions
   - **Process Improvements:** Workflow changes
   - **Pattern Additions:** New reusable patterns

7. **Metrics**
   - Validation pass rate
   - File overlap (if parallel)
   - Build/lint/type errors fixed
   - Architecture violations

8. **Artifacts**
   - Links to results files
   - Git commit hash
   - Git diff summary

### Example Structure

```markdown
---
epic_id: EPIC-042
title: Add semantic email search with vector embeddings
completed_at: 2025-10-19T14:40:00Z
execution_mode: parallel
parallel_agents: 3
---

# Post-Mortem: EPIC-042

## Summary

Successfully implemented semantic email search feature with 3-domain parallel execution (backend, frontend, database). Validation passed on second attempt after fixing type hints. Parallel execution achieved 2.1x speedup vs sequential.

## Execution Details

- **Epic ID:** EPIC-042
- **Files created:** 8
- **Files modified:** 6
- **Execution mode:** Parallel (3 agents)
- **Duration:** ~28 minutes (vs 60 min sequential estimate)
- **Validation attempts:** 2
- **Final status:** Success

## What Worked Well

- **Clear domain separation:** Backend (5 files), Frontend (6 files), Database (3 files) with zero file overlap
- **Prescriptive plan specificity:** file-tasks.md specified exact changes, implementation agents followed without confusion
- **Parallel detection accuracy:** Correctly identified 3 independent domains, predicted clean merge
- **Effective validation:** Type checker caught 3 missing annotations before commit
- **Worktree isolation:** No cross-contamination between parallel agents

## Challenges Encountered

### Challenge 1: Missing Type Hints for Async Functions

- **Description:** TypeScript linting failed due to missing return type annotations on new async API endpoints
- **Impact:** Validation failed on first attempt, required fixer agent deployment
- **Root Cause:** Prescriptive plan didn't specify return types for async functions
- **Resolution:** Fixer agent added explicit type annotations (-> Coroutine[None, None, Email])
- **Lesson:** Prescriptive plans should include type signature examples for async functions

### Challenge 2: Database Migration Ordering

- **Description:** Frontend agent tried to reference new database table before migration ran
- **Impact:** Frontend build failed temporarily during parallel execution
- **Root Cause:** Domain merge order (database → backend → frontend) was correct, but frontend agent started before database agent finished
- **Resolution:** Sequential merge ensured database changes applied first; frontend rebuild succeeded
- **Lesson:** Parallel execution timing doesn't affect final result due to sequential merge

## Recommendations

### Briefing Updates

**Backend Briefing:** `.claude/agent_briefings/backend_implementation.md`

- **Add pattern:** "When adding async API endpoints, always specify return types explicitly: `async def get_email(id: int) -> Email:`"
- **Clarify:** "Service methods should raise custom exceptions (e.g., EmailNotFoundError), not HTTPException directly"
- **Example:** Add async error handling pattern with try/except in API routes

**Implementation Agent:** `.claude/agent_definitions/implementation_agent_v1.md`

- **Add rule:** "For async functions in Python, always add explicit return type annotations"
- **Emphasize:** "If prescriptive plan is unclear about types, document in clarifications_needed"

### Process Improvements

**Parallel Detection:**
- Current threshold (8+ files, 2+ domains, <30% overlap) worked perfectly for this epic
- No changes needed to detection logic

**Validation Phase:**
- Consider adding pre-validation type check before implementation starts (catches type issues early)
- Add reminder to implementation agent: "Run type checker incrementally, not just at end"

**Prescriptive Plans:**
- Include type signature examples for complex functions (async, generics, unions)
- Specify error handling patterns explicitly (which exceptions to raise, where to catch)

### Pattern Additions

**Pattern: Async Error Handling in FastAPI**

```python
@router.get("/emails/{id}")
async def get_email(id: int) -> Email:
    try:
        service = EmailService(db)
        return await service.get_email(id)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Use Case:** API routes that call async service methods

## Metrics

- **Validation pass rate:** 50% (passed on attempt 2/2)
- **File overlap (parallel):** 0% (0 shared files out of 14 total)
- **Build errors fixed:** 0
- **Lint violations fixed:** 2 (import order)
- **Type errors fixed:** 3 (missing return type annotations)
- **Architecture violations:** 0
- **Parallel speedup:** 2.1x (28 min vs 60 min estimate)

## Artifacts

- **Implementation results:** `.workflow/outputs/EPIC-042/phase1_parallel_results.json`
- **Merge summary:** `.workflow/outputs/EPIC-042/merge_summary.json`
- **Validation results:** Embedded in git history
- **Git diff:** `git diff HEAD~1`
- **Commit:** `a3f2b1c`

## Additional Notes

- Database migrations tested manually post-deployment (not part of automated workflow)
- Performance testing recommended for vector similarity search at scale
- Consider adding integration tests for new search endpoint (manual, not automated in workflow)
```

---

## Knowledge Capture Workflow

### Step 1: Agent Generates Report

Post-mortem agent (Phase 6):
1. Reads all workflow artifacts
2. Analyzes git changes
3. Identifies patterns and issues
4. Writes structured markdown report

**Output:** `.workflow/post-mortem/EPIC-ID.md`

### Step 2: Human Reviews Report

Developer reads report:
```bash
cat .workflow/post-mortem/EPIC-042.md
```

Focus on:
- Are recommendations valuable?
- Are they generally applicable (not epic-specific)?
- Do they improve future workflows?

### Step 3: Human Applies Recommendations

**For Briefing Updates:**

```bash
# Example: Update backend briefing
nano .claude/agent_briefings/backend_implementation.md

# Add recommended pattern to appropriate section
# E.g., add async error handling example

# Commit separately
git add .claude/agent_briefings/
git commit -m "refine: add async error handling pattern (EPIC-042 post-mortem)"
```

**For Process Improvements:**

```bash
# Example: Update workflow command
nano .claude/commands/execute-workflow.md

# Add recommended improvement
# E.g., pre-validation type check step

# Commit separately
git add .claude/commands/
git commit -m "feat: add pre-validation type check (EPIC-042 post-mortem)"
```

**For Pattern Additions:**

```bash
# Option 1: Add to project patterns (if project-specific)
nano docs/patterns/async-error-handling.md

# Option 2: Add to semantic pattern library (if globally useful)
/pattern add async-error-handling-fastapi

# Commit
git add docs/patterns/
git commit -m "docs: add async error handling pattern (EPIC-042 post-mortem)"
```

### Step 4: Archive Post-Mortem

Post-mortem reports are **kept permanently** in `.workflow/post-mortem/`:
- Historical reference
- Trend analysis (see repeated issues)
- Onboarding material (learn from past workflows)

**No deletion** - storage is cheap, insights are valuable.

---

## Tier 1 vs V6 Comparison

| Feature | Tier 1 (Simple) | V6 (Complex) |
|---------|----------------|--------------|
| **Agents** | 1 (post-mortem) | 3 (implementation/validation/planning analysis) |
| **Orchestration** | Single agent call | Multi-agent coordination |
| **Output Format** | Markdown report | Markdown + JSON + semantic index |
| **Knowledge Capture** | Manual (human reviews) | Automated (semantic indexing) |
| **Briefing Updates** | Human applies suggestions | Auto-update system |
| **Pattern Extraction** | Manual curation | Automated extraction + indexing |
| **Complexity** | Low (1 file, 1 agent) | High (multiple systems, orchestration) |
| **Maintenance** | Minimal | Requires semantic infrastructure |

**Tier 1 Design Choice:** Simplicity over automation. Human judgment applied at knowledge capture phase.

---

## Integration Points

### Phase 6 in Workflow

**Location in execute-workflow.md:** After Phase 5 (Commit & Cleanup)

**Trigger:** Automatic (always runs after commit)

**Inputs:**
- Workflow artifacts (`.workflow/outputs/EPIC-ID/`)
- Git changes (`git diff HEAD~1`)
- Epic specs (`.tasks/completed/EPIC-ID/`)

**Outputs:**
- Post-mortem report (`.workflow/post-mortem/EPIC-ID.md`)
- Console summary (key recommendations)

### Post-Mortem Directory Structure

```
.workflow/
└── post-mortem/
    ├── EPIC-001.md    # Sequential execution example
    ├── EPIC-002.md    # Parallel execution example
    ├── EPIC-003.md    # Validation failure example
    └── TEMPLATE.md    # Template for manual creation
```

**Created by workflow:** `EPIC-XXX.md` files
**Manually created:** `TEMPLATE.md` (reference template)

---

## Metrics and Analysis

### Post-Mortem Metrics

Each report includes:

**Implementation Metrics:**
- Files created/modified
- Execution mode (sequential/parallel)
- Duration (estimated)
- Validation attempts (1-3)

**Validation Metrics:**
- Validation pass rate (%)
- Build errors fixed
- Lint violations fixed
- Type errors fixed
- Architecture violations

**Parallel Execution Metrics (if applicable):**
- File overlap percentage
- Number of domains
- Parallel speedup (actual)
- Merge conflicts (count)
- Worktree cleanup success

### Trend Analysis

**Over time, look for:**

**Improving Trends:**
- Validation pass rate increasing (fewer errors)
- Fewer fix attempts required
- Faster parallel execution (better detection)
- Clearer prescriptive plans (fewer clarifications)

**Worsening Trends:**
- Repeated validation errors (same issues)
- More fix attempts required
- Parallel conflicts increasing (poor domain detection)
- More clarifications needed (briefings unclear)

**Manual Review:** Periodically review all post-mortems:
```bash
# List all post-mortems
ls -lt .workflow/post-mortem/

# Search for common issues
grep -h "Challenge" .workflow/post-mortem/*.md

# Find repeated recommendations
grep -h "Add pattern" .workflow/post-mortem/*.md
```

---

## Example Use Cases

### Use Case 1: Sequential Epic

**Scenario:** Small epic, 5 files, 1 domain (backend)

**Post-Mortem Focus:**
- Prescriptive plan clarity
- Implementation quality
- Validation effectiveness
- Briefing helpfulness

**Typical Recommendations:**
- Add code examples to backend briefing
- Clarify error handling patterns
- Improve type hint examples

### Use Case 2: Parallel Epic (Clean)

**Scenario:** Large epic, 18 files, 3 domains (backend, frontend, database)

**Post-Mortem Focus:**
- Parallel detection accuracy
- Domain separation quality
- Worktree isolation effectiveness
- Merge smoothness

**Typical Recommendations:**
- Validate parallel detection thresholds
- Document domain boundary patterns
- Improve worktree cleanup verification

### Use Case 3: Validation Failure Epic

**Scenario:** Epic with 2 failed validation attempts before success

**Post-Mortem Focus:**
- Root cause of validation failures
- Fixer agent effectiveness
- Prescriptive plan gaps
- Validation gate appropriateness

**Typical Recommendations:**
- Add pre-validation checks
- Improve prescriptive plan type examples
- Update fixer agent strategies
- Clarify validation requirements in briefings

---

## Best Practices

### For Post-Mortem Agents

**DO:**
- Be specific (file names, line numbers, exact patterns)
- Provide actionable recommendations (exact file paths, suggested changes)
- Document root causes (why did issue occur?)
- Extract lessons (what to do differently next time)
- Reference specific artifacts (results files, git commits)

**DON'T:**
- Provide generic feedback ("improve documentation")
- Make recommendations without justification
- Ignore failures or challenges
- Skip analysis of parallel execution (if applicable)
- Write vague suggestions ("agents should be better")

### For Humans Reviewing Reports

**DO:**
- Read full report (not just summary)
- Evaluate recommendations critically (are they generalizable?)
- Apply valuable suggestions promptly (while context fresh)
- Track which recommendations applied (for trend analysis)
- Keep post-mortems archived (historical value)

**DON'T:**
- Apply all recommendations blindly (use judgment)
- Skip recommendations that seem "too specific" (might be pattern)
- Delete post-mortems (storage is cheap, insights valuable)
- Ignore repeated issues (signals systemic problem)
- Delay applying recommendations (context fades)

### For Briefing Evolution

**DO:**
- Add patterns from successful implementations
- Clarify ambiguities from failed implementations
- Provide concrete code examples
- Document edge cases discovered
- Update incrementally (small changes, frequent)

**DON'T:**
- Add epic-specific details (keep briefings general)
- Overload briefings with too many examples
- Remove old patterns without reason
- Ignore repeated clarification requests
- Make large briefing rewrites (incremental better)

---

## Limitations (Tier 1)

### Current Limitations

1. **Manual Knowledge Capture**
   - Human must review and apply recommendations
   - No automated briefing updates
   - Requires discipline to apply learnings

2. **Single Agent Analysis**
   - No multi-perspective analysis (like V6's 3-agent system)
   - Simpler analysis (less depth)
   - May miss some insights

3. **No Semantic Indexing**
   - No automated pattern extraction
   - No searchable knowledge base
   - Manual pattern management

4. **No Trend Tracking**
   - No automated metrics over time
   - Manual review of historical post-mortems
   - No automated "this issue appeared 3 times" alerts

5. **No Workflow Resume Analysis**
   - Can't analyze partial workflows (resume not implemented yet)
   - Only analyzes completed workflows
   - No failure recovery insights

### Acceptable Trade-offs (Tier 1 Philosophy)

**Why we accept these limitations:**
- **Simplicity:** No complex orchestration or semantic infrastructure
- **Maintainability:** Markdown files, standard tools, no dependencies
- **Transparency:** Human reviews everything, understands all changes
- **Control:** Human judgment applied at every step
- **Incrementalism:** Briefings evolve gradually based on experience

**Tier 1 is not inferior** - it's intentionally simple for reliability and maintainability.

---

## Future Enhancements (Tier 2/3)

**Potential additions for higher tiers:**

1. **Automated Trend Tracking**
   - Database of post-mortem metrics
   - Automated "repeated issue" detection
   - Visualization of improvements over time

2. **Multi-Agent Analysis**
   - Implementation agent perspective
   - Validation agent perspective
   - Planning agent perspective
   - Synthesized insights

3. **Semantic Pattern Extraction**
   - Automated pattern identification from code
   - Semantic indexing of successful implementations
   - Searchable knowledge base

4. **Automated Briefing Updates**
   - LLM-generated briefing patches
   - Human approval required before applying
   - Version control for briefing evolution

5. **Workflow Resume Analysis**
   - Analyze workflows that required manual intervention
   - Extract insights from failure recovery
   - Improve resume mechanism

**Not in Tier 1** - keeping it simple and maintainable.

---

## Testing and Validation

### How to Test Post-Mortem System

**Test Scenario 1: Sequential Epic**
```bash
# Run workflow on simple epic
/execute-workflow EPIC-001

# Verify post-mortem generated
ls -l .workflow/post-mortem/EPIC-001.md

# Review report quality
cat .workflow/post-mortem/EPIC-001.md

# Check for specific recommendations
grep "Recommendation" .workflow/post-mortem/EPIC-001.md
```

**Test Scenario 2: Parallel Epic**
```bash
# Run workflow on large epic (parallel execution)
/execute-workflow EPIC-002

# Verify parallel analysis included
grep "Parallel" .workflow/post-mortem/EPIC-002.md

# Check worktree cleanup verification
grep -A 5 "Worktree" .workflow/post-mortem/EPIC-002.md
```

**Test Scenario 3: Validation Failure Epic**
```bash
# Run workflow on epic with intentional errors
/execute-workflow EPIC-003

# Verify validation analysis included
grep "Validation" .workflow/post-mortem/EPIC-003.md

# Check fix attempt analysis
grep "fix attempt" .workflow/post-mortem/EPIC-003.md
```

### Quality Checklist

**Good Post-Mortem Report:**
- [ ] All 4 questions answered
- [ ] Specific examples (file names, patterns)
- [ ] Actionable recommendations (exact paths, changes)
- [ ] Metrics calculated
- [ ] Artifacts referenced (git commits, results files)
- [ ] Parallel analysis included (if applicable)
- [ ] Validation issues documented
- [ ] Worktree cleanup verified (if parallel)

**Bad Post-Mortem Report:**
- [ ] Generic feedback ("improve agents")
- [ ] No specific recommendations
- [ ] Missing metrics
- [ ] No artifact references
- [ ] Parallel execution not analyzed (when applicable)
- [ ] Validation issues ignored

---

## Summary

The Tier 1 Post-Mortem System provides:

**Lightweight Analysis:**
- Single agent (not 3-agent orchestration)
- Markdown reports (not complex data structures)
- Manual knowledge capture (human reviews and applies)

**Continuous Improvement:**
- Extract learnings from every workflow
- Evolve agent briefings incrementally
- Improve prescriptive plan quality
- Enhance validation effectiveness

**Human-in-the-Loop:**
- Agent suggests, human decides
- Human applies valuable recommendations
- Human curates knowledge base
- Human maintains briefing quality

**Simple and Maintainable:**
- No semantic infrastructure required
- Standard tools (markdown, git, file system)
- Easy to understand and modify
- Minimal dependencies

**Effective Knowledge Capture:**
- Post-mortems archived permanently
- Trends visible through manual review
- Briefings evolve based on experience
- Workflow reliability improves over time

**Week 4 Status:** COMPLETE

---

**Generated:** 2025-10-19
**Author:** Claude Code (Tier 1 Workflow Implementation)
**Document Version:** 1.0
