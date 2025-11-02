# Agent Model Cleanup - Testing Guide

## Overview

This guide demonstrates how to test the agent model cleanup update both manually and via the surgical update system.

## Manual Testing

### 1. Create Test Agent File with Model Definition

```bash
# Create a temporary test directory
mkdir -p /tmp/test-agent-cleanup/.claude/agents

# Create a test agent with model definition
cat > /tmp/test-agent-cleanup/.claude/agents/test_agent.md <<'EOF'
---
agent_type: test-agent
model: claude-opus-4
description: Test agent for verification
---

# Test Agent

This is a test agent with a model definition that should be removed.
EOF

# Verify model definition exists
grep "^model:" /tmp/test-agent-cleanup/.claude/agents/test_agent.md
# Should output: model: claude-opus-4
```

### 2. Apply the Update Using apply_update.py

```bash
cd /home/andreas-spannbauer/tier1_workflow_global

# Test with dry-run first
python3 template/tools/apply_update.py \
  --project-path /tmp/test-agent-cleanup \
  --update-def implementation/update_definitions.json \
  --update-id agent-model-cleanup-v1 \
  --component-index 0 \
  --dry-run

# Apply the update
python3 template/tools/apply_update.py \
  --project-path /tmp/test-agent-cleanup \
  --update-def implementation/update_definitions.json \
  --update-id agent-model-cleanup-v1 \
  --component-index 0
```

### 3. Verify Results

```bash
# Check that model definition was removed
grep "^model:" /tmp/test-agent-cleanup/.claude/agents/test_agent.md
# Should output: (nothing - pattern not found)

# Check that the rest of the file is intact
cat /tmp/test-agent-cleanup/.claude/agents/test_agent.md
# Should show the agent file without the model: line

# Test idempotent behavior (run again)
python3 template/tools/apply_update.py \
  --project-path /tmp/test-agent-cleanup \
  --update-def implementation/update_definitions.json \
  --update-id agent-model-cleanup-v1 \
  --component-index 0
# Should report: already_applied: true
```

### 4. Cleanup

```bash
rm -rf /tmp/test-agent-cleanup
```

## Testing with Installation Script

### 1. Test New Deployment

```bash
# Create a test project
mkdir -p /tmp/test-project-deploy
cd /tmp/test-project-deploy
git init

# Create a minimal package.json to make it look like a project
echo '{"name": "test-project"}' > package.json

# Run installation with dry-run
~/tier1_workflow_global/install_tier1_workflow.sh /tmp/test-project-deploy --typescript --dry-run

# Run actual installation
~/tier1_workflow_global/install_tier1_workflow.sh /tmp/test-project-deploy --typescript

# Verify no model definitions exist in agents
grep -r "^model:" .claude/agents/
# Should output: (nothing - no matches)
```

### 2. Verify Installation Script Output

Look for these messages in the installation output:

```
==> Verifying agent configurations...
✓ All agents correctly configured (no model definitions)
[INFO] Agent Configuration: All agents default to session model (Sonnet 4.5)
[INFO]   - NO 'model:' specifications in agent frontmatter
[INFO]   - Prevents unnecessary Opus token costs
[INFO]   - Ensures consistent behavior with main session
```

### 3. Test with Pre-Existing Model Definitions

```bash
# Add model definitions to test cleanup
echo "model: claude-opus-4" >> /tmp/test-project-deploy/.claude/agents/implementation_agent_v1.md
echo "model: claude-opus-4" >> /tmp/test-project-deploy/.claude/agents/post_mortem_agent_v1.md

# Re-run installation with force
~/tier1_workflow_global/install_tier1_workflow.sh /tmp/test-project-deploy --typescript --force

# Should see warnings and cleanup messages
# Verify cleanup succeeded
grep -r "^model:" /tmp/test-project-deploy/.claude/agents/
# Should output: (nothing)
```

### 4. Cleanup

```bash
rm -rf /tmp/test-project-deploy
```

## Integration Testing

### Test with Surgical Update System

If you have the `/tier1-update-surgical` command available:

```bash
# Dry-run on all projects
/tier1-update-surgical --update-id=agent-model-cleanup-v1 --dry-run

# Apply to a single test project
/tier1-update-surgical --update-id=agent-model-cleanup-v1 --project=test-project

# Apply to all projects
/tier1-update-surgical --update-id=agent-model-cleanup-v1
```

## Expected Behavior

### Before Update

Agent files contain model specifications:
```markdown
---
agent_type: implementation-agent-v1
model: claude-opus-4
description: Implements features
---
```

### After Update

Agent files have model line removed:
```markdown
---
agent_type: implementation-agent-v1
description: Implements features
---
```

### Idempotent Behavior

Running the update multiple times:
- First run: Removes model lines, reports changes
- Subsequent runs: Detects already applied, no changes
- Always safe to run, never duplicates work

## Troubleshooting

### Update reports "already_applied: true" but model lines exist

Check the idempotent condition:
```bash
# Manual check
grep -q "^model:" /path/to/agent/file.md
echo $?  # 0 = found (NOT applied), 1 = not found (already applied)
```

If the check is incorrect, verify the pattern in `update_definitions.json`:
```json
"idempotent_check": "! grep -q '^model:' {target}"
```

### Update fails with "No files match pattern"

Verify the target path exists:
```bash
ls -la /path/to/project/.claude/agents/*.md
```

If no agents exist, the project may not have Tier1 workflow installed.

### Some agent files not processed

Check for glob pattern expansion:
```bash
# This should list all agent markdown files
find /path/to/project/.claude/agents -name "*.md" -type f
```

## Success Criteria

✅ All agent files processed (*.md in .claude/agents/)
✅ All `model:` lines removed from frontmatter
✅ Rest of file content unchanged
✅ Idempotent check prevents duplicate application
✅ Installation script automatically verifies new deployments
✅ Dry-run mode accurately previews changes

## Token Cost Impact

### Before Cleanup
- Agent specifies `model: claude-opus-4`
- Every agent call uses Opus tokens (~$15/M input, $75/M output)
- Annual cost: $XXX (depends on usage)

### After Cleanup
- Agent uses session model (Sonnet 4.5)
- Agent calls use Sonnet tokens (~$3/M input, $15/M output)
- Annual savings: ~80% reduction in agent token costs
