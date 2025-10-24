# SCALAR - Systematic Review Automation

**Production-ready systematic review workflow system with AI-powered literature analysis**

## Overview

SCALAR (Systematic review **C**ollection, **A**nalysis, and **L**earning **A**utomation **R**esearch) is a comprehensive systematic review automation platform designed for biomedical research. It combines literature search, AI-powered analysis, citation networks, and meta-analysis capabilities into a unified workflow.

### Key Features

- **Literature Search**: Multi-source academic search (PubMed, OpenAlex, ArXiv, etc.)
- **AI Analysis**: LLM-powered PICO extraction, quality assessment, bias detection
- **Citation Networks**: Build and analyze research citation graphs
- **Meta-Analysis**: Statistical synthesis of research findings
- **Knowledge Management**: Bidirectional Obsidian vault integration
- **MCP Server**: 26 tools for LibreChat integration
- **Production Stack**: PostgreSQL, Elasticsearch, Qdrant, Redis

## Quick Start

### Prerequisites

- **Python**: 3.10+ (tested on 3.11)
- **Docker**: 24.0+ with Docker Compose
- **GPU Server**: Optional but recommended (for Ollama LLM, BioLORD embeddings)
- **Disk Space**: 10GB+ (core: 700MB, databases: 2-8GB, models: 4-6GB)

### Installation

```bash
# 1. Clone or extract SCALAR
cd ~/SCALAR

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# 5. Start database stack
cd config/docker
docker-compose up -d

# 6. Initialize databases
cd ~/SCALAR
python scripts/init_databases.py

# 7. Run tests (optional but recommended)
pytest tests/ -v

# 8. Start API server
python main.py
```

### First Run Checklist

- [ ] PostgreSQL running (port 5432)
- [ ] Redis running (port 6379)
- [ ] Elasticsearch running (port 9200)
- [ ] Qdrant running (ports 6333, 6334)
- [ ] Environment file configured (`.env`)
- [ ] Contact email set (for academic APIs)
- [ ] GPU server accessible (optional)
- [ ] Obsidian vault linked/configured (optional)

## Architecture

### Directory Structure

```
~/SCALAR/
├── modules/              # Core Python modules (41+ modules)
│   ├── config/          # Configuration management
│   ├── orchestration/   # Workflow orchestration
│   ├── ai_research/     # LLM integration
│   ├── collection_utils/# Literature collection
│   ├── analysis_utils/  # Statistical analysis
│   ├── citation/        # Citation network analysis
│   ├── embeddings/      # Vector embeddings
│   └── ...
├── scripts/             # Utility scripts
├── tests/              # Test suite (480+ tests)
├── config/             # Configuration files
│   ├── docker/         # Docker Compose files
│   └── config.yaml     # Main configuration
├── docs/               # Documentation
│   └── obsidian_vault/ # Symlink to Obsidian vault
├── data/               # Runtime data
├── logs/               # Application logs
├── models/             # Downloaded ML models
└── main.py            # API server entry point
```

### Microservices

1. **API Gateway** (port 8080)
   - FastAPI REST API
   - MCP server integration
   - Authentication & authorization

2. **Collection Service**
   - Multi-source literature search
   - API rate limiting
   - Deduplication

3. **Analysis Service**
   - LLM-powered PICO extraction
   - Quality assessment
   - Bias detection

4. **Citation Service**
   - Citation network construction
   - Gap analysis
   - Trend detection

5. **Meta-Analysis Service**
   - Statistical synthesis
   - Forest plots
   - Publication bias analysis

### Database Stack

- **PostgreSQL**: Primary data store (studies, citations, results)
- **Elasticsearch**: Full-text search and filtering
- **Qdrant**: Vector search (2 instances: SCALAR + Obsidian)
- **Redis**: Caching and task queues

## Configuration

### Required Environment Variables

See `.env.example` for full list. Minimum required:

```bash
# Contact (required for academic APIs)
CONTACT_EMAIL=your.email@example.com

# Database passwords
POSTGRES_PASSWORD=your_postgres_password
REDIS_PASSWORD=your_redis_password
ELASTICSEARCH_PASSWORD=your_elastic_password

# Security keys (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# GPU server (if using remote GPU)
GPU_SERVER_HOST=192.168.10.10  # or your GPU server IP
OLLAMA_BASE_URL=http://${GPU_SERVER_HOST}:11434
```

### Optional Integrations

**Obsidian Vault** (for knowledge management):
```bash
# Option 1: Symlink (recommended)
ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault ~/SCALAR/docs/obsidian_vault

# Option 2: Environment variable
export OBSIDIAN_VAULT_PATH=/path/to/your/vault
```

**LLM API Keys** (for external models):
```bash
OPENAI_API_KEY=sk-...        # For GPT models
ANTHROPIC_API_KEY=sk-ant-... # For Claude models
GOOGLE_API_KEY=...           # For Gemini models
```

**Academic APIs** (optional, most work with email only):
```bash
PUBMED_API_KEY=...           # Increases rate limits
SCOPUS_API_KEY=...           # Requires institutional access
SEMANTIC_SCHOLAR_API_KEY=... # Increases rate limits
```

## Usage

### Command Line

```bash
# Start API server
python main.py

# Run specific workflow
python scripts/run_systematic_review.py --query "diabetes treatment" --output results/

# Export results
python scripts/export_results.py --format prisma --output report.pdf
```

### MCP Server (LibreChat Integration)

```bash
# Start MCP server (included in main.py)
python main.py --enable-mcp

# Access via LibreChat at http://localhost:3080
# Available tools: scalar_search, extract_pico_elements, run_meta_analysis, etc.
```

### Python API

```python
from modules.orchestration.workflow_orchestrator import WorkflowOrchestrator

# Initialize orchestrator
orchestrator = WorkflowOrchestrator()

# Run systematic review
results = orchestrator.run_systematic_review(
    query="diabetes treatment",
    databases=["pubmed", "openalex", "arxiv"],
    filters={"year_min": 2020}
)

# Analyze results
pico = orchestrator.extract_pico_elements(results)
quality = orchestrator.assess_study_quality(results)
meta = orchestrator.run_meta_analysis(results)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/test_collection/ -v

# Run with coverage
pytest tests/ --cov=modules --cov-report=html

# Run integration tests (requires database stack)
pytest tests/integration/ -v
```

## Deployment

### Development

```bash
# Use docker-compose.yml (includes hot-reload)
cd config/docker
docker-compose up
```

### Production

```bash
# Use docker-compose.prod.yml (optimized)
cd config/docker
docker-compose -f docker-compose.prod.yml up -d

# Enable monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### Scaling

- **Horizontal**: Run multiple API workers (set `API_WORKERS` in .env)
- **Database**: PostgreSQL supports read replicas
- **Cache**: Redis cluster for distributed caching
- **Search**: Elasticsearch cluster for high availability

## Monitoring

### Observability Stack (Optional)

- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3000)
- **Jaeger**: Distributed tracing (port 16686)
- **Loki**: Log aggregation

Enable with:
```bash
cd config/docker
docker-compose -f docker-compose.monitoring.yml up -d
```

### Health Checks

```bash
# API health
curl http://localhost:8080/health

# Database connectivity
python scripts/check_databases.py

# GPU server connectivity
curl http://192.168.10.10:11434/api/tags
```

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Database Connection Failed**:
```bash
# Check containers are running
docker ps | grep -E "postgres|redis|elasticsearch|qdrant"

# Restart database stack
cd config/docker && docker-compose restart
```

**GPU Server Unreachable**:
```bash
# Test connectivity
ping 192.168.10.10

# Test Ollama service
curl http://192.168.10.10:11434/api/tags

# Check GPU_SERVER_HOST in .env
```

**MCP Tools Not Working**:
```bash
# Verify MCP server is enabled
grep MCP_SERVER_ENABLED .env  # Should be true

# Check MCP server logs
tail -f logs/mcp_server.log

# Test tool directly
curl -X POST http://localhost:8080/mcp/tools/scalar_search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes"}'
```

## Documentation

- **Architecture**: `docs/architecture.md`
- **API Reference**: `docs/api.md`
- **Module Documentation**: `docs/modules/`
- **Systematic Review Guide**: `docs/systematic_review_workflow.md`
- **MCP Tools**: `docs/mcp_tools.md`

## Contributing

This is currently a personal research project. For questions or collaboration:
- Email: See `CONTACT_EMAIL` in .env
- Issues: Track in project management system

## License

[Specify license - MIT, Apache 2.0, etc.]

## Acknowledgments

Built with:
- **FastAPI**: Web framework
- **Pydantic**: Type-safe configuration
- **txtai**: Semantic search
- **Ollama**: Local LLM inference
- **PostgreSQL, Redis, Elasticsearch, Qdrant**: Database stack
- **BioLORD**: Biomedical embeddings

Academic data sources:
- PubMed/NCBI, OpenAlex, ArXiv, bioRxiv, medRxiv, Crossref, Semantic Scholar, and more

---

**Status**: Production-ready
**Version**: Extracted from 01_second_brain (2025-10-23)
**Maintainer**: See CONTACT_EMAIL in .env
