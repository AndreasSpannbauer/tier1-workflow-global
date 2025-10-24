# tier1-init-claude-md Command Implementation

**Date:** 2025-10-22
**Status:** Complete
**Type:** Slash Command

---

## Overview

Implemented `/tier1-init-claude-md` command that intelligently inserts workflow documentation sections into project CLAUDE.md files.

## Files Created

### 1. Template Sections Document

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/implementation/architecture/CLAUDE_WORKFLOW_SECTIONS.md`

**Size:** 146 lines

**Contents:**
- Tier1 Workflow Section (standard workflow)
- V6 Workflow Section (enhanced workflow with specialized agents)

Each section includes:
- Quick start guide
- Workflow phases overview
- Key features list
- Directory structure
- Prerequisites
- References to detailed documentation

### 2. Slash Command

**Location:** `/home/andreas-spannbauer/tier1_workflow_global/template/.claude/commands/tier1-init-claude-md.md`

**Size:** 269 lines

**Allowed Tools:** Read, Edit, Write, Bash

---

## Features Implemented

### 1. Auto-Detection

The command automatically detects project type (Tier1 vs V6) by checking for:

**V6 Indicators:**
- `.claude/commands/workflow/execute-workflow.md`
- `.claude/agents/workflow-v6-agents/` directory
- `tools/workflow_utilities_v6/` directory

**Default:** If no V6 indicators found, assumes Tier1

### 2. Idempotent Operation

Safe to run multiple times:
- Uses HTML comment markers: `<!-- BEGIN WORKFLOW SECTION -->` and `<!-- END WORKFLOW SECTION -->`
- Checks if section exists before inserting
- Requires `--force` flag to replace existing section
- Won't accidentally create duplicates

### 3. Safety Features

**Backup Creation:**
- Always creates backup before modification
- Format: `CLAUDE.md.backup-YYYYMMDD-HHMMSS`
- Timestamp ensures no overwrites

**Validation:**
- Verifies CLAUDE.md exists before proceeding
- Provides clear error message if missing
- Suggests correct file location

**Dry-Run Mode:**
- Preview changes without modification
- Shows operation type (append vs replace)
- Displays project type and section size
- Safe for testing

### 4. Force Mode

Override existing sections:
- Use `--force` to replace existing workflow section
- Can combine with `--dry-run` for preview
- Useful for updating workflow documentation

---

## Command Interface

### Basic Usage

```bash
# Auto-detect and insert section
/tier1-init-claude-md

# Preview what would change
/tier1-init-claude-md --dry-run

# Force replace existing section
/tier1-init-claude-md --force

# Preview force replace
/tier1-init-claude-md --dry-run --force
```

### Arguments

- `--dry-run` - Preview changes without modifying files
- `--force` - Replace existing workflow section

### Exit Codes

- `0` - Success (or dry-run preview)
- `1` - Error (CLAUDE.md not found, or section exists without --force)

---

## Workflow Steps

### Step 1: Parse Arguments
- Detect `--dry-run` and `--force` flags
- Set mode variables
- Display project directory

### Step 2: Detect Project Type
- Check for V6 indicators
- Default to Tier1 if none found
- Display detected type

### Step 3: Verify CLAUDE.md Exists
- Check for CLAUDE.md in project root
- Exit with error if not found
- Provide guidance on creating CLAUDE.md

### Step 4: Read Template Sections
- Read template file using Read tool
- Extract appropriate section (Tier1 or V6)
- Prepare content for insertion

### Step 5: Check for Existing Section
- Search for workflow section markers
- Determine if append or replace operation
- Check force mode if section exists

### Step 6: Create Backup
- Generate timestamp
- Copy CLAUDE.md to backup file
- Skip in dry-run mode

### Step 7: Insert or Update Section
- **Append:** Use Edit tool to add section to end
- **Replace:** Use Edit tool to replace between markers
- Skip in dry-run mode (just preview)

### Step 8: Report Success
- Display operation performed
- Show project type
- Provide backup location
- Suggest git diff command
- Show restore command

---

## Output Format

### Successful Insertion

```
📁 Project: /home/user/project

🔍 Detecting project type...
   ℹ️  No V6 indicators found - assuming Tier1

📊 Project Type: Tier1

✅ Found: CLAUDE.md

🔍 Checking for existing workflow section...
   ✅ No existing workflow section found

💾 Creating backup...
   ✅ Backup created: CLAUDE.md.backup-20251022-163045

✅ Workflow section updated successfully

   📝 Operation: Appended new section
   📊 Project Type: Tier1
   💾 Backup: CLAUDE.md.backup-20251022-163045

📄 Review changes:
   git diff CLAUDE.md

🎯 To restore backup if needed:
   cp CLAUDE.md.backup-20251022-163045 CLAUDE.md
```

### V6 Detection

```
🔍 Detecting project type...
   ✅ Found: .claude/commands/workflow/execute-workflow.md (V6 indicator)

📊 Project Type: V6
```

### Section Already Exists

```
🔍 Checking for existing workflow section...
   ℹ️  Workflow section already exists in CLAUDE.md

   ⚠️  Use --force to replace existing section
   ⚠️  Use --dry-run to preview changes
```

### Dry-Run Mode

```
🔍 DRY RUN MODE - No changes will be made

📋 DRY RUN - Changes that would be applied:

   Operation: APPEND workflow section to end of file
   Target: End of CLAUDE.md

   Project Type: Tier1
   Section Size: [calculated from template]

To apply changes, run without --dry-run flag
```

### Error: CLAUDE.md Missing

```
❌ CLAUDE.md not found: /home/user/project/CLAUDE.md

Expected location: /home/user/project/CLAUDE.md

Action required: Create CLAUDE.md in your project root before running this command.
```

---

## Template Section Content

### Tier1 Section Includes

- Quick Start commands
- Workflow phases (4 phases)
- Key features (6 features)
- Directory structure diagram
- Prerequisites list
- References to integration guides

### V6 Section Includes

- Quick Start commands (with `/workflow/` prefix)
- Workflow phases (4 phases)
- V6-specific features
- Enhanced directory structure (including agents and tools)
- V6 prerequisites
- References to V6 documentation

---

## Implementation Approach

### Bash Components

- Argument parsing
- Project type detection (file existence checks)
- CLAUDE.md verification
- Backup creation
- Status reporting

### Claude Code Components

**Read Tool:**
- Read template sections file
- Extract appropriate section based on project type

**Edit Tool:**
- Replace existing section (between markers)
- Append new section (to end of file)

**Write Tool:**
- Fallback if Edit fails (creates new file)

### Markers for Idempotency

```markdown
<!-- BEGIN WORKFLOW SECTION -->
[workflow documentation content]
<!-- END WORKFLOW SECTION -->
```

These HTML comment markers:
- Are invisible in rendered markdown
- Enable precise replacement operations
- Prevent duplicate insertions
- Support idempotent updates

---

## Integration with Registry System

This command complements the existing Tier1 commands:

1. **tier1-registry-sync** - Discover and register projects
2. **tier1-check-versions** - Check which projects need updates
3. **tier1-update-all** - Update execute-workflow.md across projects
4. **tier1-init-claude-md** - Update CLAUDE.md documentation (NEW)

### Workflow

```bash
# Step 1: Sync registry to discover projects
/tier1-registry-sync

# Step 2: Check which projects need workflow updates
/tier1-check-versions

# Step 3: Update workflow commands
/tier1-update-all --dry-run
/tier1-update-all

# Step 4: Update CLAUDE.md documentation
cd ~/coding_projects/my_project
/tier1-init-claude-md --dry-run
/tier1-init-claude-md
```

---

## Testing Checklist

### Manual Testing Required

- [ ] Test Tier1 project detection
- [ ] Test V6 project detection
- [ ] Test first-time insertion (append)
- [ ] Test existing section detection
- [ ] Test force replace
- [ ] Test dry-run mode
- [ ] Test backup creation
- [ ] Test error handling (missing CLAUDE.md)
- [ ] Verify markdown rendering
- [ ] Verify markers are invisible in rendered output

### Test Projects

**Tier1 Project:** Any project with standard workflow
**V6 Project:** Project with `.claude/agents/workflow-v6-agents/`

---

## Future Enhancements

### Potential Improvements

1. **Auto-update mode:** Detect outdated workflow sections and offer update
2. **Template versioning:** Track template version in markers
3. **Custom sections:** Support project-specific customizations
4. **Validation:** Verify inserted section is valid markdown
5. **Rollback:** Quick undo command to restore from backup

### Registry Integration

Consider adding to `/tier1-update-all`:
- Optional flag to also update CLAUDE.md sections
- Batch update across all registered projects
- Report which projects need CLAUDE.md updates

---

## References

- **Command File:** `~/tier1_workflow_global/template/.claude/commands/tier1-init-claude-md.md`
- **Template Sections:** `~/tier1_workflow_global/implementation/architecture/CLAUDE_WORKFLOW_SECTIONS.md`
- **Integration Guide:** `~/tier1_workflow_global/implementation/WORKFLOW_INTEGRATION_GUIDE.md`

---

## Summary

Successfully implemented `/tier1-init-claude-md` command with:

✅ Auto-detection of project type (Tier1 vs V6)
✅ Idempotent operation (safe to run multiple times)
✅ Safety features (backup, dry-run, validation)
✅ Clear output format and error messages
✅ Template-based approach for maintainability
✅ HTML comment markers for precise updates

The command is ready for testing and deployment across Tier1 workflow projects.
