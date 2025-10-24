# CLAUDE.md Workflow Sections - Template Library

**Purpose:** Standardized workflow documentation sections for project CLAUDE.md files

**Target projects:**
- **Tier1 Workflow:** whisper_hotkeys, ppt_pipeline, clinical-eda-pipeline
- **V6 Workflow:** email_management_system

**Last updated:** 2025-10-22

---

## Section 1: Tier1 Workflow Template

Use this section for projects using the Tier1 Enhanced Workflow (simple projects without V6 architecture complexity).

```markdown
## 🚀 Tier 1 Workflow System (MANDATORY)

This project uses the **Tier 1 Enhanced Workflow** - a streamlined workflow system for AI-assisted development with prescriptive implementation plans and automated validation.

### Workflow Overview

**Philosophy:** Agents are WORKERS. You coordinate, they execute.

**Core components:**
- **Epic specification:** Interactive requirements gathering with Context7 research
- **Prescriptive implementation plans:** File-by-file instructions for agents
- **Sequential/parallel execution:** Automatic detection of parallel execution opportunities
- **Validation with retry loop:** Auto-lint + build fixer agents for error recovery
- **Post-mortem analysis:** Automated learnings capture for continuous improvement

### Key Commands

#### Create Epic Specification

```bash
/spec-epic "Epic title"
```

**What it does:**
1. Interactive questioning (12 questions across 3 rounds)
2. Consults workflow pattern library for best practices
3. Creates epic directory structure: `.tasks/backlog/EPIC-XXX-slug/`
4. Generates specification files:
   - `spec.md` - Requirements, user scenarios, acceptance criteria
   - `architecture.md` - System design, components, data flow
   - `implementation-details/file-tasks.md` - Prescriptive plan (agent source of truth)
5. Creates GitHub issue (optional, non-blocking)

**Output style:** Use `/output-style Spec Architect` for comprehensive specification generation

**Validation:** Epic MUST have complete `file-tasks.md` before execution (ADR-012 two-phase validation)

#### Execute Epic Implementation

```bash
/execute-workflow EPIC-XXX
```

**Workflow phases:**

**Phase 0: Preflight Checks**
- Verifies epic directory exists
- Two-phase validation (ADR-012):
  - Phase 1: File existence (`spec.md`, `architecture.md`, `file-tasks.md`)
  - Phase 2: Template placeholder detection (18 markers)
- Checks git working directory is clean
- Detects parallel execution opportunities
- Displays epic summary

**Phase 1A/1B: Implementation**
- **Sequential mode (1A):** Single implementation agent, main branch
- **Parallel mode (1B + 1C):** Multiple agents in git worktrees, sequential merge
- Auto-lint (`ruff check --fix`) before validation (Phase 1B)
- Agents follow prescriptive plan from `file-tasks.md`

**Phase 2: Validation with Retry Loop**
- Runs validation suite (Python: ruff + mypy, TypeScript: tsc, architecture checks)
- Auto-lint first to prevent common errors
- Max 3 validation attempts
- Deploys build fixer agent on validation failure
- Retries validation after fix

**Phase 5: Commit & Cleanup**
- Generates commit message from epic results
- Creates commit with Claude Code attribution
- Moves epic to `.tasks/completed/`
- Closes GitHub issue (optional)

**Phase 6: Post-Mortem (MANDATORY)**
- Analyzes workflow execution
- Answers 4 key questions:
  - What worked well?
  - What challenges occurred?
  - How were challenges resolved?
  - What should improve next time?
- Generates `.workflow/post-mortem/EPIC-XXX.md`
- Provides actionable recommendations for briefing updates

### Critical Architectural Patterns

#### Two-Phase Validation (ADR-012)

**Phase 1:** File existence check
**Phase 2:** Template placeholder detection

18 template markers prevent false "ready for execution" states:
- `[What happens now]`, `[What should happen]`, `[Component Name]`
- `[table_name]`, `[METHOD] /api/`, `[Performance targets]`
- `_To be defined`, `_To be determined`, etc.

**Why this matters:** Prevents workflow execution with incomplete specifications

#### Prescriptive Implementation Plans

**File:** `implementation-details/file-tasks.md`

**Format:** File-by-file instructions with exact code to write

**Example structure:**
```markdown
## File: src/components/example.py

**Purpose:** [What this file does]

**Dependencies:** [Other files it depends on]

**Implementation:**

```python
# Exact code here
from typing import Optional

class Example:
    """Example class."""

    def process(self, data: str) -> Optional[str]:
        """Process data."""
        if not data:
            return None
        return data.upper()
```

**Testing requirements:** [Unit tests to write]
```

**Why prescriptive:** Agents execute exactly as specified, no interpretation needed

#### Pre-Validation Linting Pattern

**Implementation agents MUST run auto-lint before marking tasks complete:**

```bash
# Auto-fix linting issues
ruff check --fix .

# Verify linting passes
ruff check .

# Mark task complete only if both succeed
```

**Workflow-level safety net:** Phase 1B runs auto-lint even if agent forgets

**Impact:** 50-60% reduction in linting-related validation failures

#### Parallel Execution Detection

**Automatic detection based on:**
- File count (≥3 files)
- Domain separation (backend/frontend/database/tests/docs)
- File overlap analysis (<20% overlap between domains)

**Parallel execution uses:**
- Git worktrees (isolated working directories)
- Sequential merge (dependency-ordered, conflict detection)
- GitHub sub-issues for tracking (optional)

**Benefits:**
- 2-5x faster implementation for large epics
- Domain isolation prevents conflicts
- Observable progress per domain

### Common Pitfalls & Solutions

#### Pitfall 1: Epic Not Ready for Execution

**Symptom:** `/execute-workflow` fails with "Epic not ready"

**Cause:** Missing `file-tasks.md` or incomplete specification

**Solution:**
1. Switch to Spec Architect output style: `/output-style Spec Architect`
2. Read spec and architecture: `read .tasks/backlog/EPIC-XXX-*/spec.md`
3. Ask Claude to generate file-tasks.md (Phase 5.5 of Spec Architect)
4. Re-run `/execute-workflow EPIC-XXX`

#### Pitfall 2: Validation Failures

**Symptom:** Phase 2 validation fails multiple times

**Cause:** Type errors, missing imports, architectural violations

**Solution:**
1. Check if auto-lint ran (Phase 1B should show "Running: ruff check --fix")
2. Review validation logs: `.workflow/outputs/EPIC-XXX/validation/attempt_N.log`
3. Build fixer agent should auto-fix (max 3 attempts)
4. If agent can't fix: Manual intervention required

**Prevention:**
- Use pre-validation linting pattern in agents
- Add module-level type annotations: `var_name: list[str] = []`
- Run `mypy src/` during implementation

#### Pitfall 3: Git Working Directory Not Clean

**Symptom:** Preflight check fails with uncommitted changes

**Cause:** Previous work not committed

**Solution:**
```bash
# Option 1: Commit changes
git add .
git commit -m "Your message"

# Option 2: Stash changes
git stash

# Then re-run workflow
/execute-workflow EPIC-XXX
```

#### Pitfall 4: Post-Mortem Recommendations Ignored

**Symptom:** Same issues repeat across multiple epics

**Cause:** Post-mortem learnings not applied to agent briefings

**Solution:**
1. Read post-mortem: `cat .workflow/post-mortem/EPIC-XXX.md`
2. Review "Briefing Updates" section
3. Update relevant briefings: `.claude/agent_briefings/*.md`
4. Commit separately: `git commit -m "refine: update briefings from EPIC-XXX post-mortem"`

**Why this matters:** Post-mortems enable continuous workflow improvement

### File Structure

```
.tasks/
├── backlog/           # Epics awaiting implementation
├── current/           # In-progress epics (deprecated - use status field)
├── completed/         # Completed epics
└── templates/         # Epic templates (spec.md.j2, architecture.md.j2, file-tasks.md.j2)

.workflow/
├── outputs/           # Implementation results (by epic ID)
│   └── EPIC-XXX/
│       ├── phase1_results.json           # Sequential implementation results
│       ├── phase1_parallel_results.json  # Parallel implementation results
│       ├── merge_summary.json            # Merge results (parallel mode)
│       ├── validation/                   # Validation logs and results
│       │   ├── attempt_N.log
│       │   └── result.json
│       └── fix_attempt_N.json            # Build fixer results
└── post-mortem/       # Post-mortem reports (by epic ID)
    └── EPIC-XXX.md

.claude/
├── commands/
│   ├── spec-epic.md           # Interactive specification creation
│   └── execute-workflow.md    # Workflow orchestration
├── agents/
│   ├── implementation_agent_v1.md   # Implementation agent definition
│   ├── build_fixer_agent_v1.md      # Error recovery agent
│   └── post_mortem_agent_v1.md      # Post-mortem analysis agent
└── agent_briefings/
    ├── backend_implementation.md     # Backend patterns and conventions
    ├── frontend_implementation.md    # Frontend patterns
    ├── database_implementation.md    # Database patterns
    ├── testing_implementation.md     # Testing patterns
    └── project_architecture.md       # Project-wide architectural decisions
```

### Verification Steps

**Before starting development:**
1. Verify epic specification exists: `ls .tasks/backlog/EPIC-XXX-*/`
2. Check file-tasks.md is complete: `wc -l .tasks/backlog/EPIC-XXX-*/implementation-details/file-tasks.md`
   - Expect >50 lines for real implementation plan
3. Check git status clean: `git status`
4. Review epic summary: `cat .tasks/backlog/EPIC-XXX-*/spec.md`

**During workflow execution:**
1. Monitor phase completion messages (✅/⚠️/❌)
2. Check validation logs if failures occur: `.workflow/outputs/EPIC-XXX/validation/`
3. Verify agent results files exist: `.workflow/outputs/EPIC-XXX/*.json`

**After workflow completion:**
1. Review commit: `git show`
2. Read post-mortem: `cat .workflow/post-mortem/EPIC-XXX.md`
3. Apply recommendations to briefings
4. Push changes: `git push`

### Links to Documentation

**Core workflow documentation:**
- `~/tier1_workflow_global/README.md` - Tier1 workflow overview
- `~/tier1_workflow_global/ADR-012_GLOBAL_ROLLOUT_COMPLETE.md` - Architecture decisions

**Implementation details:**
- `.claude/commands/execute-workflow.md` - Complete workflow orchestration guide
- `.claude/commands/spec-epic.md` - Interactive specification process
- `.claude/agents/*.md` - Agent definitions and constraints

**Pattern library:**
- `~/.claude/workflow_pattern_library/patterns/` - Reusable workflow patterns
- Semantic search enabled via Context7 integration

**Validation metrics:**
- `tools/validation_metrics_tracker.py` - Metrics tracking system (optional)
- `.workflow/validation_metrics.md` - Dashboard (generated after epic completion)
```

---

## Section 2: V6 Workflow Template

Use this section for projects using the V6 Workflow (complex projects with graph-server, MCP integrations, multi-agent orchestration).

```markdown
## 🚀 V6 Workflow System (MANDATORY)

This project uses the **V6 Workflow** - an advanced workflow system with graph-server intelligence, MCP tool integration, and sophisticated multi-agent orchestration.

### Workflow Overview

**Philosophy:** Graph-based workflow orchestration with dynamic agent management and multi-layered caching.

**Key differences from Tier1:**
- **Graph-server integration:** Central code intelligence, dependency analysis, workflow orchestration
- **MCP tool ecosystem:** Context7 research, unified-v6-server for workflow operations
- **Dynamic agent management:** Agent Pool Manager, Agent Selector, Multi-Agent Coordinator
- **Advanced caching:** Multi-layered caching (semantic, compilation, dependency)
- **Error recovery:** Autonomous error recovery and state management

### Key Commands

#### Execute V6 Workflow

```bash
/workflow:execute-workflow EPIC-ID
```

**CRITICAL ARCHITECTURE: Command Pattern**
- **Tool PREPARES:** `execute_workflow_v6` MCP tool validates, creates issues, loads plans
- **Claude Code session EXECUTES:** Deploys agents, runs validation, creates commits
- **Why:** MCP tools can't call Task tool (agent deployment) - separation of concerns

**Workflow phases:**

**Step 1: Call execute_workflow_v6 Tool**
```python
mcp__unified_v6_server__execute_workflow_v6(epic_id="EPIC-XXX")
```

Returns:
- Validated specification files
- GitHub issue creation status
- Implementation plan
- Phase 7 post-mortem artifact preparation
- INSTRUCTIONS for Claude Code to execute

**Step 2: Deploy Implementation Agent**
```python
Task(
    subagent_type="general-purpose",
    description=f"Implementation for EPIC-XXX",
    prompt="[Agent definition + domain briefing + spec + plan]"
)
```

**Step 3: Run Validation**
```bash
npm run validate-all
```

Includes:
- Python validation: `ruff check`, `ruff format --check`, `mypy`
- TypeScript validation: `npm run build:ts`
- Architecture validation: boundary checks, contract compliance
- Testing: `npm run test`

**Step 4: Mark Task Complete**
- Update task status
- Record completion timestamp

**Step 5: Deploy Phase 7 Post-Mortem Agent (MANDATORY)**
```python
Task(
    subagent_type="general-purpose",
    description=f"Post-mortem analysis for EPIC-XXX",
    prompt="[Post-mortem agent definition + workflow artifacts]"
)
```

**Step 6: Display Completion Summary**
- Epic status
- Files modified
- Validation results
- Post-mortem report location

### Critical Architectural Patterns

#### Graph-Server Power Tools (MANDATORY)

**BEFORE any code change:**
```bash
# Analyze dependencies
graph-server analyze <file>

# Check neighborhood (what depends on this file, what it depends on)
graph-server neighborhood <file>

# Find all dependents (impact analysis)
graph-server dependents <file>
```

**AFTER any code change:**
```bash
# Re-run analysis
graph-server analyze <file>

# Verify no broken dependencies
graph-server dependents <file>

# Document results in PR/task
```

**Why mandatory:** Prevents breaking changes, ensures architectural compliance

#### Context7 Research Integration (MANDATORY)

**BEFORE working with external libraries:**
1. Resolve library ID: `mcp__context7__resolve-library-id("library-name")`
2. Get documentation: `mcp__context7__get-library-docs("/org/project", topic="specific-feature")`
3. Capture for pattern library: `mcp__unified_v6_server__capture_context7_research(...)`

**Pattern library benefits:**
- 60-70% reduction in external Context7 calls
- Semantic search for local patterns first
- Automatic pattern extraction queue

#### V6 Agent Management

**Static domain briefings (NOT dynamic generation):**
- `docs/architecture/SUB-AGENT-BRIEFING-BACKEND.md`
- `docs/architecture/SUB-AGENT-BRIEFING-FRONTEND-OPTIMIZED.md`
- `docs/architecture/SUB-AGENT-BRIEFING-TESTING-V6.md`
- `docs/architecture/SUB-AGENT-BRIEFING-WORKFLOW.md`

**Why static:** Phase 3 validation proved static = dynamic quality, 92.5% code reduction

**Agent composition:**
- Agent Pool Manager: Persistent processes, concurrent execution, health monitoring
- Agent Selector: Capability-based selection, task requirements matching
- Multi-Agent Coordinator: Semantic conflict prediction, coordination strategy

#### Explicit Validation (Phase 6)

**Python validation:**
```bash
npm run lint:py              # Ruff linting
npm run lint:py:fix          # Auto-fix linting issues
npm run format:py:check      # Check formatting
npm run format:py            # Auto-format code
npm run typecheck:py         # Mypy type checking
npm run validate-python      # All Python checks
```

**TypeScript validation:**
```bash
npm run build:ts             # TypeScript compilation check
npm run validate-typescript  # Alias for build:ts
```

**Architecture & contracts:**
```bash
npm run validate-architecture  # Check boundaries
npm run validate-contracts     # Verify contract compliance
```

**Complete validation:**
```bash
npm run validate-all         # Run ALL validations
```

**Principle:** Explicit > Automatic. Agents run these directly, not via mysterious hooks.

#### Phase 7 Post-Mortem (MANDATORY)

**Unlike Tier1:** Phase 7 is NON-OPTIONAL in V6 workflow

**Why:** V6 complexity requires rigorous post-mortem analysis

**What happens:**
- Automated deployment at end of every workflow run
- Analyzes graph-server impact, validation results, agent coordination
- Captures learnings for documentation freshness system
- Generates recommendations for briefing updates

### Output Styles (V6-Optimized)

**Three specialized output styles for V6 workflow stages:**

#### 1. V6 Default Concise (PROJECT DEFAULT)
```bash
/output-style V6 Default Concise
```

**When:** General development, bug fixes, features, refactoring

**Features:**
- Terse, test-driven responses
- Structured format: ANALYSIS/REPRO/DIFF/VALIDATION/NOTES
- Graph-server impact analysis before changes
- Coverage enforcement (≥85% backend, ≥90% graph-server)
- Banned patterns checklist

#### 2. Spec Architect V6
```bash
/output-style Spec Architect V6
```

**When:** `/spec-epic` command, requirements gathering, architecture design

**Features:**
- Interactive specification creation
- Batched clarifying questions (≤10 per round)
- Graph-server intelligence + workflow knowledge queries
- Context7 research + pattern capture
- Contract generation and parallel work planning

#### 3. Workflow Orchestrator V6
```bash
/output-style Workflow Orchestrator V6
```

**When:** `/execute-workflow` command, multi-agent coordination

**Features:**
- Structured workflow execution
- YAML status blocks (run_id/timestamp/repo_sha)
- Task tool delegation (no prose)
- GitHub Issues tracking + worktree isolation
- Explicit npm validation scripts

### Graph-Server TypeScript Rules (CRITICAL)

**ALL agents working on graph-server TypeScript code MUST follow:**

#### Pure TypeScript
- Modern TypeScript services in `/graph-server/src/services/`
- Legacy JavaScript services archived to `/.archive/legacy-services/`
- Service registry loads ONLY TypeScript implementations

#### Mandatory TypeScript Patterns

**Service imports:**
```typescript
// REQUIRED: Import modern TypeScript services
import { ServiceName } from '../services/ServiceName.js';

// REQUIRED: Type assertion for service factories
return new ServiceName() as unknown as IService;
```

**Array type declarations:**
```typescript
// FORBIDDEN: Never use empty arrays (infers never[])
const items = [];

// REQUIRED: Always explicitly type arrays
const items: ItemType[] = [];
const items: Array<ItemType> = [];
```

**Error handling:**
```typescript
// REQUIRED: Proper error type guards
const errorMessage = error instanceof Error ? error.message : String(error);
logger.warn('Message', { error: errorMessage });
```

**Service factory pattern:**
```typescript
// REQUIRED: All service factories must return IService-compatible types
export const createServiceDefinition = (ServiceClass: any, ...args: any[]) => ({
  factory: async (container: ServiceContainer) => {
    const instance = new ServiceClass(...args);
    return instance as unknown as IService;
  }
});
```

#### Mandatory Compilation Testing

**BEFORE completing ANY graph-server task:**
```bash
cd graph-server
npm run build:ts  # MUST pass with zero errors
```

**Why:** Previous agent work generated 40-100k token fixing sessions due to TypeScript violations

### Common Pitfalls & Solutions

#### Pitfall 1: Skipping Graph-Server Analysis

**Symptom:** Breaking changes, architectural violations, broken dependencies

**Cause:** Code changes without graph-server impact analysis

**Solution:**
1. Always run graph-server tools BEFORE changes
2. Document analysis in task/PR
3. Re-run analysis AFTER changes
4. Verify no new broken dependencies

#### Pitfall 2: Not Using Context7

**Symptom:** Outdated API usage, incorrect library patterns, integration issues

**Cause:** Guessing library usage without research

**Solution:**
1. Resolve library ID: `mcp__context7__resolve-library-id`
2. Get documentation: `mcp__context7__get-library-docs`
3. Capture for pattern library
4. Apply official patterns from documentation

#### Pitfall 3: Skipping Phase 7 Post-Mortem

**Symptom:** Workflow reports "Phase 7 required but not executed"

**Cause:** Phase 7 deployment forgotten or skipped

**Solution:**
- Phase 7 is MANDATORY in V6 workflow
- Tool automatically prepares artifacts
- Claude Code session MUST deploy post-mortem agent
- Workflow cannot complete without Phase 7

#### Pitfall 4: Documentation Staleness

**Symptom:** Stale documentation warnings during workflow execution

**Cause:** Code changes without corresponding documentation updates

**Solution:**
1. Review freshness check warnings during Phase 0
2. Update relevant docs after code changes
3. Update frontmatter: `last_updated`, `git_hash`
4. Commit documentation with code changes

**Monitored documentation:**
- Core workflow references (9 docs)
- Domain briefings (4 docs)
- Key ADRs (active)

### File Structure

```
.tasks/                    # Task management (V6)
docs/
├── reference/             # V6 system reference docs
│   ├── v6-workflow-orchestration-reference.md
│   ├── v6-agent-management-reference.md
│   ├── graph-server-architecture-reference.md
│   ├── context7-research-integration-v6-reference.md
│   └── task-management-reference.md
└── architecture/
    ├── SUB-AGENT-BRIEFING-*.md    # Domain briefings
    └── ADR-*.md                    # Architecture Decision Records

.claude/
├── commands/
│   └── workflow/
│       └── execute-workflow.md    # V6 workflow orchestration
├── output-styles/
│   ├── v6-default-concise.md
│   ├── spec-architect-v6.md
│   └── workflow-orchestrator-v6.md
└── hooks/                         # Event-driven validation (tier-based)

graph-server/
├── src/
│   ├── services/                  # Modern TypeScript services
│   └── ...
└── .archive/
    └── legacy-services/           # Archived JavaScript services

tools/
├── workflow_utilities_v6/
│   ├── hooks/                     # Hook implementations
│   └── ...
└── validate_*.py                  # Validation scripts
```

### Verification Steps

**Before workflow execution:**
1. Check graph-server status: `graph-server status`
2. Verify MCP tools available: `mcp__unified_v6_server__health_check()`
3. Review task specification: `mcp__tasks__get_task(task_id="EPIC-XXX")`

**During workflow execution:**
1. Monitor YAML status blocks (run_id, timestamp, repo_sha)
2. Check validation script outputs
3. Verify graph-server analysis documented

**After workflow completion:**
1. Read post-mortem: `cat .workflow/post-mortem/EPIC-XXX.md`
2. Review documentation freshness warnings
3. Update stale documentation
4. Apply briefing recommendations

### Links to Documentation

**Core V6 references (in docs/reference/):**
- `v6-workflow-orchestration-reference.md` - Complete workflow orchestration guide
- `v6-agent-management-reference.md` - Agent Pool Manager, Agent Selector, Multi-Agent Coordinator
- `graph-server-architecture-reference.md` - Code intelligence and dependency analysis
- `context7-research-integration-v6-reference.md` - Research integration and pattern library
- `task-management-reference.md` - Task system integration
- `v6-cache-system-reference.md` - Multi-layered caching architecture
- `v6-error-handling-recovery-system-reference.md` - Autonomous error recovery
- `v6-hooks-system-reference.md` - Event-driven validation and automation

**Domain briefings (in docs/architecture/):**
- `SUB-AGENT-BRIEFING-BACKEND.md` - Backend service patterns
- `SUB-AGENT-BRIEFING-FRONTEND-OPTIMIZED.md` - Frontend EmailContext patterns
- `SUB-AGENT-BRIEFING-TESTING-V6.md` - V6 workflow testing patterns
- `SUB-AGENT-BRIEFING-WORKFLOW.md` - Workflow agent patterns

**MCP integration:**
- `v6-mcp-integration-bridge-reference.md` - MCP tool integration patterns
- `v6-phase-scripts-implementation-reference.md` - Phase script implementations

**Design system:**
- Figma integration, automated design-to-code sync
- Design token validation
```

---

## Section 2.5: Pattern Library Integration

Add this section to projects that have access to the Pattern Library MCP server (both Tier1 and V6 projects).

```markdown
# Pattern Library

**MCP Server**: `mcp__pattern_library__*` tools available globally

**Research Workflow** (when working with external libraries):

1. **Search**: `mcp__pattern_library__search_patterns query="library-name pattern"`
2. **Retrieve**: `mcp__pattern_library__retrieve_pattern pattern_id="..."`
3. **Fallback**: Call Context7 if insufficient (auto-queues for extraction)

**Benefits**: Saves 5-15k tokens per Context7 call, ensures consistency

**Note**: Pattern library is configured globally and automatically available in all projects. See `~/.claude/CLAUDE.md` for detailed documentation.
```

---

## Section 3: Implementation Guide

### How to Use These Templates

**For Tier1 projects (whisper_hotkeys, ppt_pipeline, clinical-eda-pipeline):**

1. Open project CLAUDE.md file
2. Find or create "Workflow System" section
3. Copy **Section 1: Tier1 Workflow Template** (entire section)
4. Paste into CLAUDE.md, replacing any existing workflow documentation
5. (Optional) Add **Section 2.5: Pattern Library Integration** if project uses Pattern Library MCP
6. Customize:
   - Update file paths if project structure differs
   - Add project-specific commands or patterns
   - Remove features not applicable (e.g., GitHub integration if not used)
7. Verify all links work and file paths are correct
8. Commit: `git commit -m "docs: standardize workflow documentation from tier1_workflow_global"`

**For V6 projects (email_management_system):**

1. Open project CLAUDE.md file
2. Find "Key Workflows & Commands" section (around line 198 in email_management_system)
3. Copy **Section 2: V6 Workflow Template** (entire section)
4. Replace existing V6 workflow documentation
5. (Optional) Add **Section 2.5: Pattern Library Integration** if project uses Pattern Library MCP
6. Verify:
   - Graph-server TypeScript rules section exists (lines 112-196)
   - Output styles section exists (lines 242-288)
   - Documentation workflow section exists (lines 295-351)
7. Keep existing project-specific sections:
   - System Configuration & Style Guidelines
   - Critical Architectural Compliance
   - Domain Compliance: Required/Forbidden Patterns
8. Commit: `git commit -m "docs: standardize V6 workflow documentation"`

### Template Maintenance

**Location:** `~/tier1_workflow_global/implementation/architecture/CLAUDE_WORKFLOW_SECTIONS.md`

**Update frequency:** After significant workflow improvements (e.g., EPIC-002 patterns)

**Propagation workflow:**
1. Update this template file with new patterns
2. Create ADR documenting the change (e.g., ADR-012)
3. Test in one project first
4. Propagate to all projects using template
5. Update global project registry: `~/tier1_workflow_global/implementation/PROJECT_REGISTRY.md`

### Validation Checklist

**Before committing CLAUDE.md changes:**

- [ ] All file paths are absolute or relative to project root
- [ ] All command examples are accurate (tested)
- [ ] Section headings use consistent emoji (🚀 for workflows)
- [ ] Code blocks have correct language tags
- [ ] Internal links work (checked with grep/search)
- [ ] External links to global templates are correct
- [ ] No template placeholders remain (e.g., `{{ variable }}`)
- [ ] Workflow-specific sections match project's actual workflow version
- [ ] Examples reflect current project structure

### Key Differences Between Tier1 and V6

| Feature | Tier1 | V6 |
|---------|-------|-----|
| Complexity | Simple projects | Complex projects with graph-server |
| MCP Tools | Optional (GitHub only) | Mandatory (Context7, unified-v6-server, graph-server) |
| Agent Management | Static definitions | Dynamic Pool Manager + Agent Selector |
| Validation | Auto-lint + retry loop | Explicit npm scripts + architecture checks |
| Post-Mortem | Phase 6 (optional) | Phase 7 (MANDATORY) |
| Caching | None | Multi-layered (semantic, compilation, dependency) |
| Documentation | Simple README/ADRs | Freshness check system, monitored docs |
| Error Recovery | Build fixer agent | Autonomous error recovery system |
| Output Styles | Generic or custom | Three specialized V6 styles |
| Graph Intelligence | None | graph-server mandatory for all changes |

### Common Customizations

**Project-specific additions:**

1. **Custom commands:** Add project-specific slash commands in separate subsection
2. **Domain-specific patterns:** Link to project's unique patterns (e.g., email_management_system's EmailContext)
3. **Integration notes:** Document third-party integrations (e.g., Nextcloud, Figma)
4. **Testing requirements:** Customize coverage thresholds if different from defaults
5. **Deployment notes:** Add deployment-specific instructions (e.g., Docker, blue-green)

**Sections to preserve (do not replace):**

- System Configuration & Style Guidelines (project-specific identity)
- Critical Architectural Compliance (project-specific architecture rules)
- Absolute Prohibitions (project-specific forbidden patterns, e.g., no mocking)
- Domain Compliance: Required/Forbidden Patterns (project-specific validation rules)

### Future Template Evolution

**Planned improvements:**
- Automatic template version tracking (detect when CLAUDE.md is out of sync)
- Slash command to update CLAUDE.md from template: `/update-claude-md`
- Project registry integration to track which projects use which workflow version
- Automated testing of documentation accuracy (link checking, command validation)

**Feedback loop:**
- Post-mortem recommendations automatically queued for template updates
- Quarterly review of all project CLAUDE.md files for consistency
- Pattern library integration (auto-inject relevant patterns into CLAUDE.md)

---

## Appendix: Template Versioning

**Current template version:** 1.1.0

**Changelog:**

**1.1.0 (2025-10-24):**
- Added Section 2.5: Pattern Library Integration
- Documents MCP Pattern Library workflow for both Tier1 and V6 projects
- Updated implementation guide to include optional Pattern Library section
- Provides 5-15k token savings per Context7 call through local pattern reuse

**1.0.0 (2025-10-22):**
- Initial creation of standardized workflow sections
- Tier1 workflow template based on clinical-eda-pipeline + EPIC-002 improvements
- V6 workflow template based on email_management_system current documentation
- Implementation guide for template usage and maintenance
- Validation checklist and customization guidance

**Future versions will track:**
- Template updates from post-mortem learnings
- New workflow phases or pattern additions
- Breaking changes (require manual project updates)
- Non-breaking enhancements (optional project updates)
