# Tier 1 Workflow System

## Purpose

Simplified V6 workflow for general-purpose projects with minimal complexity. This system provides a lightweight task management and development workflow suitable for single-developer projects that don't require complex agent coordination or domain-specific specialization.

## Status

**Week 5 Complete (83% of roadmap)** - Documentation suite, GitHub parallel integration, and workflow guides complete. Production-ready workflow with comprehensive documentation and troubleshooting support.

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
└── implementation/                    # Implementation artifacts
    ├── agent_definitions/             # Agent definition files (complete)
    ├── agent_briefings/               # Domain briefing files (complete)
    ├── worktree_manager/              # Worktree manager code (complete)
    ├── validation_scripts/            # Validation templates (Week 4)
    ├── test_cases/                    # Test case examples
    ├── parallel_detection.py          # Parallel detection logic (Week 3)
    ├── WEEK4_COMPLETE.md              # Week 4 completion report
    └── WEEK4_DELIVERABLES.md          # Week 4 deliverables reference
```

## Quick Links

### Week 5 Deliverables (NEW)
- **[Week 5 Complete](implementation/WEEK5_COMPLETE.md)** - Documentation suite and GitHub parallel integration (83% of roadmap)
- **[Week 5 Deliverables](implementation/WEEK5_DELIVERABLES.md)** - Detailed deliverables reference
- **[Workflow Example](implementation/WORKFLOW_EXAMPLE.md)** - End-to-end walkthrough
- **[Workflow Customization](implementation/WORKFLOW_CUSTOMIZATION.md)** - Setup guide
- **[Workflow Testing](implementation/WORKFLOW_TESTING_GUIDE.md)** - Testing procedures
- **[Troubleshooting](implementation/WORKFLOW_TROUBLESHOOTING.md)** - Common issues and solutions
- **[GitHub Integration](implementation/GITHUB_PARALLEL_INTEGRATION.md)** - Parallel execution progress tracking

### Previous Weeks
- **[Week 4 Complete](implementation/WEEK4_COMPLETE.md)** - Validation and post-mortem systems
- **[Week 4 Deliverables](implementation/WEEK4_DELIVERABLES.md)** - Validation system reference

### Key Documents
- [Assessment Overview](docs/README.md) - Documentation index and reading guide
- [Latest Enhancement Assessment](docs/assessment/tier1_enhancement_assessment.md) - Current state and planned improvements
- [Final Implementation Plan](docs/assessment/V6_TIER1_FINAL_IMPLEMENTATION_PLAN.md) - Complete Tier 1 specification
- [Week 3 Complete](implementation/WEEK3_COMPLETE.md) - Parallel execution system

### Template
- [Project Template](template/) - Ready-to-use V6 Tier 1 template

## Getting Started

### Using the Template

**Quick Start:**
1. Read the [Workflow Example](implementation/WORKFLOW_EXAMPLE.md) for an end-to-end walkthrough
2. Follow the [Workflow Customization Guide](implementation/WORKFLOW_CUSTOMIZATION.md) for setup
3. Test with the [Workflow Testing Guide](implementation/WORKFLOW_TESTING_GUIDE.md)

**Manual Installation (Week 6 will add one-command setup):**

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

4. Configure validation (see [Customization Guide](implementation/WORKFLOW_CUSTOMIZATION.md)):
   ```bash
   # Add validate-all script to package.json
   npm pkg set scripts.validate-all="your validation commands"
   ```

### Reading the Documentation

Start with the [Documentation Index](docs/README.md) for a guided tour through the assessment documents.

## Features

### Documentation Suite (Week 5)
- Complete end-to-end workflow walkthrough with real examples
- Customization guide for project-specific setup
- Testing guide with test case examples
- Troubleshooting guide for 10 common issues
- GitHub parallel integration architecture guide
- Optional documentation freshness tracking tool

### GitHub Parallel Integration (Week 5)
- Epic issue creation with workflow metadata
- Sub-issue creation for each parallel domain
- Progress updates posted during sequential merge
- Label management (status tracking)
- Non-blocking design (failures don't halt workflow)
- Automatic sub-issue closing after merge

### Parallel Execution System (Week 3)
- Automatic detection of parallelizable epics (8+ files, 2+ domains)
- Git worktree isolation for parallel agents
- Domain-specific implementation (backend, frontend, database, tests, docs)
- Sequential merge with conflict detection
- 2-4x speedup for large epics
- GitHub integration (epic and sub-issue creation)

### Validation System (Week 4)
- Automated validation with retry loop (up to 3 attempts)
- Build fixer agent auto-deployment on failures
- Multi-language support (Python, TypeScript, Go)
- Auto-fix capabilities (linting, formatting, type hints)
- Architecture and contract validation templates
- Non-blocking failures (workflow continues)

### Post-Mortem System (Week 4)
- Automated workflow analysis after completion
- Structured markdown reports (4 post-mortem questions)
- Actionable recommendations for briefing evolution
- Human-in-the-loop knowledge capture
- Metrics tracking (validation pass rate, parallel speedup)

### Task Management
- Single `.tasks/` directory with clear organization
- Status-based task workflow (pending → in-progress → completed)
- Simple archival system for completed work
- GitHub issue integration (optional)

### Output Styles
- **V6-Tier1**: Concise, fix-oriented default style
- **V6-Explanatory**: Educational mode with insights
- **V6-Learning**: Collaborative mode with guided implementation

### Workflow Tools
- Task initialization and management scripts
- Status tracking utilities
- Archive management
- Parallel detection script
- Worktree manager
- Validation templates
- Documentation freshness checker (optional)

## Comparison to Other Tiers

| Feature | Tier 1 | Tier 2+ |
|---------|--------|---------|
| Git worktrees | ✅ Yes (Week 3) | Yes |
| Parallel execution | ✅ Yes (Week 3) | Yes |
| Agent specialization | ✅ Yes (Weeks 2-3) | Yes |
| Domain briefings | ✅ Yes (Week 2) | Yes |
| Validation system | ✅ Yes (Week 4) | Yes |
| Post-mortem analysis | ✅ Yes (Week 4) | Enhanced |
| Task complexity | Simple → Complex | Complex |
| Setup time | Minutes | Hours |

**Note:** Tier 1 now includes core V6 features. Tier 2+ adds semantic indexing, automated knowledge capture, and advanced resume mechanisms.

## Development Roadmap (6 Weeks)

**Progress: 83% (5 of 6 weeks complete)**

- ✅ **Week 1:** Core template structure, task management, output styles
- ✅ **Week 2:** Agent definitions and domain briefings
- ✅ **Week 3:** Parallel execution with git worktrees, GitHub integration
- ✅ **Week 4:** Validation system with retry loop, post-mortem analysis
- ✅ **Week 5:** Documentation suite, GitHub parallel integration, troubleshooting guides ← **YOU ARE HERE**
- ⏳ **Week 6:** Installation script, rollout to 5 projects, final refinement, v1.0 release

### Completed Milestones

**Week 1-2: Foundation** (COMPLETE)
- [x] Core template structure
- [x] Task management system
- [x] Output styles
- [x] Documentation and assessment
- [x] Agent definition framework
- [x] Domain briefing templates

**Week 3: Parallelization** (COMPLETE)
- [x] Parallel detection algorithm
- [x] Worktree manager utilities
- [x] Sequential merge logic
- [x] GitHub integration (epic + sub-issues)
- [x] Testing guide and test cases

**Week 4: Quality & Knowledge** (COMPLETE)
- [x] Validation system with retry loop
- [x] Build fixer agent integration
- [x] Post-mortem analysis system
- [x] Validation script templates
- [x] Knowledge capture workflow

**Week 5: Documentation & Integration** (COMPLETE)
- [x] Comprehensive workflow documentation (3 guides)
- [x] Troubleshooting guides (2 documents)
- [x] GitHub parallel integration enhancements
- [x] Documentation freshness tool (optional)
- [x] 159 KB of production-ready documentation

### Upcoming Milestones

**Week 6: Release**
- [ ] Installation script (one-command setup)
- [ ] Rollout to 5 real-world projects
- [ ] Final refinement based on feedback
- [ ] Migration guides for Tier 2+
- [ ] v1.0 release

## Contributing

This is a personal workflow system. Modifications should maintain:
- Simplicity over features
- Clear separation from higher tiers
- Minimal cognitive overhead
- Single-developer focus

## License

Personal use only. Not intended for distribution.
