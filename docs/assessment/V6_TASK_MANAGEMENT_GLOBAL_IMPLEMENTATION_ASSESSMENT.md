# V6 Task Management & Spec Creation Pipeline - Global Implementation Assessment

**Date:** 2025-10-18
**Project Analyzed:** email_management_system
**System Version:** V6 (Production)
**Assessment Scope:** Task management, spec creation/refinement, workflow orchestration

---

## Executive Summary

The email_management_system project implements a sophisticated V6 task management and specification creation/refinement pipeline that represents a production-grade system for managing complex software development workflows. The system integrates:

- **Unified MCP Server** - Central orchestration point with 20+ tools
- **Hierarchical Epic Management** - Progressive specification refinement
- **Interactive Spec Creation** - Guided workflow with zero-ambiguity tolerance
- **File-Based Task System** - Markdown tasks with YAML frontmatter
- **Graph-Server Integration** - Code intelligence and impact analysis
- **Pattern Library Integration** - Knowledge capture and reuse
- **Constitutional Validation** - Architecture compliance enforcement

**Key Finding:** This system can be adapted for global use across all projects, but the implementation strategy significantly impacts maintainability and effectiveness.

---

## System Architecture Overview

### Core Components

```
V6 Task Management System
├── MCP Server Layer
│   ├── unified_v6_server_with_workflow.py (FastMCP, 1312 lines)
│   ├── 20+ MCP tools exposed to Claude Code
│   └── Context7 pattern capture integration
│
├── Task Management
│   ├── SmartTaskFileManager (.tasks/ directory organization)
│   ├── HierarchicalEpicManager (epic directory structures)
│   ├── Task files (.task.md with YAML frontmatter)
│   └── Status-based organization (backlog/current/completed)
│
├── Spec Creation Toolkit
│   ├── preflight_checks.py (system health validation)
│   ├── graph_analysis.py (impact & dependency analysis)
│   ├── constitutional_validator.py (architecture compliance)
│   ├── contract_generator.py (JSON Schema + type generation)
│   ├── research_coordinator.py (pattern library + Context7)
│   ├── implementation_planner.py (prescriptive execution plans)
│   └── complete_spec_workflow.py (orchestration)
│
├── Workflow Orchestration
│   ├── Phase-based execution (Phases 0-7)
│   ├── Agent coordination (sub-agent deployment)
│   ├── Quality gates (build/lint/test loops)
│   └── Post-mortem analysis
│
└── Integration Layer
    ├── Claude Code slash commands (/spec-epic, /execute-workflow)
    ├── Output styles (Spec Architect V6, Workflow Orchestrator V6)
    ├── Hooks (UserPromptSubmit, PostToolUse)
    └── Pattern library (semantic search, auto-capture)
```

---

## Deep Dive: Key Components

### 1. V6 Unified MCP Server

**File:** `tools/mcp_servers/unified_v6_server_with_workflow.py`
**Technology:** FastMCP (Python MCP SDK)
**Lines of Code:** 1,312

**Exposed Tools (20+):**

#### Task Management Tools
- `tasks_v6_create` - Create task from rich template
- `tasks_v6_get` - Retrieve task with frontmatter
- `tasks_v6_update_status` - Move task between directories
- `tasks_v6_update_subtask` - Mark subtask checkbox complete
- `tasks_v6_summary` - Filtered task listing
- `tasks_v6_create_hierarchical_epic` - Create epic with directory structure
- `tasks_v6_validate_completeness` - Preflight validation before execution
- `tasks_v6_get_spec_artifacts` - Load all spec documents

#### Pattern Library Tools
- `pattern_library_search` - Semantic search with dual-layer support
- `pattern_library_search_with_fallback` - Cascading search (project→generic→Context7)
- `pattern_library_list` - List all patterns
- `pattern_library_get` - Get pattern by ID
- `pattern_library_stats` - Library statistics
- `capture_context7_research` - Save Context7 docs to pattern library
- `pattern_extraction_check_queue` - Check pending pattern extractions
- `pattern_extraction_submit_patterns` - Submit extracted patterns

#### Workflow Orchestration Tools
- `execute_workflow_v6` - Single entry point for complete workflow
- `set_workflow_tracking_context` - Enable Context7 call tracking
- `get_workflow_context7_tracking` - Export tracking data
- `save_workflow_context7_tracking` - Save tracking to JSON

#### System Health Tools
- `v6_system_health` - Check all component initialization
- `v6_research_library_stats` - Pattern library metrics

**Architecture Principles:**

1. **Single Entry Point:** `execute_workflow_v6` replaces 6+ removed orchestration tools
2. **Stateless Tools:** MCP tools don't maintain state; rely on file system
3. **Progressive Enhancement:** Tools build on SmartTaskFileManager base class
4. **Integration First:** Direct integration with graph-server, Context7, pattern library

**Key Design Decision:** The MCP server is **project-specific** - it imports project-relative modules:

```python
from tools.pattern_library import Context7ResearchLibrary, PatternSemanticIndex
from tools.spec_creation import HealthStatus, check_system_health
from tools.workflow_utilities_v6.task_management.hierarchical_epic_manager_v6 import HierarchicalEpicManager
```

This creates tight coupling to the project structure.

---

### 2. Task Management System

**File:** `tools/workflow_utilities_v6/task_management/smart_task_file_manager_v6.py`
**Storage:** `.tasks/` directory with markdown files

#### Task File Structure

**Frontmatter (YAML):**
```yaml
---
id: FEATURE-002
title: Complete "Last Mile" - Email to Calendar/Task
type: feature
priority: high
status: in_progress
created: 2025-10-09
updated_at: 2025-10-11T07:16:32.759197
area: backend
scope:
  - src/services/meeting_extractor_service.py
  - src/api/endpoints/ai_actions.py
estimated_effort: medium
complexity: medium
blocking_deployment: False
contracts:
  schema_version: v1
  requires_json_schema: True
  requires_types: True
  test_output_dir: tests/services/extraction/
  contract_scope:
    - name: meeting_extraction_params
      path: contracts/api/ai/extract_meeting_params.schema.json
  type_generation:
    typescript:
      enabled: True
      output_dir: frontend/src/types/ai-actions/
---
```

**Body (Markdown):**
- Problem statement
- Current state vs desired state
- User scenarios
- Technical requirements
- Implementation notes
- Subtask checkboxes

#### Directory Organization

```
.tasks/
├── backlog/          # Not started
├── current/          # In progress
├── completed/        # Done
├── archive/          # Historical
└── templates/        # Task templates
```

**Key Features:**

1. **Automatic ID Assignment:** Next sequential ID per type (FEATURE-003, BUG-015)
2. **Status-Based File Movement:** Changing status physically moves the file
3. **Rich Frontmatter:** Structured metadata for filtering and reporting
4. **Content Preservation:** Updates maintain body content while modifying frontmatter
5. **Contract Integration:** JSON Schema requirements embedded in task

---

### 3. Hierarchical Epic System

**File:** `tools/workflow_utilities_v6/task_management/hierarchical_epic_manager_v6.py`

**Epic Directory Structure:**

```
.tasks/backlog/EPIC-007-SemanticEmailSearch/
├── spec.md                          # WHAT/WHY - User needs, scenarios
├── architecture.md                  # HOW - System design, components
├── task.md                          # V6 workflow metadata
├── constitutional_compliance.md     # Validation report
├── contracts/                       # JSON Schemas + generated types
│   ├── *.schema.json
│   └── generated/
│       ├── types.ts
│       └── types.py
├── implementation-details/          # Prescriptive execution plans
│   ├── file-tasks.md
│   ├── database-migrations.md
│   └── testing-strategy.md
├── research/                        # Background decisions
│   ├── pattern-library-results.md
│   └── context7-documentation.md
└── analysis/                        # Graph-server intelligence
    ├── graph_server_analysis.json
    └── impact_report.md
```

**Progressive Refinement Workflow:**

1. **Creation:** Minimal structure with placeholders
2. **Spec Phase (Phases 0-4):** Interactive refinement to completion
3. **Validation:** `tasks_v6_validate_completeness` checks all artifacts
4. **Execution Ready:** All artifacts present, workflow can proceed

**Philosophy:**
> "Smart planning, simple execution. Complexity at spec creation, not runtime."

---

### 4. Spec Creation Toolkit

**Location:** `tools/spec_creation/`
**Purpose:** Replace V6 workflow Phases 0-4 with interactive tools

#### Module Breakdown

| Module | Purpose | Output Artifacts |
|--------|---------|------------------|
| `preflight_checks.py` | System health validation | Health status report |
| `graph_analysis.py` | Impact & dependency analysis | `analysis/graph_server_analysis.json`, `analysis/impact_report.md` |
| `constitutional_validator.py` | Architecture compliance | `constitutional_compliance.md` |
| `contract_generator.py` | JSON Schema + type generation | `contracts/*.schema.json`, `contracts/generated/*.{ts,py}` |
| `research_coordinator.py` | Pattern library + Context7 | `research/pattern-library-results.md`, `research/<library>-documentation.md` |
| `implementation_planner.py` | Prescriptive execution plans | `implementation-details/file-tasks.md`, `implementation-details/database-migrations.md` |
| `complete_spec_workflow.py` | Orchestrate all phases | Complete epic directory |

**Key Innovation: Zero-Ambiguity Tolerance**

The spec creation process uses **batched clarifying questions** (≤10 per round) to eliminate all ambiguity before code generation:

```python
# From Spec Architect V6 output style
def gather_requirements():
    questions = []

    # Batch 1: Problem Understanding
    questions.extend([
        "What user pain point does this solve?",
        "What is the current manual workaround?",
        "What is the desired automated behavior?"
    ])

    # Batch 2: Scope Boundaries
    questions.extend([
        "Which existing services will this integrate with?",
        "What data sources are involved?",
        "What edge cases must be handled?"
    ])

    # Ask all at once, wait for responses
    answers = ask_user_questions(questions)

    # No proceeding until all answered
    return refine_spec_from_answers(answers)
```

**Contract-First Development:**

All epics that set `requires_json_schema: true` trigger automatic contract generation:

1. Functional requirements → JSON Schema contracts
2. Contracts → TypeScript types (`json-schema-to-typescript`)
3. Contracts → Python Pydantic models (`datamodel-code-generator`)
4. Compilation verification before execution

**Pattern Library Integration:**

Before querying Context7 (external docs), always search local pattern library:

```python
# From research_coordinator.py
def research_library(library_name: str, topic: str):
    # 1. Search local patterns first
    patterns = search_patterns(query=f"{library_name} {topic}", threshold=0.7)

    if patterns:
        return patterns  # 60-70% hit rate - no external call needed

    # 2. Context7 fallback
    docs = mcp__context7__get_library_docs(library_name, topic)

    # 3. Capture for future (pattern extraction queue)
    mcp__unified_v6_server__capture_context7_research(...)

    return docs
```

---

### 5. Workflow Orchestration

**Entry Point:** `/execute-workflow EPIC-ID` slash command
**MCP Tool:** `execute_workflow_v6`

**Execution Phases:**

```
Phase 0: Preflight
├── System health checks
├── Spec completeness validation
└── Git working directory cleanliness

Phase 1-4: [REMOVED] Now handled by spec creation toolkit

Phase 5A: Implementation
├── Generate handoff briefing
├── Load prescriptive plan from Phase 4
├── Deploy implementation agent (Task tool)
└── Graph-server integration (impact analysis)

Phase 5B: Validation
├── Test suite execution
├── Architectural boundary validation
├── Domain compliance checks
└── Contract compliance verification

Phase 5C: Build & Lint Gate (QUALITY GATE - MANDATORY LOOP)
├── TypeScript compilation (npm run build:ts)
├── Linting (npm run lint)
├── Auto-fix on failure
├── Loop until passing (max 3 attempts)
└── Block progression if still failing

Phase 5D: Integration Testing
├── Unit tests (individual functions)
├── Contract tests (JSON Schema validation)
├── Integration tests (component interaction)
├── Functional tests (end-to-end scenarios)
└── Coverage requirements (≥85% backend, ≥90% graph-server)

Phase 5E: Documentation
├── Component reference docs
├── API documentation
├── ADR (Architectural Decision Records)
└── Update affected docs (freshness tracking)

Phase 6: Commit Validation
├── Pre-commit hooks
├── Git commit creation
└── Task status update

Phase 7: Finalization
├── Optional push to remote
├── Archive workflow outputs
├── Cache cleanup
└── Mark epic complete
```

**Agent Coordination:**

Each phase deploys specialized agents via the `Task` tool:

```python
# From /execute-workflow command
Task(
    subagent_type="phase5a-implementation-agent-v6",
    prompt=f"""
    {handoff_briefing}

    IMPLEMENTATION PROTOCOL:
    Files to create: {files_to_create}
    Files to modify: {files_to_modify}
    Implementation steps: {implementation_steps}

    GRAPH-SERVER INTEGRATION (REQUIRED):
    - Before modifying any file, analyze with mcp__graph-server__analyze
    - Check dependencies with mcp__graph-server__graph_deps operation="impact"

    OUTPUT REQUIREMENTS:
    Write results to: .workflow/v6-outputs/{epic_id}/phase5a_implementation_results.json
    """
)
```

**Quality Gates:**

Phase 5C implements **mandatory looping** until build passes:

```python
build_passed = False
max_attempts = 3
attempt = 0

while not build_passed and attempt < max_attempts:
    attempt += 1

    # Deploy build fixer agent
    Task(subagent_type="build-fixer-agent-v6", ...)

    # Check results
    results = read_json(f"phase5c_build_results_attempt_{attempt}.json")
    build_passed = (
        results.build_status == "passed" AND
        results.lint_status == "passed"
    )

if not build_passed:
    # STOP EXECUTION - manual intervention required
    raise QualityGateFailure("Build gate failed after max attempts")
```

---

### 6. Integration with Claude Code

#### Slash Commands

**Location:** `.claude/commands/`

**Primary Commands:**

1. **`/spec-epic <title>`** - Create new epic with interactive refinement
2. **`/refine-spec <epic-id>`** - Regenerate spec artifacts
3. **`/execute-workflow <epic-id>`** - Run complete implementation workflow

**Command Structure:**

```markdown
---
description: "Execute V6 workflow from Phase 5A"
argument-hint: "[EPIC-ID]"
allowed-tools: [
  mcp__unified-v6-server__tasks_v6_validate_completeness,
  mcp__unified-v6-server__execute_workflow_v6,
  Read,
  Task
]
---

## WORKFLOW EXECUTION COMMAND

[Detailed instructions for Claude Code session...]
```

**Key Feature:** Commands include **prescriptive instructions** for Claude Code, telling it exactly which MCP tools to call and in what order.

#### Output Styles

**Location:** `.claude/output-styles/`

**V6-Optimized Styles:**

1. **V6 Default Concise** - Terse, test-driven, explicit validation
2. **Spec Architect V6** - Interactive spec creation, batched questions
3. **Workflow Orchestrator V6** - Structured execution, YAML status blocks

**Style Switching:**

```bash
# Specification stage
/output-style Spec Architect V6

# Execution stage
/output-style Workflow Orchestrator V6

# General work
/output-style V6 Default Concise
```

**Impact:** Output styles change Claude Code's behavior (system prompt modifications) without changing tool availability.

#### Hooks

**UserPromptSubmit Hooks:**
- `user_prompt_submit_semantic.py` - Inject relevant patterns
- `user_prompt_submit_queue_notification.sh` - Show pattern extraction queue

**PostToolUse Hooks:**
- `post_tool_use_context7_capture.py` - Capture Context7 calls for pattern extraction

**Integration Flow:**

```
User Prompt
    ↓
[UserPromptSubmit Hook]
    ↓ (inject patterns)
Claude Code Session
    ↓ (calls MCP tools)
[PostToolUse Hook]
    ↓ (capture Context7)
Pattern Extraction Queue
    ↓ (manual /extract-patterns)
Pattern Library Growth
```

---

## Implementation Strategies for Global Use

Now that we understand the V6 system architecture, let's evaluate different strategies for making this available across all projects.

### Option 1: Global MCP Server (Single Instance)

**Concept:** Create one globally-installed MCP server that all projects can access.

**Architecture:**

```
~/.claude/mcp_servers/global_v6_server/
├── server.py                    # FastMCP server
├── core/
│   ├── task_manager.py          # Core task management logic
│   ├── spec_creator.py          # Spec creation toolkit
│   └── workflow_orchestrator.py # Workflow execution
├── config/
│   └── global_config.json       # Default settings
└── templates/
    ├── task.md.j2
    └── epic_structure/
```

**Claude Code Settings (`~/.claude/settings.json`):**

```json
{
  "mcp_servers": {
    "global-v6-server": {
      "command": "python3",
      "args": [
        "/home/andreas-spannbauer/.claude/mcp_servers/global_v6_server/server.py"
      ],
      "env": {}
    }
  }
}
```

**Tool Calls:**

```python
# From any Claude Code session
mcp__global_v6_server__create_task(
    title="Add user authentication",
    type="feature",
    priority="high"
)
```

#### Pros

✅ **Single Installation** - Install once, use everywhere
✅ **Consistent Interface** - Same tools across all projects
✅ **Centralized Updates** - Fix once, benefits all projects
✅ **Shared Configuration** - Global defaults, project overrides
✅ **Resource Efficiency** - One server process

#### Cons

❌ **Project-Specific Dependencies** - Email project uses graph-server, pattern library (other projects don't)
❌ **Path Resolution** - How does server find `.tasks/` in current project?
❌ **Template Customization** - Different projects need different task templates
❌ **Integration Complexity** - Must detect and adapt to each project's tooling
❌ **Tight Coupling Risk** - Project-specific logic leaks into global server

#### Implementation Challenges

**Challenge 1: Project Detection**

The server needs to detect the current project directory:

```python
# server.py
import os
from pathlib import Path

def get_project_root() -> Path:
    """Detect current project directory from Claude Code session."""
    # Option A: Environment variable
    if "CLAUDE_PROJECT_ROOT" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_ROOT"])

    # Option B: Git root detection
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / ".git").exists():
            return cwd
        cwd = cwd.parent

    raise ValueError("Could not detect project root")
```

**Challenge 2: Project-Specific Integrations**

How does the global server access graph-server or pattern library if they're project-specific?

**Solution A: Conditional Imports**

```python
# core/integrations.py
def get_graph_server_client(project_root: Path):
    """Get graph-server client if available in project."""
    try:
        # Try to import project's graph-server client
        sys.path.insert(0, str(project_root))
        from graph_server import Client
        return Client()
    except ImportError:
        # Graph-server not available in this project
        return None
```

**Solution B: Plugin Architecture**

```python
# Project-specific plugin: .claude/v6_plugin.py
class ProjectV6Plugin:
    def get_graph_client(self):
        from graph_server import Client
        return Client()

    def get_pattern_library(self):
        from tools.pattern_library import PatternLibraryManager
        return PatternLibraryManager()

# Global server discovers and loads plugin
plugin = load_project_plugin(project_root / ".claude/v6_plugin.py")
```

**Challenge 3: Template Customization**

Different projects need different task structures:

**Solution: Template Inheritance**

```
Global templates:
  ~/.claude/mcp_servers/global_v6_server/templates/task_base.md.j2

Project overrides:
  <project>/.claude/templates/task.md.j2(extends task_base.md.j2)
```

#### Recommendation for Option 1

**Verdict:** ⚠️ **Feasible but Complex**

This approach works if:
- You **abstract away project-specific integrations** (graph-server, pattern library)
- You use a **plugin system** for project-specific logic
- You implement **template inheritance** for customization
- You maintain **strict separation** between core task management and project tooling

**Best For:**
- Organizations with standardized project structures
- Teams willing to maintain plugin system
- Projects that share common tooling

---

### Option 2: Per-Project MCP Servers (Email Model)

**Concept:** Each project installs its own copy of the V6 MCP server.

**Architecture:**

```
<project>/tools/mcp_servers/unified_v6_server.py
<project>/tools/workflow_utilities_v6/
<project>/tools/spec_creation/
<project>/.tasks/
```

**Project Settings (`.claude/settings.local.json`):**

```json
{
  "mcp_servers": {
    "project-v6-server": {
      "command": "python3",
      "args": [
        "/home/andreas-spannbauer/coding_projects/<project>/tools/mcp_servers/unified_v6_server.py"
      ],
      "env": {
        "PROJECT_ROOT": "/home/andreas-spannbauer/coding_projects/<project>"
      }
    }
  }
}
```

#### Pros

✅ **Deep Integration** - Direct access to project-specific tools (graph-server, pattern library)
✅ **Full Customization** - Tailor everything to project needs
✅ **No Abstraction Penalty** - Can use project internals directly
✅ **Proven Architecture** - This is the current email system model
✅ **Isolated Evolution** - Projects evolve independently

#### Cons

❌ **Code Duplication** - Every project copies ~5,000+ lines of V6 code
❌ **Maintenance Burden** - Bug fixes must be applied to every project
❌ **Version Fragmentation** - Projects diverge over time
❌ **Setup Overhead** - New projects require full V6 installation
❌ **Inconsistent Experience** - Different projects may behave differently

#### Implementation Approach

**Step 1: Create V6 Template Repository**

```bash
# Create template repo
mkdir -p ~/coding_projects/v6-task-management-template
cd ~/coding_projects/v6-task-management-template

# Copy core V6 files from email project
cp -r ../email_management_system/tools/mcp_servers .
cp -r ../email_management_system/tools/workflow_utilities_v6 .
cp -r ../email_management_system/tools/spec_creation .
cp -r ../email_management_system/.tasks .
cp -r ../email_management_system/.claude .

# Create installation script
cat > install_v6.sh << 'EOF'
#!/bin/bash
# Install V6 task management in current project
PROJECT_ROOT=$(pwd)

echo "Installing V6 task management system..."

# Copy files
cp -r v6-task-management-template/tools/* ./tools/
cp -r v6-task-management-template/.tasks .
cp -r v6-task-management-template/.claude .

# Configure MCP server
cat > .claude/settings.local.json << JSON
{
  "mcp_servers": {
    "project-v6-server": {
      "command": "python3",
      "args": ["$PROJECT_ROOT/tools/mcp_servers/unified_v6_server.py"],
      "env": {"PROJECT_ROOT": "$PROJECT_ROOT"}
    }
  }
}
JSON

echo "V6 installation complete. Restart Claude Code."
EOF

chmod +x install_v6.sh
```

**Step 2: Install in New Project**

```bash
cd ~/coding_projects/my-new-project
~/coding_projects/v6-task-management-template/install_v6.sh
```

**Step 3: Customize for Project**

Each project can now customize:
- Task templates (`.tasks/templates/`)
- Spec creation modules (`tools/spec_creation/`)
- Workflow phases (add/remove as needed)
- Output styles (`.claude/output-styles/`)

#### Version Control Strategy

**Option A: Git Subtree**

```bash
# Add V6 template as subtree
git subtree add \
  --prefix=tools/v6 \
  git@github.com:org/v6-task-management-template.git \
  main

# Pull updates
git subtree pull \
  --prefix=tools/v6 \
  git@github.com:org/v6-task-management-template.git \
  main
```

**Option B: Git Submodule**

```bash
# Add V6 as submodule
git submodule add \
  git@github.com:org/v6-task-management-template.git \
  tools/v6

# Update to latest
cd tools/v6
git pull origin main
```

**Option C: Copy + Fork**

```bash
# Copy template and let it diverge
cp -r ~/v6-template/* ./tools/

# Project-specific evolution
# (manual merging of upstream fixes as needed)
```

#### Recommendation for Option 2

**Verdict:** ✅ **Best for Maximum Customization**

This approach works best when:
- Projects have **unique workflows** that need deep customization
- You have **project-specific integrations** (graph-server, pattern library, etc.)
- Team is comfortable with **managing duplicated code**
- Benefits of customization **outweigh maintenance costs**

**Best For:**
- Large, complex projects with unique requirements
- Projects with existing custom tooling
- Teams with dedicated DevOps/tooling engineers

---

### Option 3: Claude Code Commands + Output Styles (No MCP)

**Concept:** Skip the MCP server entirely and implement everything using native Claude Code features.

**Architecture:**

```
.claude/
├── commands/
│   ├── task-create.md         # /task-create command
│   ├── spec-epic.md           # /spec-epic command
│   └── execute-workflow.md    # /execute-workflow command
├── output-styles/
│   ├── spec-architect.md      # For spec creation
│   └── workflow-executor.md   # For execution
└── skills/
    └── task-management.md     # Reusable skill for task operations
```

**Tool Usage:**

Instead of MCP tools, Claude Code uses **direct file operations** and **bash commands**:

```markdown
# .claude/commands/task-create.md
---
description: "Create new task with frontmatter"
argument-hint: "<title>"
---

## Create New Task

1. Determine next task ID:
   ```bash
   LAST_ID=$(ls .tasks/backlog/FEATURE-*.task.md 2>/dev/null | \
     sort -V | tail -1 | \
     grep -oP 'FEATURE-\K\d+')
   NEXT_ID=$((LAST_ID + 1))
   TASK_ID=$(printf "FEATURE-%03d" $NEXT_ID)
   ```

2. Create task file:
   ```bash
   cat > .tasks/backlog/${TASK_ID}.task.md << 'EOF'
   ---
   id: ${TASK_ID}
   title: $ARGUMENTS
   type: feature
   status: backlog
   created: $(date +%Y-%m-%d)
   ---

   # ${TASK_ID}: $ARGUMENTS

   ## Problem Statement

   [Describe the problem this task solves]

   ## Acceptance Criteria

   - [ ] Criterion 1
   - [ ] Criterion 2
   EOF
   ```

3. Display created task:
   ```
   Created task: ${TASK_ID} in .tasks/backlog/${TASK_ID}.task.md
   ```
```

#### Pros

✅ **Zero External Dependencies** - No MCP server to install or maintain
✅ **Simple Architecture** - Everything is markdown + bash
✅ **Easy to Understand** - No Python server, no FastMCP, just files
✅ **Project-Agnostic** - Works anywhere Claude Code works
✅ **Fast Iteration** - Edit markdown files, no server restart
✅ **Transparent Execution** - See exactly what commands run

#### Cons

❌ **Limited Abstraction** - Can't hide complexity behind MCP tools
❌ **Bash Complexity** - Complex operations become unwieldy bash scripts
❌ **No State Management** - Can't maintain workflow state in server
❌ **Repetitive Code** - Common operations duplicated across commands
❌ **No Type Safety** - Bash + markdown doesn't validate inputs
❌ **Error Handling** - Bash error handling is primitive

#### Implementation Example

**Task Creation Command:**

```markdown
# .claude/commands/task-create.md
---
description: "Create new task"
argument-hint: "<type> <title>"
allowed-tools: [Write, Bash, Read]
---

## Task Creation

Extract type and title from $ARGUMENTS:
- Expected format: "feature Add user authentication"
- Extract first word as type
- Rest is title

Steps:

1. **Validate Type**
   - Allowed: feature, bug, chore, refactor, docs
   - If invalid, error and stop

2. **Generate Task ID**
   ```bash
   # Find highest existing ID for this type
   TYPE_UPPER=$(echo "$TYPE" | tr '[:lower:]' '[:upper:]')
   LAST_ID=$(ls .tasks/backlog/${TYPE_UPPER}-*.task.md 2>/dev/null | \
     sort -V | tail -1 | grep -oP "${TYPE_UPPER}-\K\d+")
   NEXT_ID=$((${LAST_ID:-0} + 1))
   TASK_ID=$(printf "${TYPE_UPPER}-%03d" $NEXT_ID)
   ```

3. **Load Template**
   - Read `.tasks/templates/task.md.j2`
   - Substitute variables:
     - {{id}} → $TASK_ID
     - {{title}} → $TITLE
     - {{type}} → $TYPE
     - {{created}} → $(date +%Y-%m-%d)
     - {{status}} → backlog

4. **Write Task File**
   ```bash
   cat > .tasks/backlog/${TASK_ID}.task.md << 'EOF'
   [template content with substitutions]
   EOF
   ```

5. **Display Result**
   ```
   ✅ Created task: ${TASK_ID}
   📁 Location: .tasks/backlog/${TASK_ID}.task.md

   Next steps:
   - Edit task file to add details
   - Run `/task-get ${TASK_ID}` to view
   - Run `/task-update-status ${TASK_ID} current` to start work
   ```
```

**Spec Creation Command:**

```markdown
# .claude/commands/spec-epic.md
---
description: "Create epic with interactive refinement"
argument-hint: "<title>"
allowed-tools: [
  Write,
  Read,
  Bash(git*),
  AskUserQuestion,
  Task(subagent_type=general-purpose)
]
---

## Epic Spec Creation

Switch to Spec Architect output style:

/output-style Spec Architect V6

## Interactive Refinement Process

### Round 1: Problem Understanding

Ask user:
1. What user pain point does this solve?
2. What is the current manual workaround?
3. What is the desired automated behavior?
4. What is the expected impact (users affected, time saved)?

[Wait for responses]

### Round 2: Scope Definition

Based on Round 1 answers, ask:
1. Which existing components will this integrate with?
2. What new components are needed?
3. What data sources are involved?
4. What are the edge cases?
5. What are the non-goals (explicitly out of scope)?

[Wait for responses]

### Round 3: Technical Constraints

Ask:
1. What are the performance requirements?
2. What are the security considerations?
3. What are the compliance requirements?
4. What existing patterns should be followed?

[Wait for responses]

### Generate Epic Structure

Create epic directory:

```bash
EPIC_ID=$(generate_next_epic_id)  # Defined elsewhere
EPIC_SLUG=$(echo "$ARGUMENTS" | sed 's/ //g')
EPIC_DIR=".tasks/backlog/${EPIC_ID}-${EPIC_SLUG}"

mkdir -p "${EPIC_DIR}"/{contracts,implementation-details,research,analysis}
```

Write spec.md:

[Use Write tool with user's answers from all rounds]

Write architecture.md:

[Initial template, to be refined]

Write task.md:

[Epic metadata for workflow integration]

### Next Steps

Display:
```
✅ Epic structure created: ${EPIC_ID}
📁 Location: ${EPIC_DIR}

Created files:
- spec.md (WHAT/WHY)
- architecture.md (HOW - needs refinement)
- task.md (workflow metadata)

Next: Refine architecture with /refine-epic ${EPIC_ID}
```
```

**Workflow Execution Command:**

```markdown
# .claude/commands/execute-workflow.md
---
description: "Execute implementation workflow"
argument-hint: "<epic-id>"
allowed-tools: [Read, Bash, Task(subagent_type=general-purpose)]
---

## Workflow Execution

### Preflight Checks

1. **Verify Epic Exists**
   ```bash
   EPIC_DIR=$(find .tasks/backlog .tasks/current -name "${ARGUMENTS}-*" -type d)
   if [ -z "$EPIC_DIR" ]; then
     echo "❌ Epic ${ARGUMENTS} not found"
     exit 1
   fi
   ```

2. **Validate Completeness**

   Check required files:
   - [ ] spec.md exists
   - [ ] architecture.md exists
   - [ ] implementation-details/ has at least one .md file
   - [ ] contracts/ populated if requires_json_schema=true in task.md

   If any missing:
   ```
   ❌ Epic specification incomplete
   Missing: [list files]
   Run: /refine-epic ${ARGUMENTS}
   ```

3. **Check Git Cleanliness**
   ```bash
   if [ -n "$(git status --porcelain)" ]; then
     echo "⚠️ Working directory not clean. Commit or stash changes."
     exit 1
   fi
   ```

### Phase 5A: Implementation

Load prescriptive plan:

```bash
IMPL_PLAN="${EPIC_DIR}/implementation-details/file-tasks.md"
```

[Read file and parse]

Deploy implementation agent:

```
Task(
  subagent_type="general-purpose",
  description="Implement epic ${ARGUMENTS}",
  prompt="""
  You are implementing epic ${ARGUMENTS}.

  SPECIFICATION CONTEXT:
  [Content of spec.md]

  ARCHITECTURE:
  [Content of architecture.md]

  PRESCRIPTIVE PLAN:
  [Content of file-tasks.md]

  INSTRUCTIONS:
  - Follow the prescriptive plan exactly
  - Create/modify files as specified
  - Run validation after each file
  - Document any deviations

  OUTPUT:
  Save results to ${EPIC_DIR}/workflow-output/phase5a-results.json:
  {
    "files_created": [...],
    "files_modified": [...],
    "status": "success|partial|failed",
    "issues": [...]
  }
  """
)
```

### Phase 5B-5E: Validation, Testing, Documentation

[Similar agent deployments for each phase]

### Phase 6: Commit

```bash
# Collect all changed files
git add .

# Generate commit message
COMMIT_MSG="feat(${ARGUMENTS}): ${EPIC_TITLE}

Implementation of epic ${ARGUMENTS}.

Files changed:
[list from phase5a-results.json]

Tests: [test count from phase5d-results.json]
Coverage: [coverage % from phase5d-results.json]

Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "$COMMIT_MSG"
```

### Completion

Display summary and next steps.
```

#### Skills Integration

**Reusable Skill:**

```markdown
# .claude/skills/task-management.md
---
description: "Core task management operations"
---

## Task Management Skill

This skill provides reusable task operations for commands.

### Operations

#### get_next_task_id(type)

```bash
TYPE_UPPER=$(echo "$type" | tr '[:lower:]' '[:upper:]')
LAST_ID=$(ls .tasks/backlog/${TYPE_UPPER}-*.task.md 2>/dev/null | \
  sort -V | tail -1 | grep -oP "${TYPE_UPPER}-\K\d+")
NEXT_ID=$((${LAST_ID:-0} + 1))
echo $(printf "${TYPE_UPPER}-%03d" $NEXT_ID)
```

#### find_task(task_id)

```bash
find .tasks -name "${task_id}*.task.md" -o -name "*${task_id}*.task.md"
```

#### update_task_status(task_id, new_status)

```bash
# Find task file
TASK_FILE=$(find_task "$task_id")

# Read frontmatter
# [YAML parsing in bash is complex - consider using yq or Python helper]

# Update status field

# Move file to correct directory
NEW_DIR=".tasks/${new_status}"
mv "$TASK_FILE" "$NEW_DIR/"
```

[Additional operations...]
```

#### Recommendation for Option 3

**Verdict:** ✅ **Best for Simplicity and Portability**

This approach works best when:
- You want **zero external dependencies**
- Projects are **diverse and non-standardized**
- Team prefers **transparent, visible operations**
- Complexity of task management is **moderate** (not enterprise-scale)

**Best For:**
- Small to medium projects
- Teams new to V6 concepts
- Projects without existing custom tooling infrastructure
- Quick iteration and experimentation

---

### Option 4: Hybrid Approach (Recommended)

**Concept:** Combine the best of all approaches - lightweight MCP server for core operations, Claude Code commands for workflow, skills for reusable logic.

**Architecture:**

```
Global MCP Server (Core Only):
  ~/.claude/mcp_servers/v6_core_server/
  └── Provides:
      - Task CRUD operations (create, get, update, list)
      - Epic structure creation
      - Template rendering
      - File-based state management
  └── Does NOT provide:
      - Project-specific integrations
      - Workflow orchestration
      - Spec creation logic

Project-Level Components:
  <project>/.claude/
  ├── commands/
  │   ├── spec-epic.md          # Uses MCP for task ops + custom logic
  │   └── execute-workflow.md   # Orchestrates phases
  ├── skills/
  │   ├── spec-creation.md      # Project-specific spec workflow
  │   └── pattern-library.md    # Pattern integration (if available)
  └── output-styles/
      └── spec-architect.md     # Spec creation behavior

Integration:
  Commands → MCP Server (core ops) + Skills (custom logic) + Task tool (agents)
```

**Example: Task Creation**

```markdown
# .claude/commands/task-create.md

## Task Creation

Use MCP server for ID generation and file creation:

```
task = mcp__v6_core_server__create_task(
    title="$ARGUMENTS",
    type="feature",
    template="default"
)
```

Display result:
```
✅ Created: ${task.id}
📁 ${task.file_path}
```
```

**Example: Epic Spec Creation**

```markdown
# .claude/commands/spec-epic.md

## Epic Spec Creation

### Step 1: Interactive Refinement

[Use AskUserQuestion for batched questions]

### Step 2: Create Epic Structure

Use MCP server:

```
epic = mcp__v6_core_server__create_epic(
    title="$ARGUMENTS",
    user_scenarios=[...],
    functional_requirements=[...]
)
```

### Step 3: Project-Specific Analysis

Invoke project skill:

```
/skill spec-creation analyze-epic ${epic.id}
```

This runs project-specific logic:
- Graph-server analysis (if available)
- Pattern library search (if available)
- Constitutional validation (if .claude/constitution.md exists)

### Step 4: Generate Implementation Plan

Deploy planning agent:

```
Task(
  subagent_type="general-purpose",
  prompt="""
  Generate prescriptive implementation plan for epic ${epic.id}.

  Context:
  [spec.md content]
  [architecture.md content]
  [analysis results from skill]

  Output:
  ${epic.dir}/implementation-details/file-tasks.md
  """
)
```
```

#### Component Responsibilities

**MCP Server (Global):**
- ✅ Task CRUD (create, read, update, delete, list)
- ✅ Epic structure creation (directories + template files)
- ✅ Template rendering (Jinja2)
- ✅ File-based state (no external DB)
- ✅ ID generation (sequential, collision-free)
- ❌ NO project-specific integrations
- ❌ NO workflow orchestration
- ❌ NO spec creation logic

**Claude Code Commands (Project-Specific):**
- ✅ Workflow orchestration (Phase execution)
- ✅ Interactive refinement (AskUserQuestion)
- ✅ Agent deployment (Task tool)
- ✅ Git operations (commit, branch management)
- ✅ Quality gates (build loops, test enforcement)

**Skills (Project-Specific):**
- ✅ Spec creation logic
- ✅ Graph-server integration (if available)
- ✅ Pattern library integration (if available)
- ✅ Constitutional validation (if .claude/constitution.md exists)
- ✅ Reusable operations (find task, parse frontmatter)

**Output Styles (Project-Specific):**
- ✅ Behavior modification (Spec Architect, Workflow Orchestrator)
- ✅ Communication patterns (terse vs verbose)
- ✅ Validation strictness (quality gates)

#### Implementation Steps

**Step 1: Build Core MCP Server**

```bash
mkdir -p ~/.claude/mcp_servers/v6_core_server
cd ~/.claude/mcp_servers/v6_core_server
```

```python
# server.py
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List

mcp = FastMCP("v6-core-server")

def get_project_root() -> Path:
    """Detect project root from working directory."""
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / ".git").exists() or (cwd / ".tasks").exists():
            return cwd
        cwd = cwd.parent
    return Path.cwd()  # Fallback to cwd

@mcp.tool()
def create_task(
    title: str,
    type: str = "feature",
    priority: str = "medium",
    area: str = "general",
    template: str = "default"
) -> Dict[str, Any]:
    """Create new task with auto-generated ID."""
    project_root = get_project_root()
    tasks_dir = project_root / ".tasks" / "backlog"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    # Generate next ID
    type_upper = type.upper()
    existing = list(tasks_dir.glob(f"{type_upper}-*.task.md"))
    last_id = 0
    for task_file in existing:
        match = re.match(rf"{type_upper}-(\d+)", task_file.stem)
        if match:
            last_id = max(last_id, int(match.group(1)))
    next_id = last_id + 1
    task_id = f"{type_upper}-{next_id:03d}"

    # Load template
    template_file = project_root / ".tasks" / "templates" / f"{template}.md"
    if not template_file.exists():
        # Use built-in default template
        template_content = DEFAULT_TASK_TEMPLATE
    else:
        template_content = template_file.read_text()

    # Render template (Jinja2)
    from jinja2 import Template
    content = Template(template_content).render(
        id=task_id,
        title=title,
        type=type,
        priority=priority,
        area=area,
        created=datetime.now().strftime("%Y-%m-%d"),
        status="backlog"
    )

    # Write task file
    task_path = tasks_dir / f"{task_id}.task.md"
    task_path.write_text(content)

    return {
        "status": "success",
        "id": task_id,
        "file_path": str(task_path),
        "title": title
    }

@mcp.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """Get task by ID."""
    project_root = get_project_root()

    # Search all task directories
    for status_dir in ["backlog", "current", "completed", "archive"]:
        tasks_dir = project_root / ".tasks" / status_dir
        if not tasks_dir.exists():
            continue

        # Find matching file
        matches = list(tasks_dir.glob(f"{task_id}*.task.md"))
        if matches:
            task_file = matches[0]
            content = task_file.read_text()

            # Parse frontmatter
            frontmatter = parse_frontmatter(content)

            return {
                "status": "success",
                "id": task_id,
                "file_path": str(task_file),
                "frontmatter": frontmatter,
                "content": content
            }

    return {
        "status": "not_found",
        "id": task_id
    }

@mcp.tool()
def update_task_status(
    task_id: str,
    new_status: str
) -> Dict[str, Any]:
    """Update task status and move file."""
    project_root = get_project_root()

    # Find task
    task_data = get_task(task_id)
    if task_data["status"] == "not_found":
        return task_data

    old_path = Path(task_data["file_path"])
    new_dir = project_root / ".tasks" / new_status
    new_dir.mkdir(parents=True, exist_ok=True)
    new_path = new_dir / old_path.name

    # Update frontmatter
    content = old_path.read_text()
    updated_content = update_frontmatter(content, {
        "status": new_status,
        "updated_at": datetime.now().isoformat()
    })

    # Move file
    new_path.write_text(updated_content)
    old_path.unlink()

    return {
        "status": "success",
        "id": task_id,
        "old_status": old_path.parent.name,
        "new_status": new_status,
        "file_path": str(new_path)
    }

@mcp.tool()
def list_tasks(
    status: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """List tasks with optional filtering."""
    project_root = get_project_root()

    tasks = []
    search_dirs = [status] if status else ["backlog", "current", "completed"]

    for status_dir in search_dirs:
        tasks_dir = project_root / ".tasks" / status_dir
        if not tasks_dir.exists():
            continue

        for task_file in tasks_dir.glob("*.task.md"):
            content = task_file.read_text()
            frontmatter = parse_frontmatter(content)

            # Apply filters
            if type and frontmatter.get("type") != type:
                continue
            if priority and frontmatter.get("priority") != priority:
                continue

            tasks.append({
                "id": frontmatter.get("id"),
                "title": frontmatter.get("title"),
                "type": frontmatter.get("type"),
                "priority": frontmatter.get("priority"),
                "status": status_dir,
                "file_path": str(task_file)
            })

    return {
        "status": "success",
        "count": len(tasks),
        "tasks": tasks
    }

@mcp.tool()
def create_epic(
    epic_id: str,
    title: str,
    priority: str = "high",
    area: str = "general",
    description: str = "",
    user_scenarios: Optional[List[Dict]] = None,
    functional_requirements: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Create epic with directory structure."""
    project_root = get_project_root()

    # Create epic directory
    epic_slug = title.replace(" ", "").replace("/", "")
    epic_dir = project_root / ".tasks" / "backlog" / f"{epic_id}-{epic_slug}"

    if epic_dir.exists():
        return {
            "status": "error",
            "message": f"Epic {epic_id} already exists"
        }

    # Create subdirectories
    epic_dir.mkdir(parents=True, exist_ok=True)
    (epic_dir / "contracts").mkdir()
    (epic_dir / "implementation-details").mkdir()
    (epic_dir / "research").mkdir()
    (epic_dir / "analysis").mkdir()

    # Create spec.md
    spec_content = render_spec_template(
        epic_id=epic_id,
        title=title,
        description=description,
        user_scenarios=user_scenarios or [],
        functional_requirements=functional_requirements or []
    )
    (epic_dir / "spec.md").write_text(spec_content)

    # Create architecture.md (template)
    arch_content = render_architecture_template(epic_id, title)
    (epic_dir / "architecture.md").write_text(arch_content)

    # Create task.md
    task_content = render_epic_task_template(
        epic_id=epic_id,
        title=title,
        priority=priority,
        area=area
    )
    (epic_dir / "task.md").write_text(task_content)

    return {
        "status": "success",
        "epic_id": epic_id,
        "epic_dir": str(epic_dir),
        "files_created": {
            "spec": str(epic_dir / "spec.md"),
            "architecture": str(epic_dir / "architecture.md"),
            "task": str(epic_dir / "task.md")
        }
    }

# Helper functions
def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter."""
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        return {}

    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}

    try:
        frontmatter_text = "\n".join(lines[1:end_idx])
        return yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        return {}

def update_frontmatter(content: str, updates: Dict[str, Any]) -> str:
    """Update YAML frontmatter."""
    frontmatter = parse_frontmatter(content)
    frontmatter.update(updates)

    # Find content start
    lines = content.split("\n")
    content_start = 0
    if lines and lines[0] == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                content_start = i + 1
                break

    # Rebuild with updated frontmatter
    new_lines = ["---"]
    new_lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False))
    new_lines.append("---")
    new_lines.extend(lines[content_start:])

    return "\n".join(new_lines)

# Template constants
DEFAULT_TASK_TEMPLATE = """---
id: {{ id }}
title: {{ title }}
type: {{ type }}
priority: {{ priority }}
status: {{ status }}
created: {{ created }}
area: {{ area }}
---

# {{ id }}: {{ title }}

## Problem Statement

[Describe what this task solves]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Implementation Notes

[Technical details, links, references]
"""

# [Additional template rendering functions...]

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Step 2: Install Global Server**

```bash
# Add to ~/.claude/settings.json
{
  "mcp_servers": {
    "v6-core": {
      "command": "python3",
      "args": ["/home/andreas-spannbauer/.claude/mcp_servers/v6_core_server/server.py"]
    }
  }
}

# Restart Claude Code
```

**Step 3: Create Project Commands**

```bash
mkdir -p <project>/.claude/commands
```

**Create Task Command:**

```markdown
# <project>/.claude/commands/task-create.md
---
description: "Create new task"
argument-hint: "<type> <title>"
allowed-tools: [mcp__v6_core__create_task]
---

## Create Task

Parse $ARGUMENTS:
- First word = type (feature/bug/chore/refactor/docs)
- Rest = title

Validate type is allowed.

Create task:

```
task = mcp__v6_core__create_task(
    title=title,
    type=type,
    priority="medium",
    area="general"
)
```

Display:
```
✅ Created ${task.id}: ${task.title}
📁 ${task.file_path}
```
```

**Epic Creation Command:**

```markdown
# <project>/.claude/commands/spec-epic.md
---
description: "Create epic with interactive refinement"
argument-hint: "<title>"
allowed-tools: [
  mcp__v6_core__create_epic,
  AskUserQuestion,
  Task(subagent_type=general-purpose),
  Write,
  Read
]
---

## Epic Spec Creation

Switch to Spec Architect output style (if available):

/output-style Spec Architect V6

### Round 1: Problem Understanding

[Interactive questioning using AskUserQuestion...]

### Round 2: Scope Definition

[More questions...]

### Generate Epic ID

Determine next epic ID:

```bash
LAST_EPIC=$(ls .tasks/backlog/EPIC-*.task.md 2>/dev/null | \
  sort -V | tail -1 | grep -oP 'EPIC-\K\d+')
NEXT_EPIC=$((${LAST_EPIC:-0} + 1))
EPIC_ID=$(printf "EPIC-%03d" $NEXT_EPIC)
```

### Create Epic Structure

Use MCP server:

```
epic = mcp__v6_core__create_epic(
    epic_id=EPIC_ID,
    title="$ARGUMENTS",
    priority="high",
    user_scenarios=[...from Round 1],
    functional_requirements=[...from Round 2]
)
```

### Project-Specific Analysis

**If graph-server available:**

```bash
# Check for graph-server
if [ -f "tools/graph_server.py" ]; then
  # Run graph analysis using project-specific integration
  python3 tools/spec_creation/graph_analysis.py \
    --epic-id ${EPIC_ID} \
    --output ${epic.epic_dir}/analysis/
fi
```

**If pattern library available:**

```bash
# Search pattern library
if [ -f "tools/pattern_library_manager.py" ]; then
  python3 -c "
from tools.pattern_library_manager import PatternLibraryManager
manager = PatternLibraryManager()
patterns = manager.search('$ARGUMENTS')
print(patterns)
" > ${epic.epic_dir}/research/pattern-library-results.md
fi
```

### Generate Implementation Plan

Deploy planning agent:

```
Task(
  subagent_type="general-purpose",
  prompt="""
  Generate prescriptive implementation plan for ${EPIC_ID}.

  SPEC:
  [Read ${epic.epic_dir}/spec.md]

  ARCHITECTURE:
  [Read ${epic.epic_dir}/architecture.md]

  ANALYSIS:
  [Read ${epic.epic_dir}/analysis/* if exists]

  PATTERNS:
  [Read ${epic.epic_dir}/research/* if exists]

  OUTPUT:
  File-level implementation tasks to:
  ${epic.epic_dir}/implementation-details/file-tasks.md

  Format:
  ## Files to Create
  - file_path: description

  ## Files to Modify
  - file_path: changes needed

  ## Implementation Steps
  1. Step 1
  2. Step 2
  """
)
```

### Next Steps

Display completion and next actions.
```

**Step 4: Create Project Skills** (Optional)

```markdown
# <project>/.claude/skills/spec-creation.md
---
description: "Project-specific spec creation operations"
---

## Spec Creation Skill

### analyze_epic(epic_id)

Run project-specific analysis:

```bash
EPIC_DIR=$(find .tasks -name "${epic_id}-*" -type d)

# Graph-server analysis
if [ -f "tools/graph_server.py" ]; then
  python3 tools/spec_creation/graph_analysis.py \
    --epic-id ${epic_id} \
    --output ${EPIC_DIR}/analysis/
  echo "✅ Graph analysis complete"
fi

# Pattern library search
if [ -f "tools/pattern_library_manager.py" ]; then
  python3 tools/pattern_library_manager.py search \
    --query "$(cat ${EPIC_DIR}/spec.md | head -50)" \
    --output ${EPIC_DIR}/research/patterns.md
  echo "✅ Pattern search complete"
fi

# Constitutional validation
if [ -f ".claude/constitution.md" ]; then
  python3 tools/spec_creation/constitutional_validator.py \
    --epic-id ${epic_id} \
    --constitution .claude/constitution.md \
    --output ${EPIC_DIR}/constitutional_compliance.md
  echo "✅ Constitutional validation complete"
fi
```

### validate_epic_completeness(epic_id)

Check if epic is ready for execution:

```bash
EPIC_DIR=$(find .tasks -name "${epic_id}-*" -type d)

REQUIRED_FILES=(
  "spec.md"
  "architecture.md"
  "implementation-details/file-tasks.md"
)

MISSING=()

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "${EPIC_DIR}/${file}" ]; then
    MISSING+=("$file")
  fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
  echo "✅ Epic complete and ready for execution"
  exit 0
else
  echo "❌ Epic incomplete. Missing:"
  for file in "${MISSING[@]}"; do
    echo "  - $file"
  done
  exit 1
fi
```

[Additional operations...]
```

#### Benefits of Hybrid Approach

✅ **Consistent Core Operations** - MCP server ensures task management works the same everywhere
✅ **Project Flexibility** - Commands and skills customize for each project's needs
✅ **No Code Duplication** - Core logic in one place, project logic in commands
✅ **Easy Updates** - Update MCP server once, benefits all projects
✅ **Optional Integrations** - Projects with graph-server/pattern library get extra features
✅ **Progressive Enhancement** - Start simple, add complexity as needed
✅ **Observable Workflow** - Commands show exactly what's happening
✅ **Reusable Patterns** - Skills capture common operations

#### Migration Path

**Phase 1: Install Core MCP Server (Week 1)**

1. Extract core task management from email project
2. Create global MCP server with 5 essential tools:
   - create_task
   - get_task
   - update_task_status
   - list_tasks
   - create_epic
3. Install in `~/.claude/mcp_servers/v6_core_server/`
4. Test in one project

**Phase 2: Create Standard Commands (Week 2)**

1. Create command templates:
   - task-create.md
   - spec-epic.md
   - execute-workflow.md
2. Test in 2-3 diverse projects
3. Refine based on feedback

**Phase 3: Add Optional Skills (Week 3)**

1. Create skill templates:
   - spec-creation.md (graph-server, pattern library integration)
   - workflow-helpers.md (common operations)
2. Document integration points
3. Create examples for projects with/without graph-server

**Phase 4: Roll Out to All Projects (Week 4)**

1. For each project:
   - Install `.tasks/` directory structure
   - Copy commands to `.claude/commands/`
   - Adapt skills if project has graph-server/pattern library
   - Create project-specific templates if needed
2. Document per-project customizations
3. Train team on workflow

---

## Recommendations

Based on the thorough analysis above, here are my recommendations:

### Primary Recommendation: **Hybrid Approach**

**Why:**

1. **Balance of Consistency and Flexibility**
   - Core task management (CRUD operations) is identical across all projects
   - Workflow orchestration adapts to each project's unique needs
   - No forced standardization where it doesn't fit

2. **Maintainability**
   - 80% of code (core MCP server) maintained in one place
   - 20% of code (commands/skills) distributed but simple markdown
   - Bug fixes to core propagate instantly to all projects

3. **Progressive Enhancement**
   - Start with minimal setup (MCP + basic commands)
   - Add complexity only where needed (graph-server, pattern library)
   - Projects without advanced tooling still get full task management

4. **Observable and Debuggable**
   - Commands show exact operations (bash commands visible)
   - Skills are readable markdown, not opaque Python
   - Easy to modify and experiment

5. **Proven Patterns from Email Project**
   - Keep the best parts: hierarchical epics, interactive refinement, quality gates
   - Simplify the over-engineered parts: remove workflow DAG orchestrator, simplify phase handlers
   - Make it reusable: abstract core, keep project-specific in commands

### Implementation Roadmap

**Week 1: Core MCP Server**

- [ ] Extract task management logic from email project
- [ ] Create `~/.claude/mcp_servers/v6_core_server/server.py`
- [ ] Implement 5 core tools:
  - create_task
  - get_task
  - update_task_status
  - list_tasks
  - create_epic
- [ ] Add helper functions (parse_frontmatter, update_frontmatter)
- [ ] Create default templates (task.md, epic structure)
- [ ] Test in one project

**Deliverables:**
- Global MCP server (functional)
- Basic task CRUD working
- Epic creation working
- Documentation for MCP tools

**Week 2: Standard Commands**

- [ ] Create command templates:
  - task-create.md
  - task-get.md
  - task-update-status.md
  - task-list.md
  - spec-epic.md (interactive refinement)
- [ ] Test commands in 3 diverse projects:
  - Project with graph-server (email_management_system)
  - Project without graph-server (whisper_hotkeys)
  - New empty project
- [ ] Refine based on feedback
- [ ] Document command parameters and behavior

**Deliverables:**
- 5 reusable commands (tested)
- Command usage documentation
- Examples from 3 projects

**Week 3: Optional Skills**

- [ ] Create skill templates:
  - spec-creation.md (graph-server integration, pattern library)
  - workflow-helpers.md (common operations)
- [ ] Add conditional logic:
  - Detect if graph-server available
  - Detect if pattern library available
  - Graceful degradation if not present
- [ ] Test in projects with/without integrations
- [ ] Document integration requirements

**Deliverables:**
- 2 reusable skills (tested)
- Integration documentation
- Conditional logic examples

**Week 4: Workflow Execution**

- [ ] Create execute-workflow.md command
- [ ] Implement phase execution:
  - Preflight validation
  - Implementation (agent deployment)
  - Validation (tests, linting)
  - Build gate (mandatory loop)
  - Documentation
  - Commit
- [ ] Add quality gates:
  - Build/lint loops (max 3 attempts)
  - Test coverage enforcement
  - Constitutional validation
- [ ] Test end-to-end workflow in 2 projects
- [ ] Document workflow phases

**Deliverables:**
- Complete workflow command (tested end-to-end)
- Quality gate implementation
- Phase execution documentation

**Week 5: Output Styles**

- [ ] Extract output styles from email project:
  - Spec Architect V6
  - Workflow Orchestrator V6
- [ ] Make them project-agnostic:
  - Remove project-specific references
  - Generalize patterns
- [ ] Test in 3 projects
- [ ] Document when to use each style

**Deliverables:**
- 2 portable output styles
- Style selection guide
- Usage examples

**Week 6: Rollout to All Projects**

- [ ] Create installation script:
  ```bash
  ~/install_v6_task_management.sh <project-dir>
  ```
- [ ] For each project:
  - Run installation script
  - Customize templates if needed
  - Add project-specific skills
  - Test workflow end-to-end
  - Document customizations
- [ ] Team training:
  - Demo workflow
  - Hands-on practice
  - Q&A session

**Deliverables:**
- Automated installation script
- V6 installed in all active projects
- Team training complete
- Project-specific documentation

### Secondary Recommendation: **Fallback to Option 3 (Commands Only)**

**When to Use:**

If the hybrid approach proves too complex, fall back to **Option 3: Claude Code Commands + Output Styles (No MCP)**.

**Why It Works:**

- Zero external dependencies (no MCP server to maintain)
- Everything is markdown + bash (transparent and debuggable)
- Easy to understand and modify
- Fast iteration (edit markdown, no server restart)

**Trade-offs Accepted:**

- More bash complexity for advanced operations
- Some code duplication across projects (acceptable for <10 projects)
- Manual ID generation (bash script instead of MCP tool)

**When to Choose Fallback:**

- Team is not comfortable with Python/MCP servers
- Projects are very diverse (standardization doesn't provide value)
- Only 2-3 projects need task management (duplication acceptable)
- Rapid experimentation phase (not ready to commit to architecture)

---

## Comparison Matrix

| Criteria | Global MCP | Per-Project MCP | Commands Only | Hybrid (Recommended) |
|----------|-----------|-----------------|---------------|----------------------|
| **Setup Complexity** | Low (install once) | High (per project) | Very Low (copy files) | Medium (MCP + commands) |
| **Maintenance** | ⭐⭐⭐⭐⭐ Centralized | ⭐⭐ Duplicated | ⭐⭐⭐ Distributed | ⭐⭐⭐⭐ Mostly centralized |
| **Customization** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Full control | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐ Flexible |
| **Project-Specific Integration** | ⭐⭐ Plugin system | ⭐⭐⭐⭐⭐ Direct | ⭐⭐⭐⭐ Skill-based | ⭐⭐⭐⭐⭐ Skill-based |
| **Learning Curve** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ High | ⭐⭐ Low | ⭐⭐⭐ Moderate |
| **Debugging** | ⭐⭐⭐ MCP logs | ⭐⭐⭐ MCP logs | ⭐⭐⭐⭐⭐ Visible bash | ⭐⭐⭐⭐ Mostly visible |
| **Code Reuse** | ⭐⭐⭐⭐⭐ Maximum | ⭐ Minimal | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ High |
| **Consistency** | ⭐⭐⭐⭐⭐ Identical | ⭐⭐ Fragmentation | ⭐⭐⭐ Template-based | ⭐⭐⭐⭐ Core identical |
| **Portability** | ⭐⭐⭐⭐⭐ Any project | ⭐⭐ Project-coupled | ⭐⭐⭐⭐⭐ Any project | ⭐⭐⭐⭐ Any project |
| **Recommended For** | Standardized orgs | Large complex projects | Small teams, diverse projects | **Most use cases** |

---

## Conclusion

The V6 task management and spec creation pipeline in the email_management_system project represents a sophisticated, production-ready system for managing complex software development workflows.

**Key Takeaway:**

> The system's power comes from **progressive refinement** (spec creation), **hierarchical organization** (epic structures), and **explicit validation** (quality gates). These principles are more valuable than any specific implementation technology.

**The Hybrid Approach is recommended because:**

1. It keeps the **best architectural patterns** from the email project (hierarchical epics, interactive refinement, quality gates)
2. It removes **unnecessary complexity** (workflow DAG orchestrator, complex phase handlers)
3. It provides **consistency where it matters** (core task operations)
4. It allows **flexibility where it's needed** (workflow orchestration, project integrations)
5. It's **maintainable** (centralized core, distributed customization)
6. It's **observable** (commands show operations, not hidden in MCP server)

**Next Steps:**

1. **Validate this assessment** with the team
2. **Prototype the core MCP server** (Week 1 deliverables)
3. **Test in 1-2 projects** to validate architecture
4. **Iterate based on feedback** before full rollout
5. **Execute 6-week implementation roadmap** if validated

The email project has demonstrated that this approach scales to complex, enterprise-grade development. With the hybrid architecture, we can bring these benefits to all projects while maintaining flexibility and simplicity.

---

**End of Assessment**
