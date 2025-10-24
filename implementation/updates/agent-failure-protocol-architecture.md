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
