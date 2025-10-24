# SCALAR Directory Structure

**Target Location:** `~/SCALAR/`
**Purpose:** Standalone SCALAR project with tier1 workflow integration

---

## Complete Directory Tree

```
~/SCALAR/
├── .claude/                              # Tier1 workflow integration
│   ├── commands/                         # Slash commands
│   │   ├── execute-workflow.md          # Main workflow orchestrator
│   │   ├── spec-epic.md                 # Epic specification
│   │   ├── commit-epic.md               # Epic commit workflow
│   │   ├── review-code.md               # Code review
│   │   └── review-architecture.md       # Architecture review
│   ├── docs/                            # Agent briefings
│   │   ├── scalar_architecture.md       # SCALAR architecture guide
│   │   ├── systematic_review_domain.md  # Domain knowledge
│   │   └── agent_guidelines.md          # Best practices
│   ├── hooks/                           # Claude Code hooks
│   │   ├── user_prompt_submit.sh        # Pre-prompt hook
│   │   └── stop.sh                      # Post-response hook
│   ├── output-styles/                   # Custom output styles
│   │   └── scientific.md                # Scientific writing style
│   └── settings.local.json              # Project settings
├── .tasks/                              # Epic task tracking
│   ├── EPIC-001_description.md          # Epic descriptions
│   └── .gitkeep
├── .workflow/                           # Workflow state
│   ├── outputs/                         # Workflow outputs
│   │   ├── EPIC-001/                    # Per-epic outputs
│   │   │   ├── conversation-transcript.md
│   │   │   ├── post-mortem.md
│   │   │   └── artifacts/
│   │   └── .gitkeep
│   └── .session_state                   # Current state
├── modules/                             # Core Python modules (41+ modules)
│   ├── __init__.py
│   ├── config/                          # Configuration management
│   │   ├── __init__.py
│   │   ├── base_config.py              # Pydantic base
│   │   ├── secrets_config.py           # API keys, passwords
│   │   ├── api_config.py               # API server config
│   │   ├── database_config.py          # Database settings
│   │   ├── search_config.py            # Elasticsearch, Qdrant
│   │   ├── ai_config.py                # LLM, NLP, embeddings
│   │   ├── feature_flags.py            # Feature toggles
│   │   ├── monitoring_config.py        # Observability
│   │   ├── pdf_processor_config.py     # PDF processing
│   │   ├── citation_config.py          # Citation management
│   │   └── gpu_services/               # GPU server configs
│   ├── orchestration/                  # Workflow orchestration
│   │   ├── __init__.py
│   │   ├── workflow_orchestrator.py    # Main orchestrator
│   │   ├── stage_manager.py            # Stage transitions
│   │   └── pipeline_executor.py        # Pipeline execution
│   ├── ai_research/                    # LLM integration
│   │   ├── __init__.py
│   │   ├── llm_client.py               # Ollama client
│   │   ├── prompt_templates.py         # PICO, quality prompts
│   │   └── response_parser.py          # Parse LLM outputs
│   ├── collection_utils/               # Literature collection
│   │   ├── __init__.py
│   │   ├── api_client_factory.py       # Multi-source API
│   │   ├── pubmed_client.py            # PubMed integration
│   │   ├── openalex_client.py          # OpenAlex integration
│   │   ├── deduplicator.py             # Deduplication
│   │   └── rate_limiter.py             # API rate limiting
│   ├── analysis_utils/                 # Statistical analysis
│   │   ├── __init__.py
│   │   ├── meta_analysis.py            # Meta-analysis
│   │   ├── forest_plots.py             # Visualization
│   │   └── publication_bias.py         # Bias detection
│   ├── citation/                       # Citation network
│   │   ├── __init__.py
│   │   ├── network_builder.py          # Build citation graph
│   │   ├── gap_analyzer.py             # Find citation gaps
│   │   └── trend_detector.py           # Research trends
│   ├── embeddings/                     # Vector embeddings
│   │   ├── __init__.py
│   │   ├── biolord_embeddings.py       # BioLORD (GPU)
│   │   └── sentence_transformer.py     # Local fallback
│   ├── quality_assessment/             # Study quality
│   │   ├── __init__.py
│   │   ├── bias_detector.py            # Bias detection
│   │   └── quality_scorer.py           # Quality scoring
│   ├── pico/                           # PICO extraction
│   │   ├── __init__.py
│   │   ├── pico_extractor.py           # Extract PICO elements
│   │   └── pico_validator.py           # Validate extractions
│   ├── obsidian/                       # Obsidian integration
│   │   ├── __init__.py
│   │   ├── vault_reader.py             # Read from vault
│   │   └── vault_writer.py             # Write to vault
│   ├── mcp_server/                     # MCP server integration
│   │   ├── __init__.py
│   │   ├── mcp_tools.py                # 26 MCP tools
│   │   └── librechat_integration.py    # LibreChat setup
│   └── ... (30+ additional modules)
├── scripts/                            # Utility scripts
│   ├── init_databases.py              # Initialize DB schema
│   ├── run_systematic_review.py       # CLI workflow
│   ├── export_results.py              # Export to PRISMA, etc.
│   ├── check_databases.py             # Health checks
│   └── quick_biolord_deployment.py    # Deploy BioLORD
├── tests/                             # Test suite (480+ tests)
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_collection/               # Collection tests
│   ├── test_analysis/                 # Analysis tests
│   ├── test_citation/                 # Citation tests
│   ├── test_mcp_server/               # MCP tests
│   ├── integration/                   # Integration tests
│   ├── external/                      # External test files
│   │   └── reed/                      # Reed framework tests
│   └── fixtures/                      # Test data
├── config/                            # Configuration files
│   ├── config.yaml                    # Main config (from template)
│   ├── docker/                        # Docker Compose files
│   │   ├── docker-compose.yml         # Base stack
│   │   ├── docker-compose.prod.yml    # Production
│   │   └── docker-compose.monitoring.yml # Observability
│   └── gpu_services/                  # GPU config
├── docs/                              # Documentation
│   ├── architecture.md                # System architecture
│   ├── api.md                         # API reference
│   ├── systematic_review_workflow.md  # Workflow guide
│   ├── mcp_tools.md                   # MCP tools docs
│   ├── modules/                       # Module docs
│   └── obsidian_vault/                # Symlink to Obsidian
│       → ~/coding_projects/projects/01_second_brain/obsidian_llm_vault
├── data/                              # Runtime data (gitignored)
│   ├── postgres/                      # PostgreSQL data
│   ├── redis/                         # Redis data
│   ├── elasticsearch/                 # Elasticsearch data
│   ├── qdrant/                        # Qdrant SCALAR data
│   └── qdrant-obsidian/               # Qdrant Obsidian data
├── logs/                              # Application logs (gitignored)
│   ├── scalar.log                     # Main log
│   ├── api.log                        # API server log
│   ├── mcp_server.log                 # MCP server log
│   ├── database.log                   # Database log
│   └── academic_apis.log              # API client log
├── outputs/                           # Generated outputs (gitignored)
│   ├── reports/                       # Generated reports
│   ├── exports/                       # Exported data
│   └── visualizations/                # Plots, graphs
├── models/                            # Downloaded ML models (gitignored)
│   ├── biolord/                       # BioLORD models
│   ├── biobert/                       # BioBERT models
│   └── sentence_transformers/         # Sentence transformers
├── .cache/                            # Cache directory (gitignored)
│   ├── embeddings/                    # Embedding cache
│   ├── api_responses/                 # API response cache
│   └── llm_responses/                 # LLM response cache
├── .env                               # Environment config (gitignored)
├── .env.example                       # Example config (from template)
├── .gitignore                         # Git exclusions (from template)
├── README.md                          # Project README (from template)
├── requirements.txt                   # Python dependencies
├── main.py                            # API server entry point
├── LICENSE                            # License file
└── .git/                              # Git repository
```

---

## Directory Categories

### Tier1 Workflow Integration (3 directories)

- `.claude/` - Workflow commands, docs, hooks
- `.tasks/` - Epic task tracking
- `.workflow/` - Workflow state and outputs

### Core Application (6 directories)

- `modules/` - Python modules (41+ modules)
- `scripts/` - Utility scripts
- `tests/` - Test suite
- `config/` - Configuration files
- `docs/` - Documentation
- `main.py` - Entry point

### Runtime Data (5 directories - gitignored)

- `data/` - Database data
- `logs/` - Application logs
- `outputs/` - Generated outputs
- `models/` - Downloaded ML models
- `.cache/` - Cache files

### Configuration Files (3 files)

- `.env` - Runtime config (gitignored)
- `.env.example` - Template (from /tmp/scalar_config_templates/)
- `config/config.yaml` - Main config (from template)

---

## Post-Extraction Setup

### 1. Create Obsidian Symlink

```bash
# Create docs directory if it doesn't exist
mkdir -p ~/SCALAR/docs

# Create symlink to Obsidian vault
ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault ~/SCALAR/docs/obsidian_vault

# Verify symlink
ls -la ~/SCALAR/docs/obsidian_vault
```

### 2. Copy Configuration Templates

```bash
# Copy .env.example
cp /tmp/scalar_config_templates/.env.example ~/SCALAR/.env.example

# Copy README.md
cp /tmp/scalar_config_templates/README.md ~/SCALAR/README.md

# Copy config.yaml.template
cp /tmp/scalar_config_templates/config.yaml.template ~/SCALAR/config/config.yaml

# Copy docker-compose.yml
cp /tmp/scalar_config_templates/docker-compose.yml ~/SCALAR/config/docker/docker-compose.yml

# Copy .gitignore
cp /tmp/scalar_config_templates/.gitignore ~/SCALAR/.gitignore
```

### 3. Create Runtime Directories

```bash
cd ~/SCALAR

# Create data directories
mkdir -p data/{postgres,redis,elasticsearch,qdrant,qdrant-obsidian}

# Create log directory
mkdir -p logs

# Create output directories
mkdir -p outputs/{reports,exports,visualizations}

# Create model directory
mkdir -p models

# Create cache directory
mkdir -p .cache/{embeddings,api_responses,llm_responses}

# Create tier1 workflow directories
mkdir -p .tasks
mkdir -p .workflow/outputs
touch .tasks/.gitkeep
touch .workflow/outputs/.gitkeep
```

### 4. Initialize Tier1 Workflow

```bash
cd ~/SCALAR

# Create .claude/docs/ with SCALAR-specific briefings
mkdir -p .claude/docs

# Create scalar_architecture.md briefing
cat > .claude/docs/scalar_architecture.md << 'EOF'
# SCALAR Architecture Briefing

## System Overview
SCALAR is a microservices-based systematic review automation platform...
[Add comprehensive architecture guide]
EOF

# Create systematic_review_domain.md briefing
cat > .claude/docs/systematic_review_domain.md << 'EOF'
# Systematic Review Domain Knowledge

## PRISMA Framework
[Add PRISMA, Cochrane guidelines, etc.]
EOF

# Create agent_guidelines.md
cat > .claude/docs/agent_guidelines.md << 'EOF'
# Agent Guidelines for SCALAR

## Code Style
- Follow PEP 8
- Use Pydantic for type safety
- Document all public APIs
[Add comprehensive guidelines]
EOF
```

### 5. Configure .env

```bash
cd ~/SCALAR

# Copy example to .env
cp .env.example .env

# Edit .env (required changes)
nano .env
# Set:
# - CONTACT_EMAIL
# - All passwords (POSTGRES, REDIS, ELASTICSEARCH)
# - Security keys (JWT_SECRET_KEY, ENCRYPTION_KEY)
# - GPU_SERVER_HOST
```

---

## Size Breakdown

| Category | Size | Status |
|----------|------|--------|
| **Core code** | ~500 MB | ✅ Extracted |
| **Tests** | ~200 MB | ✅ Extracted |
| **Config & docs** | ~10 MB | ✅ Extracted |
| **Virtual env** | 0 MB | ❌ Excluded (recreate) |
| **ML models** | 0 MB | ❌ Excluded (re-download) |
| **Database data** | 0 MB | ❌ Excluded (reinitialize) |
| **Cache** | 0 MB | ❌ Excluded (regenerate) |
| **Total extracted** | **~700 MB** | ✅ |

---

## External Dependencies

### Must Configure Post-Extraction

1. **Obsidian Vault** - Symlink to `~/coding_projects/projects/01_second_brain/obsidian_llm_vault`
2. **GPU Server** - Update `GPU_SERVER_HOST` in .env
3. **Database Stack** - Start with `docker-compose up -d`
4. **Python Env** - Recreate with `python3 -m venv venv`

### External Test Files

8 external test files were moved from `claude-workflow/reed/` to `tests/external/reed/`:
- `test_citation_network_enhancements.py`
- `framework/base_reed_test.py`
- `run_playwright_enhancement_test.py`
- `test_reference_processing_phase2.py`
- 4 additional reed framework files

---

## Validation Checklist

After extraction, verify:

- [ ] Directory structure matches this document
- [ ] Obsidian symlink works: `ls ~/SCALAR/docs/obsidian_vault`
- [ ] Configuration files exist: `.env`, `config.yaml`
- [ ] Runtime directories created: `data/`, `logs/`, `outputs/`
- [ ] Tier1 workflow integrated: `.claude/`, `.tasks/`, `.workflow/`
- [ ] Git initialized: `.git/` exists
- [ ] Dependencies installable: `pip install -r requirements.txt`
- [ ] Imports work: `python -c "from modules.config import BaseConfig"`
- [ ] Database stack starts: `cd config/docker && docker-compose up -d`
- [ ] Tests pass: `pytest tests/ -v`

---

**Created:** 2025-10-23
**Purpose:** Post-extraction directory structure guide for ~/SCALAR
**Next:** Run extraction script, then apply this structure
