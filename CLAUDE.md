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

### Agent Model Configuration

**Status**: ✅ Implemented (2025-10-26)
**Update ID**: `agent-model-cleanup-v1`

Ensures agents use the session model (Sonnet 4.5) to prevent token waste:
- Removes `model:` specifications from agent frontmatter
- Prevents unnecessary Opus token costs
- Ensures consistent behavior with main session
- Automatically verified during new deployments

**Apply to existing projects:**
```bash
/tier1-update-surgical --update-id=agent-model-cleanup-v1
```

**New deployments:** Agent verification runs automatically during `install_tier1_workflow.sh`

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

### Intelligent Planning Mode Selection

**Status**: ✅ Implemented (2025-10-29)
**Feature**: Adaptive execution mode (direct vs planning)

Workflow automatically assesses epic complexity and recommends execution mode:

**Direct Mode (Lightweight):**
- ✅ No detailed task files required (file-tasks.md optional)
- ✅ Agents implement from briefings + architecture
- ✅ Saves 40-60% of tokens for routine features
- ✅ Best for: CRUD operations, established patterns, single-domain changes

**Planning Mode (Detailed):**
- ✅ Requires detailed implementation plan (file-tasks.md)
- ✅ Agents follow prescriptive file-by-file instructions
- ✅ Best for: Novel architecture, high-risk changes, complex cross-domain features

**Complexity Assessment (automatic during /spec-epic):**
- Architectural novelty (low/medium/high)
- Cross-domain impact (low/medium/high)
- Risk level (low/medium/high)
- Established patterns (low/medium/high)
- Complexity score (0-10)

**Mode recommendation displayed in spec.md:**
```markdown
**Recommended Mode:** direct ✅
**Complexity Score:** 3.5/10
**Reasoning:** Follows established EmailService patterns, single backend domain...
```

**Usage:**
```bash
/execute-workflow EPIC-007            # Uses recommended mode (prompts for confirmation)
/execute-workflow EPIC-007 --direct   # Force direct mode
/execute-workflow EPIC-007 --planning # Force planning mode
```

**Token Savings:**
- Routine CRUD epic: ~50% token reduction
- Moderate feature: ~30% token reduction
- Complex/novel feature: Planning mode worth the investment

### GitHub AI Review Integration

**Status**: ✅ Implemented (2025-10-29)
**Update ID**: `github-ai-review-integration-v1`

Automatic GitHub integration with @claude and @codex AI review:
- **@claude mentions:** GitHub Actions workflow responds in 30-60 seconds
- **@codex review:** Optional Codex Cloud integration for inline code review
- **Automatic PR creation:** Phase 5.3 creates feature branch and PR with AI tags
- **Non-blocking:** PR creation failures don't stop workflow execution

**Features:**
- GitHub Actions workflow (`.github/workflows/claude.yml`) triggers on @claude mentions
- PR helper script (`tools/github_integration/pr_with_ai_review.py`) for automation
- Comprehensive setup docs and verification scripts
- Integrated into `/execute-workflow` Phase 5.3

**Setup (one-time per repository):**
```bash
# Generate OAuth token
claude /token

# Add to GitHub Settings → Secrets → Actions
# Secret name: CLAUDE_CODE_OAUTH_TOKEN
# Secret value: [paste token]

# Test in any GitHub issue
@claude Hello! Can you summarize CLAUDE.md?
```

**Apply to projects:**
```bash
/tier1-update-surgical --update-id=github-ai-review-integration-v1
```

**Documentation:** `implementation/GITHUB_AI_REVIEW_INTEGRATION.md`

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

## 📊 Repomap Generation & AI Code Review

**Status**: ✅ Implemented (2025-11-01)
**Update ID**: `repomap-global-v1`
**Source**: email_management_system extraction + 2025 research

Generates focused repository maps for efficient AI code review (ChatGPT, Gemini, Claude) with optional 77% token reduction via Repomix integration.

### Overview

Repository maps package your codebase into AI-friendly formats optimized for external review. The system supports:
- **10 predefined scopes** (backend, frontend, workflow, tests, etc.)
- **Auto-detection** of project type
- **TXT + PDF generation** (automatic compression)
- **Repomix integration** (77% token reduction)
- **PR-specific repomaps** (changed files + dependencies)
- **Full ChatGPT automation** (upload → wait → download → apply patches)

### Quick Start

```bash
# Interactive scope selection
/generate-repomap

# Generate specific scope
/generate-repomap backend

# Generate for AI review
/generate-repomap review-ready

# PR-specific repomap
/generate-pr-repomap 123

# Full ChatGPT automation
/chatgpt-implement EPIC-025 --auto
```

### Available Scopes

**Single Scopes (10):**

1. **`backend`** - Backend code (Python, TypeScript, Go, Rust)
   - Includes: `src/**/*.py`, `api/**/*.ts`, `server/**/*.go`, tests, migrations
   - Use for: Backend architecture review, API design validation

2. **`frontend`** - Frontend code (React, Vue, Svelte, Next.js)
   - Includes: Components, hooks, pages, styles, config
   - Use for: UI/UX review, component architecture

3. **`workflow`** - Tier1 workflow and task management
   - Includes: `.tasks/`, `.claude/`, docs, tools
   - Use for: Workflow system review, epic structure validation

4. **`specs`** - Specifications and documentation
   - Includes: Epic specs, architecture docs, ADRs, README, CLAUDE.md
   - Use for: High-level architecture review, documentation check

5. **`infrastructure`** - Deployment and DevOps
   - Includes: Docker, GitHub Actions, scripts, deployment config
   - Use for: Infrastructure review, CI/CD analysis

6. **`tests`** - Test coverage and patterns
   - Includes: All test files, fixtures, test utilities
   - Use for: Test coverage review, test pattern validation

7. **`complete-backend`** - Complete backend view
   - Includes: Backend code + specs + workflow context
   - Use for: Comprehensive backend assessment

8. **`complete-frontend`** - Complete frontend view
   - Includes: Frontend code + specs + workflow context
   - Use for: Comprehensive frontend assessment

9. **`review-ready`** - Optimized for external AI review
   - Includes: Most relevant files for ChatGPT/Gemini/Claude
   - Use for: Quick external review, getting feedback

10. **`generic`** - Generic project overview
    - Includes: All source code, docs, config
    - Use for: Initial project understanding, broad context

**Scope Combinations (4):**

1. **`full-review`** - Complete codebase review
   - Combines: workflow + backend + frontend
   - Max size: 5MB

2. **`fullstack-review`** - Full-stack application review
   - Combines: backend + frontend + specs
   - Max size: 4MB

3. **`epic-context`** - Context for epic implementation
   - Combines: specs + backend
   - Max size: 3MB

4. **`deployment-ready`** - Deployment validation
   - Combines: infrastructure + backend
   - Max size: 2MB

### Repomix Integration (77% Token Reduction)

**What is Repomix?**
- State-of-the-art codebase packaging tool (2025)
- Tree-sitter based intelligent compression
- Git-aware sorting (changed files first)
- Security scanning (excludes sensitive files)

**Token Reduction:**
- **77-79% fewer tokens** vs glob-based pattern matching
- **Example**: 3.15M tokens → 663K tokens (backend scope)
- **Compression ratio**: 4.41x

**When to use:**
- Sharing with external AI (token limits matter)
- Context window is tight
- 77% reduction is worth 15 seconds

**When to use proven engine:**
- Speed matters (CI/CD pipelines)
- Simplicity preferred
- No Node.js available

**Engine selection:**
```bash
# Default (auto) - tries Repomix, falls back to proven
/generate-repomap backend

# Force proven (glob-based, fast)
python3 tools/generate_scoped_repomap.py --scope backend --engine proven

# Force Repomix (compressed)
python3 tools/generate_scoped_repomap.py --scope backend --engine repomix
```

### ChatGPT Automation

**Full workflow automation** via Playwright MCP:

```bash
# Manual mode (generate package only)
/chatgpt-implement EPIC-025

# Auto mode (full automation)
/chatgpt-implement EPIC-025 --auto
```

**Auto mode workflow:**
1. Generate repomap for EPIC scope
2. Upload files to ChatGPT (repomap + spec + prompt)
3. Wait for response (extended thinking support)
4. Download generated patches
5. Apply patches with `git apply`
6. Display summary

**Prerequisite**: `/setup-chatgpt-browser` (tier1 global command)

### PR-Specific Repomaps

Generate focused repomap for specific pull request:

```bash
/generate-pr-repomap 123
```

**Output includes:**
- Changed files with +/- counts
- File tree context
- Imports/dependencies
- Function/class structure
- Reverse dependencies (files that import changed files)
- Summary statistics

**Output location**: `workspace/pr-exports/PR-123-repomap.txt`

### Project-Specific Customization

Override or extend scopes by creating:
```
tools/repomap_scopes_custom.json
```

**Example:**
```json
{
  "scopes": {
    "hardware-control": {
      "description": "Hardware control layer",
      "include_patterns": [
        "src/hardware/**/*.py",
        "src/daemon/**/*.py"
      ],
      "exclude_patterns": ["**/__pycache__/**"],
      "max_file_size": 100000
    }
  }
}
```

### Output Format

**Directory structure:**
```
repomaps/
└── YYYYMMDD_HHMMSS/
    ├── repomap-backend.txt          # TXT format
    └── repomap-backend.pdf          # PDF format (if enscript/ps2pdf available)
```

**File header:**
```
# Repository Map: email_management_system
# Scope: backend
# Generated: 2025-11-01 10:30:00 UTC
# Files: 586
# Total Size: 2.73 MB
# Tokens: ~663K (77% reduction)
```

### Dependencies

**Required:**
- Python 3.x
- Git

**Optional:**
- `repomix` (77% token reduction) - `npm install -g repomix`
- `enscript` + `ps2pdf` (PDF generation) - `sudo apt install enscript ghostscript`
- `gh` (GitHub CLI for PR repomaps) - GitHub CLI
- `tree` (directory visualization)

### Documentation

**User guides:**
- `tools/REPOMAP_GUIDE.md` - Complete user documentation
- `tools/REPOMIX_INTEGRATION.md` - Repomix setup and usage

**Commands:**
- `/generate-repomap` - Interactive generation
- `/chatgpt-implement` - Full ChatGPT automation
- `/generate-pr-repomap` - PR-specific repomap

### Tips for External AI Review

**ChatGPT prompts** (examples):

```
I'm implementing [FEATURE] and need code review.

Context: [Attached repomap-review-ready.txt]

Please review for:
1. Architectural soundness
2. Best practices compliance
3. Potential bugs or issues
4. Missing edge cases
5. Security concerns

Focus on: [SPECIFIC_AREA]
```

**Token limits:**
- ChatGPT: 20MB text or 512MB PDF
- Gemini 1.5 Pro: 1M tokens (~250MB)
- Claude: Context window varies by model

**Best practices:**
1. Use `review-ready` scope for quick feedback
2. Use specific scope for focused review
3. Use Repomix for token reduction
4. Generate PDF for large codebases
5. Include relevant epic spec with repomap

### Troubleshooting

**Issue: "Repomix not available"**
```bash
npm install -g repomix
```

**Issue: "enscript: command not found"**
```bash
sudo apt install enscript ghostscript
```

**Issue: "PDF exceeds 20MB"**
- Use Repomix compression: `--engine repomix`
- Use smaller scope: `review-ready` instead of `complete-backend`
- Split into multiple scopes

**Issue: "No files matched patterns"**
- Check scope patterns in `tools/repomap_scopes.json`
- Create custom scope in `tools/repomap_scopes_custom.json`
- Use auto-detection: `--auto-detect`

### Apply to Projects

```bash
# Deploy to all projects
/tier1-update-surgical --update-id=repomap-global-v1

# Deploy to specific project
/tier1-update-surgical --update-id=repomap-global-v1 --project=my-project
```

**Files deployed:**
- `tools/generate_scoped_repomap.py` - Main generation script
- `tools/repomap_scopes.json` - Scope definitions
- `tools/repomix_adapter.py` - Optional Repomix integration
- `scripts/generate_pr_repomap.sh` - PR-specific generator
- `.claude/commands/generate-repomap.md` - Interactive command
- `.claude/commands/chatgpt-implement.md` - Full automation
- `.claude/commands/generate-pr-repomap.md` - PR command

**Restoration:**

Original email_management_system files archived in:
```
.archive/email_management_system_repomap_original/
```

Restore command:
```bash
cp .archive/email_management_system_repomap_original/* tools/
```

---

## 📋 Available Updates

### Current Updates

1. **agent-model-cleanup-v1** (2025-10-26) ⭐ NEW
   - Priority: High
   - Components: 1 (removes model definitions from agent frontmatter)
   - Purpose: Prevent token waste by ensuring agents use session model
   - Status: Ready for deployment
   - Apply: `/tier1-update-surgical --update-id=agent-model-cleanup-v1`
   - Impact: Reduces unnecessary Opus costs, ensures consistent behavior

2. **agent-failure-reporting-protocol-v1** (2025-10-24)
   - Priority: High
   - Components: 3 (agent briefings, detection script, documentation)
   - Status: Ready for deployment
   - Apply: `/tier1-update-surgical --update-id=agent-failure-reporting-protocol-v1`

3. **github-ai-review-integration-v1** (2025-10-29) ⭐ NEW
   - Priority: Medium
   - Components: 6 (GitHub Actions workflow, PR helper, docs, execute-workflow update)
   - Purpose: Automatic @claude and @codex AI review for all PRs
   - Status: ✅ Deployed to: whisper_hotkeys, ppt_pipeline, orchestrator
   - Apply: `/tier1-update-surgical --update-id=github-ai-review-integration-v1`
   - Impact: 30-60s AI code review on every PR, automatic PR creation in workflow
   - Setup Required: CLAUDE_CODE_OAUTH_TOKEN secret per repository

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

### Repomap Generation
- `/generate-repomap [scope]` - Generate repository map for AI review
- `/chatgpt-implement EPIC-ID [--auto]` - Full ChatGPT automation workflow
- `/generate-pr-repomap <PR_NUM>` - Generate PR-specific repomap

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

**Last Updated**: 2025-11-01
**Surgical Update System Version**: 1.0.0
**Agent Failure Reporting Protocol**: Implemented
**Repomap Generation System**: Implemented
