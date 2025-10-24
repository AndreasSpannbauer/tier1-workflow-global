---
description: "Complete intelligent deployment of Tier1 workflow to any project with automatic adaptation"
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion]
---

# Tier 1 Workflow - Intelligent Deploy

**ONE COMMAND** to fully deploy and adapt Tier1 workflow to any project.

This command orchestrates:
1. **Bash installation script** - Copies all workflow files
2. **Project analysis** - Detects tech stack, domain, architecture
3. **Template adaptation** - Customizes output styles and configs for the project
4. **Initialization** - Runs tier1-init-claude-md and epic-registry-init
5. **Verification** - Ensures all components are correctly deployed

**Usage:**
```bash
/tier1-deploy [project-path] [--project-type=python|typescript|mixed]
```

---

## Step 1: Parse Arguments and Detect Project

```bash
PROJECT_PATH="${1:-.}"
PROJECT_TYPE=""
FORCE=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --project-type=*)
      PROJECT_TYPE="${arg#*=}"
      ;;
    --force)
      FORCE=true
      ;;
    *)
      if [[ "$arg" != "$PROJECT_PATH" ]]; then
        PROJECT_PATH="$arg"
      fi
      ;;
  esac
done

# Resolve to absolute path
cd "$PROJECT_PATH" || exit 1
PROJECT_PATH="$PWD"
PROJECT_NAME=$(basename "$PROJECT_PATH")

echo "🎯 Tier1 Workflow - Intelligent Deploy"
echo ""
echo "📁 Project: $PROJECT_NAME"
echo "📍 Path: $PROJECT_PATH"
echo ""
```

---

## Step 2: Run Installation Script

**Execute the bash installation script to copy all workflow files:**

```bash
echo "🚀 Step 1/5: Running installation script..."
echo ""

TIER1_GLOBAL="$HOME/tier1_workflow_global"
INSTALL_SCRIPT="$TIER1_GLOBAL/install_tier1_workflow.sh"

if [ ! -f "$INSTALL_SCRIPT" ]; then
  echo "❌ Installation script not found: $INSTALL_SCRIPT"
  exit 1
fi

# Determine project type if not specified
if [ -z "$PROJECT_TYPE" ]; then
  if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    if [ -f "tsconfig.json" ] || [ -f "package.json" ]; then
      PROJECT_TYPE="mixed"
    else
      PROJECT_TYPE="python"
    fi
  elif [ -f "tsconfig.json" ] || [ -f "package.json" ]; then
    PROJECT_TYPE="typescript"
  else
    PROJECT_TYPE="python"  # Default
  fi
fi

echo "   Project type: $PROJECT_TYPE"
echo ""

# Run installation script
if [ "$FORCE" = true ]; then
  "$INSTALL_SCRIPT" "$PROJECT_PATH" --"$PROJECT_TYPE" --force
else
  "$INSTALL_SCRIPT" "$PROJECT_PATH" --"$PROJECT_TYPE"
fi

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Installation script failed"
  exit 1
fi

echo ""
echo "✅ Installation script completed"
echo ""
```

---

## Step 3: Analyze Project

**Claude Code analyzes the project to gather context for template customization.**

Use the Read tool to analyze key project files:
- `README.md` (if exists) - Project description and purpose
- `pyproject.toml` or `package.json` - Dependencies and metadata
- Main source directory structure (detect domains: backend, frontend, data, etc.)

**Gather the following information:**
1. **Primary tech stack**: Python/TypeScript/mixed and key frameworks (FastAPI, React, etc.)
2. **Project domain**: Scientific/ML, Web API, CLI tool, Desktop app, Data pipeline, etc.
3. **Key characteristics**: Async-heavy, database-driven, API-focused, analysis-heavy, etc.

**Store analysis in variables for template customization:**
- `PROJECT_NAME`: Directory name (already have)
- `TECH_STACK`: e.g., "Python (FastAPI + SQLAlchemy)"
- `PROJECT_DOMAIN`: e.g., "Scientific Data Analysis"
- `KEY_FRAMEWORKS`: List of detected frameworks

---

## Step 4: Customize Output Style Template

**Adapt the spec-architect template to the specific project.**

**Check if customized version already exists:**

```bash
CUSTOMIZED_FILE=".claude/output-styles/spec-architect-${PROJECT_NAME}.md"

if [ -f "$CUSTOMIZED_FILE" ]; then
  echo "ℹ️  Customized output style already exists: spec-architect-${PROJECT_NAME}.md"
  echo "   Preserving existing customizations"
  echo ""
else
  echo "📝 Creating customized output style: spec-architect-${PROJECT_NAME}.md"
  echo ""
fi
```

**If customized version doesn't exist, create it:**

Only proceed if the file doesn't already exist.

1. **Read the template**:
   ```bash
   TEMPLATE_FILE=".claude/output-styles/spec-architect-template.md"
   ```

2. **Create customized version** with:
   - File name: `spec-architect-${PROJECT_NAME}.md`
   - Replace `<PROJECT_NAME>` → `$PROJECT_NAME` in name and description
   - Add project-specific context section after the role:

   ```markdown
   ## Project Context: ${PROJECT_NAME}

   **Tech Stack**: ${TECH_STACK}
   **Domain**: ${PROJECT_DOMAIN}
   **Key Frameworks**: ${KEY_FRAMEWORKS}

   **When creating specifications for this project:**
   - Consider ${PROJECT_DOMAIN} best practices
   - Leverage ${KEY_FRAMEWORKS} patterns from pattern library
   - Ensure compatibility with existing ${TECH_STACK} infrastructure
   ```

3. **Use Write tool** to create the new file (don't use Edit on template - create new file)

**Preserve user customizations**: Never overwrite existing customized output styles.

---

## Step 5: Initialize Workflow Components

### 5a: Initialize CLAUDE.md

**Only if CLAUDE.md exists in the project:**

```bash
if [ -f "CLAUDE.md" ]; then
  echo "🔧 Step 4/5: Initializing CLAUDE.md workflow section..."
  echo ""

  # Use the tier1-init-claude-md command (call it programmatically via SlashCommand tool)
  # This will insert workflow documentation into project CLAUDE.md

  # Claude Code: Execute /tier1-init-claude-md here

  echo ""
  echo "✅ CLAUDE.md initialized"
  echo ""
else
  echo "ℹ️  No CLAUDE.md found - skipping workflow documentation"
  echo "   (Create CLAUDE.md later and run /tier1-init-claude-md)"
  echo ""
fi
```

### 5b: Initialize Epic Registry

```bash
echo "📋 Step 5/5: Initializing epic registry..."
echo ""

# Use the epic-registry-init command (call it programmatically via SlashCommand tool)
# This will create .tasks/epic_registry.json

# Claude Code: Execute /epic-registry-init here

echo ""
echo "✅ Epic registry initialized"
echo ""
```

---

## Step 6: Verify Deployment

**Verify all critical components are present:**

```bash
echo "🔍 Verifying deployment..."
echo ""

ERRORS=0

# Check agents
for agent in implementation_agent_v1 post_mortem_agent_v1 build_fixer_agent_v1 integration_planning_agent_v1; do
  if [ ! -f ".claude/agents/${agent}.md" ]; then
    echo "   ❌ Missing agent: ${agent}.md"
    ((ERRORS++))
  fi
done

# Check customized output style
if [ ! -f ".claude/output-styles/spec-architect-${PROJECT_NAME}.md" ]; then
  echo "   ❌ Missing customized output style: spec-architect-${PROJECT_NAME}.md"
  ((ERRORS++))
fi

# Check commands
if [ ! -f ".claude/commands/execute-workflow.md" ]; then
  echo "   ❌ Missing command: execute-workflow.md"
  ((ERRORS++))
fi

# Check task templates
if [ ! -f ".tasks/templates/spec.md.j2" ]; then
  echo "   ❌ Missing template: spec.md.j2"
  ((ERRORS++))
fi

# Check epic registry
if [ ! -f ".tasks/epic_registry.json" ]; then
  echo "   ⚠️  Epic registry not initialized (run /epic-registry-init)"
fi

if [ $ERRORS -eq 0 ]; then
  echo "   ✅ All critical components verified"
else
  echo ""
  echo "   ⚠️  Found $ERRORS missing components"
fi

echo ""
```

---

## Step 7: Report Summary

```bash
echo "═══════════════════════════════════════════════════════"
echo "✅ Tier1 Workflow Deployment Complete"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📊 Deployment Summary:"
echo ""
echo "   Project: $PROJECT_NAME"
echo "   Type: $PROJECT_TYPE"
echo "   Domain: ${PROJECT_DOMAIN}"
echo "   Tech Stack: ${TECH_STACK}"
echo ""
echo "📁 Installed Components:"
echo "   ├── 4 agents (implementation, post-mortem, build-fixer, integration-planning)"
echo "   ├── 20+ slash commands"
echo "   ├── Customized output style: spec-architect-${PROJECT_NAME}"
echo "   ├── 5 task templates"
echo "   ├── Validation scripts"
echo "   ├── GitHub integration tools"
echo "   ├── Worktree manager"
echo "   └── Epic registry"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "   1. Set output style:"
echo "      /output-style spec-architect-${PROJECT_NAME}"
echo ""
echo "   2. Create your first epic:"
echo "      /spec-epic \"Your epic title\""
echo ""
echo "   3. Execute workflow:"
echo "      /execute-workflow"
echo ""
echo "   4. View available commands:"
echo "      Type / to see all workflow commands"
echo ""
echo "📚 Documentation:"
echo "   - Quick start: .claude/README.md"
echo "   - Customization: ~/tier1_workflow_global/implementation/WORKFLOW_CUSTOMIZATION.md"
echo "   - Troubleshooting: ~/tier1_workflow_global/implementation/TROUBLESHOOTING_QUICK_REFERENCE.md"
echo ""
```

---

## Usage Examples

```bash
# Deploy to current directory with auto-detection
/tier1-deploy

# Deploy to specific project
/tier1-deploy ~/my-project

# Deploy with explicit project type
/tier1-deploy ~/my-project --project-type=python

# Force reinstall (overwrite existing)
/tier1-deploy --force
```

---

## Notes

**Intelligent Adaptation:**
- Detects project type automatically (Python/TypeScript/mixed)
- Analyzes project domain and tech stack
- Customizes output style template with project-specific context
- Renames template file to match project name

**Idempotent:**
- Safe to run multiple times
- Use `--force` to overwrite existing files
- Epic registry init checks for existing registry

**Complete Workflow:**
- Runs bash installation script (file copying)
- Performs intelligent project analysis
- Adapts templates to project specifics
- Initializes all workflow components
- Verifies deployment completeness

**Template Customization:**
- `spec-architect-template.md` → `spec-architect-${PROJECT_NAME}.md`
- Replaces `<PROJECT_NAME>` placeholders
- Adds project-specific context section
- Preserves all workflow features

**Post-Deployment:**
- Sets up epic registry for tracking
- Optionally initializes CLAUDE.md workflow section
- Ready to use immediately with `/spec-epic`
