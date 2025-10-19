# Tier 1 Workflow Installation Guide

Complete guide for installing and configuring the Tier 1 workflow system in any project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation Options](#installation-options)
- [Post-Installation Setup](#post-installation-setup)
- [Verification](#verification)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [Examples](#examples)

## Prerequisites

### Required

- **Git** (version 2.25+)
  ```bash
  git --version
  ```

- **Git repository** (existing or new)
  ```bash
  git init  # if not already a git repo
  ```

### Recommended

- **Python 3.11+** (for validation scripts)
  ```bash
  python3 --version
  ```

- **Node.js 18+** (for TypeScript projects)
  ```bash
  node --version
  ```

### Optional

- **GitHub CLI** (for GitHub integration)
  ```bash
  gh --version
  # Install: https://cli.github.com/
  ```

## Quick Start

### Interactive Installation

The simplest way to install is to run the script interactively:

```bash
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-project
```

The script will:
1. Check prerequisites
2. Validate your project directory
3. Auto-detect project type (Python/TypeScript/Mixed)
4. Prompt for confirmation if needed
5. Install all components
6. Show a summary of what was installed

### Non-Interactive Installation

For automation or CI/CD, specify the project type explicitly:

```bash
# Python project
./install_tier1_workflow.sh ~/my-python-project --python

# TypeScript project
./install_tier1_workflow.sh ~/my-ts-project --typescript

# Mixed project
./install_tier1_workflow.sh ~/my-mixed-project --mixed
```

## Installation Options

### Command-Line Flags

```bash
./install_tier1_workflow.sh <project-dir> [options]
```

| Flag | Description |
|------|-------------|
| `--python` | Python-focused project (pytest, mypy, black) |
| `--typescript` | TypeScript-focused project (tsc, eslint, prettier) |
| `--mixed` | Mixed language project (Python + TypeScript) |
| `--dry-run` | Show what would be installed without doing it |
| `--force` | Overwrite existing files (use with caution!) |
| `--quiet` | Minimal output (errors only) |
| `--help` | Show help message |

### Dry Run Mode

Preview what will be installed without making any changes:

```bash
./install_tier1_workflow.sh ~/my-project --python --dry-run
```

This will show all files and directories that would be created.

### Force Overwrite

If you have an existing workflow and want to overwrite it:

```bash
./install_tier1_workflow.sh ~/my-project --python --force
```

**Warning:** This will overwrite existing files! A backup will be created first.

## Post-Installation Setup

### 1. Review Installed Files

Check what was installed:

```bash
cd ~/my-project
tree -L 2 .claude .tasks tools
```

You should see:
- `.claude/` - Claude Code configuration
- `.tasks/` - Task management structure
- `.workflow/` - Workflow state tracking
- `tools/` - Validation and integration scripts

### 2. Set Output Style

Open your project in Claude Code and set the output style:

```bash
cd ~/my-project
claude-code .  # or open in your IDE
```

Then in Claude Code:
```
/output-style V6-Tier1
```

Available styles:
- **V6-Tier1**: Concise, fix-oriented (default)
- **V6-Explanatory**: Educational with insights
- **V6-Learning**: Collaborative with guided implementation

### 3. Configure Validation (Optional)

Edit validation scripts for your project:

**Python projects:**
```bash
# Edit tools/validate_architecture.py
# Add project-specific checks (imports, structure, etc.)
```

**TypeScript projects:**
```bash
# Edit package.json scripts
# Customize lint/format/type-check commands
```

### 4. GitHub Integration (Optional)

If you want GitHub issue sync:

```bash
# Install GitHub CLI
# See: https://cli.github.com/

# Authenticate
gh auth login

# Test connection
gh repo view

# Read setup guide
cat tools/github_integration/README.md
```

### 5. Create Your First Task

In Claude Code:
```
/task-create
```

Follow the prompts to create your first task.

## Verification

### Automated Verification

The installation script automatically verifies the installation. If verification fails, installation is rolled back.

### Manual Verification

Check that all components are installed:

```bash
cd ~/my-project

# Check directories exist
ls -la .claude .tasks .workflow tools

# Check commands are available
ls .claude/commands/

# Check output styles are available
ls .claude/output-styles/

# Check validation scripts
ls tools/validate_*.py

# Check GitHub integration
ls tools/github_integration/

# Check worktree manager
ls tools/worktree_manager/
```

Expected output:

```
.claude/commands/:
- execute-workflow.md
- refine-spec.md
- spec-epic.md
- spec-master.md
- task-create.md
- task-get.md
- task-list.md
- task-update.md

.claude/output-styles/:
- spec-architect-template.md

.tasks/templates/:
- architecture.md.j2
- spec.md.j2
- task.md.j2

tools/:
- validate_architecture.py
- validate_contracts.py
- parallel_detection.py
- github_integration/
- worktree_manager/
```

### Test Workflow Commands

In Claude Code, test that commands work:

```
/task-list          # Should show empty task list
/task-create        # Should prompt for task creation
```

## Configuration

### Project Type Detection

The installer auto-detects project type based on files:

| File | Detected Type |
|------|---------------|
| `setup.py`, `pyproject.toml`, `requirements.txt` | Python |
| `tsconfig.json`, `package.json` | TypeScript |
| Both present | Mixed |

You can override auto-detection with `--python`, `--typescript`, or `--mixed`.

### Validation Scripts

Validation scripts are customizable:

**Python (`tools/validate_architecture.py`):**
- Checks imports, structure, naming conventions
- Runs pytest, mypy, black (if available)
- Customizable rules

**TypeScript (via `package.json`):**
- `npm run validate` - Run all validations
- `npm run validate:lint` - ESLint checks
- `npm run validate:types` - TypeScript checks
- `npm run validate:format` - Prettier checks

### GitHub Integration

GitHub integration is opt-in. To enable:

1. Install GitHub CLI: `gh auth login`
2. Configure repository: Set remote URL
3. Test: `gh repo view`
4. Use: `/execute-workflow` will offer GitHub sync

See `tools/github_integration/README.md` for details.

## Troubleshooting

### Installation Fails

**Problem:** Installation fails with errors

**Solution:**
1. Check the log file: `.tier1_install_YYYYMMDD_HHMMSS.log`
2. Review prerequisites: Git, Python version
3. Try dry-run mode: `--dry-run` to see what would happen
4. Check permissions: Ensure write access to project directory

### Git Repository Required

**Problem:** Error: "Tier 1 workflow requires a Git repository"

**Solution:**
```bash
cd ~/my-project
git init
```

### Python Version Warning

**Problem:** Warning: "Python 3.11+ recommended for best compatibility"

**Solution:**
- Upgrade Python: `sudo apt install python3.11` (Ubuntu/Debian)
- Or use pyenv: `pyenv install 3.11 && pyenv local 3.11`
- Workflow will still work, but some validation features may not work

### Commands Not Available

**Problem:** Commands like `/task-create` don't work in Claude Code

**Solution:**
1. Ensure `.claude/commands/` directory exists
2. Check commands are readable: `ls -la .claude/commands/`
3. Restart Claude Code
4. Check Claude Code version supports slash commands

### Validation Fails

**Problem:** Validation scripts fail when running `/execute-workflow`

**Solution:**
1. Check validation script exists: `ls tools/validate_*.py`
2. Make scripts executable: `chmod +x tools/validate_*.py`
3. Install dependencies: `pip install pytest mypy black` (Python)
4. Review validation output for specific errors

### GitHub Integration Not Working

**Problem:** GitHub sync doesn't create issues

**Solution:**
1. Check GitHub CLI is installed: `gh --version`
2. Authenticate: `gh auth login`
3. Check repository remote: `git remote -v`
4. Test: `gh repo view`
5. Review `tools/github_integration/README.md`

## Uninstallation

To remove the Tier 1 workflow from a project:

```bash
cd ~/my-project

# Remove workflow directories
rm -rf .claude .tasks .workflow .worktrees

# Remove tools (careful if you have other tools)
rm -rf tools/validate_*.py
rm -rf tools/github_integration
rm -rf tools/worktree_manager
rm -rf tools/parallel_detection.py

# Remove package.json if created by installer
# (Only if you don't have other dependencies)
# rm package.json
```

**Note:** This does NOT delete your code or Git history. Only workflow configuration is removed.

### Restore from Backup

If you have a backup (created during installation):

```bash
cd ~/my-project

# Find backup directory
ls -la | grep tier1_backup

# Restore from backup
cp -r .tier1_backup_YYYYMMDD_HHMMSS/.claude .
cp -r .tier1_backup_YYYYMMDD_HHMMSS/.tasks .
# etc.
```

## Examples

### Example 1: Python Data Science Project

```bash
# Project structure
~/my-ds-project/
├── requirements.txt
├── setup.py
├── src/
└── tests/

# Install workflow
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-ds-project --python

# Result
~/my-ds-project/
├── .claude/              # ← New
├── .tasks/               # ← New
├── .workflow/            # ← New
├── tools/                # ← New
│   ├── validate_architecture.py
│   ├── validate_contracts.py
│   └── ...
├── requirements.txt
├── setup.py
├── src/
└── tests/
```

In Claude Code:
```
/output-style V6-Tier1
/task-create
# Create: "Implement data preprocessing pipeline"
/execute-workflow
# Workflow executes with validation
```

### Example 2: TypeScript Web App

```bash
# Project structure
~/my-web-app/
├── package.json
├── tsconfig.json
├── src/
└── tests/

# Install workflow
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-web-app --typescript

# Result
~/my-web-app/
├── .claude/              # ← New
├── .tasks/               # ← New
├── .workflow/            # ← New
├── tools/                # ← New
├── package.json          # ← Updated (validation scripts added)
├── tsconfig.json
├── src/
└── tests/
```

In Claude Code:
```
/output-style V6-Tier1
/task-create
# Create: "Add user authentication"
/execute-workflow
# Workflow executes with TypeScript validation
```

### Example 3: Mixed Project (Python Backend + TypeScript Frontend)

```bash
# Project structure
~/my-fullstack-app/
├── backend/
│   ├── requirements.txt
│   └── src/
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
└── README.md

# Install workflow
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-fullstack-app --mixed

# Result
~/my-fullstack-app/
├── .claude/              # ← New
├── .tasks/               # ← New
├── .workflow/            # ← New
├── tools/                # ← New
├── backend/
├── frontend/
└── README.md
```

In Claude Code:
```
/output-style V6-Tier1
/task-create
# Create: "Implement REST API and React UI"
/execute-workflow
# Workflow detects parallelizable epic
# Executes backend + frontend in parallel
# Validates both Python and TypeScript
```

### Example 4: GitHub Integration

```bash
# Install with GitHub integration
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-project --python

# Setup GitHub CLI
gh auth login

# Configure repository
cd ~/my-project
git remote add origin https://github.com/username/my-project.git

# Test GitHub integration
cat tools/github_integration/README.md
```

In Claude Code:
```
/task-create
# Create: "Add user authentication"
/execute-workflow
# Prompt: "Create GitHub issue for this epic? [y/N]"
# Type: y
# Result: Epic created on GitHub with sub-issues
```

### Example 5: Dry Run (Preview Installation)

```bash
# Preview what would be installed
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-project --python --dry-run

# Output shows all files that would be created
# No actual changes made
# Review output, then run without --dry-run
```

### Example 6: Force Overwrite Existing Workflow

```bash
# Existing workflow (outdated)
~/my-project/.claude/     # Old version

# Force update to latest version
cd ~/tier1_workflow_global
./install_tier1_workflow.sh ~/my-project --python --force

# Result:
# - Backup created: .tier1_backup_YYYYMMDD_HHMMSS/
# - Old workflow overwritten with new version
# - All files updated
```

## Best Practices

### 1. Version Control

Add workflow files to Git:

```bash
cd ~/my-project
git add .claude .tasks tools
git commit -m "Add Tier 1 workflow system"
```

**Recommended .gitignore additions:**
```gitignore
# Workflow state (user-specific)
.workflow/

# Worktrees (temporary)
.worktrees/

# Installation logs
.tier1_install_*.log
.tier1_backup_*/
```

### 2. Team Collaboration

For team projects:
- Commit `.claude/` and `.tasks/templates/` to version control
- Keep `.workflow/` local (add to `.gitignore`)
- Document workflow in project README
- Share GitHub integration setup instructions

### 3. Multiple Projects

Install workflow in multiple projects:

```bash
for project in project1 project2 project3; do
    ./install_tier1_workflow.sh ~/projects/$project --python
done
```

### 4. Custom Validation

Customize validation scripts for your project:

```python
# tools/validate_architecture.py
def validate_imports():
    """Project-specific import validation"""
    # Check that all imports follow project conventions
    # Check for circular dependencies
    # Validate package structure
```

### 5. Workflow Updates

To update workflow to latest version:

```bash
cd ~/tier1_workflow_global
git pull  # Get latest changes

# Force reinstall in project
./install_tier1_workflow.sh ~/my-project --python --force
```

## Next Steps

After installation:

1. **Read the workflow guide:**
   ```bash
   cd ~/my-project
   cat .claude/README.md
   ```

2. **Explore available commands:**
   - Open Claude Code
   - Type `/` to see all commands
   - Try `/task-list`, `/task-create`

3. **Set your output style:**
   ```
   /output-style V6-Tier1
   ```

4. **Create your first task:**
   ```
   /task-create
   ```

5. **Execute workflow:**
   ```
   /execute-workflow
   ```

6. **Read documentation:**
   - [Workflow Integration Guide](~/tier1_workflow_global/implementation/WORKFLOW_INTEGRATION_GUIDE.md)
   - [Testing Guide](~/tier1_workflow_global/implementation/WEEK4_TESTING_GUIDE.md)
   - [Customization Guide](~/tier1_workflow_global/implementation/WORKFLOW_CUSTOMIZATION.md)

## Support

### Documentation

- [Tier 1 Workflow README](~/tier1_workflow_global/README.md)
- [Week 4 Complete](~/tier1_workflow_global/implementation/WEEK4_COMPLETE.md)
- [Validation System](~/tier1_workflow_global/implementation/VALIDATION_SYSTEM.md)
- [Post-Mortem System](~/tier1_workflow_global/implementation/POST_MORTEM_SYSTEM.md)

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

### Updates

Check for workflow updates:

```bash
cd ~/tier1_workflow_global
git log --oneline -10  # See recent changes
git pull               # Update to latest version
```

## License

Personal use only. Not intended for distribution.
