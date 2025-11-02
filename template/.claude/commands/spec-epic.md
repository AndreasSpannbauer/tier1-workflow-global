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

**CRITICAL:** Provide intelligent analysis and recommendations, NOT just naked questions.

### Your Task:

1. **Analyze the epic title** (`$ARGUMENTS`) - what does it suggest?
2. **For each question**, provide:
   - Context (why this matters)
   - 3-4 suggested options (specific to the epic title)
   - Your recommendation
3. **Then** let user answer

### Output Format:

Start with epic analysis:

```markdown
## Round 1: Problem Understanding

I see you want to create: **"$ARGUMENTS"**

**What this epic suggests:**
- [3-4 bullet points analyzing what the epic title indicates]
- [Problem domain, technical approach, likely goals]
- [Key ambiguities that need clarification]

I'll now ask 4 questions with context and recommendations for each.

---
```

Then for each question, follow this pattern:

```markdown
### Question 1: Pain Point

**What user pain point does this solve?**

**Why this matters:** Understanding the pain point ensures we're solving a real problem, not building something nobody needs.

**Based on "$ARGUMENTS", the pain point might be:**
- Option A: [Specific pain related to the title]
- Option B: [Another specific pain]
- Option C: [Third possibility]

**My recommendation:** [Your assessment of most likely pain point]

**Your answer:**
[Wait for user response]

---
```

Repeat this intelligent pattern for all 4 questions:
1. **Pain Point** (as above)
2. **Current Workaround** - Ask "What is the current manual workaround?" with context about why understanding current workflow matters, suggest specific workarounds based on the epic title, recommend most likely workaround
3. **Desired Behavior** - Ask "What is the desired automated behavior?" with context about automation scenarios, suggest specific desired outcomes, recommend ideal automation approach
4. **Expected Impact** - Ask "What is the expected impact? (users affected, time saved, business value)" with context about measuring value, suggest specific impact estimates (users, time, business metrics), recommend expected impact range

At the end:

```markdown
---

**Once you've answered all 4 questions, I'll proceed to Round 2: Scope Definition.**
```

[Store answers as: pain_point, current_workaround, desired_behavior, expected_impact]

---

## Round 2: Scope Definition

**Based on your Round 1 answers, let me analyze the technical scope.**

### Your Task:

Analyze Round 1 answers and provide intelligent context for scope questions.

### Output Format:

```markdown
## Round 2: Scope Definition

Based on your answers, here's my analysis of the technical scope:
- [Synthesize what Round 1 answers suggest about scope]
- [Identify likely components/integrations needed]
- [Flag potential complexity or risks]

Now for 5 scope questions with recommendations:

---

### Question 5: Integrations

**Which existing components will this integrate with?**

**Why this matters:** Integration points are often the highest-risk areas - they determine complexity and potential breaking changes.

**Given "$ARGUMENTS" and your pain point of "[pain_point]", likely integrations:**
- [Component/system 1]: [Why it's relevant]
- [Component/system 2]: [Why it's relevant]
- [Component/system 3]: [Why it's relevant]

**My recommendation:** [Which integrations are critical vs nice-to-have]

**Your answer:**
[Wait for user response]

---
```

Continue this pattern for questions 6-9:
- **Question 6: New Components** - Ask "What new components are needed?" with context about component design principles, suggest specific new components based on integration analysis, recommend component architecture approach
- **Question 7: Data Sources** - Ask "What data sources are involved? (databases, APIs, files, etc.)" with context about data flow complexity, suggest likely data sources based on components, recommend data access patterns
- **Question 8: Edge Cases** - Ask "What are the edge cases to consider?" with context about robustness, predict specific edge cases from scope, recommend which edge cases to handle vs defer
- **Question 9: Non-Goals** - Ask "What are the non-goals? (explicitly out of scope)" with context about scope creep prevention, suggest likely scope boundaries, recommend what to defer to future epics

At the end:

```markdown
---

**Once you've answered all 5 questions, I'll proceed to Round 3: Technical Constraints.**
```

[Store answers as: existing_components, new_components, data_sources, edge_cases, non_goals]

---

## Round 3: Technical Constraints

**Now let's define the technical constraints and requirements.**

### Your Task:

Based on Rounds 1 & 2, analyze technical constraints.

### Output Format:

```markdown
## Round 3: Technical Constraints

Given the scope we've defined, here are the technical considerations:
- [Analyze performance implications based on data sources and components]
- [Identify security concerns based on integrations and data]
- [Note compatibility requirements based on existing components]

Final 3 questions with recommendations:

---

### Question 10: Performance

**What are the performance requirements? (latency, throughput, scale)**

**Why this matters:** Performance requirements drive architecture decisions (caching, async processing, database choice, etc.).

**For "$ARGUMENTS", performance might need:**
- Latency: [Estimate based on use case - e.g., <100ms for UI, <1s for background]
- Throughput: [Estimate based on usage - e.g., 100 req/sec, 1000 events/min]
- Scale: [Estimate based on user base - e.g., 10 concurrent users, 1000 records]

**My recommendation:** [Suggested performance targets with rationale based on pain point and expected impact]

**Your answer:**
[Wait for user response]

---
```

Continue for questions 11-12:
- **Question 11: Security** - Ask "What are the security considerations? (auth, data protection, compliance)" with context about security trade-offs, suggest specific security requirements based on data sources, recommend security measures appropriate to risk level
- **Question 12: Compatibility** - Ask "What are compatibility constraints? (browsers, platforms, APIs, dependencies)" with context about compatibility impact, suggest specific compatibility requirements based on integrations, recommend compatibility approach

At the end:

```markdown
---

**Once you've answered all 3 questions, I'll proceed to consult the workflow pattern library and past epics.**
```

[Store answers as: performance_requirements, security_considerations, compatibility_constraints]

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

## Round 4: Complexity Assessment & Mode Recommendation

**Now analyze the epic complexity to recommend direct vs planning mode.**

### Evaluation Criteria:

Assess each factor (low/medium/high):

1. **Architectural Novelty** - Does this introduce new patterns not in the codebase?
   - Low: Follows existing patterns (CRUD, service methods, standard components)
   - Medium: Adapts existing patterns with minor variations
   - High: Introduces novel architecture or patterns

2. **Cross-Domain Impact** - How many domains affected and how tightly coupled?
   - Low: Single domain (backend only, frontend only, database only)
   - Medium: 2 domains with loose coupling
   - High: 3+ domains with tight coupling requiring careful coordination

3. **Risk Level** - What's the risk if implementation goes wrong?
   - Low: Routine features, easy to rollback, minimal user impact
   - Medium: Important features, moderate rollback complexity
   - High: Security implications, external integrations, breaking changes, performance-critical

4. **Established Patterns** - Are there clear examples in the codebase?
   - High: Multiple similar examples exist (e.g., 5+ CRUD endpoints)
   - Medium: Some similar code exists but needs adaptation
   - Low: No similar patterns, need to establish new conventions

### Complexity Score Calculation:

```
Score = 0
- If architectural_novelty = high: +3
- If architectural_novelty = medium: +1.5
- If cross_domain = high: +3
- If cross_domain = medium: +1.5
- If risk_level = high: +3
- If risk_level = medium: +1.5
- If established_patterns = low: +3
- If established_patterns = medium: +1.5

Complexity Score = Score (0-12, normalize to 0-10)
```

### Mode Recommendation Logic:

```
If Complexity Score >= 6.5: RECOMMEND planning
If Complexity Score < 6.5: RECOMMEND direct
```

**Planning mode triggers (any of these = planning):**
- Architectural novelty = high
- Cross-domain = high AND risk_level = medium+
- Risk_level = high
- Established_patterns = low AND cross-domain = medium+

**Direct mode appropriate (all must be true):**
- Architectural novelty = low or medium
- Cross-domain = low or (medium AND risk_level = low)
- Risk_level = low or medium
- Established_patterns = medium or high

### Output Format:

Analyze the epic and display:

```markdown
## Complexity Assessment

Based on the epic requirements, here's my complexity analysis:

**Architectural Novelty:** [low|medium|high]
[1-2 sentences explaining why - reference specific patterns or novelty]

**Cross-Domain Impact:** [low|medium|high]
[1-2 sentences - which domains affected, coupling level]

**Risk Level:** [low|medium|high]
[1-2 sentences - security/external/breaking change concerns]

**Established Patterns:** [low|medium|high]
[1-2 sentences - reference existing similar code or lack thereof]

---

**Complexity Score:** [X.X]/10

**Recommended Mode:** [direct|planning] [✅|⚠️]

**Reasoning:**
[2-3 sentences explaining the recommendation based on the factors above]

{% if planning mode %}
**Why planning mode:**
- [Primary reason from factors]
- [Secondary reason]
- Suggests generating detailed implementation plan (file-tasks.md) before execution

**You'll need to:**
1. Complete architecture.md
2. Generate detailed file-tasks.md (use /output-style Spec Architect + ask for Phase 5.5)
3. Then run /execute-workflow --planning (or let it auto-select)
{% else %}
**Why direct mode:**
- [Primary reason from factors]
- [Secondary reason]
- Agents can implement directly from briefings and architecture

**You'll need to:**
1. Complete architecture.md
2. Run /execute-workflow --direct (or let it auto-select, no file-tasks.md needed)
{% endif %}
```

Store the following for spec generation:
- `recommended_mode`: "direct" or "planning"
- `estimated_complexity`: score (0-10)
- `architectural_novelty`: "low" | "medium" | "high"
- `cross_domain`: "low" | "medium" | "high"
- `risk_level`: "low" | "medium" | "high"
- `established_patterns`: "low" | "medium" | "high"
- `mode_reasoning`: your 2-3 sentence reasoning

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
- `{{ recommended_mode }}` → "direct" or "planning" (from Round 4)
- `{{ estimated_complexity }}` → Complexity score 0-10 (from Round 4)
- `{{ architectural_novelty }}` → "low"|"medium"|"high" (from Round 4)
- `{{ cross_domain }}` → "low"|"medium"|"high" (from Round 4)
- `{{ risk_level }}` → "low"|"medium"|"high" (from Round 4)
- `{{ established_patterns }}` → "low"|"medium"|"high" (from Round 4)
- `{{ mode_reasoning }}` → 2-3 sentence reasoning for mode recommendation (from Round 4)

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
