# ADR-013: Epic Registry and Longitudinal Tracking System

**Status**: Proposed
**Date**: 2025-10-23
**Deciders**: Andreas Spannbauer
**Context**: Tier 1 Workflow Global - Epic Management Enhancement

---

## Problem Statement

The current Tier 1 workflow has critical gaps in epic lifecycle management and knowledge continuity:

### 1. GitHub Integration Failure
**Current State**: GitHub issue creation is "optional" in `/spec-epic` and `/execute-workflow`, leading to:
- ❌ Epics never synced to GitHub unless explicitly instructed
- ❌ Silent failures (non-blocking errors swallowed)
- ❌ No centralized tracking of work items
- ❌ Parallel work across projects difficult to coordinate

**Evidence**: Email Management System project has no GitHub issues despite multiple epic executions.

### 2. Epic Numbering Chaos
**Current State**: Epic IDs are generated sequentially based on file scanning, leading to:
- ❌ EPIC-002 executed 3 times (same ID, different work)
- ❌ No unique constraint enforcement
- ❌ Epic ID collisions when working in parallel
- ❌ Can't track "what was EPIC-002 v1 vs v2 vs v3"

**Evidence**: User reported executing "epic two, I think three times by now" in email management project.

### 3. No Epic Registry
**Current State**: No centralized view of epic lifecycle, leading to:
- ❌ Can't answer "which epics are defined vs prepared vs implemented?"
- ❌ Can't identify next epic to implement
- ❌ No coverage analysis (are all master spec requirements covered?)
- ❌ Can't track epic dependencies or integration needs

**Evidence**: User has to manually track which epics are complete across projects.

### 4. Manual Epic Selection
**Current State**: Must explicitly name epic to execute, leading to:
- ❌ `/execute-workflow EPIC-003` requires knowing epic ID
- ❌ Can't automate "execute next pending epic"
- ❌ Parallel work on multiple projects requires manual coordination
- ❌ Wastes time searching for next task

**User Need**: "I just say execute workflow, next, and then simply the next upcoming epic is executed automatically without me having to specify which one."

### 5. No Integration Planning
**Current State**: Epics complete in isolation, leading to:
- ❌ No step to integrate with past epics
- ❌ No plan for integrating with future epics
- ❌ User had to manually ask "how do we integrate epics 1-3?" in clinical EDA project
- ❌ Integration becomes a separate manual task

**User Need**: "This kind of recursive action where we don't just focus on each individual epic, but also that there is a step in between where the epic is put into context of already completed epics and planned epics."

### 6. No Longitudinal Learning
**Current State**: Post-mortems are isolated documents, leading to:
- ❌ Epic N+1 doesn't benefit from Epic N learnings
- ❌ Same mistakes repeated across epics
- ❌ No "project memory" beyond CLAUDE.md
- ❌ Can't identify patterns across epic implementations

**User Need**: "There is some learning process with the post-mortem. But I think that sort of project-specific journey from the first epic to the 10th isn't as well implemented as it should be."

---

## Decision

Implement a **Project-Level Epic Registry and Longitudinal Tracking System** with these components:

### 1. Epic Registry (`project/.tasks/epic_registry.json`)

Centralized state machine tracking all epics across their lifecycle:

```json
{
  "schema_version": "2.0",
  "project_name": "email_management_system",
  "master_spec_path": ".tasks/master_spec.md",
  "created": "2025-10-23T10:00:00Z",
  "last_updated": "2025-10-23T14:30:00Z",
  "github_repo": "user/email-management-system",
  "next_epic_number": 4,
  "statistics": {
    "total_epics": 3,
    "defined": 0,
    "prepared": 1,
    "ready": 0,
    "implemented": 2,
    "archived": 0
  },
  "epics": [
    {
      "epic_id": "EPIC-001",
      "epic_number": 1,
      "title": "Email Parser Foundation",
      "slug": "email-parser-foundation",
      "status": "implemented",
      "created_date": "2025-10-15",
      "prepared_date": "2025-10-15",
      "implemented_date": "2025-10-16",
      "directory": ".tasks/completed/EPIC-001-email-parser-foundation",
      "github_issue": 15,
      "github_url": "https://github.com/user/email-management-system/issues/15",
      "execution_mode": "sequential",
      "files_created": 8,
      "files_modified": 2,
      "post_mortem": ".workflow/post-mortem/EPIC-001.md",
      "integration_notes": "Foundation epic - no prior epics to integrate with",
      "tags": ["backend", "core", "foundation"],
      "dependencies": {
        "blocks": ["EPIC-002", "EPIC-003"],
        "blocked_by": [],
        "integrates_with": []
      }
    },
    {
      "epic_id": "EPIC-002",
      "epic_number": 2,
      "title": "Gmail API Integration",
      "slug": "gmail-api-integration",
      "status": "implemented",
      "created_date": "2025-10-17",
      "prepared_date": "2025-10-17",
      "implemented_date": "2025-10-18",
      "directory": ".tasks/completed/EPIC-002-gmail-api-integration",
      "github_issue": 18,
      "github_url": "https://github.com/user/email-management-system/issues/18",
      "execution_mode": "parallel",
      "files_created": 12,
      "files_modified": 5,
      "post_mortem": ".workflow/post-mortem/EPIC-002.md",
      "integration_notes": "Extends EPIC-001 parser with Gmail-specific auth and fetching",
      "tags": ["backend", "integration", "gmail"],
      "dependencies": {
        "blocks": ["EPIC-004"],
        "blocked_by": ["EPIC-001"],
        "integrates_with": ["EPIC-001"]
      }
    },
    {
      "epic_id": "EPIC-003",
      "epic_number": 3,
      "title": "Semantic Email Search",
      "slug": "semantic-email-search",
      "status": "prepared",
      "created_date": "2025-10-20",
      "prepared_date": "2025-10-21",
      "implemented_date": null,
      "directory": ".tasks/backlog/EPIC-003-semantic-email-search",
      "github_issue": 22,
      "github_url": "https://github.com/user/email-management-system/issues/22",
      "execution_mode": null,
      "files_created": null,
      "files_modified": null,
      "post_mortem": null,
      "integration_notes": "Will integrate with EPIC-001 parsed emails and EPIC-002 Gmail data",
      "tags": ["backend", "ml", "search"],
      "dependencies": {
        "blocks": [],
        "blocked_by": ["EPIC-001", "EPIC-002"],
        "integrates_with": ["EPIC-001", "EPIC-002"]
      }
    }
  ],
  "master_spec_coverage": {
    "total_requirements": 15,
    "covered_by_epics": 8,
    "coverage_percentage": 53.3,
    "uncovered_requirements": [
      "REQ-007: Email categorization ML model",
      "REQ-009: Attachment extraction",
      "REQ-011: Thread reconstruction",
      "REQ-013: Smart reply suggestions",
      "REQ-014: Priority inbox",
      "REQ-015: Bulk operations",
      "REQ-016: Search filters"
    ]
  }
}
```

**Epic Status Lifecycle**:
```
defined → prepared → ready → implemented → archived
   ↓          ↓         ↓          ↓
Created   file-tasks  Preflight  Executed
         .md exists    passed
```

### 2. Mandatory GitHub Integration

**Changes to `/spec-epic`**:
- GitHub issue creation is **MANDATORY** (no longer optional)
- If GitHub creation fails, **BLOCK** epic creation (don't proceed)
- Epic registry tracks `github_issue` and `github_url`
- Epic status synced to GitHub labels (`status:defined`, `status:prepared`, `status:ready`, `status:implemented`)

**Changes to `/execute-workflow`**:
- Phase 0: Verify GitHub issue exists for epic (fail if missing)
- Phase 1B (parallel): Create sub-issues for each domain (mandatory)
- Phase 5: Close GitHub issue on completion (mandatory)
- Phase 6: Post post-mortem summary to GitHub issue

**Error Handling**:
```bash
if ! gh auth status &> /dev/null; then
  echo "❌ GitHub CLI not authenticated"
  echo ""
  echo "GitHub integration is MANDATORY for Tier 1 workflow."
  echo ""
  echo "Authenticate with:"
  echo "  gh auth login"
  echo ""
  exit 1
fi
```

### 3. Smart Epic Selector (`/execute-workflow next`)

**New Command Syntax**:
```bash
/execute-workflow next          # Execute next ready epic
/execute-workflow EPIC-003      # Execute specific epic (existing)
/execute-workflow --list-ready  # Show all ready epics
```

**Selection Algorithm** (priority order):
1. **Blocked by nothing**: Filter epics where `dependencies.blocked_by` is empty or all blocking epics are `implemented`
2. **Has integration plan**: Prefer epics with `integration_notes` populated
3. **Priority tag**: Prefer epics tagged `critical` > `high` > `medium` > `low`
4. **Creation date**: Oldest first (FIFO)

**Implementation**:
```bash
# Select next epic using Python
NEXT_EPIC=$(python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

registry_file = Path(".tasks/epic_registry.json")
with open(registry_file) as f:
    registry = json.load(f)

# Filter: status = "ready"
ready_epics = [e for e in registry["epics"] if e["status"] == "ready"]

if not ready_epics:
    print("ERROR:no-ready-epics")
    exit(1)

# Filter: not blocked
def is_blocked(epic):
    blocked_by = epic["dependencies"]["blocked_by"]
    if not blocked_by:
        return False
    # Check if all blocking epics are implemented
    for block_id in blocked_by:
        blocker = next((e for e in registry["epics"] if e["epic_id"] == block_id), None)
        if blocker and blocker["status"] != "implemented":
            return True
    return False

unblocked = [e for e in ready_epics if not is_blocked(e)]

if not unblocked:
    print("ERROR:all-blocked")
    exit(1)

# Priority sort
priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}

def get_priority(epic):
    for tag in epic["tags"]:
        if tag in priority_map:
            return priority_map[tag]
    return 2  # default medium

# Sort by: priority (asc), created_date (asc)
unblocked.sort(key=lambda e: (get_priority(e), e["created_date"]))

# Return first
print(unblocked[0]["epic_id"])
EOF
)

if [[ "$NEXT_EPIC" == ERROR:* ]]; then
  echo "❌ Cannot select next epic: ${NEXT_EPIC#ERROR:}"
  exit 1
fi

echo "🎯 Selected next epic: $NEXT_EPIC"
```

### 4. Integration Planning Phase (New Phase 4.5)

**Insert between Phase 4 (Validation) and Phase 5 (Commit)**:

```
Phase 1: Implementation
Phase 2: Auto-Lint
Phase 3: Validation
Phase 4.5: Integration Planning  ← NEW
Phase 5: Commit & Cleanup
Phase 6: Post-Mortem
```

**Phase 4.5 Implementation**:

Deploy **Integration Planning Agent** to:
1. Read current epic spec and implementation
2. Read all **past** epic post-mortems and specs
3. Read all **future** epic specs (status: defined, prepared, ready)
4. Generate integration analysis:
   - How does this epic integrate with past epics?
   - What changes to past epics are needed?
   - How should future epics integrate with this?
   - Should we create integration sub-epics?

**Agent Prompt Template**:
```markdown
YOU ARE: Integration Planning Agent V1

---

CURRENT EPIC:
[Read ${EPIC_DIR}/spec.md]
[Read .workflow/outputs/${EPIC_ID}/phase1_results.json]

---

PAST EPICS (implemented):
[For each epic with status="implemented" in registry:]
  - Read epic spec.md
  - Read post-mortem.md
  - Identify integration points

---

FUTURE EPICS (defined, prepared, ready):
[For each epic with status in ["defined", "prepared", "ready"]:]
  - Read epic spec.md
  - Identify how they depend on current epic

---

YOUR TASK:

1. **Backward Integration** (with past epics):
   - Does this epic extend/modify functionality from past epics?
   - Are there breaking changes?
   - Do we need to update past epic code?
   - Are there integration tests needed?

2. **Forward Integration** (with future epics):
   - What interfaces should this epic expose for future use?
   - Are there design decisions that affect future epics?
   - Should we create integration sub-epics?

3. **Recommendations**:
   - Integration tasks to do NOW (before commit)
   - Integration sub-epics to create
   - Future epic spec updates needed

---

OUTPUT FILE:
.workflow/outputs/${EPIC_ID}/integration_plan.json

Format:
{
  "backward_integration": {
    "integrated_with": ["EPIC-001", "EPIC-002"],
    "breaking_changes": [],
    "code_updates_needed": [
      {
        "epic_id": "EPIC-001",
        "file": "src/parser.py",
        "reason": "Add support for new Gmail attachment format"
      }
    ],
    "integration_tests": [
      "test_gmail_parser_integration.py"
    ]
  },
  "forward_integration": {
    "exposes_interfaces": [
      "GmailClient.fetch_emails()",
      "GmailClient.search_by_label()"
    ],
    "design_decisions": [
      "Using OAuth2 flow (future epics must use same auth)"
    ],
    "sub_epics_needed": []
  },
  "recommendations": {
    "immediate_tasks": [
      "Update EPIC-001 parser to handle Gmail-specific headers",
      "Add integration test between parser and Gmail client"
    ],
    "future_epic_updates": [
      {
        "epic_id": "EPIC-003",
        "spec_section": "Architecture",
        "update": "Must use GmailClient.search_by_label() instead of direct API"
      }
    ]
  }
}
```

**Integration Plan Storage**:
- Save to `.workflow/outputs/${EPIC_ID}/integration_plan.json`
- Update epic registry: `epics[N].integration_notes` with summary
- Create integration sub-epics if needed (status: `defined`)

### 5. Longitudinal Learning System

**Knowledge Capture Points**:

1. **Post-Mortem → Agent Briefings** (existing, enhanced):
   - Phase 6 agent extracts patterns
   - Human reviews and applies to `.claude/agent_briefings/`

2. **Post-Mortem → Next Epic Planning** (NEW):
   - When creating EPIC N+1, read post-mortems from EPIC 1..N
   - Extract relevant patterns for the new epic domain
   - Pre-populate "Lessons from Past Epics" section in spec

3. **Epic Registry → Coverage Analysis** (NEW):
   - Track master spec coverage
   - Identify gaps
   - Suggest next epics to fill gaps

**Enhanced `/spec-epic` Flow**:

```markdown
## Phase 0.5: Consult Past Epics (NEW)

Read epic registry and identify lessons from similar epics:

```bash
echo "📚 Consulting past epics for lessons..."

python3 << 'EOF'
import json
from pathlib import Path

registry_file = Path(".tasks/epic_registry.json")
with open(registry_file) as f:
    registry = json.load(f)

# Find implemented epics
implemented = [e for e in registry["epics"] if e["status"] == "implemented"]

if not implemented:
    print("ℹ️ No past epics to learn from (first epic in project)")
    exit(0)

print(f"📊 Found {len(implemented)} implemented epics")
print("")
print("Reading post-mortems for lessons...")

for epic in implemented:
    post_mortem_file = Path(epic["post_mortem"])
    if post_mortem_file.exists():
        print(f"\n## {epic['epic_id']}: {epic['title']}")
        print(f"Tags: {', '.join(epic['tags'])}")
        print("")
        # Extract "Recommendations" section
        with open(post_mortem_file) as f:
            content = f.read()
            if "## Recommendations" in content:
                recs = content.split("## Recommendations")[1].split("##")[0]
                print(recs.strip()[:500])  # First 500 chars
    else:
        print(f"⚠️  Post-mortem missing for {epic['epic_id']}")

EOF
```

Use these lessons to inform:
- Architecture decisions
- Technology choices
- Common pitfalls to avoid
- Briefing improvements to apply
```

**Master Spec Coverage Tracking**:

Add to `/spec-epic` Phase 6:

```bash
echo "📊 Updating master spec coverage..."

python3 << 'EOF'
import json
from pathlib import Path

# Read master spec
master_spec_file = Path(".tasks/master_spec.md")
# TODO: Parse requirements (assume format: "- REQ-XXX: Description")

# Read epic spec to identify which requirements this epic covers
epic_spec_file = Path("${EPIC_DIR}/spec.md")
# TODO: Extract requirement references

# Update registry coverage tracking
registry_file = Path(".tasks/epic_registry.json")
with open(registry_file) as f:
    registry = json.load(f)

# Recalculate coverage
# TODO: Count which requirements are covered by defined/prepared/implemented epics

with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2)

print("✅ Coverage updated")
EOF
```

### 6. Epic Registry Management Commands

**New slash commands**:

```markdown
# /epic-registry-status
Show epic registry summary and statistics

# /epic-registry-sync
Scan .tasks/ directories and sync to registry (detect orphaned epics, fix inconsistencies)

# /epic-registry-coverage
Analyze master spec coverage and suggest next epics

# /epic-registry-graph
Generate Mermaid dependency graph of all epics
```

---

## Implementation Plan

### File Structure

```
project/
├── .tasks/
│   ├── epic_registry.json                    ← NEW (central registry)
│   ├── master_spec.md
│   ├── backlog/
│   │   └── EPIC-003-semantic-search/
│   │       ├── spec.md
│   │       ├── architecture.md
│   │       ├── task.md                       ← MODIFIED (add registry metadata)
│   │       └── implementation-details/
│   │           └── file-tasks.md
│   ├── completed/
│   │   ├── EPIC-001-email-parser/
│   │   └── EPIC-002-gmail-integration/
│   └── templates/
│       └── epic_registry.json.j2             ← NEW
├── .workflow/
│   ├── outputs/
│   │   └── EPIC-002/
│   │       ├── phase1_results.json
│   │       ├── integration_plan.json         ← NEW
│   │       └── ...
│   └── post-mortem/
│       ├── EPIC-001.md
│       └── EPIC-002.md
├── .claude/
│   ├── commands/
│   │   ├── spec-epic.md                      ← MODIFIED (registry integration)
│   │   ├── execute-workflow.md               ← MODIFIED (Phase 4.5, 'next' support)
│   │   ├── epic-registry-status.md           ← NEW
│   │   ├── epic-registry-sync.md             ← NEW
│   │   ├── epic-registry-coverage.md         ← NEW
│   │   └── epic-registry-graph.md            ← NEW
│   ├── agents/
│   │   └── integration_planning_agent_v1.md  ← NEW
│   └── agent_briefings/
│       └── integration_planning.md           ← NEW
└── tools/
    ├── epic_registry/
    │   ├── __init__.py                        ← NEW
    │   ├── registry_manager.py                ← NEW (CRUD operations)
    │   ├── epic_selector.py                   ← NEW (smart selection)
    │   ├── coverage_analyzer.py               ← NEW (master spec coverage)
    │   └── dependency_resolver.py             ← NEW (dependency graph)
    └── github_integration/
        ├── issue_sync_gh.py                   ← MODIFIED (mandatory mode)
        └── ...
```

### Phase 1: Epic Registry Core (Week 1)

**Files to create**:

1. `tools/epic_registry/registry_manager.py` - CRUD operations for registry
2. `tools/epic_registry/models.py` - Pydantic models for epic metadata
3. `.tasks/templates/epic_registry.json.j2` - Template for new registries
4. `.claude/commands/epic-registry-init.md` - Initialize registry in project

**Files to modify**:

1. `.claude/commands/spec-epic.md` - Add registry integration
2. `.claude/commands/execute-workflow.md` - Update registry on status changes

### Phase 2: GitHub Integration Hardening (Week 1-2)

**Files to modify**:

1. `.claude/commands/spec-epic.md` - Make GitHub mandatory
2. `tools/github_integration/issue_sync_gh.py` - Add blocking mode
3. `.claude/commands/execute-workflow.md` - Verify GitHub issue exists in Phase 0

### Phase 3: Smart Epic Selector (Week 2)

**Files to create**:

1. `tools/epic_registry/epic_selector.py` - Selection algorithm
2. `tools/epic_registry/dependency_resolver.py` - Dependency graph

**Files to modify**:

1. `.claude/commands/execute-workflow.md` - Add 'next' argument support

### Phase 4: Integration Planning Phase (Week 3)

**Files to create**:

1. `.claude/agents/integration_planning_agent_v1.md` - Agent definition
2. `.claude/agent_briefings/integration_planning.md` - Domain briefing

**Files to modify**:

1. `.claude/commands/execute-workflow.md` - Add Phase 4.5

### Phase 5: Longitudinal Learning (Week 4)

**Files to create**:

1. `tools/epic_registry/coverage_analyzer.py` - Master spec coverage tracking

**Files to modify**:

1. `.claude/commands/spec-epic.md` - Add Phase 0.5 (consult past epics)
2. `.claude/agents/post_mortem_agent_v1.md` - Extract structured lessons

### Phase 6: Registry Management Commands (Week 4)

**Files to create**:

1. `.claude/commands/epic-registry-status.md`
2. `.claude/commands/epic-registry-sync.md`
3. `.claude/commands/epic-registry-coverage.md`
4. `.claude/commands/epic-registry-graph.md`

---

## Consequences

### Positive

1. ✅ **GitHub Integration**: All epics tracked as issues (visibility, coordination)
2. ✅ **Unique Epic IDs**: No more collisions or confusion
3. ✅ **Smart Automation**: `/execute-workflow next` saves time
4. ✅ **Integration Planning**: No more isolated epics
5. ✅ **Longitudinal Learning**: Each epic benefits from past lessons
6. ✅ **Coverage Tracking**: Know what's implemented vs. planned
7. ✅ **Dependency Management**: Clear blocking relationships
8. ✅ **Parallel Work**: Can see status across projects via GitHub

### Negative

1. ⚠️ **Complexity**: More infrastructure to maintain
2. ⚠️ **GitHub Dependency**: Requires authenticated `gh` CLI
3. ⚠️ **Migration**: Existing projects need registry initialization
4. ⚠️ **Learning Curve**: Users must understand registry concepts

### Mitigations

1. **Gradual Rollout**: Phase 1-2 first (registry + GitHub), then add smart features
2. **Migration Tools**: `/epic-registry-sync` auto-discovers existing epics
3. **Documentation**: Clear CLAUDE.md updates and examples
4. **Fallback**: If registry corrupted, can rebuild from `.tasks/` directories

---

## Alternatives Considered

### Alternative 1: External Project Management Tool (e.g., Jira, Linear)

**Rejected because**:
- Requires external service (not self-contained)
- Doesn't integrate with local file structure
- Can't use Claude Code agents to manage it
- Adds cognitive overhead (switch contexts)

### Alternative 2: Git-Only Tracking (branches, tags)

**Rejected because**:
- Git branches don't map to epic status lifecycle
- Can't track coverage, dependencies, integration notes
- Harder to query ("which epics are ready?")
- GitHub Issues better for project visibility

### Alternative 3: Markdown-Only Registry (no JSON)

**Rejected because**:
- Hard to parse programmatically for smart selection
- Can't do complex queries (blocked_by calculation)
- JSON enables tool integration (Python scripts)
- Markdown good for humans, JSON good for machines (use both!)

---

## References

- ADR-012: Global Rollout Complete (Tier 1 workflow standardization)
- `/spec-epic` command documentation
- `/execute-workflow` command documentation
- GitHub CLI documentation: https://cli.github.com/manual/
- Agentic Project Management framework: https://github.com/sdi2200262/agentic-project-management

---

## Approval

- [ ] Andreas Spannbauer reviews and approves
- [ ] Test in single project (email_management_system)
- [ ] Rollout to all Tier 1 projects
- [ ] Document in CLAUDE.md
