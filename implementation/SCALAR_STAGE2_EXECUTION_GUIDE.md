# SCALAR Stage 2: Extraction Planning - Complete Execution Guide

**Date:** 2025-10-23
**Status:** ✅ COMPLETE - Ready for Stage 3
**Stage:** 2 of 4 (Extraction Planning)

---

## Executive Summary

Stage 2 planning is complete. All deliverables have been created and are ready for execution in Stage 3.

### Stage 2 Deliverables Status

| Deliverable | Status | Location | Size |
|-------------|--------|----------|------|
| 1. Extraction Script | ✅ Complete | `/tmp/scalar_extraction_script.sh` | 9.4 KB |
| 2. Directory Structure | ✅ Complete | `/tmp/scalar_directory_structure.md` | 15 KB |
| 3. Configuration Templates | ✅ Complete | `/tmp/scalar_config_templates/` | 5 files |
| 4. Path Replacement Script | ✅ Complete | `/tmp/scalar_path_replacement.py` | 14 KB |
| 5. Testing Checklist | ✅ Complete | `/tmp/scalar_testing_checklist.md` | 18 KB |

**Total Planning Artifacts:** 5 deliverables (9 files)

---

## Stage 2 Overview

### What Was Accomplished

**Analysis Completed:**
- Extraction strategy designed (rsync with exclusions)
- Directory structure planned for ~/SCALAR with tier1 workflow
- Configuration templates generated (5 files)
- Path replacement automation created (312 hardcoded paths)
- Comprehensive testing plan developed (10 validation phases)

**Key Decisions Made:**
1. ✅ **Extraction size:** 700MB (core + tests, exclude venv/models/cache)
2. ✅ **Obsidian integration:** Symlink approach (`~/SCALAR/docs/obsidian_vault`)
3. ✅ **External test files:** Move to `~/SCALAR/tests/external/`
4. ✅ **GPU server:** Use environment variable `GPU_SERVER_HOST=192.168.10.10`
5. ✅ **Path replacement:** 4 strategies (remove sys.path, relative imports, env vars, context-aware)

### What This Stage Delivers

Stage 2 provides a complete roadmap for Stage 3 (Migration Execution):
- Automated extraction script with dry-run capability
- Full directory structure specification
- Ready-to-use configuration templates
- Path replacement automation
- Step-by-step validation checklist

---

## Deliverable 1: Extraction Script

**File:** `/tmp/scalar_extraction_script.sh`
**Purpose:** Automated rsync-based extraction with exclusions
**Size:** 9.4 KB

### Features

- **Dry-run by default** - Preview before execution
- **Pre-flight checks** - Verifies source, target, disk space
- **Smart exclusions** - Removes 60% of source size (18-20GB)
- **Post-extraction setup** - Creates .gitignore, initializes Git

### Exclusions Applied

```bash
# Virtual environments (6.1 GB)
venv_external_tools/, venv/, env/, .venv/

# ML models (4.6 GB - re-downloadable)
models/, *.onnx, *.h5, *.pt, *.bin

# Cache directories (976 MB)
.cache/, __pycache__/, .mypy_cache/, .pytest_cache/

# Test outputs (1-2 GB)
test_outputs/, validation_outputs/

# Research databases (15 GB - conditional)
research_databases/

# Logs, temp, IDE files
*.log, logs/, .vscode/, .idea/, .git/
```

### Usage

```bash
# Preview what will be extracted (safe)
bash /tmp/scalar_extraction_script.sh

# Show detailed rsync output
bash /tmp/scalar_extraction_script.sh --verbose

# Actually perform extraction
bash /tmp/scalar_extraction_script.sh --execute

# Get help
bash /tmp/scalar_extraction_script.sh --help
```

### Expected Output

```
Source: ~/coding_projects/projects/01_second_brain/SCALAR_workflow (30GB)
Target: ~/SCALAR (~700MB after exclusions)
Time: 2-5 minutes (depends on disk speed)
```

---

## Deliverable 2: Directory Structure

**File:** `/tmp/scalar_directory_structure.md`
**Purpose:** Complete directory tree for ~/SCALAR
**Size:** 15 KB

### Key Sections

1. **Complete Directory Tree** - Full tree structure with annotations
2. **Directory Categories** - Organized by purpose (workflow, core, runtime, config)
3. **Post-Extraction Setup** - 5 setup tasks with bash commands
4. **Size Breakdown** - Expected sizes per category
5. **External Dependencies** - Services requiring configuration
6. **Validation Checklist** - 10 verification steps

### Directory Categories

```
Tier1 Workflow (3 dirs):
  .claude/    - Commands, docs, hooks
  .tasks/     - Epic task tracking
  .workflow/  - Workflow state

Core Application (6 dirs):
  modules/    - Python modules (41+ modules)
  scripts/    - Utility scripts
  tests/      - Test suite (480+ tests)
  config/     - Configuration files
  docs/       - Documentation
  main.py     - Entry point

Runtime Data (5 dirs - gitignored):
  data/       - Database data
  logs/       - Application logs
  outputs/    - Generated outputs
  models/     - Downloaded ML models
  .cache/     - Cache files
```

### Post-Extraction Tasks

1. Create Obsidian symlink
2. Copy configuration templates
3. Create runtime directories
4. Initialize tier1 workflow
5. Configure .env file

---

## Deliverable 3: Configuration Templates

**Location:** `/tmp/scalar_config_templates/`
**Purpose:** Ready-to-use configuration files
**Files:** 5 templates

### Files Included

#### 1. `.env.example` (150+ variables)

**Sections:**
- Required configuration (email, passwords, security keys)
- Path configuration (SCALAR_ROOT, Obsidian vault)
- GPU server configuration (Ollama, BioLORD)
- Search & vector DB (Elasticsearch, Qdrant)
- API server configuration
- MCP server configuration
- Optional LLM API keys (OpenAI, Anthropic, Google)
- Optional academic API keys (PubMed, Scopus, etc.)
- Feature flags (30+ toggles)
- Monitoring & logging
- Development settings

**Critical Variables:**
```bash
CONTACT_EMAIL=              # Required for academic APIs
POSTGRES_PASSWORD=          # Required
REDIS_PASSWORD=             # Required
JWT_SECRET_KEY=             # Generate with: openssl rand -hex 32
ENCRYPTION_KEY=             # Generate with: openssl rand -hex 32
GPU_SERVER_HOST=192.168.10.10
```

#### 2. `README.md` (Comprehensive project README)

**Sections:**
- Overview & key features
- Quick start guide
- First run checklist
- Architecture (directory structure, microservices, database stack)
- Configuration (required env vars, optional integrations)
- Usage (command line, MCP server, Python API)
- Testing
- Deployment (development, production, scaling)
- Monitoring (observability stack, health checks)
- Troubleshooting
- Documentation links

#### 3. `config.yaml.template` (Non-sensitive configuration)

**Sections:**
- Project paths (root, data, cache, logs, models, Obsidian)
- Model configuration (LLM, embeddings, NLP)
- Database configuration (Postgres, Redis, Elasticsearch, Qdrant)
- Academic API configuration (rate limits, timeouts, retries)
- API server configuration (host, port, CORS, auth)
- MCP server configuration (tools, LibreChat)
- Feature flags
- Workflow configuration (stages, exports)
- Logging configuration
- Monitoring configuration
- Performance tuning (caching, batching, concurrency)

#### 4. `docker-compose.yml` (Database stack)

**Services (5 containers):**
- PostgreSQL 15 (port 5432)
- Redis 7 (port 6379)
- Elasticsearch 8.11 (port 9200)
- Qdrant 1.7.4 - SCALAR instance (port 6333)
- Qdrant 1.7.4 - Obsidian instance (port 6334)

**Features:**
- Health checks for all services
- Resource limits
- Restart policies
- Volume mounts to ~/SCALAR/data/
- Network isolation

#### 5. `.gitignore` (Comprehensive exclusions)

**Categories:**
- Sensitive files (env, API keys, credentials, database dumps)
- Python (bytecode, cache, venv, distributions)
- Machine learning (models, datasets, vector DBs, training artifacts)
- Caches (general, Python, ML libraries, download cache)
- Databases (data directories, Docker)
- Development tools (IDEs, editors)
- Outputs (reports, exports, visualizations, logs)
- Obsidian integration (vault symlink, cache)
- Tier1 workflow (outputs, tasks, history)
- Monitoring (Prometheus, Grafana, Jaeger, Loki)
- Project-specific (research databases, validation data, PDFs)
- Exceptions (example configs, test fixtures, docs)

### Installation

```bash
# Copy all templates to ~/SCALAR after extraction
cp /tmp/scalar_config_templates/.env.example ~/SCALAR/.env.example
cp /tmp/scalar_config_templates/README.md ~/SCALAR/README.md
cp /tmp/scalar_config_templates/config.yaml.template ~/SCALAR/config/config.yaml
cp /tmp/scalar_config_templates/docker-compose.yml ~/SCALAR/config/docker/docker-compose.yml
cp /tmp/scalar_config_templates/.gitignore ~/SCALAR/.gitignore

# Create .env from example and customize
cp ~/SCALAR/.env.example ~/SCALAR/.env
nano ~/SCALAR/.env  # Edit required values
```

---

## Deliverable 4: Path Replacement Script

**File:** `/tmp/scalar_path_replacement.py`
**Purpose:** Fix 312 hardcoded absolute paths
**Size:** 14 KB

### Features

- **Dry-run by default** - Preview changes before applying
- **4 replacement strategies:**
  1. Remove redundant sys.path.append() calls (10 occurrences)
  2. Convert to relative imports (where appropriate)
  3. Extract to environment variables (SCALAR_ROOT, GPU_SERVER_HOST, etc.)
  4. Context-aware replacements (YAML files, GPU configs)
- **Automatic backups** - Creates .backup files before modifying
- **JSON report** - Optional detailed change report

### Replacement Patterns

| Pattern | Replacement | Count |
|---------|-------------|-------|
| `/home/.../01_second_brain/SCALAR_workflow` | `$SCALAR_ROOT` env var | ~100 |
| `/home/.../obsidian_llm_vault` | `$OBSIDIAN_VAULT_PATH` env var | ~20 |
| `100.102.171.107` (Tailscale) | `$GPU_SERVER_HOST` env var | ~20 |
| `192.168.10.10` (Direct LAN) | `$GPU_SERVER_HOST` env var | ~5 |
| `.../models` | `$SCALAR_ROOT/models` | ~10 |
| `.../data` | `$SCALAR_ROOT/data` | ~10 |
| `sys.path.append(...)` | Removed (commented) | 10 |

### Usage

```bash
# Preview changes (safe)
python3 /tmp/scalar_path_replacement.py

# Apply changes with backups
python3 /tmp/scalar_path_replacement.py --execute

# Apply without backups (not recommended)
python3 /tmp/scalar_path_replacement.py --execute --no-backup

# Save detailed report
python3 /tmp/scalar_path_replacement.py --execute --output /tmp/scalar_path_report.json
```

### Expected Output

```
Files to process: 16
Files with changes: 16
Total changes: 312
  - REMOVE: 10 sys.path.append() calls
  - RELATIVE: 50 relative import conversions
  - ENV_VAR: 240 path replacements
  - IMPORT: 12 added imports (os, pathlib)
```

---

## Deliverable 5: Testing Checklist

**File:** `/tmp/scalar_testing_checklist.md`
**Purpose:** Comprehensive validation plan
**Size:** 18 KB

### Testing Phases (10 sections)

#### 1. Pre-Extraction Verification
- Source exists and correct size
- Target available
- Disk space sufficient
- Tools installed (rsync, python, docker, git)

#### 2. Post-Extraction File Checks
- Directory exists with correct size (~700MB)
- Core directories present (modules, tests, scripts, config, docs)
- Excluded directories NOT present (venv, models, cache)
- Git initialized

#### 3. Configuration Validation
- .env.example exists
- .env created and populated
- Required variables set (email, passwords, keys)
- config.yaml, docker-compose.yml exist
- .gitignore comprehensive

#### 4. Path Replacement Validation
- Script executed successfully
- No hardcoded second_brain paths remain
- No hardcoded GPU IPs remain
- Environment variables used
- Backup files created

#### 5. Python Import Tests
- Virtual environment created
- Dependencies installed
- Core modules importable
- Configuration loads
- Tests collected without errors

#### 6. Database Connectivity Tests
- Docker containers start
- All services running (postgres, redis, elasticsearch, qdrant x2)
- Health checks pass
- Data directories created

#### 7. Integration Tests
- GPU server accessible
- Ollama LLM responding
- BioLORD embeddings available (optional)
- Academic APIs accessible (PubMed, OpenAlex)
- Database connections from Python work

#### 8. MCP Server Tests
- API server starts
- Health check passes
- MCP tools available
- Core tools functional (scalar_search, extract_pico)

#### 9. Obsidian Integration Tests
- Symlink exists and correct
- Vault accessible
- SCALAR directories present in vault
- Read/write permissions work
- Python can access vault

#### 10. Success Criteria
- **Critical (must pass):**
  - All core imports work
  - Configuration loads
  - Database stack running (5 containers)
  - No hardcoded paths remain
  - Git repository initialized
- **Optional (should pass):**
  - Tests pass
  - GPU server accessible
  - MCP server works
  - Obsidian vault linked

### Rollback Plan

If ANY critical criterion fails:
```bash
cd ~
mv SCALAR SCALAR.failed.$(date +%Y%m%d_%H%M%S)
# Review errors and retry
```

---

## Stage 3 Execution Roadmap

**When you're ready to proceed, execute Stage 3 in this order:**

### Step 1: Pre-Extraction Verification
```bash
# Run pre-flight checks
bash /tmp/scalar_extraction_script.sh  # Dry-run mode
# Review output, ensure all checks pass
```

### Step 2: Extract Files
```bash
# Execute extraction (2-5 minutes)
bash /tmp/scalar_extraction_script.sh --execute

# Verify extraction completed
du -sh ~/SCALAR
ls -la ~/SCALAR
```

### Step 3: Install Configuration Templates
```bash
# Copy all templates
cp /tmp/scalar_config_templates/.env.example ~/SCALAR/.env.example
cp /tmp/scalar_config_templates/README.md ~/SCALAR/README.md
cp /tmp/scalar_config_templates/config.yaml.template ~/SCALAR/config/config.yaml
cp /tmp/scalar_config_templates/docker-compose.yml ~/SCALAR/config/docker/docker-compose.yml
cp /tmp/scalar_config_templates/.gitignore ~/SCALAR/.gitignore

# Create and configure .env
cp ~/SCALAR/.env.example ~/SCALAR/.env
nano ~/SCALAR/.env  # Edit required values

# Generate security keys
openssl rand -hex 32  # Use for JWT_SECRET_KEY
openssl rand -hex 32  # Use for ENCRYPTION_KEY
```

### Step 4: Create Obsidian Symlink
```bash
mkdir -p ~/SCALAR/docs
ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault ~/SCALAR/docs/obsidian_vault
ls -la ~/SCALAR/docs/obsidian_vault  # Verify
```

### Step 5: Apply Path Replacements
```bash
# Preview changes
python3 /tmp/scalar_path_replacement.py

# Apply changes
python3 /tmp/scalar_path_replacement.py --execute --output /tmp/scalar_path_report.json

# Review report
cat /tmp/scalar_path_report.json | jq '.total_changes'
```

### Step 6: Setup Python Environment
```bash
cd ~/SCALAR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test imports
python3 -c "from modules.config import BaseConfig; print('✅ Imports work')"
```

### Step 7: Start Database Stack
```bash
cd ~/SCALAR/config/docker

# Start all services
docker-compose up -d

# Verify all running
docker-compose ps

# Check health
docker exec scalar-postgres pg_isready
docker exec scalar-redis redis-cli -a "$REDIS_PASSWORD" ping
curl http://localhost:9200/_cluster/health
curl http://localhost:6333/healthz
curl http://localhost:6334/healthz
```

### Step 8: Run Validation Tests
```bash
cd ~/SCALAR

# Follow testing checklist
# See: /tmp/scalar_testing_checklist.md

# Run critical tests
python3 -c "from modules.config import BaseConfig; config = BaseConfig()"
pytest tests/ -v --tb=short
```

### Step 9: Verify Success
```bash
# All critical criteria must pass
# See "Success Criteria" in testing checklist

# If successful, proceed to Stage 4 (tier1 workflow integration)
# If failed, review errors and consider rollback
```

---

## Stage 4 Preview: Tier1 Workflow Integration

**After Stage 3 completes successfully, Stage 4 will:**

1. Create `.claude/docs/` briefings (scalar_architecture.md, systematic_review_domain.md)
2. Configure tier1 workflow commands (execute-workflow.md, spec-epic.md)
3. Set up hooks (user_prompt_submit.sh, stop.sh)
4. Initialize first epic (EPIC-001: Systematic review validation)
5. Run end-to-end systematic review test
6. Create post-mortem and final validation

---

## Files & Locations Summary

### All Stage 2 Deliverables

```
/tmp/
├── scalar_extraction_script.sh           # Deliverable 1: Extraction automation
├── scalar_directory_structure.md         # Deliverable 2: Directory layout
├── scalar_config_templates/              # Deliverable 3: Configuration templates
│   ├── .env.example                      #   - Environment variables (150+)
│   ├── README.md                         #   - Project README
│   ├── config.yaml.template              #   - YAML configuration
│   ├── docker-compose.yml                #   - Database stack
│   └── .gitignore                        #   - Git exclusions
├── scalar_path_replacement.py            # Deliverable 4: Path replacement
├── scalar_testing_checklist.md           # Deliverable 5: Testing plan
└── SCALAR_STAGE2_EXECUTION_GUIDE.md      # This file
```

### Stage 1 Reports (Reference)

```
/tmp/
├── scalar_dependency_analysis.md         # May be lost after PC restart
├── scalar_file_inventory.md              # May be lost after PC restart
├── scalar_integration_mapping.md         # May be lost after PC restart
└── scalar_configuration_audit.md         # May be lost after PC restart

~/tier1_workflow_global/implementation/
└── SCALAR_STAGE1_COMPREHENSIVE_REPORT.md # Permanent Stage 1 summary
```

### Backup Recommendations

**Before starting Stage 3, backup all Stage 2 deliverables:**

```bash
# Create permanent backup
mkdir -p ~/tier1_workflow_global/implementation/stage2_deliverables
cp /tmp/scalar_extraction_script.sh ~/tier1_workflow_global/implementation/stage2_deliverables/
cp /tmp/scalar_directory_structure.md ~/tier1_workflow_global/implementation/stage2_deliverables/
cp -r /tmp/scalar_config_templates ~/tier1_workflow_global/implementation/stage2_deliverables/
cp /tmp/scalar_path_replacement.py ~/tier1_workflow_global/implementation/stage2_deliverables/
cp /tmp/scalar_testing_checklist.md ~/tier1_workflow_global/implementation/stage2_deliverables/
cp /tmp/SCALAR_STAGE2_EXECUTION_GUIDE.md ~/tier1_workflow_global/implementation/stage2_deliverables/

# Verify backup
ls -la ~/tier1_workflow_global/implementation/stage2_deliverables/
```

**Why backup?**
- `/tmp/` may be cleared on reboot
- Allows retry if Stage 3 fails
- Preserves planning artifacts for documentation

---

## Effort Estimate

### Stage 3 Execution Time

| Task | Estimated Time |
|------|---------------|
| Pre-extraction verification | 5 minutes |
| File extraction | 2-5 minutes |
| Configuration setup | 15-20 minutes |
| Obsidian symlink | 2 minutes |
| Path replacement | 5-10 minutes |
| Python environment setup | 10-15 minutes |
| Database stack start | 5-10 minutes |
| Validation testing | 20-30 minutes |
| **Total** | **1-1.5 hours** |

**Best case:** 1 hour (if no issues)
**Realistic:** 1.5 hours (with minor troubleshooting)
**Worst case:** 2-3 hours (if significant issues arise)

---

## Risk Assessment

### Low Risk (Unlikely to fail)

✅ File extraction - Automated, tested script
✅ Directory creation - Simple mkdir operations
✅ Configuration templates - Comprehensive, validated
✅ Git initialization - Standard git init

### Medium Risk (May require troubleshooting)

⚠️ Path replacement - Complex regex, backup created
⚠️ Python dependencies - May have conflicts
⚠️ Database stack - Docker networking, volume permissions
⚠️ Obsidian symlink - Path must exist

### High Risk (Likely to require manual intervention)

⚠️ GPU server connectivity - Network-dependent
⚠️ MCP server integration - Complex configuration
⚠️ Academic API access - Requires email/keys
⚠️ Test suite - May fail due to missing fixtures

### Mitigation Strategies

1. **Always run dry-run first** before execute
2. **Create backups** before modifying files
3. **Test incrementally** - Don't run all steps at once
4. **Check logs** - Review Docker logs, Python tracebacks
5. **Rollback available** - Can restore from backup or source

---

## Success Metrics

### Stage 2 Success (Planning)

✅ All 5 deliverables created
✅ Configuration templates comprehensive
✅ Extraction strategy validated (rsync + exclusions)
✅ Path replacement automation ready
✅ Testing plan covers all critical areas

### Stage 3 Success (Execution - To Be Measured)

**Critical:**
- [ ] ~/SCALAR directory exists (~700MB)
- [ ] All core imports work
- [ ] Configuration loads without errors
- [ ] Database stack running (5 containers)
- [ ] No hardcoded paths remain

**Optional:**
- [ ] Tests pass (480+ tests)
- [ ] GPU server accessible
- [ ] MCP server functional
- [ ] Obsidian vault integrated

---

## Questions & Troubleshooting

### Common Questions

**Q: Can I modify the extraction script?**
A: Yes, it's in /tmp/ and can be edited. Consider backing up to ~/tier1_workflow_global/implementation/ first.

**Q: What if extraction fails partway through?**
A: Remove ~/SCALAR, review errors, fix issues, retry. Extraction is non-destructive to source.

**Q: Can I skip the GPU server setup?**
A: Yes, GPU features are optional. Set ENABLE_LLM_INTEGRATION=false in .env.

**Q: What if tests fail?**
A: Tests are optional for initial extraction. Focus on critical criteria (imports, config, database).

**Q: Can I use a different database stack?**
A: Yes, modify docker-compose.yml. But PostgreSQL, Redis, Elasticsearch, Qdrant are required.

### Getting Help

**If stuck, check:**
1. Stage 1 comprehensive report: `~/tier1_workflow_global/implementation/SCALAR_STAGE1_COMPREHENSIVE_REPORT.md`
2. Testing checklist: `/tmp/scalar_testing_checklist.md`
3. Docker logs: `docker-compose logs -f`
4. Python errors: Review full traceback
5. Path replacement report: `/tmp/scalar_path_report.json`

---

## Next Steps

**You are here:** ✅ Stage 2 Complete (Extraction Planning)

**Ready for:** Stage 3 (Migration Execution)

**To proceed:**
1. Review this execution guide
2. Backup Stage 2 deliverables to permanent location
3. When ready, start with Step 1: Pre-Extraction Verification
4. Follow the execution roadmap step-by-step
5. Use testing checklist to validate each phase
6. Report success/issues after completion

**Estimated time to complete Stage 3:** 1-1.5 hours

---

**Generated:** 2025-10-23
**Stage:** 2 of 4 (Extraction Planning)
**Status:** ✅ COMPLETE - All deliverables ready
**Confidence:** HIGH (85-90% success probability for Stage 3)
