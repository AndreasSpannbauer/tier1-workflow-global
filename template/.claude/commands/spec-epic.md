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

## Generate Epic ID

Use bash to find the next epic ID:

```bash
cd /home/andreas-spannbauer/v6-tier1-template

# Find all epic directories and task files
LAST_EPIC=$(find .tasks/backlog .tasks/current .tasks/completed -name "EPIC-*.task.md" -o -name "EPIC-*" -type d 2>/dev/null | \
  sed 's/.*EPIC-\([0-9]*\).*/\1/' | \
  sort -n | \
  tail -1)

# Calculate next ID
NEXT_EPIC=$((${LAST_EPIC:-0} + 1))
EPIC_ID=$(printf "EPIC-%03d" $NEXT_EPIC)

echo "Generated Epic ID: ${EPIC_ID}"
```

Store the EPIC_ID for use in subsequent steps.

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

## Create GitHub Issue

**CRITICAL: GitHub integration is CORE functionality - this is NOT optional**

Use Python to create GitHub issue from the epic:

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
from tools.github_integration.issue_sync_gh import create_github_issue_from_epic

# Get epic details from environment
epic_id = "${EPIC_ID}"
epic_dir = Path("${EPIC_DIR}")

# Create GitHub issue
print(f"\n🔗 Creating GitHub issue for {epic_id}...")
issue_url = create_github_issue_from_epic(epic_id, epic_dir)

if issue_url:
    print(f"✅ GitHub Issue created: {issue_url}")
    print(f"   Issue will be synced with epic status changes")
else:
    print(f"⚠️  GitHub issue creation failed")
    print(f"   Check logs for details (non-blocking)")
    print(f"   You can manually create issue later using:")
    print(f"   python3 -c 'from tools.github_integration.issue_sync_gh import create_github_issue_from_epic; create_github_issue_from_epic(\"{epic_id}\", Path(\"{epic_dir}\"))'")

PYTHON_EOF
```

**What this does:**
1. Reads spec.md and architecture.md from epic directory
2. Extracts summary (problem statement, requirements)
3. Formats as GitHub issue body with proper markdown
4. Creates issue with labels (epic, domain, priority)
5. Updates task.md frontmatter with GitHub metadata:
   - issue_number
   - issue_url
   - sync_enabled: true
   - last_synced timestamp

**Non-blocking:** If GitHub creation fails (network, auth, etc.), logs warning but doesn't block epic creation.

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

Next steps:
1. Review specification: code ${EPIC_DIR}/spec.md
2. Design architecture: code ${EPIC_DIR}/architecture.md
3. Define contracts: code ${EPIC_DIR}/contracts/
4. Break into tasks: /task-create feature "Task title"
5. View epic: /task-get ${EPIC_ID}

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
