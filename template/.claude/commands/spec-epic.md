---
description: "Create epic with interactive spec refinement and GitHub issue"
argument-hint: "<title>"
allowed-tools: [Write, Read, Bash]
---

## Epic Spec Creation

Switch to Spec Architect output style (if available):
```
/output-style Spec Architect
```

If style not available, continue with default style.

---

## Round 1: Problem Understanding

Ask these 4 questions using plain text format:

```markdown
**Round 1: Problem Understanding (4 questions)**

Please provide your answers below each question:

**1. Pain Point:** What user pain point does this solve?

**Your answer:**

**2. Workaround:** What is the current manual workaround?

**Your answer:**

**3. Desired:** What is the desired automated behavior?

**Your answer:**

**4. Impact:** What is the expected impact? (users affected, time saved, business value)

**Your answer:**
```

[Wait for user responses - store answers as: pain_point, current_workaround, desired_behavior, expected_impact]

---

## Round 2: Scope Definition

Based on Round 1 answers, ask these 5 questions using plain text:

```markdown
**Round 2: Scope Definition (5 questions)**

Please provide your answers below each question:

**5. Integrations:** Which existing components will this integrate with?

**Your answer:**

**6. New Components:** What new components are needed?

**Your answer:**

**7. Data Sources:** What data sources are involved? (databases, APIs, files, etc.)

**Your answer:**

**8. Edge Cases:** What are the edge cases to consider?

**Your answer:**

**9. Non-Goals:** What are the non-goals? (explicitly out of scope)

**Your answer:**
```

[Wait for user responses - store answers as: existing_components, new_components, data_sources, edge_cases, non_goals]

---

## Round 3: Technical Constraints

Ask these 3 questions using plain text:

```markdown
**Round 3: Technical Constraints (3 questions)**

Please provide your answers below each question:

**10. Performance:** What are the performance requirements? (latency, throughput, scale)

**Your answer:**

**11. Security:** What are the security considerations? (auth, data protection, compliance)

**Your answer:**

**12. Compatibility:** What are compatibility constraints? (browsers, platforms, APIs, dependencies)

**Your answer:**
```

[Wait for user responses - store answers as: performance_requirements, security_considerations, compatibility_constraints]

---

## Consult Workflow Pattern Library

**CRITICAL:** Query the workflow pattern library to improve spec quality and completeness.

Search the workflow pattern library for relevant patterns in three areas:

### 1. Spec Completeness Patterns

```bash
# Search for spec-related patterns
echo "🔍 Searching workflow patterns for spec guidance..."
echo ""

# Check if pattern library exists
if [ -d "$HOME/.claude/workflow_pattern_library/patterns" ]; then
  # Use Context7-style semantic search via Python
  python3 << 'EOF'
import os
from pathlib import Path

pattern_dir = Path.home() / ".claude" / "workflow_pattern_library" / "patterns"

if pattern_dir.exists():
    print("📚 Consulting workflow pattern library...")
    print("")
    print("**Spec-related patterns found:**")

    # Search for spec-related patterns
    spec_patterns = list(pattern_dir.glob("*spec*.md")) + list(pattern_dir.glob("*completeness*.md"))

    if spec_patterns:
        for pattern in spec_patterns[:3]:  # Top 3
            print(f"  - {pattern.name}")
    else:
        print("  (No spec-specific patterns yet)")

    print("")
else:
    print("ℹ️ Workflow pattern library not found (first epic in workflow)")
    print("")
EOF
else
  echo "ℹ️ Workflow pattern library not initialized (first epic in workflow)"
  echo ""
fi
```

**Action:** Read relevant spec patterns and incorporate their guidance:
- Missing sections that should be included
- Common acceptance criteria structures
- Edge cases frequently forgotten
- Contract definition patterns

### 2. Architecture Design Patterns

```bash
echo "🔍 Searching for architecture patterns..."
echo ""

python3 << 'EOF'
from pathlib import Path

pattern_dir = Path.home() / ".claude" / "workflow_pattern_library" / "patterns"

if pattern_dir.exists():
    print("**Architecture-related patterns found:**")

    # Search for architecture patterns
    arch_patterns = list(pattern_dir.glob("*architecture*.md")) + list(pattern_dir.glob("*design*.md"))

    if arch_patterns:
        for pattern in arch_patterns[:3]:  # Top 3
            print(f"  - {pattern.name}")
    else:
        print("  (No architecture-specific patterns yet)")

    print("")
EOF
```

**Action:** Read relevant architecture patterns and apply:
- Component separation principles
- Data flow patterns
- Integration patterns with existing systems
- Common architectural mistakes to avoid

### 3. Implementation Planning Patterns

```bash
echo "🔍 Searching for planning patterns..."
echo ""

python3 << 'EOF'
from pathlib import Path

pattern_dir = Path.home() / ".claude" / "workflow_pattern_library" / "patterns"

if pattern_dir.exists():
    print("**Planning-related patterns found:**")

    # Search for planning patterns
    plan_patterns = list(pattern_dir.glob("*plan*.md")) + list(pattern_dir.glob("*task*.md")) + list(pattern_dir.glob("*implementation*.md"))

    if plan_patterns:
        for pattern in plan_patterns[:3]:  # Top 3
            print(f"  - {pattern.name}")
    else:
        print("  (No planning-specific patterns yet)")

    print("")
EOF
```

**Action:** Read relevant planning patterns for later use:
- Task breakdown strategies
- File-tasks.md structure patterns
- Dependency ordering
- Common implementation oversights

### Pattern Integration

**Important:** The patterns above are GUIDANCE, not strict requirements. Use professional judgment:
- Apply patterns that fit the current epic
- Adapt patterns to specific context
- Skip patterns that don't apply
- Document deviations if significant

```bash
echo "✅ Pattern consultation complete"
echo ""
echo "Continue with epic generation, incorporating pattern guidance..."
echo ""
```

---

## Phase 0.5: Consult Past Epics (Longitudinal Learning)

**Purpose**: Learn from past epic implementations before planning new epic.

Read epic registry and identify lessons from similar epics:

```bash
echo "📚 Consulting past epics for lessons..."
echo ""

python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry

try:
    registry = load_registry()

    # Find implemented epics
    implemented = [e for e in registry.data.epics if e.status == "implemented"]

    if not implemented:
        print("ℹ️  No past epics to learn from (first epic in project)")
        sys.exit(0)

    print(f"📊 Found {len(implemented)} implemented epics")
    print("")
    print("Reading post-mortems for lessons...")
    print("")

    for epic in implemented:
        if epic.post_mortem:
            post_mortem_file = Path(epic.post_mortem)
            if post_mortem_file.exists():
                print(f"## {epic.epic_id}: {epic.title}")
                print(f"Tags: {', '.join(epic.tags)}")
                print("")

                # Extract "Recommendations" section
                with open(post_mortem_file) as f:
                    content = f.read()
                    if "## Recommendations" in content:
                        recs_section = content.split("## Recommendations")[1]
                        # Get until next ## or end
                        if "##" in recs_section[2:]:
                            recs_section = recs_section.split("##")[0]

                        # Truncate to 500 chars
                        recs = recs_section.strip()[:500]
                        print(recs)
                        if len(recs_section.strip()) > 500:
                            print("... (truncated)")
                        print("")
            else:
                print(f"⚠️  Post-mortem missing for {epic.epic_id}")
                print("")

except FileNotFoundError:
    print("ℹ️  Epic registry not found (initialize with /epic-registry-init)")
    sys.exit(0)

EOF

echo ""
echo "Use these lessons to inform:"
echo "  - Architecture decisions"
echo "  - Technology choices"
echo "  - Common pitfalls to avoid"
echo "  - Briefing improvements to apply"
echo ""
```

---

## Generate Epic ID

Use bash to generate the next epic ID from the registry:

```bash
cd /home/andreas-spannbauer/v6-tier1-template

# Load registry and generate ID
NEXT_EPIC_INFO=$(python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry

try:
    registry = load_registry()
    epic_id = registry.generate_epic_id()
    epic_number = registry.get_next_epic_number()
    print(f"{epic_id}:{epic_number}")
except FileNotFoundError:
    print("ERROR:registry-not-found")
    exit(1)

EOF
)

if [[ "$NEXT_EPIC_INFO" == ERROR:* ]]; then
  echo "❌ Epic registry not found"
  echo ""
  echo "Initialize registry first:"
  echo "  /epic-registry-init"
  echo ""
  exit 1
fi

EPIC_ID=$(echo "$NEXT_EPIC_INFO" | cut -d: -f1)
EPIC_NUMBER=$(echo "$NEXT_EPIC_INFO" | cut -d: -f2)

echo "Generated Epic ID: ${EPIC_ID} (number: ${EPIC_NUMBER})"
```

Store both EPIC_ID and EPIC_NUMBER for use in subsequent steps.

---

## Create Epic Directory Structure

```bash
cd /home/andreas-spannbauer/v6-tier1-template

# Create slug from title (remove spaces and special chars)
TITLE="$ARGUMENTS"
EPIC_SLUG=$(echo "$TITLE" | sed 's/ /-/g' | sed 's/[^a-zA-Z0-9-]//g' | tr '[:upper:]' '[:lower:]')
EPIC_DIR=".tasks/backlog/${EPIC_ID}-${EPIC_SLUG}"

# Create directory structure
mkdir -p "${EPIC_DIR}"/{contracts,implementation-details,research}

echo "Created epic directory: ${EPIC_DIR}"
```

Store EPIC_DIR and EPIC_SLUG for use in subsequent steps.

---

## Write spec.md

Read the template from `.tasks/templates/spec.md.j2`

Substitute the following variables (use sed or manual string replacement):
- `{{ epic_id }}` → ${EPIC_ID}
- `{{ title }}` → ${TITLE} (from $ARGUMENTS)
- `{{ priority }}` → "high"
- `{{ created }}` → $(date +%Y-%m-%d)
- `{{ domain }}` → "general" (default, user can change later)
- `{{ pain_point }}` → Answer from Question 1
- `{{ current_workaround }}` → Answer from Question 2
- `{{ desired_behavior }}` → Answer from Question 3
- `{{ expected_impact }}` → Answer from Question 4
- `{{ existing_components }}` → Answer from Question 5
- `{{ new_components }}` → Answer from Question 6
- `{{ data_sources }}` → Answer from Question 7
- `{{ edge_cases }}` → Answer from Question 8
- `{{ non_goals }}` → Answer from Question 9
- `{{ performance_requirements }}` → Answer from Question 10
- `{{ security_considerations }}` → Answer from Question 11
- `{{ compatibility_constraints }}` → Answer from Question 12
- `{{ core_features }}` → Synthesize from answers (2-3 bullet points)

Write the completed spec to `${EPIC_DIR}/spec.md`

---

## Write architecture.md

Read the template from `.tasks/templates/architecture.md.j2`

Substitute variables:
- `{{ epic_id }}` → ${EPIC_ID}
- `{{ title }}` → ${TITLE}
- `{{ created }}` → $(date +%Y-%m-%d)

Write the template to `${EPIC_DIR}/architecture.md` (this is a skeleton for user to fill in)

---

## Write task.md

Create `${EPIC_DIR}/task.md` with frontmatter and links to spec/architecture:

```markdown
---
id: ${EPIC_ID}
title: ${TITLE}
type: epic
priority: high
status: backlog
created: $(date +%Y-%m-%d)
area: general
---

# ${EPIC_ID}: ${TITLE}

## Epic Artifacts

This epic consists of the following documentation:

- **[Specification](./spec.md)** - WHAT/WHY: User scenarios, requirements, contracts
- **[Architecture](./architecture.md)** - HOW: System design, components, data flow
- **[Implementation Details](./implementation-details/)** - Technical decisions, ADRs
- **[Contracts](./contracts/)** - API contracts, data schemas, event definitions
- **[Research](./research/)** - Spikes, investigations, prototypes

## Next Steps

1. Review and refine specification with stakeholders
2. Complete architecture design
3. Break down into implementation tasks
4. Create GitHub issue (auto-generated)

## Progress

- [x] Epic created
- [ ] Specification approved
- [ ] Architecture finalized
- [ ] Tasks created
- [ ] Implementation started
```

Write to `${EPIC_DIR}/task.md`

---

## Create GitHub Issue (MANDATORY)

**CRITICAL: GitHub integration is MANDATORY - failures will block epic creation**

Use Python to create GitHub issue from the epic (BLOCKING mode):

```bash
cd /home/andreas-spannbauer/v6-tier1-template

python3 << 'PYTHON_EOF'
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Import from tools.github_integration
sys.path.insert(0, str(Path.cwd()))
from tools.github_integration.issue_sync_gh import create_github_issue_from_epic_blocking

# Get epic details from environment
epic_id = "${EPIC_ID}"
epic_dir = Path("${EPIC_DIR}")

# Create GitHub issue (BLOCKING - will raise on failure)
print(f"\n🔗 Creating GitHub issue for {epic_id}...")

try:
    issue_url = create_github_issue_from_epic_blocking(epic_id, epic_dir)
    print(f"✅ GitHub Issue created: {issue_url}")

    # Export for use in next steps
    import os
    os.environ["GITHUB_ISSUE_URL"] = issue_url

except FileNotFoundError as e:
    print(f"\n❌ EPIC CREATION FAILED")
    print(f"   Missing artifact: {e}")
    print(f"\n   Epic directory incomplete - cannot proceed")
    print(f"   Fix the missing file and try again.")
    sys.exit(1)

except RuntimeError as e:
    print(f"\n❌ EPIC CREATION FAILED")
    print(f"   GitHub integration error: {e}")
    print(f"\n   GitHub integration is MANDATORY for Tier 1 workflow.")

    if "not authenticated" in str(e):
        print(f"\n   Authenticate with:")
        print(f"     gh auth login")
    elif "not found" in str(e):
        print(f"\n   Install GitHub CLI:")
        print(f"     https://cli.github.com/")

    sys.exit(1)

except Exception as e:
    print(f"\n❌ EPIC CREATION FAILED")
    print(f"   Unexpected error: {e}")
    print(f"\n   Contact maintainer if issue persists.")
    sys.exit(1)

PYTHON_EOF

# Check exit code
if [ $? -ne 0 ]; then
  echo ""
  echo "======================================================================"
  echo "❌ Epic creation aborted due to GitHub integration failure"
  echo "======================================================================"
  exit 1
fi

echo ""
echo "✅ GitHub issue creation succeeded"
echo ""
```

**What this does:**
1. Calls `create_github_issue_from_epic_blocking()` instead of non-blocking version
2. Catches exceptions and provides clear error messages
3. Exits with code 1 on failure (blocks epic creation)
4. Provides actionable guidance (how to auth, install gh CLI)

---

## Add Epic to Registry

Add the newly created epic to the registry:

```bash
python3 << 'PYTHON_EOF'
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry
from tools.epic_registry.models import Epic, EpicStatus, EpicDependencies

registry = load_registry()

# Extract issue number from issue_url if available
issue_number = None
issue_url = "${issue_url}" if "${issue_url}" else None

if issue_url:
    # Extract issue number from URL (e.g., https://github.com/user/repo/issues/42 -> 42)
    import re
    match = re.search(r'/issues/(\d+)$', issue_url)
    if match:
        issue_number = int(match.group(1))

# Create epic object
epic = Epic(
    epic_id="${EPIC_ID}",
    epic_number=${EPIC_NUMBER},
    title="${TITLE}",
    slug="${EPIC_SLUG}",
    status=EpicStatus.DEFINED,
    created_date=datetime.now(timezone.utc).date().isoformat(),
    directory="${EPIC_DIR}",
    github_issue=issue_number,
    github_url=issue_url,
    tags=["${domain}"],
    dependencies=EpicDependencies(),
)

# Add to registry
registry.add_epic(epic)
registry.save()

print(f"✅ Epic added to registry: {epic.epic_id}")
print(f"   Status: {epic.status.value}")
print(f"   Next epic number: {registry.data.next_epic_number}")

PYTHON_EOF
```

---

## Validation Check

**CRITICAL:** Verify the Spec Architect output style generated the implementation plan.

```bash
echo ""
echo "Validating epic completeness..."
echo "----------------------------------------------------------------------"

# Check if file-tasks.md was created
if [ ! -f "${EPIC_DIR}/implementation-details/file-tasks.md" ]; then
  echo ""
  echo "⚠️  WARNING: Implementation plan missing"
  echo ""
  echo "   Required file not found:"
  echo "   ${EPIC_DIR}/implementation-details/file-tasks.md"
  echo ""
  echo "   This file contains the prescriptive implementation plan"
  echo "   that agents need to execute the epic."
  echo ""
  echo "   Cause: The Spec Architect output style should have generated"
  echo "   this file automatically in Phase 5.5."
  echo ""
  echo "   Solutions:"
  echo "   1. Use Spec Architect output style: /output-style Spec Architect V6"
  echo "   2. Manually create file-tasks.md using the template:"
  echo "      .tasks/templates/file-tasks.md.j2"
  echo "   3. Or use /generate-implementation-plan ${EPIC_ID} (if available)"
  echo ""
  echo "   ❌ Epic is INCOMPLETE without this file."
  echo "   ❌ /execute-workflow will FAIL if you proceed."
  echo ""
else
  # file-tasks.md exists - verify it's not empty
  FILE_SIZE=$(wc -l < "${EPIC_DIR}/implementation-details/file-tasks.md")

  if [ "$FILE_SIZE" -lt 50 ]; then
    echo ""
    echo "⚠️  WARNING: Implementation plan seems incomplete"
    echo ""
    echo "   ${EPIC_DIR}/implementation-details/file-tasks.md"
    echo "   only has $FILE_SIZE lines (expected >50 for a real plan)"
    echo ""
    echo "   Review the file to ensure it contains:"
    echo "   - File-by-file implementation instructions"
    echo "   - Exact code to write for each file"
    echo "   - Dependencies and testing requirements"
    echo ""
  else
    echo "✅ Implementation plan verified:"
    echo "   ${EPIC_DIR}/implementation-details/file-tasks.md ($FILE_SIZE lines)"
  fi
fi

echo ""
```

---

## Display Completion

```
✅ Epic created: ${EPIC_ID}
📁 Location: ${EPIC_DIR}

Created files:
- spec.md (WHAT/WHY - user scenarios, requirements, contracts)
- architecture.md (HOW - system design, components)
- task.md (workflow metadata)
- contracts/ (contract definitions)
- implementation-details/ (ADRs, technical docs)
- research/ (spikes, investigations)

🔗 GitHub Issue: [URL from creation step]
📋 Registry: .tasks/epic_registry.json (updated)
📊 Status: DEFINED

Next steps:
1. Review specification: code ${EPIC_DIR}/spec.md
2. Design architecture: code ${EPIC_DIR}/architecture.md
3. Define contracts: code ${EPIC_DIR}/contracts/
4. View registry: /epic-registry-status
5. Execute epic: /execute-workflow ${EPIC_ID}
6. Break into tasks: /task-create feature "Task title"
7. View epic: /task-get ${EPIC_ID}

Pro tips:
- Use contracts/ for API schemas, event definitions
- Use implementation-details/ for ADRs (Architecture Decision Records)
- Use research/ for spike results and prototypes
- Link sub-tasks back to epic in their frontmatter
```

---

## Implementation Notes

**Variable Storage:**
After each question round (using plain text questions), store the user's answers in bash variables or Python variables for template substitution.

**Template Substitution:**
Use bash `sed` for simple replacements:
```bash
sed "s|{{ epic_id }}|${EPIC_ID}|g" | \
sed "s|{{ title }}|${TITLE}|g" | \
sed "s|{{ pain_point }}|${PAIN_POINT}|g"
```

Or use Python for more complex substitution:
```python
template = template_file.read_text()
content = template.replace("{{ epic_id }}", epic_id)
content = content.replace("{{ title }}", title)
# ... etc
```

**Error Handling:**
- If template files don't exist, create minimal versions inline
- If GitHub creation fails, warn user but continue
- If directory creation fails, abort with clear error message

**Validation:**
- Ensure $ARGUMENTS (title) is not empty
- Ensure all question answers are provided
- Verify epic directory doesn't already exist
