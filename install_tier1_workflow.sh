#!/usr/bin/env bash
# MIT License
#
# Copyright (c) 2025 Tier 1 Workflow System
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

set -euo pipefail

# ============================================================================
# Tier 1 Workflow Installation Script
# ============================================================================
#
# Installs the Tier 1 workflow system into any project with one command.
# Provides task management, validation, parallel execution, and GitHub integration.
#
# Usage:
#   ./install_tier1_workflow.sh <project-dir> [options]
#
# Options:
#   --python          Python-focused project
#   --typescript      TypeScript-focused project
#   --mixed           Mixed language project
#   --dry-run         Show what would be installed without doing it
#   --force           Overwrite existing files
#   --quiet           Minimal output
#   --help            Show this help message
#
# ============================================================================

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/template"
IMPL_DIR="${SCRIPT_DIR}/implementation"
LOG_FILE=""
DRY_RUN=false
FORCE=false
QUIET=false
PROJECT_TYPE=""
PROJECT_DIR=""
PROJECT_NAME=""

# Colors (with fallback)
if [[ -t 1 ]] && command -v tput &>/dev/null; then
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    MAGENTA=$(tput setaf 5)
    CYAN=$(tput setaf 6)
    BOLD=$(tput bold)
    RESET=$(tput sgr0)
else
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    MAGENTA=""
    CYAN=""
    BOLD=""
    RESET=""
fi

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"

    if [[ "${QUIET}" == "true" ]] && [[ "${level}" != "ERROR" ]]; then
        return
    fi

    case "${level}" in
        INFO)
            echo "${BLUE}[INFO]${RESET} ${message}"
            ;;
        SUCCESS)
            echo "${GREEN}[SUCCESS]${RESET} ${message}"
            ;;
        WARNING)
            echo "${YELLOW}[WARNING]${RESET} ${message}"
            ;;
        ERROR)
            echo "${RED}[ERROR]${RESET} ${message}" >&2
            ;;
        STEP)
            echo "${CYAN}${BOLD}==>${RESET} ${message}"
            ;;
    esac

    # Also log to file if available
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] ${message}" >> "${LOG_FILE}"
    fi
}

show_progress() {
    if [[ "${QUIET}" == "false" ]]; then
        echo -n "${MAGENTA}${1}${RESET}"
    fi
}

clear_progress() {
    if [[ "${QUIET}" == "false" ]]; then
        echo -e "\r\033[K"
    fi
}

show_help() {
    cat << EOF
${BOLD}Tier 1 Workflow Installation Script${RESET}

${BOLD}USAGE:${RESET}
    ${0} <project-dir> [options]

${BOLD}ARGUMENTS:${RESET}
    project-dir         Target project directory (must exist)

${BOLD}OPTIONS:${RESET}
    --python            Python-focused project (pytest, mypy, black)
    --typescript        TypeScript-focused project (tsc, eslint, prettier)
    --mixed             Mixed language project (Python + TypeScript)
    --dry-run           Show what would be installed without doing it
    --force             Overwrite existing files (use with caution!)
    --quiet             Minimal output (errors only)
    --help              Show this help message

${BOLD}EXAMPLES:${RESET}
    # Interactive installation (prompts for project type)
    ${0} ~/my-project

    # Python project
    ${0} ~/my-python-project --python

    # TypeScript project with dry-run
    ${0} ~/my-ts-project --typescript --dry-run

    # Mixed project, force overwrite
    ${0} ~/my-mixed-project --mixed --force

${BOLD}WHAT GETS INSTALLED:${RESET}
    - .claude/          Claude Code configuration (commands, output styles)
    - .tasks/           Task management structure (backlog, current, completed)
    - .workflow/        Workflow state tracking
    - tools/            Validation scripts and GitHub integration
    - .worktrees/       Git worktree directory (created if needed)

${BOLD}MORE INFO:${RESET}
    See INSTALLATION_GUIDE.md for detailed documentation.
EOF
}

confirm() {
    local prompt="$1"
    local response

    if [[ "${FORCE}" == "true" ]]; then
        return 0
    fi

    read -r -p "${YELLOW}${prompt} [y/N]${RESET} " response
    case "${response}" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

check_prerequisites() {
    log STEP "Checking prerequisites..."

    # Check Git
    if ! command -v git &>/dev/null; then
        log ERROR "Git is not installed. Please install Git first."
        exit 1
    fi

    # Check Python (optional but recommended)
    if ! command -v python3 &>/dev/null; then
        log WARNING "Python 3 is not installed. Some features may not work."
    else
        local python_version=$(python3 --version 2>&1 | awk '{print $2}')
        log INFO "Python version: ${python_version}"

        # Check if Python >= 3.11
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            log INFO "Python 3.11+ detected"
        else
            log WARNING "Python 3.11+ recommended for best compatibility"
        fi
    fi

    # Check gh CLI (optional)
    if command -v gh &>/dev/null; then
        log INFO "GitHub CLI detected"
    else
        log INFO "GitHub CLI not found (optional - install for GitHub integration)"
    fi

    log SUCCESS "Prerequisites check complete"
}

validate_project_dir() {
    log STEP "Validating project directory..."

    if [[ ! -d "${PROJECT_DIR}" ]]; then
        log ERROR "Project directory does not exist: ${PROJECT_DIR}"
        exit 1
    fi

    # Check if it's a Git repository
    if [[ ! -d "${PROJECT_DIR}/.git" ]]; then
        log WARNING "Project directory is not a Git repository"
        if confirm "Initialize Git repository?"; then
            (cd "${PROJECT_DIR}" && git init)
            log SUCCESS "Git repository initialized"
        else
            log ERROR "Tier 1 workflow requires a Git repository"
            exit 1
        fi
    fi

    # Check if workflow already exists
    if [[ -d "${PROJECT_DIR}/.claude" ]] && [[ "${FORCE}" == "false" ]]; then
        log WARNING "Workflow already exists in ${PROJECT_DIR}"
        if ! confirm "Overwrite existing workflow?"; then
            log ERROR "Installation cancelled"
            exit 1
        fi
    fi

    log SUCCESS "Project directory validated"
}

detect_project_type() {
    log STEP "Detecting project type..."

    local has_python=false
    local has_typescript=false

    # Check for Python indicators
    if [[ -f "${PROJECT_DIR}/setup.py" ]] || \
       [[ -f "${PROJECT_DIR}/pyproject.toml" ]] || \
       [[ -f "${PROJECT_DIR}/requirements.txt" ]]; then
        has_python=true
    fi

    # Check for TypeScript indicators
    if [[ -f "${PROJECT_DIR}/tsconfig.json" ]] || \
       [[ -f "${PROJECT_DIR}/package.json" ]]; then
        has_typescript=true
    fi

    if [[ "${has_python}" == "true" ]] && [[ "${has_typescript}" == "true" ]]; then
        log INFO "Detected: Mixed (Python + TypeScript)"
        PROJECT_TYPE="mixed"
    elif [[ "${has_python}" == "true" ]]; then
        log INFO "Detected: Python"
        PROJECT_TYPE="python"
    elif [[ "${has_typescript}" == "true" ]]; then
        log INFO "Detected: TypeScript"
        PROJECT_TYPE="typescript"
    else
        log INFO "Could not auto-detect project type"
        PROJECT_TYPE=""
    fi
}

prompt_project_type() {
    if [[ -n "${PROJECT_TYPE}" ]]; then
        return
    fi

    log STEP "Select project type:"
    echo "  ${BOLD}1)${RESET} Python"
    echo "  ${BOLD}2)${RESET} TypeScript"
    echo "  ${BOLD}3)${RESET} Mixed (Python + TypeScript)"
    echo ""

    local choice
    read -r -p "Enter choice [1-3]: " choice

    case "${choice}" in
        1)
            PROJECT_TYPE="python"
            ;;
        2)
            PROJECT_TYPE="typescript"
            ;;
        3)
            PROJECT_TYPE="mixed"
            ;;
        *)
            log ERROR "Invalid choice"
            exit 1
            ;;
    esac

    log INFO "Selected: ${PROJECT_TYPE}"
}

create_backup() {
    log STEP "Creating backup of existing files..."

    local backup_dir="${PROJECT_DIR}/.tier1_backup_$(date +%Y%m%d_%H%M%S)"

    if [[ -d "${PROJECT_DIR}/.claude" ]] || \
       [[ -d "${PROJECT_DIR}/.tasks" ]] || \
       [[ -d "${PROJECT_DIR}/.workflow" ]]; then

        mkdir -p "${backup_dir}"

        [[ -d "${PROJECT_DIR}/.claude" ]] && cp -r "${PROJECT_DIR}/.claude" "${backup_dir}/"
        [[ -d "${PROJECT_DIR}/.tasks" ]] && cp -r "${PROJECT_DIR}/.tasks" "${backup_dir}/"
        [[ -d "${PROJECT_DIR}/.workflow" ]] && cp -r "${PROJECT_DIR}/.workflow" "${backup_dir}/"
        [[ -d "${PROJECT_DIR}/tools" ]] && cp -r "${PROJECT_DIR}/tools" "${backup_dir}/"

        log SUCCESS "Backup created: ${backup_dir}"
    else
        log INFO "No existing files to backup"
    fi
}

copy_with_substitution() {
    local src="$1"
    local dst="$2"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log INFO "[DRY RUN] Would copy: ${src} -> ${dst}"
        return
    fi

    # Create destination directory
    mkdir -p "$(dirname "${dst}")"

    # Copy file
    cp "${src}" "${dst}"

    # Perform substitutions
    if [[ -f "${dst}" ]]; then
        sed -i "s/{{PROJECT_NAME}}/${PROJECT_NAME}/g" "${dst}" 2>/dev/null || true
        sed -i "s/{{PROJECT_TYPE}}/${PROJECT_TYPE}/g" "${dst}" 2>/dev/null || true
    fi
}

install_directory_structure() {
    log STEP "Creating directory structure..."

    local dirs=(
        ".claude/commands"
        ".claude/output-styles"
        ".claude/agents"
        ".claude/agent_briefings"
        ".tasks/backlog"
        ".tasks/current"
        ".tasks/completed"
        ".tasks/templates"
        ".workflow"
        ".worktrees"
        "tools"
    )

    for dir in "${dirs[@]}"; do
        if [[ "${DRY_RUN}" == "true" ]]; then
            log INFO "[DRY RUN] Would create: ${PROJECT_DIR}/${dir}"
        else
            mkdir -p "${PROJECT_DIR}/${dir}"
            log INFO "Created: ${dir}"
        fi
    done

    log SUCCESS "Directory structure created"
}

install_claude_config() {
    log STEP "Installing Claude Code configuration..."

    # Copy commands
    if [[ -d "${TEMPLATE_DIR}/.claude/commands" ]]; then
        for file in "${TEMPLATE_DIR}/.claude/commands"/*.md; do
            [[ -f "${file}" ]] || continue
            local filename=$(basename "${file}")
            copy_with_substitution "${file}" "${PROJECT_DIR}/.claude/commands/${filename}"
            log INFO "Installed command: ${filename}"
        done
    fi

    # Copy output styles
    if [[ -d "${TEMPLATE_DIR}/.claude/output-styles" ]]; then
        for file in "${TEMPLATE_DIR}/.claude/output-styles"/*.md; do
            [[ -f "${file}" ]] || continue
            local filename=$(basename "${file}")
            copy_with_substitution "${file}" "${PROJECT_DIR}/.claude/output-styles/${filename}"
            log INFO "Installed output style: ${filename}"
        done
    fi

    log SUCCESS "Claude Code configuration installed"
}

install_agents() {
    log STEP "Installing agent definitions and briefings..."

    # Create agent directories
    mkdir -p "${PROJECT_DIR}/.claude/agents"
    mkdir -p "${PROJECT_DIR}/.claude/agent_briefings"

    # Copy agent definitions from implementation/agents to .claude/agents
    if [[ -d "${IMPL_DIR}/agents" ]]; then
        for file in "${IMPL_DIR}/agents"/*.md; do
            [[ -f "${file}" ]] || continue
            local filename=$(basename "${file}")
            copy_with_substitution "${file}" "${PROJECT_DIR}/.claude/agents/${filename}"
            log INFO "Installed agent: ${filename}"
        done
    fi

    # Copy agent briefings from implementation/agent_briefings to .claude/agent_briefings
    if [[ -d "${IMPL_DIR}/agent_briefings" ]]; then
        for file in "${IMPL_DIR}/agent_briefings"/*.md; do
            [[ -f "${file}" ]] || continue
            local filename=$(basename "${file}")
            copy_with_substitution "${file}" "${PROJECT_DIR}/.claude/agent_briefings/${filename}"
            log INFO "Installed briefing: ${filename}"
        done
    fi

    log SUCCESS "Agents and briefings installed"
}

install_task_templates() {
    log STEP "Installing task templates..."

    if [[ -d "${TEMPLATE_DIR}/.tasks/templates" ]]; then
        for file in "${TEMPLATE_DIR}/.tasks/templates"/*.j2; do
            [[ -f "${file}" ]] || continue
            local filename=$(basename "${file}")
            copy_with_substitution "${file}" "${PROJECT_DIR}/.tasks/templates/${filename}"
            log INFO "Installed template: ${filename}"
        done
    fi

    log SUCCESS "Task templates installed"
}

install_validation_scripts() {
    log STEP "Installing validation scripts..."

    # Copy validation scripts based on project type
    local scripts=()

    case "${PROJECT_TYPE}" in
        python)
            scripts=("validate_architecture.py" "validate_contracts.py")
            ;;
        typescript)
            scripts=("validate_architecture.py" "validate_contracts.py")
            ;;
        mixed)
            scripts=("validate_architecture.py" "validate_contracts.py")
            ;;
    esac

    if [[ -d "${TEMPLATE_DIR}/tools" ]]; then
        for script in "${scripts[@]}"; do
            local src="${TEMPLATE_DIR}/tools/${script}"
            if [[ -f "${src}" ]]; then
                copy_with_substitution "${src}" "${PROJECT_DIR}/tools/${script}"
                chmod +x "${PROJECT_DIR}/tools/${script}" 2>/dev/null || true
                log INFO "Installed: ${script}"
            fi
        done
    fi

    log SUCCESS "Validation scripts installed"
}

install_github_integration() {
    log STEP "Installing GitHub integration..."

    if [[ -d "${TEMPLATE_DIR}/tools/github_integration" ]]; then
        # Copy entire github_integration directory (excluding __pycache__)
        if [[ "${DRY_RUN}" == "true" ]]; then
            log INFO "[DRY RUN] Would copy GitHub integration tools"
        else
            mkdir -p "${PROJECT_DIR}/tools/github_integration"

            for file in "${TEMPLATE_DIR}/tools/github_integration"/*.py; do
                [[ -f "${file}" ]] || continue
                local filename=$(basename "${file}")
                copy_with_substitution "${file}" "${PROJECT_DIR}/tools/github_integration/${filename}"
                log INFO "Installed: github_integration/${filename}"
            done

            for file in "${TEMPLATE_DIR}/tools/github_integration"/*.md; do
                [[ -f "${file}" ]] || continue
                local filename=$(basename "${file}")
                copy_with_substitution "${file}" "${PROJECT_DIR}/tools/github_integration/${filename}"
            done
        fi
    fi

    log SUCCESS "GitHub integration installed"
}

install_worktree_manager() {
    log STEP "Installing worktree manager..."

    if [[ -d "${IMPL_DIR}/worktree_manager" ]]; then
        if [[ "${DRY_RUN}" == "true" ]]; then
            log INFO "[DRY RUN] Would copy worktree manager"
        else
            mkdir -p "${PROJECT_DIR}/tools/worktree_manager"

            for file in "${IMPL_DIR}/worktree_manager"/*.py; do
                [[ -f "${file}" ]] || continue
                local filename=$(basename "${file}")
                copy_with_substitution "${file}" "${PROJECT_DIR}/tools/worktree_manager/${filename}"
                log INFO "Installed: worktree_manager/${filename}"
            done

            # Copy README
            if [[ -f "${IMPL_DIR}/worktree_manager/README.md" ]]; then
                copy_with_substitution "${IMPL_DIR}/worktree_manager/README.md" "${PROJECT_DIR}/tools/worktree_manager/README.md"
            fi
        fi
    fi

    log SUCCESS "Worktree manager installed"
}

install_parallel_detection() {
    log STEP "Installing parallel detection..."

    if [[ -f "${IMPL_DIR}/parallel_detection.py" ]]; then
        copy_with_substitution "${IMPL_DIR}/parallel_detection.py" "${PROJECT_DIR}/tools/parallel_detection.py"
        chmod +x "${PROJECT_DIR}/tools/parallel_detection.py" 2>/dev/null || true
        log SUCCESS "Parallel detection installed"
    else
        log WARNING "Parallel detection script not found"
    fi
}

create_package_json() {
    log STEP "Setting up package.json..."

    local package_json="${PROJECT_DIR}/package.json"

    if [[ -f "${package_json}" ]]; then
        log INFO "package.json already exists, skipping"
        return
    fi

    if [[ "${PROJECT_TYPE}" == "typescript" ]] || [[ "${PROJECT_TYPE}" == "mixed" ]]; then
        if [[ "${DRY_RUN}" == "true" ]]; then
            log INFO "[DRY RUN] Would create package.json"
        else
            cat > "${package_json}" << 'EOF'
{
  "name": "{{PROJECT_NAME}}",
  "version": "0.1.0",
  "scripts": {
    "validate": "npm run validate:lint && npm run validate:types",
    "validate:lint": "eslint . --ext .ts,.tsx",
    "validate:types": "tsc --noEmit",
    "validate:format": "prettier --check .",
    "fix": "npm run fix:lint && npm run fix:format",
    "fix:lint": "eslint . --ext .ts,.tsx --fix",
    "fix:format": "prettier --write ."
  }
}
EOF
            sed -i "s/{{PROJECT_NAME}}/${PROJECT_NAME}/g" "${package_json}"
            log SUCCESS "package.json created with validation scripts"
        fi
    fi
}

create_readme() {
    log STEP "Creating workflow README..."

    local readme="${PROJECT_DIR}/.claude/README.md"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log INFO "[DRY RUN] Would create .claude/README.md"
        return
    fi

    cat > "${readme}" << 'EOF'
# Tier 1 Workflow

This project uses the Tier 1 workflow system for task management, validation, and parallel execution.

## Quick Start

### Available Commands

```bash
# Task management
/task-list              # List all tasks
/task-create            # Create a new task
/task-get <id>          # Get task details
/task-update <id>       # Update task status

# Workflow execution
/execute-workflow       # Execute parallel workflow with validation
/spec-master            # Master architect (epic planning)
/spec-epic              # Epic architect (epic breakdown)
/refine-spec            # Refine specifications
```

### Output Styles

- **V6-Tier1**: Concise, fix-oriented (default)
- **V6-Explanatory**: Educational with insights
- **V6-Learning**: Collaborative with guided implementation

Switch: `/output-style V6-Tier1`

### Validation

Automated validation runs after each implementation:
- Build checks (compile, lint, format)
- Architecture validation
- Contract validation
- Up to 3 retry attempts with build fixer agent

### Parallel Execution

Large epics (8+ files, 2+ domains) automatically execute in parallel:
- Git worktree isolation
- Domain-specific agents (backend, frontend, database, tests, docs)
- Sequential merge with conflict detection
- 2-4x speedup

### GitHub Integration

Optional GitHub sync:
- Epic creation with sub-issues
- Automatic label management
- Progress tracking
- Offline queue for network resilience

See `tools/github_integration/README.md` for setup.

## Directory Structure

```
.claude/                # Claude Code configuration
  commands/             # Slash commands
  output-styles/        # Output style definitions
.tasks/                 # Task management
  backlog/              # Pending tasks
  current/              # Active tasks
  completed/            # Finished tasks
  templates/            # Task templates
.workflow/              # Workflow state
.worktrees/             # Git worktrees (parallel execution)
tools/                  # Validation and integration tools
```

## Next Steps

1. Set output style: `/output-style V6-Tier1`
2. Create your first task: `/task-create`
3. Review available commands: Type `/` to see all commands
4. Read documentation: `tier1_workflow_global/docs/`

## Resources

- [Tier 1 Workflow Docs](~/tier1_workflow_global/docs/)
- [GitHub Integration Guide](tools/github_integration/README.md)
- [Workflow Customization](~/tier1_workflow_global/implementation/WORKFLOW_CUSTOMIZATION.md)
- [Testing Guide](~/tier1_workflow_global/implementation/WEEK4_TESTING_GUIDE.md)
EOF

    log SUCCESS "Workflow README created"
}

rollback_installation() {
    log ERROR "Installation failed! Rolling back changes..."

    if [[ "${DRY_RUN}" == "true" ]]; then
        log INFO "[DRY RUN] Would rollback installation"
        return
    fi

    # Remove installed directories
    rm -rf "${PROJECT_DIR}/.claude" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/.tasks" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/.workflow" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/.worktrees" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/tools/validate_*.py" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/tools/github_integration" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/tools/worktree_manager" 2>/dev/null || true
    rm -rf "${PROJECT_DIR}/tools/parallel_detection.py" 2>/dev/null || true

    log WARNING "Installation rolled back"
}

show_summary() {
    log SUCCESS "Installation complete!"
    echo ""
    echo "${BOLD}${GREEN}Installed Files:${RESET}"
    echo ""

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "${YELLOW}[DRY RUN MODE - No files were actually installed]${RESET}"
        echo ""
    fi

    echo "  ${BOLD}.claude/${RESET}"
    echo "    ├── commands/          (8 workflow commands)"
    echo "    ├── output-styles/     (1 spec architect style)"
    echo "    └── README.md          (workflow guide)"
    echo ""
    echo "  ${BOLD}.tasks/${RESET}"
    echo "    ├── backlog/"
    echo "    ├── current/"
    echo "    ├── completed/"
    echo "    └── templates/         (3 templates: spec, task, architecture)"
    echo ""
    echo "  ${BOLD}.workflow/${RESET}"
    echo "    └── (workflow state tracking)"
    echo ""
    echo "  ${BOLD}.worktrees/${RESET}"
    echo "    └── (git worktrees for parallel execution)"
    echo ""
    echo "  ${BOLD}tools/${RESET}"
    echo "    ├── validate_architecture.py"
    echo "    ├── validate_contracts.py"
    echo "    ├── parallel_detection.py"
    echo "    ├── github_integration/    (GitHub sync tools)"
    echo "    └── worktree_manager/      (worktree utilities)"
    echo ""

    echo "${BOLD}${CYAN}Next Steps:${RESET}"
    echo ""
    echo "  1. ${BOLD}Open Claude Code in your project:${RESET}"
    echo "     cd ${PROJECT_DIR}"
    echo "     claude-code ."
    echo ""
    echo "  2. ${BOLD}Set your output style:${RESET}"
    echo "     /output-style V6-Tier1"
    echo ""
    echo "  3. ${BOLD}List available commands:${RESET}"
    echo "     Type / to see all workflow commands"
    echo ""
    echo "  4. ${BOLD}Create your first task:${RESET}"
    echo "     /task-create"
    echo ""
    echo "  5. ${BOLD}Read the workflow guide:${RESET}"
    echo "     cat .claude/README.md"
    echo ""

    if [[ -n "${LOG_FILE}" ]]; then
        echo "${BOLD}${BLUE}Installation log:${RESET} ${LOG_FILE}"
        echo ""
    fi

    echo "${GREEN}Happy coding!${RESET}"
}

verify_installation() {
    log STEP "Verifying installation..."

    local errors=0

    # Check critical directories
    local required_dirs=(
        ".claude/commands"
        ".claude/output-styles"
        ".tasks/templates"
        "tools"
    )

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "${PROJECT_DIR}/${dir}" ]] && [[ "${DRY_RUN}" == "false" ]]; then
            log ERROR "Missing directory: ${dir}"
            ((errors++))
        fi
    done

    # Check critical files
    local required_files=(
        ".claude/commands/execute-workflow.md"
        ".claude/output-styles/spec-architect-template.md"
        ".tasks/templates/spec.md.j2"
        "tools/validate_architecture.py"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "${PROJECT_DIR}/${file}" ]] && [[ "${DRY_RUN}" == "false" ]]; then
            log ERROR "Missing file: ${file}"
            ((errors++))
        fi
    done

    if [[ ${errors} -gt 0 ]]; then
        log ERROR "Verification failed with ${errors} errors"
        return 1
    fi

    log SUCCESS "Verification complete"
    return 0
}

# ============================================================================
# Main Installation Flow
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --python)
                PROJECT_TYPE="python"
                shift
                ;;
            --typescript)
                PROJECT_TYPE="typescript"
                shift
                ;;
            --mixed)
                PROJECT_TYPE="mixed"
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --quiet)
                QUIET=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            -*)
                log ERROR "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
            *)
                if [[ -z "${PROJECT_DIR}" ]]; then
                    PROJECT_DIR="$1"
                else
                    log ERROR "Multiple project directories specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Validate arguments
    if [[ -z "${PROJECT_DIR}" ]]; then
        log ERROR "Project directory not specified"
        echo ""
        show_help
        exit 1
    fi

    # Resolve to absolute path
    PROJECT_DIR="$(cd "${PROJECT_DIR}" 2>/dev/null && pwd)" || {
        log ERROR "Cannot access project directory: ${PROJECT_DIR}"
        exit 1
    }

    # Extract project name
    PROJECT_NAME="$(basename "${PROJECT_DIR}")"

    # Initialize log file
    LOG_FILE="${PROJECT_DIR}/.tier1_install_$(date +%Y%m%d_%H%M%S).log"

    # Print banner
    echo ""
    echo "${BOLD}${BLUE}╔════════════════════════════════════════════════╗${RESET}"
    echo "${BOLD}${BLUE}║     Tier 1 Workflow Installation Script       ║${RESET}"
    echo "${BOLD}${BLUE}╚════════════════════════════════════════════════╝${RESET}"
    echo ""

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "${YELLOW}${BOLD}[DRY RUN MODE - No files will be modified]${RESET}"
        echo ""
    fi

    log INFO "Project: ${PROJECT_NAME}"
    log INFO "Directory: ${PROJECT_DIR}"
    echo ""

    # Run installation steps
    trap 'rollback_installation' ERR

    check_prerequisites
    validate_project_dir

    # Auto-detect or prompt for project type
    if [[ -z "${PROJECT_TYPE}" ]]; then
        detect_project_type
        if [[ -z "${PROJECT_TYPE}" ]]; then
            prompt_project_type
        fi
    fi

    log INFO "Project type: ${PROJECT_TYPE}"
    echo ""

    # Create backup if needed
    if [[ "${FORCE}" == "false" ]]; then
        create_backup
    fi

    # Install components
    install_directory_structure
    install_claude_config
    install_agents
    install_task_templates
    install_validation_scripts
    install_github_integration
    install_worktree_manager
    install_parallel_detection
    create_package_json
    create_readme

    # Verify installation
    if ! verify_installation; then
        rollback_installation
        exit 1
    fi

    echo ""
    show_summary
}

# Run main function
main "$@"
