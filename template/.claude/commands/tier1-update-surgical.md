---
description: Apply surgical updates to Tier1 workflow projects using update definitions
tags: [tier1, update, maintenance]
---

# Tier1 Workflow Surgical Update System

**Purpose:** Apply targeted updates to registered Tier1 projects while preserving customizations.

**Location:** `~/tier1_workflow_global`

---

## Command Usage

```bash
/tier1-update-surgical [OPTIONS]
```

**Options:**
- `--dry-run` - Preview changes without applying them
- `--project=<name>` - Update only specified project
- `--update-id=<id>` - Apply only specified update ID
- `--force` - Skip idempotent checks (reapply all updates)
- `--validate-only` - Check if updates are already applied

**Examples:**
```bash
/tier1-update-surgical --dry-run
/tier1-update-surgical --project=whisper_hotkeys
/tier1-update-surgical --update-id=agent-failure-reporting-protocol-v1
/tier1-update-surgical --project=ppt_pipeline --dry-run
```

---

## What This Command Does

### Step 1: Load Update Definitions

Read `~/tier1_workflow_global/implementation/update_definitions.json` to get:
- Available updates (id, version, description, priority)
- Update components (files to modify, content to add)
- Idempotent checks (how to detect if already applied)
- Validation rules (keywords to verify)

### Step 2: Load Project Registry

Read `~/tier1_workflow_global/implementation/project_registry.json` to get:
- List of registered projects
- Applied updates per project (from `applied_updates` field)
- Custom modifications per project (from `custom_modifications` field)
- Project workflow version

### Step 3: Filter Updates

For each project:
1. Check `applied_updates` field
2. Filter out already-applied updates (unless `--force`)
3. Show only pending updates

### Step 4: Deploy Subagents

For each project with pending updates:
1. Deploy one surgical update subagent
2. Subagent applies updates using `apply_update.py` script
3. Subagent reports success/failure per update
4. Subagent updates project registry with applied updates

### Step 5: Aggregate Results

Collect results from all subagents:
- Total projects updated
- Total updates applied
- Any failures or blockers
- Updated project registry

---

## Update Types

The system supports multiple update types:

### 1. `append_section`

Adds a section BEFORE a specified marker.

**Use case:** Add new protocol section before checklist.

**Example:**
```json
{
  "type": "append_section",
  "target": ".claude/agent_briefings/backend_implementation.md",
  "marker": "## Post-Implementation Checklist",
  "section_file": "implementation/updates/agent-failure-protocol-backend.md",
  "idempotent_check": "grep -q 'BLOCKER DETECTED' {target}",
  "description": "Add blocker reporting protocol"
}
```

**Behavior:**
- Searches for marker line in target file
- Inserts section content BEFORE marker
- Preserves all existing content
- Skips if idempotent check passes

### 2. `insert_after`

Inserts content AFTER a specific line.

**Use case:** Add import after existing imports.

**Example:**
```json
{
  "type": "insert_after",
  "target": "src/services/email_service.py",
  "pattern": "from sqlalchemy import select",
  "content": "from sqlalchemy.orm import selectinload",
  "idempotent_check": "grep -q 'selectinload' {target}"
}
```

**Behavior:**
- Finds first line matching pattern
- Inserts content on next line
- Preserves indentation
- Skips if idempotent check passes

### 3. `copy_if_missing`

Copies file from template to project (only if doesn't exist).

**Use case:** Add new tool script to project.

**Example:**
```json
{
  "type": "copy_if_missing",
  "target": "tools/detect_simulation_code.py",
  "source": "template/tools/detect_simulation_code.py",
  "idempotent_check": "test -f {target}"
}
```

**Behavior:**
- Checks if target file exists
- If not, copies from source
- Preserves file permissions
- Skips if file already exists

### 4. `patch_line`

Replaces specific lines (diff-style).

**Use case:** Update version number or configuration.

**Example:**
```json
{
  "type": "patch_line",
  "target": "pyproject.toml",
  "old_line": "version = \"1.0.0\"",
  "new_line": "version = \"1.1.0\"",
  "idempotent_check": "grep -q 'version = \"1.1.0\"' {target}"
}
```

**Behavior:**
- Finds exact line match
- Replaces with new line
- Fails if multiple matches (ambiguous)
- Skips if idempotent check passes

---

## Idempotent Checks

Every update component has an idempotent check command. This ensures updates can be run multiple times safely.

**Format:** Shell command that returns exit code 0 if update is already applied.

**Placeholder:** `{target}` is replaced with actual target file path.

**Examples:**

```bash
# Check if text exists in file
grep -q 'BLOCKER DETECTED' .claude/agent_briefings/backend_implementation.md

# Check if file exists
test -f tools/detect_simulation_code.py

# Check if line exists
grep -q 'version = "1.1.0"' pyproject.toml

# Check if import exists
grep -q 'from sqlalchemy.orm import selectinload' src/services/email_service.py
```

**Usage:**
- Run check BEFORE applying update
- If exit code 0 → Update already applied, skip
- If exit code non-zero → Update not applied, proceed

---

## Surgical Update Workflow

### Phase 1: Analysis (Main Agent)

```
1. Read update_definitions.json
2. Read project_registry.json
3. For each project:
   - Load applied_updates field
   - Filter out already-applied updates
   - Identify pending updates
4. Generate execution plan
5. Show summary to user (if interactive)
```

### Phase 2: Execution (Subagents)

```
For each project with pending updates:
  1. Deploy subagent with:
     - Project path
     - Pending updates list
     - Update definitions
  2. Subagent runs apply_update.py for each update
  3. Subagent updates project registry
  4. Subagent reports results
```

### Phase 3: Aggregation (Main Agent)

```
1. Collect subagent results
2. Update project_registry.json:
   - Add update IDs to applied_updates
   - Update last_updated timestamp
3. Generate summary report
4. Validate updates using validation rules
```

---

## Subagent Specification

**Name:** Surgical Update Subagent

**Input:**
- `project_path` - Absolute path to project
- `project_name` - Project name (for logging)
- `pending_updates` - List of update definitions to apply
- `update_definitions_path` - Path to update_definitions.json
- `dry_run` - Boolean (preview mode)

**Output:**
```json
{
  "project": "whisper_hotkeys",
  "status": "success",
  "updates_applied": [
    {
      "update_id": "agent-failure-reporting-protocol-v1",
      "status": "success",
      "components_applied": 3,
      "skipped_components": 0,
      "errors": []
    }
  ],
  "registry_updated": true
}
```

**Responsibilities:**
1. Change to project directory
2. For each update:
   - For each component:
     - Run idempotent check
     - If not applied, apply update
     - Report success/failure
3. Update project registry JSON
4. Return results

---

## apply_update.py Helper Script

**Location:** `~/tier1_workflow_global/template/tools/apply_update.py`

**Usage:**
```bash
python tools/apply_update.py \
  --project-path /path/to/project \
  --update-def update_definitions.json \
  --update-id agent-failure-reporting-protocol-v1 \
  --component-index 0 \
  --dry-run
```

**Parameters:**
- `--project-path` - Project root directory
- `--update-def` - Path to update_definitions.json
- `--update-id` - Update ID to apply
- `--component-index` - Which component to apply (0-based)
- `--dry-run` - Preview mode (don't modify files)

**Output:**
```json
{
  "status": "success",
  "update_id": "agent-failure-reporting-protocol-v1",
  "component_index": 0,
  "component_type": "append_section",
  "target_file": ".claude/agent_briefings/backend_implementation.md",
  "already_applied": false,
  "changes_made": true,
  "error": null
}
```

**Behavior:**
1. Load update definition
2. Extract specified component
3. Run idempotent check
4. If not applied:
   - Apply update based on type
   - Verify success
   - Report result
5. If already applied:
   - Skip update
   - Report "already_applied"

---

## Example Execution

### Command

```bash
/tier1-update-surgical --project=whisper_hotkeys
```

### Output

```
Surgical Update System - Execution Report

Reading update definitions: ~/tier1_workflow_global/implementation/update_definitions.json
Found 1 update definition:
  - agent-failure-reporting-protocol-v1 (priority: high)

Reading project registry: ~/tier1_workflow_global/implementation/project_registry.json
Found 5 registered projects

Filtering updates for project: whisper_hotkeys
  Applied updates: []
  Pending updates: [agent-failure-reporting-protocol-v1]

Deploying subagent for project: whisper_hotkeys
  Project path: /home/andreas-spannbauer/whisper_hotkeys
  Updates to apply: 1
  Components to apply: 3

Subagent execution started...

Component 1/3: append_section
  Target: .claude/agent_briefings/backend_implementation.md
  Idempotent check: grep -q 'BLOCKER DETECTED' .claude/agent_briefings/backend_implementation.md
  Status: Not applied, proceeding...
  Result: SUCCESS (section added before marker)

Component 2/3: append_section
  Target: .claude/agent_briefings/project_architecture.md
  Idempotent check: grep -q 'BLOCKER DETECTED' .claude/agent_briefings/project_architecture.md
  Status: Not applied, proceeding...
  Result: SUCCESS (section added before marker)

Component 3/3: copy_if_missing
  Target: tools/detect_simulation_code.py
  Source: ~/tier1_workflow_global/template/tools/detect_simulation_code.py
  Idempotent check: test -f tools/detect_simulation_code.py
  Status: Not applied, proceeding...
  Result: SUCCESS (file copied)

Updating project registry...
  Added to applied_updates: agent-failure-reporting-protocol-v1
  Updated last_updated: 2025-10-24T11:45:00Z

Validating updates...
  Required keywords found: ✓
  All target files updated: ✓

Summary:
  Projects processed: 1
  Updates applied: 1
  Components applied: 3
  Errors: 0

whisper_hotkeys is now up to date with agent-failure-reporting-protocol-v1
```

---

## Dry Run Mode

Use `--dry-run` to preview changes without modifying files.

```bash
/tier1-update-surgical --dry-run
```

**Behavior:**
- All analysis runs normally
- Idempotent checks run normally
- File operations are SIMULATED (not executed)
- Reports show "WOULD apply" instead of "Applied"
- Registry is NOT updated

**Example output:**
```
[DRY RUN MODE - No changes will be made]

Component 1/3: append_section
  Target: .claude/agent_briefings/backend_implementation.md
  Status: Not applied
  Result: WOULD ADD section (234 lines) before marker "## Post-Implementation Checklist"
```

---

## Validation Rules

Each update can specify validation rules to verify success:

```json
"validation": {
  "required_keywords": ["BLOCKER DETECTED", "No Improvisation When Blocked"],
  "files_to_check": [
    ".claude/agent_briefings/backend_implementation.md",
    ".claude/agent_briefings/project_architecture.md"
  ]
}
```

**Validation process:**
1. For each file in `files_to_check`:
2. For each keyword in `required_keywords`:
3. Verify keyword exists in file
4. Report validation success/failure

---

## Error Handling

### Idempotent Check Fails

If idempotent check command fails (non-zero exit, not just "not applied"):
- Report error
- Skip component
- Continue with next component
- Mark update as "partial success"

### File Not Found

If target file doesn't exist:
- Report error
- Skip component
- Continue with next component
- Suggest creating missing file structure

### Marker Not Found

If marker (for `append_section`) doesn't exist:
- Report error
- Skip component
- Continue with next component
- Suggest checking file structure

### Ambiguous Pattern

If pattern matches multiple lines (for `patch_line`, `insert_after`):
- Report error
- Skip component
- Suggest making pattern more specific

---

## Registry Update Logic

After successful update application:

```python
# Load project registry
registry = json.load("project_registry.json")

# Find project
project = registry["projects"].find(name=project_name)

# Add update ID to applied_updates (if not already there)
if update_id not in project["applied_updates"]:
    project["applied_updates"].append(update_id)

# Update timestamp
project["last_updated"] = datetime.now().isoformat()

# Save registry
json.dump(registry, "project_registry.json")
```

---

## Success Criteria

This command succeeds when:

1. All pending updates are identified correctly
2. Idempotent checks prevent duplicate applications
3. All components apply successfully
4. Project registry is updated correctly
5. Validation rules pass
6. No existing content is damaged
7. Custom modifications are preserved

---

## Common Issues

### Issue: "Update already applied but file content missing"

**Cause:** Registry shows update applied but idempotent check fails.

**Solution:**
- Use `--force` to reapply update
- Manually verify file content
- Check if file was rolled back by git

### Issue: "Marker not found in target file"

**Cause:** Target file structure changed (custom modifications).

**Solution:**
- Check target file for marker existence
- Update marker in update definition
- Manually apply update if necessary

### Issue: "Idempotent check command not found"

**Cause:** Check command uses tool not available in project.

**Solution:**
- Update check command to use available tools
- Install missing tool in project

---

## Best Practices

### Creating Update Definitions

1. Always include idempotent checks
2. Use specific markers (not generic ones)
3. Test on reference project first
4. Document why update is needed
5. Use high priority for critical fixes
6. Include validation rules

### Running Updates

1. Always run `--dry-run` first
2. Review changes before applying
3. Update one project at a time (for testing)
4. Commit changes after successful update
5. Verify functionality after update
6. Update template hash if template changed

### Maintaining Registry

1. Keep `applied_updates` field accurate
2. Document custom modifications
3. Update `last_updated` timestamp
4. Sync registry across machines
5. Backup registry before mass updates

---

## Integration with Other Commands

### /tier1-check-versions

Check which updates are pending:
```bash
/tier1-check-versions
```

Shows:
- Current workflow version per project
- Applied updates per project
- Pending updates per project

### Batch Updates

To apply updates to all projects at once:
```bash
/tier1-update-surgical --dry-run
/tier1-update-surgical
```

### /tier1-registry-sync

Sync registry after manual changes:
```bash
/tier1-registry-sync
```

Discovers projects, verifies registry accuracy.

---

## Subagent Prompt Template

```markdown
You are a Surgical Update Subagent for Tier1 Workflow.

**Project:** {project_name}
**Project Path:** {project_path}
**Updates to Apply:** {update_ids}

**Your Task:**

For each update in {update_ids}:
1. Read update definition from {update_definitions_path}
2. For each component in update:
   a. Run idempotent check command
   b. If exit code non-zero (not applied):
      - Apply update using apply_update.py script
      - Verify success
   c. If exit code 0 (already applied):
      - Skip component
      - Report "already applied"
3. Update project registry JSON:
   - Add update ID to applied_updates
   - Update last_updated timestamp
4. Return results JSON

**Tools:**
- Use apply_update.py script for all file operations
- Use Bash for idempotent checks
- Use Read/Write for registry updates

**Output Format:**
```json
{
  "project": "{project_name}",
  "status": "success|partial|failure",
  "updates_applied": [...],
  "registry_updated": true|false
}
```

**Important:**
- NEVER modify files without idempotent check
- PRESERVE all existing content
- RESPECT custom modifications
- REPORT all errors (don't skip silently)

**Execute now.**
```

---

## Implementation Checklist

Before marking this command complete:

- [ ] Update definitions file created
- [ ] Project registry schema updated
- [ ] apply_update.py script created
- [ ] Command file (this file) created
- [ ] Idempotent checks tested
- [ ] Dry run mode tested
- [ ] Subagent prompt tested
- [ ] Registry update logic tested
- [ ] Validation rules tested
- [ ] Error handling tested
- [ ] Documentation complete

---

## Summary

The Surgical Update System enables:

- Targeted updates to registered projects
- Idempotent operations (safe to run multiple times)
- Preservation of custom modifications
- Automated validation
- Parallel execution (multiple projects)
- Audit trail (registry tracks applied updates)

**Use this command when:** You have a fix/enhancement that needs to be applied to multiple projects without manual intervention.

**Next steps:** Create update definitions for common fixes, test on reference project, roll out globally.
