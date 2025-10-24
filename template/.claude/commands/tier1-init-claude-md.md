---
description: "Insert or update workflow section in project CLAUDE.md"
allowed-tools: [Read, Edit, Write, Bash]
---

# Tier 1 Workflow - Initialize CLAUDE.md

Intelligently inserts workflow documentation into project CLAUDE.md files.

**Features:**
- Auto-detects project type (Tier1 vs V6)
- Idempotent operation (safe to run multiple times)
- Backup creation before modification
- Dry-run mode for preview
- Force mode to override existing sections
- Pattern library MCP server (available globally, no project setup required)

---

## Step 1: Parse Arguments

```bash
DRY_RUN=false
FORCE=false

# Parse command-line arguments
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    *)
      # Unknown argument
      ;;
  esac
done

if [ "$DRY_RUN" = true ]; then
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo ""
fi

PROJECT_DIR="$PWD"
echo "📁 Project: $PROJECT_DIR"
echo ""
```

---

## Step 2: Detect Project Type

```bash
echo "🔍 Detecting project type..."
echo ""

PROJECT_TYPE="Tier1"

# Check for V6 indicators
if [ -f ".claude/commands/workflow/execute-workflow.md" ]; then
  echo "   ✅ Found: .claude/commands/workflow/execute-workflow.md (V6 indicator)"
  PROJECT_TYPE="V6"
elif [ -d ".claude/agents/workflow-v6-agents" ]; then
  echo "   ✅ Found: .claude/agents/workflow-v6-agents/ (V6 indicator)"
  PROJECT_TYPE="V6"
elif [ -d "tools/workflow_utilities_v6" ]; then
  echo "   ✅ Found: tools/workflow_utilities_v6/ (V6 indicator)"
  PROJECT_TYPE="V6"
else
  echo "   ℹ️  No V6 indicators found - assuming Tier1"
fi

echo ""
echo "📊 Project Type: $PROJECT_TYPE"
echo ""
```

---

## Step 3: Verify CLAUDE.md Exists

```bash
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"

if [ ! -f "$CLAUDE_MD" ]; then
  echo "❌ CLAUDE.md not found: $CLAUDE_MD"
  echo ""
  echo "Expected location: $PROJECT_DIR/CLAUDE.md"
  echo ""
  echo "Action required: Create CLAUDE.md in your project root before running this command."
  exit 1
fi

echo "✅ Found: CLAUDE.md"
echo ""
```

---

## Step 4: Read Template Sections

**This step requires Claude Code to read the template file using the Read tool.**

Read the template sections from:
`/home/andreas-spannbauer/tier1_workflow_global/implementation/architecture/CLAUDE_WORKFLOW_SECTIONS.md`

Extract TWO sections:

1. **Main workflow section** based on detected project type:
   - If `PROJECT_TYPE="Tier1"`: Extract "Section 1: Tier1 Workflow Template"
   - If `PROJECT_TYPE="V6"`: Extract "Section 2: V6 Workflow Template"

2. **Pattern Library section** (ALWAYS):
   - Extract "Section 2.5: Pattern Library Integration"

Store both extracted sections for insertion (workflow section + pattern library section).

---

## Step 5: Check for Existing Section

```bash
echo "🔍 Checking for existing workflow section..."
echo ""

if grep -q "<!-- BEGIN WORKFLOW SECTION -->" "$CLAUDE_MD"; then
  SECTION_EXISTS=true
  echo "   ℹ️  Workflow section already exists in CLAUDE.md"
  echo ""

  if [ "$FORCE" = true ]; then
    echo "   🔧 Force mode enabled - will replace existing section"
    echo ""
  elif [ "$DRY_RUN" = false ]; then
    echo "   ⚠️  Use --force to replace existing section"
    echo "   ⚠️  Use --dry-run to preview changes"
    echo ""
    exit 0
  fi
else
  SECTION_EXISTS=false
  echo "   ✅ No existing workflow section found"
  echo ""
fi
```

---

## Step 6: Create Backup

```bash
if [ "$DRY_RUN" = false ]; then
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  BACKUP_FILE="${CLAUDE_MD}.backup-${TIMESTAMP}"

  echo "💾 Creating backup..."
  cp "$CLAUDE_MD" "$BACKUP_FILE"
  echo "   ✅ Backup created: $(basename "$BACKUP_FILE")"
  echo ""
fi
```

---

## Step 7: Insert or Update Sections

**This step requires Claude Code to use Edit or Write tool based on the situation.**

**Insert BOTH sections** (workflow section + pattern library section):

**If SECTION_EXISTS is true:**
- Use the Edit tool to replace content between markers:
  - `old_string`: Everything from `<!-- BEGIN WORKFLOW SECTION -->` to `<!-- END WORKFLOW SECTION -->` (inclusive)
  - `new_string`: The extracted workflow template section + two newlines + pattern library section (with markers)

**If SECTION_EXISTS is false:**
- Use the Edit tool to append to the end of CLAUDE.md:
  - `old_string`: The last line of the file (or last N lines to make it unique)
  - `new_string`: The last line + two newlines + workflow section + two newlines + pattern library section

**Combined content format:**
```
<!-- BEGIN WORKFLOW SECTION -->

[Main Workflow Section Content]

[Pattern Library Section Content]

<!-- END WORKFLOW SECTION -->
```

**Dry-run mode:**
If `DRY_RUN=true`, do NOT perform the Edit/Write operation. Instead, output what would be changed:

```bash
if [ "$DRY_RUN" = true ]; then
  echo "📋 DRY RUN - Changes that would be applied:"
  echo ""

  if [ "$SECTION_EXISTS" = true ]; then
    echo "   Operation: REPLACE existing workflow section"
    echo "   Target: Between markers in CLAUDE.md"
  else
    echo "   Operation: APPEND workflow section to end of file"
    echo "   Target: End of CLAUDE.md"
  fi

  echo ""
  echo "   Project Type: $PROJECT_TYPE"
  echo "   Section Size: [calculated from template]"
  echo ""
  echo "To apply changes, run without --dry-run flag"
  exit 0
fi
```

---

## Step 8: Report Success

```bash
echo "✅ Workflow section updated successfully"
echo ""

if [ "$SECTION_EXISTS" = true ]; then
  echo "   📝 Operation: Replaced existing section"
else
  echo "   📝 Operation: Appended new section"
fi

echo "   📊 Project Type: $PROJECT_TYPE"
echo "   💾 Backup: $(basename "$BACKUP_FILE")"
echo ""

echo "📄 Review changes:"
echo "   git diff CLAUDE.md"
echo ""

echo "🎯 To restore backup if needed:"
echo "   cp $BACKUP_FILE CLAUDE.md"
echo ""
```

---

## Usage Examples

```bash
# Preview what would change
/tier1-init-claude-md --dry-run

# Insert section (first time)
/tier1-init-claude-md

# Try to update again (will exit with message)
/tier1-init-claude-md

# Force replace existing section
/tier1-init-claude-md --force

# Preview force replace
/tier1-init-claude-md --dry-run --force
```

---

## Notes

**Idempotent:** Safe to run multiple times. Won't modify if section already exists unless `--force` is used.

**Backup:** Always creates backup before modifications (CLAUDE.md.backup-TIMESTAMP).

**Dry-run:** Use `--dry-run` to see what would change without modifying files.

**Force:** Use `--force` to replace existing workflow section.

**Auto-detection:** Detects V6 vs Tier1 based on presence of:
- `.claude/commands/workflow/execute-workflow.md`
- `.claude/agents/workflow-v6-agents/`
- `tools/workflow_utilities_v6/`

**Pattern Library:** ALWAYS includes Section 2.5 (Pattern Library Integration) after the main workflow section. This is a global feature available in all projects.

**Markers:** Uses HTML comments as markers to enable idempotent updates:
- `<!-- BEGIN WORKFLOW SECTION -->`
- `<!-- END WORKFLOW SECTION -->`
