# Tier1 Workflow Global - Project Instructions

**Repository**: tier1_workflow_global
**Purpose**: Central template and update system for Tier1 workflow across all projects
**Location**: `~/tier1_workflow_global`

---

## Overview

This repository contains:
- **Template files** for Tier1 workflow deployment (`.claude/`, `.tasks/`, `tools/`)
- **Installation script** (`install_tier1_workflow.sh`)
- **Surgical update system** for maintaining deployed projects
- **Agent briefings** with domain-specific patterns
- **Project registry** tracking all Tier1 deployments

---

## 🎯 Primary Use Cases

### 1. Deploy Tier1 Workflow to New Project

Use the **deployment command** (recommended):

```bash
/tier1-deploy ~/path/to/project
```

**Or manually:**

```bash
cd ~/path/to/project
~/tier1_workflow_global/install_tier1_workflow.sh ~/path/to/project --python
```

This installs all workflow files, agents, commands, and tools.

### 2. Update Existing Projects ⭐ DEFAULT METHOD

Use the **surgical update system** to apply updates to deployed projects:

```bash
# Preview updates across all projects
/tier1-update-surgical --dry-run

# Update all projects with new improvements
/tier1-update-surgical

# Update specific project
/tier1-update-surgical --project=whisper_hotkeys

# Apply specific update only
/tier1-update-surgical --update-id=agent-failure-reporting-protocol-v1
```

**Why surgical updates?**
- ✅ **Preserves customizations** - Only adds missing content, never overwrites
- ✅ **Idempotent** - Safe to run multiple times
- ✅ **Tracked** - Registry knows what's applied where
- ✅ **Intelligent** - Respects project-specific improvements
- ✅ **Parallel** - Updates multiple projects simultaneously

### 3. Sync Project Registry

Keep track of all Tier1 deployments:

```bash
/tier1-registry-sync
```

This discovers all projects with Tier1 workflow and updates the registry.

---

## 🏗️ Surgical Update System

### How It Works

1. **Update definitions** in `implementation/update_definitions.json` specify what to update
2. **Content fragments** in `implementation/updates/` contain the actual content
3. **Project registry** in `implementation/project_registry.json` tracks what's applied where
4. **Subagents** apply updates surgically to each project in parallel
5. **Tracking files** (`.tier1_updates.json`) in each project record applied updates

### Update Types

The system supports 4 types of surgical modifications:

1. **`append_section`** - Add content before a marker (e.g., before "## Summary")
2. **`insert_after`** - Insert content after a specific pattern
3. **`copy_if_missing`** - Copy file only if it doesn't exist
4. **`patch_line`** - Replace specific lines (diff-style)

All updates include **idempotent checks** that prevent duplicate application.

### Creating New Updates

To add a new update to the system:

1. **Define the update** in `implementation/update_definitions.json`:

```json
{
  "id": "my-new-feature-v1",
  "version": "1.0.0",
  "date": "2025-10-24",
  "description": "Add my new feature",
  "components": [
    {
      "type": "append_section",
      "target": ".claude/agents/implementation_agent_v1.md",
      "marker": "## Validation",
      "section_file": "updates/my-new-feature-section.md",
      "idempotent_check": "grep -q 'MY_FEATURE_MARKER' {{target}}"
    }
  ]
}
```

2. **Create content fragment** in `implementation/updates/my-new-feature-section.md`

3. **Test with dry-run**:
```bash
/tier1-update-surgical --update-id=my-new-feature-v1 --dry-run
```

4. **Apply to projects**:
```bash
/tier1-update-surgical --update-id=my-new-feature-v1
```

---

## 📁 Repository Structure

```
tier1_workflow_global/
├── install_tier1_workflow.sh          # Installation script
├── template/                           # Template files for deployment
│   ├── .claude/
│   │   ├── commands/                   # Slash commands
│   │   ├── agents/                     # Agent definitions
│   │   └── output-styles/              # Output style templates
│   ├── .tasks/
│   │   └── templates/                  # Task templates
│   └── tools/                          # Validation and utility scripts
│       ├── detect_simulation_code.py   # Simulation detection
│       ├── apply_update.py             # Surgical update engine
│       ├── validate_architecture.py
│       └── validate_contracts.py
├── implementation/                     # Implementation artifacts
│   ├── agent_briefings/                # Domain-specific briefings
│   │   ├── backend_implementation.md   # Backend patterns (FastAPI, etc.)
│   │   ├── project_architecture.md     # Architecture guidelines
│   │   └── CREATION_COMPLETE.md        # Briefing creation guide
│   ├── agents/                         # Agent definitions
│   ├── updates/                        # Update content fragments
│   │   ├── agent-failure-protocol-backend.md
│   │   └── agent-failure-protocol-architecture.md
│   ├── update_definitions.json         # Central update registry
│   ├── project_registry.json           # All Tier1 projects
│   ├── AGENT_FAILURE_REPORTING_PROTOCOL.md
│   └── SURGICAL_UPDATE_SYSTEM_COMPLETE.md
└── CLAUDE.md                           # This file
```

---

## 🔧 Key Features

### Agent Failure Reporting Protocol

**Status**: ✅ Implemented (2025-10-24)
**Update ID**: `agent-failure-reporting-protocol-v1`

Prevents agents from creating mocked/simulated implementations when blocked:
- Agents MUST report blockers using standardized format
- Absolute prohibition on improvisation when fundamentally blocked
- Automated detection script catches simulation patterns
- Integrated into all agent briefings

**Apply to projects:**
```bash
/tier1-update-surgical --update-id=agent-failure-reporting-protocol-v1
```

### Pattern Library Integration

All workflows support pattern library auto-injection via UserPromptSubmit hooks:
- Semantic search for relevant patterns
- Auto-injection of up to 3 patterns per prompt
- Context7 fallback with automatic queue capture
- Extract patterns with `/extract-patterns`

### Project Registry

Tracks all Tier1 deployments:
- Location: `implementation/project_registry.json`
- Tracks: workflow version, applied updates, customizations
- Update with `/tier1-registry-sync`

---

## 📋 Available Updates

### Current Updates

1. **agent-failure-reporting-protocol-v1** (2025-10-24)
   - Priority: High
   - Components: 3 (agent briefings, detection script, documentation)
   - Status: Ready for deployment
   - Apply: `/tier1-update-surgical --update-id=agent-failure-reporting-protocol-v1`

### Future Updates

To create additional updates:
1. Learn from post-mortems and workflow improvements
2. Define update in `update_definitions.json`
3. Create content fragments in `implementation/updates/`
4. Test with `--dry-run` on single project
5. Deploy to all projects

---

## 🚀 Workflow Commands

### Deployment
- `/tier1-deploy [path]` - Deploy to new project
- `/tier1-init-claude-md` - Initialize project CLAUDE.md

### Updates
- `/tier1-update-surgical` - **DEFAULT: Surgical updates to projects**
- `/tier1-check-versions` - Check workflow versions across projects

### Registry
- `/tier1-registry-sync` - Sync project registry
- `/epic-registry-init` - Initialize epic registry in project
- `/epic-registry-status` - Check epic registry status

---

## 🎯 Best Practices

### When Updating Projects

1. **Always use surgical updates** (`/tier1-update-surgical`)
2. **Test first with --dry-run** to preview changes
3. **Update one project first** (`--project=name`) to verify
4. **Review changes** before committing to Git
5. **Update registry** after successful deployment

### When Creating Updates

1. **Make updates idempotent** - Include checks to prevent duplicate application
2. **Preserve customizations** - Use append/insert, not replace
3. **Test thoroughly** - Dry-run on multiple project types
4. **Document clearly** - Update this CLAUDE.md with new features
5. **Version appropriately** - Follow semantic versioning

### When Deploying to New Projects

1. **Initialize Git first** - Projects must be Git repositories
2. **Detect project type** - Let script auto-detect Python/TypeScript/Mixed
3. **Customize output style** - Template creates project-specific version
4. **Initialize epic registry** - Use `/epic-registry-init`
5. **Set output style** - Use `/output-style spec-architect-{project}`

---

## 🔍 Troubleshooting

### "Update already applied" message

This is normal and expected. Surgical updates are idempotent - they check if content already exists before applying. This prevents duplicate application.

### "File not found" during update

Ensure project registry is up to date:
```bash
/tier1-registry-sync
```

Check that project has Tier1 workflow installed:
```bash
ls -la ~/project/.claude/agents/
```

### Changes not appearing in project

Verify update was actually applied:
```bash
cat ~/project/.tier1_updates.json
```

Check if idempotent condition is too strict:
```bash
# Example: Check if grep pattern matches
cd ~/project
grep -q "EXPECTED_PATTERN" target/file.md && echo "Already present"
```

---

## 📚 Related Documentation

- **Surgical Update System**: `implementation/SURGICAL_UPDATE_SYSTEM_COMPLETE.md`
- **Agent Failure Protocol**: `implementation/AGENT_FAILURE_REPORTING_PROTOCOL.md`
- **Update Definitions**: `implementation/update_definitions.json`
- **Project Registry**: `implementation/project_registry.json`

---

## ⚡ Quick Reference

**Deploy new project:**
```bash
/tier1-deploy ~/my-project
```

**Update all projects (surgical, safe):**
```bash
/tier1-update-surgical
```

**Preview updates:**
```bash
/tier1-update-surgical --dry-run
```

**Update single project:**
```bash
/tier1-update-surgical --project=my-project
```

**Check versions:**
```bash
/tier1-check-versions
```

**Sync registry:**
```bash
/tier1-registry-sync
```

---

## 🎓 Philosophy

**Surgical over Destructive**
Updates should enhance, not replace. Preserve local improvements and customizations.

**Idempotent over One-time**
Updates should be safe to run multiple times. Include checks to prevent duplicate application.

**Tracked over Blind**
Know what's applied where. Maintain registry of deployed projects and applied updates.

**Intelligent over Mechanical**
Respect project-specific needs. Don't blindly copy templates - adapt to context.

**Parallel over Sequential**
Update multiple projects simultaneously for speed and efficiency.

---

**Last Updated**: 2025-10-24
**Surgical Update System Version**: 1.0.0
**Agent Failure Reporting Protocol**: Implemented
