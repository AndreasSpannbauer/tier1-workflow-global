# Tier 1 Workflow System

## Purpose

Simplified V6 workflow for general-purpose projects with minimal complexity. This system provides a lightweight task management and development workflow suitable for single-developer projects that don't require complex agent coordination or domain-specific specialization.

## Status

**In Development** - Core template and documentation complete, implementation artifacts in progress.

## Overview

The Tier 1 workflow is designed for:
- General-purpose projects without domain-specific requirements
- Single-developer or small team projects
- Projects where Claude Code's default capabilities are sufficient
- Codebases where git worktree complexity is unnecessary

### What's Included

- **Template**: Ready-to-use project structure with task management and output styles
- **Documentation**: Comprehensive assessment and planning documents
- **Implementation Artifacts**: Tools and utilities for workflow management (in development)

## Directory Structure

```
tier1_workflow_global/
├── README.md                          # This file
├── docs/                              # All documentation
│   ├── README.md                      # Documentation index
│   ├── assessment/                    # Assessment and planning documents
│   └── architecture/                  # Architecture diagrams and specs (future)
├── template/                          # V6 Tier 1 project template
│   ├── .claude/                       # Claude Code configuration
│   ├── .tasks/                        # Task management structure
│   └── tools/                         # Workflow tools and scripts
└── implementation/                    # Implementation artifacts (future)
    ├── agent_definitions/             # Agent definition files
    ├── agent_briefings/               # Domain briefing files
    └── worktree_manager/              # Worktree manager code
```

## Quick Links

### Key Documents
- [Assessment Overview](docs/README.md) - Documentation index and reading guide
- [Latest Enhancement Assessment](docs/assessment/tier1_enhancement_assessment.md) - Current state and planned improvements
- [Final Implementation Plan](docs/assessment/V6_TIER1_FINAL_IMPLEMENTATION_PLAN.md) - Complete Tier 1 specification

### Template
- [Project Template](template/) - Ready-to-use V6 Tier 1 template

## Getting Started

### Using the Template

1. Copy the template to your project directory:
   ```bash
   cp -r ~/tier1_workflow_global/template/.claude ~/your-project/
   cp -r ~/tier1_workflow_global/template/.tasks ~/your-project/
   cp -r ~/tier1_workflow_global/template/tools ~/your-project/
   ```

2. Initialize the workflow:
   ```bash
   cd ~/your-project
   ./tools/task init
   ```

3. Set your preferred output style:
   ```bash
   # In Claude Code
   /output-style V6-Tier1
   ```

### Reading the Documentation

Start with the [Documentation Index](docs/README.md) for a guided tour through the assessment documents.

## Features

### Task Management
- Single `.tasks/` directory with clear organization
- Status-based task workflow (pending → in-progress → completed)
- Simple archival system for completed work
- No git worktree complexity

### Output Styles
- **V6-Tier1**: Concise, fix-oriented default style
- **V6-Explanatory**: Educational mode with insights
- **V6-Learning**: Collaborative mode with guided implementation

### Workflow Tools
- Task initialization and management scripts
- Status tracking utilities
- Archive management

## Comparison to Other Tiers

| Feature | Tier 1 | Tier 2+ |
|---------|--------|---------|
| Git worktrees | No | Yes |
| Agent specialization | No | Yes |
| Domain briefings | No | Yes |
| Task complexity | Simple | Complex |
| Setup time | Minutes | Hours |

## Development Roadmap

- [x] Core template structure
- [x] Task management system
- [x] Output styles
- [x] Documentation and assessment
- [ ] Agent definition framework
- [ ] Domain briefing templates
- [ ] Worktree manager utilities
- [ ] Migration guides for Tier 2+

## Contributing

This is a personal workflow system. Modifications should maintain:
- Simplicity over features
- Clear separation from higher tiers
- Minimal cognitive overhead
- Single-developer focus

## License

Personal use only. Not intended for distribution.
