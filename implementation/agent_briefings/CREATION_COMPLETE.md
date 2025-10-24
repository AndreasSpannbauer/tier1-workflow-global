# Agent Briefing Template Creation Complete

**Date:** 2025-10-19
**Task:** Create agent briefing template files for Tier 1 workflow system
**Status:** ✅ COMPLETE

---

## Files Created

### 1. backend_implementation.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md`

**Type:** Domain-specific briefing (Backend/Python/FastAPI)

**Contents:**
- YAML frontmatter (domain, updated, applies_to)
- Project Architecture (Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, asyncio)
- File Structure (api/, services/, models/, schemas/)
- 6 detailed coding patterns:
  1. Service Layer Pattern (business logic separation)
  2. Dependency Injection Pattern (FastAPI Depends)
  3. Error Handling (custom exceptions + HTTPException)
  4. Database Query Pattern (SQLAlchemy 2.0 select())
  5. Transaction Pattern (explicit transactions with rollback)
  6. Type Hints (mandatory for all functions)
- Common Mistakes to Avoid (5 examples with ✅/❌)
- Post-Implementation Checklist
- Questions to Ask if Unclear

**Key Features:**
- Python/FastAPI examples throughout
- Service layer pattern emphasized
- Async/await best practices
- Error handling with custom exceptions
- Type hints mandatory
- Clear DO NOT instructions (no tests, no docs in implementation phase)

**Line Count:** ~600 lines

---

### 2. project_architecture.md

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/agent_briefings/project_architecture.md`

**Type:** Project-wide architectural rules (template)

**Contents:**
- YAML frontmatter (type, applies_to, updated)
- 10 major sections:
  1. **Project Overview** - Technology stack, architecture style
  2. **Directory Structure** - Standard layout with explanations
  3. **Code Organization Principles** - Layered architecture, dependency rules, SRP, naming
  4. **Error Handling Strategy** - Custom exceptions, error handling patterns
  5. **Logging and Monitoring** - Logging standards, what to log
  6. **Testing Philosophy** - Testing strategy for Tier 1 (minimal testing)
  7. **Documentation Standards** - What to document, what to skip
  8. **Performance Considerations** - Database optimization, async/await
  9. **Security Patterns** - Authentication, authorization, input validation
  10. **Deployment Considerations** - Environment config, Docker

**Additional Sections:**
- Agent Instructions (MUST/MUST NOT lists)
- Common Anti-Patterns to Avoid (3 examples with ✅/❌)
- Questions to Escalate
- Summary of core principles

**Key Features:**
- Comprehensive template covering all architectural aspects
- Layered architecture pattern (API → Service → Data)
- Dependency rules (downward flow only)
- Security patterns (JWT, input validation, SQL injection prevention)
- Performance optimization (eager loading, pagination, async)
- Environment-specific configuration
- Clear instructions for implementation and build fixer agents

**Line Count:** ~650 lines

---

## Validation Checklist

All requirements met:

- [x] 2 markdown files created in correct directory
- [x] Each file has YAML frontmatter
- [x] backend_implementation.md has Python/FastAPI examples
- [x] backend_implementation.md has service layer pattern examples
- [x] backend_implementation.md has error handling examples
- [x] project_architecture.md is a comprehensive template
- [x] Both files have code examples with ✅/❌ annotations

---

## File Statistics

| File | Lines | Sections | Code Examples | ✅/❌ Comparisons |
|------|-------|----------|---------------|------------------|
| backend_implementation.md | ~600 | 11 | 25+ | 15+ |
| project_architecture.md | ~650 | 13 | 20+ | 10+ |
| **TOTAL** | **~1,250** | **24** | **45+** | **25+** |

---

## Key Design Decisions

### 1. Python/FastAPI Focus

Both templates use Python/FastAPI as the primary example technology:
- Python 3.11+ syntax
- FastAPI dependency injection
- SQLAlchemy 2.0 query patterns
- Async/await throughout
- Type hints mandatory

**Rationale:** Most Tier 1 projects use Python backend (per assessment doc).

### 2. Service Layer Pattern Emphasized

Backend briefing heavily emphasizes service layer pattern:
- Business logic in services/ (not routes)
- API routes are thin wrappers
- Services raise custom exceptions
- Routes convert to HTTPException

**Rationale:** V6 workflow success depends on consistent architecture patterns.

### 3. No Testing in Implementation Phase

Both templates explicitly state:
- ❌ Implementation agents DO NOT write tests
- ✅ Testing phase handles this (if needed)

**Rationale:** User stated "most tests are written to pass and not to actually identify issues - when written by coding agents"

### 4. Manual Documentation Updates

Both templates emphasize:
- ❌ No auto-generated documentation
- ✅ Manual updates preferred

**Rationale:** V6 workflow learned this lesson (automatic docs are fragile).

### 5. Comprehensive Error Handling

Both templates require:
- Custom exceptions in services
- HTTPException in API routes
- Database rollback on errors
- Explicit error handling (no silent failures)

**Rationale:** Quality gate requires clean error handling.

### 6. Template Structure

`project_architecture.md` is a TEMPLATE:
- Projects should customize for their needs
- Covers all major architectural concerns
- Placeholder sections for project-specific details

**Rationale:** Every project has different needs, template provides structure.

---

## Usage Instructions

### For Projects Using These Templates

**1. Copy to project:**
```bash
cp ~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md \
   <project>/.claude/agent_briefings/

cp ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md \
   <project>/.claude/agent_briefings/
```

**2. Customize project_architecture.md:**
- Update project name
- Update technology stack
- Adjust directory structure
- Add/remove sections as needed

**3. Customize backend_implementation.md (if needed):**
- Adjust for framework differences
- Add project-specific patterns
- Update file structure examples

**4. Create additional domain briefings:**
- frontend_implementation.md (if frontend exists)
- database_implementation.md (if complex DB patterns)
- testing_implementation.md (if testing phase used)

**5. Reference in workflow command:**
```markdown
Task(
  subagent_type="implementation-agent-v1",
  prompt=f"""
  {read_file(".claude/agent_briefings/backend_implementation.md")}
  {read_file(".claude/agent_briefings/project_architecture.md")}

  [... epic spec, prescriptive plan ...]
  """
)
```

---

## Briefing Evolution Strategy

These briefings should evolve based on post-mortem feedback:

**After each epic execution:**
1. Post-mortem agent analyzes what worked/didn't
2. Agent suggests briefing updates
3. Human reviews suggestions
4. Human updates briefings accordingly

**Example workflow:**
```
Epic Execution
    ↓
Post-Mortem Analysis
    ↓
Recommendations: "Add pattern: Define Pydantic schemas before endpoints"
    ↓
Human updates backend_implementation.md
    ↓
Next epic benefits from improved briefing
```

**Track changes:**
- Update `updated:` field in YAML frontmatter
- Add version history comments
- Document why changes were made

---

## Integration with Agent Definitions

These briefings work WITH agent definitions:

**Agent Definition** (e.g., implementation_agent_v1.md):
- Phase-specific rules (MUST/MUST NOT)
- What agent is responsible for
- Output format requirements

**Domain Briefing** (e.g., backend_implementation.md):
- Domain-specific patterns
- Technology-specific conventions
- Project-specific architecture

**Project Architecture** (project_architecture.md):
- Project-wide rules
- Cross-domain patterns
- Organizational standards

**Composition in workflow:**
```
Agent Prompt = Agent Definition + Domain Briefing + Project Architecture + Epic Spec + Prescriptive Plan
```

---

## Next Steps

**Immediate:**
1. Create agent definitions (implementation_agent_v1.md, build_fixer_agent_v1.md, etc.)
2. Test briefings in sample epic
3. Validate patterns are clear and actionable

**Short-term:**
4. Create frontend_implementation.md (if applicable)
5. Create database_implementation.md (if complex patterns)
6. Integrate into execute-workflow.md command

**Long-term:**
7. Collect post-mortem feedback
8. Refine patterns based on real usage
9. Add project-specific patterns
10. Version control briefing evolution

---

## Success Criteria

These briefings are successful if:

- ✅ Implementation agents produce consistent code quality
- ✅ Fewer validation retry attempts (build/lint pass on first try)
- ✅ Post-mortems report clear, actionable patterns
- ✅ New agents understand project conventions quickly
- ✅ Code reviews find fewer architectural issues

**Measure via:**
- Post-mortem reports (track build retry count)
- Validation pass rate (% of epics passing on attempt 1)
- Briefing update frequency (how often patterns change)

---

## 🚫 CRITICAL: Agent Failure Reporting Protocol

**Source:** EPIC-013 post-mortem analysis (email_management_system)
**Applies to:** ALL implementation agents

### The Problem This Solves

**EPIC-013 Failure Mode:**
- Spec required: `claude-agent-sdk` package from specific source
- Agent tried: `pip install claude-agent-sdk` → Package not found
- Agent response: Created ENTIRE mocked infrastructure (simulation functions, hardcoded responses)
- Result: Tests passed against fake code, task marked "complete", massive waste of time/tokens

**Root cause:** Agent improvised when fundamentally blocked instead of reporting the blocker.

### Blocker Definition

A **blocker** is when:
1. Specification requires resource X (package, API, service, file)
2. You cannot access/find X using available tools
3. Proceeding without X would require improvisation/simulation
4. No alternative approach achieves the same functional result

### Examples: Blocker vs. Solvable

**✅ BLOCKERS (must report, cannot proceed):**
- Package not found in PyPI as specified: `pip install claude-agent-sdk` → Not found
- API endpoint returns 404 with no alternative: `POST /api/v2/complete` → 404
- Authentication fails despite correct credentials: `API_KEY=xxx` → 401 Unauthorized
- Service not running: `curl http://localhost:8000/health` → Connection refused
- Required file doesn't exist: Spec says "use config/database.yaml" → File not found

**❌ NOT BLOCKERS (solvable, proceed with problem-solving):**
- Need different import path: Try `from foo import bar` → Try `from foo.bar import baz`
- Minor syntax error: Fix and retry
- Test fails: Debug, identify issue, fix root cause
- Type hint error: Investigate types, add correct annotations
- Linting issue: Run `ruff check --fix .`, address remaining issues

**Key distinction:** Can you solve this with available tools and knowledge? YES = not a blocker. NO = blocker.

### 🚫 ABSOLUTE PROHIBITION: No Improvisation When Blocked

If you encounter a blocker, you are **FORBIDDEN** from:

- ❌ Creating simulation/stub implementations (`def _simulate_*`, `def _mock_*`, `def _fake_*`)
- ❌ Returning hardcoded/pattern-based data (if "keyword" in prompt: return "hardcoded")
- ❌ Writing tests that validate mocks instead of real behavior
- ❌ Marking task complete when functionality doesn't work
- ❌ Saying "I'll fake it for now and come back later"
- ❌ Creating placeholder implementations with TODOs
- ❌ Improvising alternative approaches not in specification

**Why this is critical:**
- Mocked code wastes tokens on useless implementation
- Tests pass against fake functionality (false confidence)
- Validation phase doesn't catch the issue (no real tests)
- Human discovers broken functionality much later
- Massive cleanup required to remove simulation code

### ✅ REQUIRED: Stop and Report

When you encounter a blocker, you **MUST**:

1. ✅ **Stop immediately** - Do not proceed with improvisation
2. ✅ **Output blocker report** - Use standardized format below
3. ✅ **Mark task as BLOCKED** - NOT "complete", NOT "in progress"
4. ✅ **Preserve diagnostic info** - Include error messages, commands tried, outputs

### Blocker Report Format

Use this exact format in your output:

```
🚫 BLOCKER DETECTED 🚫

**Blocker Type:** [Package Not Found | API Error | Auth Failure | Service Unavailable | File Not Found]

**What was expected:**
- [Specific requirement from spec/task file]
- [Exact resource/package/endpoint expected]
- [Where it was supposed to be found]

**What actually happened:**
- [Specific error encountered]
- [Exact command that failed]
- [Error message/output received]

**Tools/methods attempted:**
- [Command 1: result]
- [Command 2: result]
- [Command 3: result]

**Cannot proceed because:**
- [Why this blocks functional implementation]
- [What would need to be mocked/simulated to proceed]
- [Why alternative approaches won't achieve spec requirements]

**Awaiting human intervention to:**
- [ ] Verify package name/source is correct
- [ ] Provide correct installation instructions
- [ ] Update specification if alternative approach needed
- [ ] Provide credentials/access if auth issue
- [ ] Start required service if service unavailable

**Task Status:** BLOCKED (not proceeding with implementation)
```

### When to Use This Protocol

**Use blocker reporting when:**
- External resource required by spec cannot be accessed
- No reasonable alternative exists within project constraints
- Proceeding would require inventing/mocking functionality

**Do NOT use blocker reporting for:**
- Normal debugging (syntax errors, type issues, logic bugs)
- Solvable problems (wrong import path, missing dependency declaration)
- Optimization issues (slow query, inefficient algorithm)
- Test failures (these are expected, debug and fix)

**If uncertain:** Ask yourself: "Can I solve this without inventing functionality?"
- YES → Not a blocker, solve it
- NO → Blocker, report it

### Integration with Workflow

**After blocker report:**
1. Agent outputs blocker report in standardized format
2. Agent marks task as BLOCKED in results JSON
3. Orchestrator detects blocked status → pauses workflow
4. Human reviews blocker → provides resolution
5. Workflow resumes with corrected information

**Validation pipeline includes:**
- Automated detection of simulation patterns (see `scripts/detect_simulation_code.py`)
- Reality checks in tests to prove real external integration
- Blocker report parsing to track and resolve blockers systematically

---

## Conclusion

Two comprehensive agent briefing templates created:

1. **backend_implementation.md** - Python/FastAPI domain briefing with service layer, error handling, async patterns
2. **project_architecture.md** - Project-wide architectural rules covering all major concerns

Both templates include:
- Clear code examples (✅ correct vs ❌ wrong)
- Complete type hints
- Error handling patterns
- Checklists for validation
- Questions to ask if unclear

**Ready for integration into Tier 1 workflow system.**

**Next:** Create agent definitions to complete the agent/briefing system.
