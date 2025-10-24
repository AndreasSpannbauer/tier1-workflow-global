# SCALAR Project: Extraction & Revival Plan

**Date:** 2025-10-22
**Status:** DRAFT - Awaiting approval
**Project:** Extract SCALAR from 01_second_brain → Standalone ~/SCALAR with Tier1 workflow

---

## Executive Summary

**Current State:**
- **Location:** `/home/andreas-spannbauer/coding_projects/projects/01_second_brain`
- **Size:** 30GB (SCALAR_workflow alone)
- **Complexity:** 18,175 Python files
- **Status:** Production-ready but dormant, scattered across second_brain project
- **Integration:** MCP server, Obsidian vault, LibreChat

**Target State:**
- **Location:** `~/SCALAR` (new standalone project)
- **Workflow:** Tier1 workflow implemented
- **Status:** Active development with epic-driven workflow
- **Integration:** Preserve MCP/Obsidian connections, clean separation

**Recommendation:** **PHASED 4-STAGE APPROACH** with analysis → planning → migration → validation

---

## 1. Discovery Analysis (Current State)

### 1.1 SCALAR Components Identified

**Core Codebase** (`SCALAR_workflow/` - 30GB):
- 18,175 Python files
- Microservice architecture (API gateway, collection service, analysis service)
- 41+ modules (orchestration, AI research, citation analysis, meta-analysis, etc.)
- Production-ready with 480+ tests (coverage reporting issues noted)
- Version: 2.2

**Documentation** (scattered):
- `docs/SCALAR_TECHNICAL_REFERENCE.md` - Technical reference
- `docs/SCALAR_ROADMAP_2025.md` - Roadmap and status
- `docs/SCALAR_MCP_LIBRECHAT_TROUBLESHOOTING.md` - MCP integration guide
- `docs/clinical_eda_scalar_integration.md` - Integration notes
- `SCALAR_WORKFLOW_INTEGRATION_PLAN.md` - MCP integration plan (60+ operations)

**Obsidian Integration** (`obsidian_llm_vault/`):
- `SCALAR_METHOD_DOCUMENTATION/` - Method documentation
- `SCALAR_PROJECT_EXTERNAL_LLM_OUTPUTS/` - External outputs
- `SCALAR_METHOD_SEARCHES/` - Search results
- Multiple markdown files with observations, prompts, roadmaps

**Scripts & Utilities**:
- `scripts/start_scalar_mcp.py` - MCP server launcher
- `scripts/activate-scalar.sh` - Environment activation
- `test_outputs/scalar_*.json` - Test results
- `scalar_performance_models/` - Performance models

**Key Features:**
- Systematic review workflow (Collection → Analysis → Articulation)
- 26 MCP tools for LibreChat integration
- Living systematic reviews & evidence surveillance
- Multi-database search (16 API clients)
- Citation network analysis
- Meta-analysis automation
- ONNX-based ML models
- Observability stack (Prometheus, Grafana, Jaeger, Loki)

---

## 2. Challenges & Risks

### 2.1 Complexity Challenges

**Size:**
- 30GB of data (models, cached data, results)
- 18,175 files to analyze and migrate
- Large Git history if tracked

**Integration Density:**
- Tightly coupled with Obsidian vault
- MCP server dependencies
- External service integrations (LibreChat, Traefik, Cloudflare)
- Shared configuration with second_brain project

**Dependencies:**
- Python packages (extensive requirements.txt)
- External services (PubMed, ArXiv, OpenAlex, etc.)
- Docker containers
- Environment variables (.env)

### 2.2 Risk Assessment

**High Risk:**
- Breaking MCP server integration during migration
- Losing Obsidian vault connections
- Incomplete dependency extraction
- Configuration drift

**Medium Risk:**
- Missing scattered files
- Test suite breakage
- Documentation loss

**Low Risk:**
- Git history preservation
- Code organization

---

## 3. Proposed Approach: 4-Stage Phased Migration

### STAGE 1: Deep Analysis & Inventory (1-2 hours)

**Goal:** Comprehensive understanding of SCALAR's footprint in second_brain

**Tasks:**

**1.1 Dependency Analysis**
```bash
# Run from second_brain project
cd ~/coding_projects/projects/01_second_brain

# Find all imports referencing SCALAR
grep -r "from SCALAR_workflow" --include="*.py" .
grep -r "import SCALAR_workflow" --include="*.py" .

# Find all references to SCALAR outside SCALAR_workflow/
grep -r "SCALAR" --include="*.py" --include="*.md" --include="*.sh" . \
  | grep -v "SCALAR_workflow/" | grep -v "obsidian_llm_vault/"

# Check for shared configuration
find . -name ".env" -o -name "config.py" -o -name "settings.py" \
  | xargs grep -l "SCALAR" 2>/dev/null
```

**1.2 File Inventory**
```bash
# Create complete file inventory
find SCALAR_workflow -type f > /tmp/scalar_files_inventory.txt

# Categorize by type
cat /tmp/scalar_files_inventory.txt | \
  awk -F. '{print $NF}' | sort | uniq -c | sort -rn

# Identify large files (>10MB)
find SCALAR_workflow -type f -size +10M -exec ls -lh {} \;

# Check for symlinks
find SCALAR_workflow -type l -ls
```

**1.3 External Integration Mapping**
```bash
# Find all external service references
grep -r "http://" SCALAR_workflow --include="*.py" --include="*.env*"
grep -r "api_key" SCALAR_workflow --include="*.py" --include="*.env*"
grep -r "localhost" SCALAR_workflow --include="*.py"

# Map Obsidian vault dependencies
find obsidian_llm_vault -name "*SCALAR*" -type f -o -type d
```

**1.4 Configuration Audit**
```bash
# List all config files
find SCALAR_workflow -name "*.env*" -o -name "*config*" -o -name "*.yml" -o -name "*.yaml"

# Check Docker configuration
find SCALAR_workflow -name "Dockerfile" -o -name "docker-compose.yml"
```

**Outputs:**
- `SCALAR_DEPENDENCY_REPORT.md` - Complete dependency map
- `SCALAR_FILE_INVENTORY.csv` - Categorized file list
- `SCALAR_INTEGRATION_MAP.md` - External integrations
- `SCALAR_EXTRACTION_CHECKLIST.md` - Migration checklist

**Decision Point:** Review analysis → Approve extraction plan or adjust scope

---

### STAGE 2: Extraction Planning (1-2 hours)

**Goal:** Detailed migration plan with rollback strategy

**Tasks:**

**2.1 Create Extraction Blueprint**

**What to Extract (Core):**
- `SCALAR_workflow/` - Entire directory
- `docs/SCALAR_*.md` - All SCALAR documentation
- `scripts/start_scalar_mcp.py` - MCP launcher
- `scripts/activate-scalar.sh` - Activation script
- `scalar_performance_models/` - If exists outside SCALAR_workflow

**What to Handle Specially (Obsidian):**
- **Option A (Symlink):** Keep Obsidian vault in original location, symlink from ~/SCALAR
- **Option B (Copy):** Copy relevant SCALAR documentation to ~/SCALAR/docs/obsidian_export/
- **Option C (Reference):** Document path to Obsidian vault in SCALAR README

**What to Leave Behind:**
- `test_outputs/scalar_*.json` - Test outputs (regenerable)
- `.cache/`, `.mypy_cache/`, `.pytest_cache/` - Cache directories
- `venv_external_tools/` - Virtual environment (recreate)
- Large binary files unless critical

**2.2 Design Directory Structure**

```
~/SCALAR/
├── .claude/                          # Tier1 workflow
│   ├── commands/
│   │   ├── execute-workflow.md      # From template
│   │   └── spec-epic.md             # From template
│   ├── agents/                      # From template
│   ├── agent_briefings/             # SCALAR-specific briefings
│   │   ├── scalar_architecture.md   # NEW: SCALAR system architecture
│   │   └── systematic_review.md     # NEW: Domain expertise
│   └── output-styles/               # Optional: SCALAR-specific styles
├── .tasks/                          # Epic management
│   ├── backlog/
│   ├── current/
│   └── completed/
├── .workflow/                       # Workflow outputs
│   ├── outputs/
│   └── post-mortem/
├── tools/                           # Workflow utilities
│   └── export_conversation_transcript.py  # From template
├── src/                             # SCALAR core (from SCALAR_workflow/)
│   ├── api_gateway/
│   ├── collection_service/
│   ├── analysis_service/
│   ├── modules/                     # 41+ modules
│   ├── models/
│   ├── config/
│   └── scripts/
├── docs/                            # Consolidated documentation
│   ├── SCALAR_TECHNICAL_REFERENCE.md
│   ├── SCALAR_ROADMAP_2025.md
│   ├── ARCHITECTURE.md              # From SCALAR_workflow/
│   ├── README.md                    # Main project README
│   └── migration/                   # Migration documentation
│       ├── EXTRACTION_NOTES.md
│       └── OBSIDIAN_INTEGRATION.md
├── tests/                           # Test suite (from SCALAR_workflow/tests/)
├── scripts/                         # Utility scripts
│   ├── start_scalar_mcp.py
│   └── activate-scalar.sh
├── .env.example                     # Template environment variables
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # Docker stack (if applicable)
└── README.md                        # Project overview
```

**2.3 Define Migration Strategy**

**Approach:** Copy, don't move (preserve original until validated)

1. Create `~/SCALAR/` directory structure
2. Copy files from second_brain to ~/SCALAR (rsync with exclusions)
3. Initialize Git repository in ~/SCALAR
4. Apply tier1 workflow template
5. Update paths and configuration
6. Test in isolation
7. **Only after validation:** Remove from second_brain (optional)

**Rollback Plan:**
- Original second_brain remains untouched
- Delete ~/SCALAR if migration fails
- Zero risk to existing setup

**Outputs:**
- `SCALAR_EXTRACTION_BLUEPRINT.md` - Complete migration plan
- `SCALAR_DIRECTORY_STRUCTURE.md` - Target structure
- `migration_script.sh` - Automated migration script (with dry-run)

**Decision Point:** Review extraction plan → Approve for execution

---

### STAGE 3: Migration Execution (2-4 hours)

**Goal:** Create standalone ~/SCALAR project with tier1 workflow

**Tasks:**

**3.1 Create Base Structure**
```bash
# Create project directory
mkdir -p ~/SCALAR
cd ~/SCALAR

# Initialize Git
git init
echo "# SCALAR: Systematic Review Workflow" > README.md
git add README.md
git commit -m "init: create SCALAR standalone project"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtual environments
venv/
.venv/
env/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
.windsurf/

# Data & cache
*.db
*.sqlite
.cache/
data/
logs/
test_outputs/

# Models (large files)
*.onnx
*.pkl
*.model

# Workflow outputs
.workflow/outputs/
EOF

git add .gitignore
git commit -m "init: add .gitignore"
```

**3.2 Copy SCALAR Core**
```bash
# Dry-run first (verify what will be copied)
rsync -avhn --progress \
  --exclude='.cache' \
  --exclude='.mypy_cache' \
  --exclude='.pytest_cache' \
  --exclude='__pycache__' \
  --exclude='venv*' \
  --exclude='test_outputs' \
  --exclude='*.pyc' \
  ~/coding_projects/projects/01_second_brain/SCALAR_workflow/ \
  ~/SCALAR/src/

# If dry-run looks good, execute
rsync -av --progress \
  --exclude='.cache' \
  --exclude='.mypy_cache' \
  --exclude='.pytest_cache' \
  --exclude='__pycache__' \
  --exclude='venv*' \
  --exclude='test_outputs' \
  --exclude='*.pyc' \
  ~/coding_projects/projects/01_second_brain/SCALAR_workflow/ \
  ~/SCALAR/src/

# Copy documentation
mkdir -p ~/SCALAR/docs
cp ~/coding_projects/projects/01_second_brain/docs/SCALAR_*.md ~/SCALAR/docs/
cp ~/coding_projects/projects/01_second_brain/SCALAR_WORKFLOW_INTEGRATION_PLAN.md ~/SCALAR/docs/

# Copy scripts
mkdir -p ~/SCALAR/scripts
cp ~/coding_projects/projects/01_second_brain/scripts/start_scalar_mcp.py ~/SCALAR/scripts/
cp ~/coding_projects/projects/01_second_brain/scripts/activate-scalar.sh ~/SCALAR/scripts/

# Commit core extraction
git add .
git commit -m "extract: copy SCALAR core from 01_second_brain"
```

**3.3 Apply Tier1 Workflow Template**
```bash
# Copy tier1 workflow structure
cp -r ~/tier1_workflow_global/template/.claude ~/SCALAR/
cp -r ~/tier1_workflow_global/template/.tasks ~/SCALAR/
mkdir -p ~/SCALAR/.workflow/{outputs,post-mortem}
cp ~/tier1_workflow_global/template/tools/export_conversation_transcript.py ~/SCALAR/tools/

# Customize for SCALAR
cd ~/SCALAR

# Create SCALAR-specific agent briefings
mkdir -p .claude/agent_briefings

cat > .claude/agent_briefings/scalar_architecture.md << 'EOF'
# SCALAR System Architecture Briefing

## Overview
SCALAR is a production-ready systematic review workflow system with:
- Microservice architecture (API gateway, collection service, analysis service)
- 26 MCP tools for LibreChat integration
- LangGraph-based orchestration
- 41+ specialized modules

## Architecture Layers
1. **API Gateway**: FastAPI router with authentication
2. **Collection Service**: Multi-database literature search
3. **Analysis Service**: Citation analysis, meta-analysis
4. **Orchestration**: LangGraph workflow management
5. **Integrations**: MCP server, Obsidian, Zotero

## Key Directories
- `src/modules/`: 41+ modules (orchestration, AI research, citation analysis, etc.)
- `src/api_gateway/`: API routing
- `src/models/`: ONNX models for ML
- `src/config/`: Configuration management

## Development Guidelines
- Python 3.10+
- FastAPI for APIs
- LangGraph for workflows
- Pytest for testing
- Docker for deployment

## Common Patterns
- Async/await for I/O
- Pydantic models for validation
- Dependency injection
- Comprehensive error handling
EOF

cat > .claude/agent_briefings/systematic_review_domain.md << 'EOF'
# Systematic Review Domain Expertise

## Domain: Systematic Literature Review

SCALAR implements the systematic review methodology used in biomedical research:

1. **Collection Stage**: Search databases, screen studies
2. **Analysis Stage**: Extract data, assess quality, analyze citations
3. **Articulation Stage**: Synthesize evidence, generate reports

## Key Concepts
- **PICO**: Population, Intervention, Comparison, Outcome
- **PRISMA**: Reporting standard for systematic reviews
- **Meta-analysis**: Statistical synthesis of study results
- **Risk of Bias**: Quality assessment frameworks (RoB2, GRADE, Newcastle-Ottawa)
- **Living Reviews**: Continuously updated reviews

## Critical Domain Knowledge
- PubMed/MEDLINE search syntax
- Citation network analysis
- Publication bias detection
- Evidence grading systems
- Study screening workflows

## SCALAR-Specific
- 16 database integrations
- Automated PICO extraction
- AI-powered quality assessment
- Living review surveillance
EOF

# Commit tier1 setup
git add .
git commit -m "setup: apply tier1 workflow template"
```

**3.4 Update Configuration**
```bash
cd ~/SCALAR/src

# Update paths in configuration
# (This will need manual review based on Stage 1 analysis)

# Example: Update absolute paths to relative
find . -name "*.py" -type f -exec grep -l "01_second_brain" {} \; | \
  while read file; do
    echo "File with absolute paths: $file"
  done

# Create .env.example for documentation
cat > ../.env.example << 'EOF'
# SCALAR Configuration Template

# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database APIs
PUBMED_API_KEY=optional
OPENALEX_EMAIL=your_email@domain.com

# MCP Server
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost

# Obsidian Integration (if using symlink approach)
OBSIDIAN_VAULT_PATH=/home/andreas-spannbauer/coding_projects/projects/01_second_brain/obsidian_llm_vault

# Feature Flags
ENABLE_SURVEILLANCE=true
ENABLE_LIVING_REVIEWS=true
EOF

# Commit configuration
git add ../.env.example
git commit -m "config: create .env.example template"
```

**3.5 Handle Obsidian Integration**

**Option A: Symlink (Recommended for initial setup)**
```bash
cd ~/SCALAR/docs
ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault/SCALAR_METHOD_DOCUMENTATION obsidian_scalar_docs
ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault/SCALAR_PROJECT_EXTERNAL_LLM_OUTPUTS obsidian_outputs

# Document the symlink approach
cat > docs/OBSIDIAN_INTEGRATION.md << 'EOF'
# Obsidian Vault Integration

SCALAR documentation is maintained in the Obsidian vault at:
`~/coding_projects/projects/01_second_brain/obsidian_llm_vault/`

## Symlinks
- `docs/obsidian_scalar_docs/` → `SCALAR_METHOD_DOCUMENTATION/`
- `docs/obsidian_outputs/` → `SCALAR_PROJECT_EXTERNAL_LLM_OUTPUTS/`

## Rationale
Obsidian vault remains in original location to preserve:
- Cross-project links
- Obsidian plugin functionality
- Git history

## Alternative: Full Extraction
If full extraction is desired, copy Obsidian SCALAR docs to `docs/obsidian_export/`
and update .env to point to new location.
EOF

git add .
git commit -m "docs: add Obsidian integration via symlinks"
```

**Outputs:**
- `~/SCALAR/` - Standalone project
- Git repository initialized
- Tier1 workflow applied
- Configuration updated
- Initial commit created

**Decision Point:** Test basic functionality → Proceed to validation

---

### STAGE 4: Validation & Testing (2-3 hours)

**Goal:** Verify SCALAR works standalone and tier1 workflow is functional

**Tasks:**

**4.1 Environment Setup Test**
```bash
cd ~/SCALAR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Test imports
python3 -c "import sys; sys.path.insert(0, 'src'); from modules.orchestration import workflow_manager; print('✅ Imports working')"
```

**4.2 Configuration Validation**
```bash
# Test configuration loading
cd ~/SCALAR/src
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from config import settings  # Adjust based on actual config module
print(f"✅ Configuration loaded: {settings}")
EOF
```

**4.3 MCP Server Test**
```bash
cd ~/SCALAR/scripts
python3 start_scalar_mcp.py --test-mode

# Expected output: MCP server starts without errors
```

**4.4 Test Suite Execution**
```bash
cd ~/SCALAR/src
pytest tests/ -v --tb=short

# Expected: Tests run (may have failures due to environment, but should execute)
```

**4.5 Tier1 Workflow Test**
```bash
cd ~/SCALAR

# Test spec-epic command
/spec-epic "Test SCALAR Workflow Setup"

# Expected: Epic creation works, pattern library consulted
```

**4.6 Documentation Review**
```bash
# Verify documentation is accessible
ls -la ~/SCALAR/docs/
cat ~/SCALAR/docs/README.md  # If created

# Check Obsidian symlinks
ls -la ~/SCALAR/docs/obsidian_scalar_docs/
```

**Validation Checklist:**
- [ ] Python environment activates
- [ ] Dependencies install without errors
- [ ] Core imports work
- [ ] Configuration loads
- [ ] MCP server starts
- [ ] Test suite executes (at least partially)
- [ ] Tier1 workflow commands available
- [ ] Documentation accessible
- [ ] Obsidian links intact (if using symlinks)

**Outputs:**
- `SCALAR_VALIDATION_REPORT.md` - Test results
- `SCALAR_KNOWN_ISSUES.md` - Issues discovered during validation
- `SCALAR_NEXT_STEPS.md` - Recommended actions

**Decision Point:** If validation passes → Project is ready for active development

---

## 4. Post-Migration Tasks

### 4.1 Immediate (Day 1)

**Create First Epic**
```bash
cd ~/SCALAR
/spec-epic "SCALAR Revival: Update Dependencies and Test Suite"

# This epic should:
# - Update Python dependencies
# - Fix any broken imports
# - Run full test suite
# - Document current state
```

**Update Global CLAUDE.md**
- Add SCALAR project to project list
- Document Obsidian integration approach
- Note any special considerations

**Create Project README**
```markdown
# SCALAR: Systematic Review Workflow

Production-ready systematic review automation system.

## Quick Start
...

## Tier1 Workflow
This project uses the tier1 epic-driven workflow.
See `.claude/commands/` for available commands.

## Documentation
- Technical Reference: `docs/SCALAR_TECHNICAL_REFERENCE.md`
- Roadmap: `docs/SCALAR_ROADMAP_2025.md`
- Architecture: `docs/ARCHITECTURE.md`

## Obsidian Integration
See `docs/OBSIDIAN_INTEGRATION.md` for details.
```

### 4.2 Short-term (Week 1)

**Clean Up Second Brain (Optional)**
- After confirming ~/SCALAR works, optionally archive SCALAR components in second_brain
- Document what was removed in second_brain README

**Set Up Development Environment**
- Configure IDE for ~/SCALAR
- Set up pre-commit hooks
- Configure linting (ruff, mypy)

**Update Dependencies**
- Review and update requirements.txt
- Test with latest package versions
- Document any breaking changes

### 4.3 Medium-term (Month 1)

**Create Development Roadmap**
- Convert SCALAR_ROADMAP_2025.md tasks to epics
- Prioritize features for active development
- Set milestones

**Enhance Documentation**
- Create comprehensive README
- Add architecture diagrams
- Write contributor guide

**Set Up CI/CD**
- GitHub Actions for testing
- Docker image builds
- Automated deployment (if applicable)

---

## 5. Decision Matrix

### Option 1: Full Extraction (Recommended)

**Pros:**
- Clean separation
- Independent development
- Easier to apply tier1 workflow
- No cross-project dependencies

**Cons:**
- Requires careful migration
- Potential configuration updates
- Need to handle Obsidian integration

**Effort:** 6-10 hours total
**Risk:** Low (copy, don't move)

### Option 2: In-Place Tier1 Workflow

**Pros:**
- No file migration
- Preserve all integrations

**Cons:**
- SCALAR remains nested in second_brain
- Harder to manage as standalone project
- Confusing project structure

**Effort:** 2-3 hours
**Risk:** Low

**Recommendation:** **Option 1 (Full Extraction)** - cleaner long-term solution

---

## 6. Resource Requirements

### Time Estimates

| Stage | Optimistic | Realistic | Pessimistic |
|-------|-----------|-----------|-------------|
| Stage 1: Analysis | 1 hour | 2 hours | 3 hours |
| Stage 2: Planning | 1 hour | 2 hours | 3 hours |
| Stage 3: Migration | 2 hours | 4 hours | 6 hours |
| Stage 4: Validation | 2 hours | 3 hours | 5 hours |
| **Total** | **6 hours** | **11 hours** | **17 hours** |

**Recommended:** Budget 2-3 full working sessions (mornings or afternoons)

### Skills Required

- Python project structure understanding
- Git proficiency
- Bash scripting
- Understanding of SCALAR architecture (from docs)
- Familiarity with tier1 workflow

---

## 7. Success Criteria

**Migration Success:**
- [ ] ~/SCALAR directory created with tier1 workflow
- [ ] All core SCALAR files extracted
- [ ] Configuration updated for new paths
- [ ] Git repository initialized
- [ ] Documentation consolidated

**Functionality Success:**
- [ ] Python environment activates
- [ ] Core imports work
- [ ] MCP server starts
- [ ] Test suite runs (even if with failures)
- [ ] Tier1 workflow commands available

**Integration Success:**
- [ ] Obsidian vault accessible (symlink or copy)
- [ ] MCP server connects
- [ ] External APIs configurable

---

## 8. Rollback Strategy

**If migration fails at any stage:**

1. Delete ~/SCALAR directory:
   ```bash
   rm -rf ~/SCALAR
   ```

2. Original second_brain remains untouched (we copied, didn't move)

3. Re-evaluate approach:
   - Consider Option 2 (in-place tier1)
   - Break migration into smaller chunks
   - Seek additional analysis

**Risk:** MINIMAL (non-destructive copy approach)

---

## 9. Next Steps for User

**To proceed, user should:**

1. **Review this plan** - Does the approach make sense?

2. **Choose option:**
   - **Option A:** Full 4-stage migration (recommended, 10-15 hours)
   - **Option B:** In-place tier1 workflow (quicker, 2-3 hours)
   - **Option C:** Defer until more convenient time

3. **If Option A, decide on Obsidian handling:**
   - **Symlink approach** (keep vault in second_brain)
   - **Copy approach** (extract to ~/SCALAR/docs/)
   - **Reference approach** (document path only)

4. **Schedule time:**
   - Stage 1 (Analysis): 2 hours
   - Stage 2 (Planning): 2 hours
   - Stage 3 (Migration): 4 hours
   - Stage 4 (Validation): 3 hours
   - **Total:** 11 hours across 2-3 sessions

5. **Approve to start Stage 1** (Deep Analysis)

---

## 10. Appendix: SCALAR Project Statistics

**Discovered from analysis:**

- **Total size:** 30GB
- **Python files:** 18,175
- **Microservices:** 3 (API gateway, collection, analysis)
- **Modules:** 41+
- **MCP tools:** 26
- **Test functions:** 480+
- **Documentation files:** 15+
- **Obsidian notes:** 10+ directories
- **API integrations:** 16 databases
- **Version:** 2.2 (production-ready)

**Key technologies:**
- Python 3.10+
- FastAPI
- LangGraph (orchestration)
- ONNX (ML models)
- Docker
- Prometheus/Grafana (observability)
- MCP server

---

**End of Extraction & Revival Plan**

**Status:** DRAFT - Awaiting user approval for Stage 1 (Deep Analysis)
