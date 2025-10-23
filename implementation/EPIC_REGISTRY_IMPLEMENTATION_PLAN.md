# Epic Registry and Longitudinal Tracking - Implementation Plan

**Related ADR**: ADR-013_EPIC_REGISTRY_AND_LONGITUDINAL_TRACKING.md
**Execution Mode**: Sequential (dependencies between phases)
**Estimated Time**: 16-24 hours across 4 weeks

---

## Overview

This plan implements the Epic Registry system in 6 phases:

1. **Phase 1**: Epic Registry Core (foundation)
2. **Phase 2**: GitHub Integration Hardening (make mandatory)
3. **Phase 3**: Smart Epic Selector (`/execute-workflow next`)
4. **Phase 4**: Integration Planning Phase (Phase 4.5)
5. **Phase 5**: Longitudinal Learning (past epics inform new ones)
6. **Phase 6**: Registry Management Commands (utilities)

**Execution Order**: MUST be sequential (each phase depends on previous)

---

## Phase 1: Epic Registry Core (Week 1, 6-8 hours)

### File 1: `template/tools/epic_registry/__init__.py`

**Action**: CREATE
**Purpose**: Package initialization

```python
"""
Epic Registry - Centralized epic lifecycle tracking system.

Provides:
- Epic state management (defined → prepared → ready → implemented)
- Unique epic ID generation
- Dependency tracking
- Master spec coverage analysis
"""

from .registry_manager import (
    EpicRegistry,
    create_registry,
    load_registry,
    save_registry,
)
from .models import Epic, EpicStatus, EpicDependencies

__all__ = [
    "EpicRegistry",
    "create_registry",
    "load_registry",
    "save_registry",
    "Epic",
    "EpicStatus",
    "EpicDependencies",
]
```

**Testing**: Import package, verify exports available

---

### File 2: `template/tools/epic_registry/models.py`

**Action**: CREATE
**Purpose**: Pydantic models for type-safe epic data

```python
"""
Data models for epic registry system.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class EpicStatus(str, Enum):
    """Epic lifecycle states."""
    DEFINED = "defined"          # spec.md created, not yet prepared
    PREPARED = "prepared"         # file-tasks.md exists
    READY = "ready"               # passed preflight checks
    IMPLEMENTED = "implemented"   # workflow executed successfully
    ARCHIVED = "archived"         # deprecated/cancelled


class EpicDependencies(BaseModel):
    """Epic dependency relationships."""
    blocks: List[str] = Field(default_factory=list, description="Epic IDs this epic blocks")
    blocked_by: List[str] = Field(default_factory=list, description="Epic IDs blocking this epic")
    integrates_with: List[str] = Field(default_factory=list, description="Epic IDs this integrates with")


class Epic(BaseModel):
    """Complete epic metadata."""
    epic_id: str = Field(..., description="Unique epic identifier (e.g., EPIC-001)")
    epic_number: int = Field(..., description="Sequential epic number")
    title: str = Field(..., description="Human-readable epic title")
    slug: str = Field(..., description="URL-safe slug for directory name")
    status: EpicStatus = Field(..., description="Current lifecycle status")

    # Dates
    created_date: str = Field(..., description="Date epic was created (YYYY-MM-DD)")
    prepared_date: Optional[str] = Field(None, description="Date file-tasks.md was created")
    implemented_date: Optional[str] = Field(None, description="Date workflow completed")

    # Paths
    directory: str = Field(..., description="Relative path to epic directory")

    # GitHub
    github_issue: Optional[int] = Field(None, description="GitHub issue number")
    github_url: Optional[str] = Field(None, description="GitHub issue URL")

    # Implementation stats
    execution_mode: Optional[str] = Field(None, description="sequential or parallel")
    files_created: Optional[int] = Field(None, description="Number of files created")
    files_modified: Optional[int] = Field(None, description="Number of files modified")

    # Knowledge
    post_mortem: Optional[str] = Field(None, description="Path to post-mortem report")
    integration_notes: Optional[str] = Field(None, description="How this epic integrates")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    dependencies: EpicDependencies = Field(default_factory=EpicDependencies)


class MasterSpecCoverage(BaseModel):
    """Master specification coverage tracking."""
    total_requirements: int = Field(..., description="Total requirements in master spec")
    covered_by_epics: int = Field(..., description="Requirements covered by epics")
    coverage_percentage: float = Field(..., description="Coverage as percentage")
    uncovered_requirements: List[str] = Field(default_factory=list, description="Requirements not yet covered")


class RegistryStatistics(BaseModel):
    """Aggregate registry statistics."""
    total_epics: int = 0
    defined: int = 0
    prepared: int = 0
    ready: int = 0
    implemented: int = 0
    archived: int = 0


class EpicRegistryData(BaseModel):
    """Root epic registry structure."""
    schema_version: str = "2.0"
    project_name: str = Field(..., description="Project name")
    master_spec_path: str = Field(default=".tasks/master_spec.md")
    created: str = Field(..., description="Registry creation timestamp (ISO 8601)")
    last_updated: str = Field(..., description="Last modification timestamp (ISO 8601)")
    github_repo: Optional[str] = Field(None, description="GitHub repo (user/repo)")
    next_epic_number: int = Field(1, description="Next epic number to assign")
    statistics: RegistryStatistics = Field(default_factory=RegistryStatistics)
    epics: List[Epic] = Field(default_factory=list)
    master_spec_coverage: Optional[MasterSpecCoverage] = Field(None)
```

**Testing**: Create Epic instance, verify validation works

---

### File 3: `template/tools/epic_registry/registry_manager.py`

**Action**: CREATE
**Purpose**: CRUD operations for epic registry

```python
"""
Epic Registry Manager - CRUD operations for epic lifecycle tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import Epic, EpicRegistryData, EpicStatus, RegistryStatistics

logger = logging.getLogger(__name__)


class EpicRegistry:
    """
    Epic Registry manager for project-level epic tracking.

    Usage:
        registry = EpicRegistry.load(Path(".tasks/epic_registry.json"))
        epic = registry.get_epic("EPIC-001")
        registry.update_epic_status("EPIC-001", EpicStatus.IMPLEMENTED)
        registry.save()
    """

    def __init__(self, data: EpicRegistryData, file_path: Path):
        self.data = data
        self.file_path = file_path

    @classmethod
    def load(cls, file_path: Path) -> "EpicRegistry":
        """Load registry from JSON file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Registry not found: {file_path}")

        with open(file_path) as f:
            data_dict = json.load(f)

        data = EpicRegistryData(**data_dict)
        return cls(data, file_path)

    @classmethod
    def create(cls, project_name: str, file_path: Path, github_repo: Optional[str] = None) -> "EpicRegistry":
        """Create new epic registry."""
        now = datetime.utcnow().isoformat() + "Z"

        data = EpicRegistryData(
            project_name=project_name,
            created=now,
            last_updated=now,
            github_repo=github_repo,
        )

        registry = cls(data, file_path)
        registry.save()
        return registry

    def save(self) -> None:
        """Save registry to JSON file."""
        # Update statistics before saving
        self._recalculate_statistics()

        # Update last_updated timestamp
        self.data.last_updated = datetime.utcnow().isoformat() + "Z"

        # Write JSON
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.data.model_dump(), f, indent=2)

        logger.info(f"Registry saved: {self.file_path}")

    def _recalculate_statistics(self) -> None:
        """Recalculate epic statistics."""
        stats = RegistryStatistics()
        stats.total_epics = len(self.data.epics)

        for epic in self.data.epics:
            if epic.status == EpicStatus.DEFINED:
                stats.defined += 1
            elif epic.status == EpicStatus.PREPARED:
                stats.prepared += 1
            elif epic.status == EpicStatus.READY:
                stats.ready += 1
            elif epic.status == EpicStatus.IMPLEMENTED:
                stats.implemented += 1
            elif epic.status == EpicStatus.ARCHIVED:
                stats.archived += 1

        self.data.statistics = stats

    def add_epic(self, epic: Epic) -> None:
        """Add new epic to registry."""
        # Verify epic_id is unique
        if self.get_epic(epic.epic_id):
            raise ValueError(f"Epic {epic.epic_id} already exists in registry")

        # Verify epic_number matches next_epic_number
        if epic.epic_number != self.data.next_epic_number:
            raise ValueError(
                f"Epic number mismatch: expected {self.data.next_epic_number}, got {epic.epic_number}"
            )

        self.data.epics.append(epic)
        self.data.next_epic_number += 1
        logger.info(f"Added epic: {epic.epic_id}")

    def get_epic(self, epic_id: str) -> Optional[Epic]:
        """Get epic by ID."""
        for epic in self.data.epics:
            if epic.epic_id == epic_id:
                return epic
        return None

    def update_epic_status(self, epic_id: str, status: EpicStatus) -> None:
        """Update epic status with automatic timestamp updates."""
        epic = self.get_epic(epic_id)
        if not epic:
            raise ValueError(f"Epic not found: {epic_id}")

        old_status = epic.status
        epic.status = status

        # Update timestamps based on status transitions
        today = datetime.utcnow().date().isoformat()

        if status == EpicStatus.PREPARED and not epic.prepared_date:
            epic.prepared_date = today
        elif status == EpicStatus.IMPLEMENTED and not epic.implemented_date:
            epic.implemented_date = today

        logger.info(f"Updated {epic_id} status: {old_status} → {status}")

    def update_epic_github(self, epic_id: str, issue_number: int, issue_url: str) -> None:
        """Update epic GitHub metadata."""
        epic = self.get_epic(epic_id)
        if not epic:
            raise ValueError(f"Epic not found: {epic_id}")

        epic.github_issue = issue_number
        epic.github_url = issue_url
        logger.info(f"Updated {epic_id} GitHub issue: #{issue_number}")

    def get_epics_by_status(self, status: EpicStatus) -> List[Epic]:
        """Get all epics with given status."""
        return [e for e in self.data.epics if e.status == status]

    def get_next_epic_number(self) -> int:
        """Get next epic number to assign."""
        return self.data.next_epic_number

    def generate_epic_id(self) -> str:
        """Generate next epic ID."""
        return f"EPIC-{self.data.next_epic_number:03d}"


# Convenience functions for quick access

def load_registry(project_dir: Optional[Path] = None) -> EpicRegistry:
    """Load registry from project directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    registry_file = project_dir / ".tasks" / "epic_registry.json"
    return EpicRegistry.load(registry_file)


def create_registry(project_name: str, project_dir: Optional[Path] = None, github_repo: Optional[str] = None) -> EpicRegistry:
    """Create new registry in project directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    registry_file = project_dir / ".tasks" / "epic_registry.json"
    return EpicRegistry.create(project_name, registry_file, github_repo)


def save_registry(registry: EpicRegistry) -> None:
    """Save registry."""
    registry.save()
```

**Testing**:
```python
# Create test registry
registry = EpicRegistry.create("test_project", Path("/tmp/test"))

# Add epic
epic = Epic(
    epic_id="EPIC-001",
    epic_number=1,
    title="Test Epic",
    slug="test-epic",
    status=EpicStatus.DEFINED,
    created_date="2025-10-23",
    directory=".tasks/backlog/EPIC-001-test-epic",
    tags=["backend"],
)
registry.add_epic(epic)

# Update status
registry.update_epic_status("EPIC-001", EpicStatus.PREPARED)

# Save
registry.save()

# Reload and verify
registry2 = EpicRegistry.load(Path("/tmp/test/.tasks/epic_registry.json"))
assert registry2.get_epic("EPIC-001").status == EpicStatus.PREPARED
```

---

### File 4: `template/.tasks/templates/epic_registry.json.j2`

**Action**: CREATE
**Purpose**: Template for new epic registries

```json
{
  "schema_version": "2.0",
  "project_name": "{{ project_name }}",
  "master_spec_path": ".tasks/master_spec.md",
  "created": "{{ created_timestamp }}",
  "last_updated": "{{ created_timestamp }}",
  "github_repo": "{{ github_repo }}",
  "next_epic_number": 1,
  "statistics": {
    "total_epics": 0,
    "defined": 0,
    "prepared": 0,
    "ready": 0,
    "implemented": 0,
    "archived": 0
  },
  "epics": [],
  "master_spec_coverage": null
}
```

**Testing**: Verify valid JSON, use in initialization script

---

### File 5: `template/.claude/commands/epic-registry-init.md`

**Action**: CREATE
**Purpose**: Initialize epic registry in a project

```markdown
---
description: "Initialize epic registry in current project"
allowed-tools: [Read, Write, Bash]
---

# Initialize Epic Registry

Creates `.tasks/epic_registry.json` for epic lifecycle tracking.

---

## Step 1: Verify Project Structure

```bash
if [ ! -d ".tasks" ]; then
  echo "❌ .tasks directory not found"
  echo "   This command must be run from project root"
  exit 1
fi

if [ -f ".tasks/epic_registry.json" ]; then
  echo "⚠️  Epic registry already exists"
  echo "   .tasks/epic_registry.json"
  echo ""
  echo "Delete it first if you want to re-initialize:"
  echo "  rm .tasks/epic_registry.json"
  exit 1
fi
```

---

## Step 2: Detect Project Information

```bash
# Get project name from directory
PROJECT_NAME=$(basename "$PWD")

# Detect GitHub repo (if git remote exists)
GITHUB_REPO=""
if git remote get-url origin &> /dev/null; then
  REMOTE_URL=$(git remote get-url origin)
  # Extract user/repo from URL
  GITHUB_REPO=$(echo "$REMOTE_URL" | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | sed 's/.*github.com[:/]\(.*\)/\1/')
fi

echo "Project name: $PROJECT_NAME"
echo "GitHub repo: ${GITHUB_REPO:-<not detected>}"
echo ""
```

---

## Step 3: Create Registry

```bash
python3 << 'EOF'
import sys
from pathlib import Path
from datetime import datetime

# Add tools to path
sys.path.insert(0, str(Path.home() / "tier1_workflow_global" / "template"))

from tools.epic_registry import create_registry
import os

project_name = os.environ.get("PROJECT_NAME", "unknown")
github_repo = os.environ.get("GITHUB_REPO") or None

registry = create_registry(project_name, Path.cwd(), github_repo)

print(f"✅ Epic registry created")
print(f"   File: .tasks/epic_registry.json")
print(f"   Project: {project_name}")
if github_repo:
    print(f"   GitHub: {github_repo}")

EOF
```

---

## Step 4: Scan for Existing Epics (Optional)

```bash
echo ""
echo "Scanning for existing epics..."
echo ""

# Find epic directories
EPIC_DIRS=$(find .tasks/backlog .tasks/current .tasks/completed -name "EPIC-*" -type d 2>/dev/null | sort)

if [ -z "$EPIC_DIRS" ]; then
  echo "No existing epics found (empty project)"
else
  echo "Found existing epics:"
  echo "$EPIC_DIRS"
  echo ""
  echo "⚠️  To import these epics into the registry, run:"
  echo "   /epic-registry-sync"
fi

echo ""
```

---

## Completion

```
✅ Epic registry initialized

File: .tasks/epic_registry.json

Next steps:
  1. Import existing epics: /epic-registry-sync
  2. Create first epic: /spec-epic "Epic Title"
  3. View registry status: /epic-registry-status
```

---

## Notes

- Registry is automatically updated by `/spec-epic` and `/execute-workflow`
- Use `/epic-registry-sync` to fix inconsistencies
- Registry is JSON for programmatic access (Python, jq)
```

**Testing**: Run in test project, verify JSON created

---

### File 6: Modify `template/.claude/commands/spec-epic.md`

**Action**: MODIFY
**Purpose**: Integrate with epic registry

**Changes**:

1. **After "Generate Epic ID" section (line 244)**, replace with:

```markdown
## Generate Epic ID from Registry

Use epic registry to get next unique epic ID:

```bash
# Load registry and generate ID
NEXT_EPIC_INFO=$(python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "tier1_workflow_global" / "template"))

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

Store EPIC_ID and EPIC_NUMBER for use in subsequent steps.
```

2. **After "Create GitHub Issue" section (line 428)**, add:

```markdown
## Add Epic to Registry

Add the newly created epic to the registry:

```bash
python3 << 'PYTHON_EOF'
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / "tier1_workflow_global" / "template"))

from tools.epic_registry import load_registry
from tools.epic_registry.models import Epic, EpicStatus, EpicDependencies

registry = load_registry()

# Create epic object
epic = Epic(
    epic_id="${EPIC_ID}",
    epic_number=${EPIC_NUMBER},
    title="${TITLE}",
    slug="${EPIC_SLUG}",
    status=EpicStatus.DEFINED,
    created_date=datetime.utcnow().date().isoformat(),
    directory="${EPIC_DIR}",
    github_issue=${issue_number if issue_url else None},
    github_url="${issue_url}" if "${issue_url}" else None,
    tags=["${domain}"],
    dependencies=EpicDependencies(),
)

# Add to registry
registry.add_epic(epic)
registry.save()

print(f"✅ Epic added to registry: {epic.epic_id}")

PYTHON_EOF
```
```

3. **Update final "Display Completion" section** to show registry status:

```markdown
## Display Completion

```
✅ Epic created: ${EPIC_ID}
📁 Location: ${EPIC_DIR}
📊 Registry: .tasks/epic_registry.json (updated)

Created files:
- spec.md (WHAT/WHY - user scenarios, requirements, contracts)
- architecture.md (HOW - system design, components)
- task.md (workflow metadata)
- contracts/ (contract definitions)
- implementation-details/ (ADRs, technical docs)
- research/ (spikes, investigations)

🔗 GitHub Issue: [URL from creation step]
📋 Registry Status: DEFINED

Next steps:
1. Review specification: code ${EPIC_DIR}/spec.md
2. Design architecture: code ${EPIC_DIR}/architecture.md
3. Generate implementation plan (auto via Spec Architect output style)
4. View registry: /epic-registry-status
5. Execute epic: /execute-workflow ${EPIC_ID}
```
```

**Testing**: Create epic, verify registry updated

---

## Phase 1 Testing Checklist

- [ ] Create test project with `.tasks/` directory
- [ ] Run `/epic-registry-init`
- [ ] Verify `.tasks/epic_registry.json` created
- [ ] Run `/spec-epic "Test Epic 1"`
- [ ] Verify epic added to registry with EPIC-001
- [ ] Run `/spec-epic "Test Epic 2"`
- [ ] Verify epic added to registry with EPIC-002 (no collision)
- [ ] Check registry statistics updated
- [ ] Verify next_epic_number incremented

---

## Phase 2: GitHub Integration Hardening (Week 1-2, 3-4 hours)

### File 7: Modify `template/tools/github_integration/issue_sync_gh.py`

**Action**: MODIFY
**Purpose**: Add blocking mode for mandatory GitHub integration

**Changes**:

1. **Add new function at end of file** (around line 200):

```python
def create_github_issue_from_epic_blocking(epic_id: str, epic_dir: Path) -> str:
    """
    Create GitHub Issue from epic (BLOCKING mode - raises on failure).

    Unlike create_github_issue_from_epic(), this function RAISES exceptions
    instead of returning None. Use for mandatory GitHub integration.

    Args:
        epic_id: Epic identifier (e.g., "EPIC-007")
        epic_dir: Path to epic directory

    Returns:
        issue_url (guaranteed to be non-None)

    Raises:
        FileNotFoundError: If epic artifacts missing
        GitHubCLIError: If gh CLI fails
        RuntimeError: If gh CLI not authenticated

    Example:
        >>> url = create_github_issue_from_epic_blocking("EPIC-007", epic_dir)
        >>> # url is guaranteed to be valid, or exception was raised
    """
    # Check gh CLI authentication first
    import subprocess

    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "GitHub CLI not authenticated. Run: gh auth login"
            )
    except FileNotFoundError:
        raise RuntimeError(
            "GitHub CLI not found. Install from: https://cli.github.com/"
        )

    # Now call normal creation (will raise on error)
    url = create_github_issue_from_epic(epic_id, epic_dir)

    if url is None:
        # Should not happen, but defensive check
        raise RuntimeError(
            f"GitHub issue creation returned None for {epic_id}"
        )

    return url
```

**Testing**: Call with invalid epic_dir, verify exception raised

---

### File 8: Modify `template/.claude/commands/spec-epic.md`

**Action**: MODIFY
**Purpose**: Make GitHub integration mandatory

**Changes**:

1. **Replace "Create GitHub Issue" section** (around line 376) with:

```markdown
## Create GitHub Issue (MANDATORY)

**CRITICAL: GitHub integration is MANDATORY - failures will block epic creation**

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

# Success - export URL for use in next steps
import os
os.environ["GITHUB_ISSUE_URL"] = issue_url

PYTHON_EOF

# Check exit code
if [ $? -ne 0 ]; then
  echo ""
  echo "======================================================================"
  echo "❌ Epic creation aborted due to GitHub integration failure"
  echo "======================================================================"
  exit 1
fi

# Extract issue URL from Python output
GITHUB_ISSUE_URL=$(echo "$PYTHON_OUTPUT" | grep "https://github.com" | head -1)

echo ""
echo "✅ GitHub issue creation succeeded"
echo "   URL: $GITHUB_ISSUE_URL"
echo ""
```
```

**Testing**: Run without `gh` auth, verify epic creation blocked

---

## Phase 2 Testing Checklist

- [ ] Unauth `gh` CLI: `gh auth logout`
- [ ] Run `/spec-epic "Test"`
- [ ] Verify epic creation BLOCKED with clear error message
- [ ] Re-auth: `gh auth login`
- [ ] Run `/spec-epic "Test Epic 3"`
- [ ] Verify epic created AND GitHub issue created

---

## Phase 3: Smart Epic Selector (Week 2, 4-5 hours)

[Implementation continues for remaining phases...]

---

## Testing Strategy

### Unit Tests
- `test_epic_registry.py` - Registry CRUD operations
- `test_epic_selector.py` - Selection algorithm
- `test_dependency_resolver.py` - Dependency graph

### Integration Tests
- Create 5 epics with dependencies
- Execute `/execute-workflow next` 5 times
- Verify correct order (dependency-respecting)

### End-to-End Test
1. Initialize new project
2. Create 3 epics (EPIC-001, EPIC-002, EPIC-003)
3. Set dependencies: EPIC-003 blocked by EPIC-001, EPIC-002
4. Execute `/execute-workflow next` → should pick EPIC-001 or EPIC-002
5. Execute `/execute-workflow next` → should pick remaining unblocked
6. Execute `/execute-workflow next` → should pick EPIC-003 (now unblocked)

---

## Rollout Plan

### Week 1: Foundation
- Phase 1 + Phase 2 complete
- Test in `email_management_system` project
- Verify GitHub integration working

### Week 2: Smart Selection
- Phase 3 complete
- Test `/execute-workflow next` in email_management_system
- Roll out to `ppt_pipeline` project

### Week 3: Integration Planning
- Phase 4 complete
- Test Phase 4.5 in clinical-eda-pipeline (reference project)
- Verify integration agent provides useful insights

### Week 4: Learning & Utilities
- Phase 5 + Phase 6 complete
- Test full workflow end-to-end
- Document in CLAUDE.md
- Roll out to all Tier 1 projects

---

## Success Metrics

- [ ] Zero epic ID collisions across all projects
- [ ] 100% GitHub issue creation rate
- [ ] `/execute-workflow next` works in 100% of test cases
- [ ] Integration agent identifies 3+ integration points per epic
- [ ] Post-mortem findings appear in next epic planning
- [ ] Coverage tracking shows gaps in master spec implementation
