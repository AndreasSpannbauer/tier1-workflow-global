# SCALAR Testing & Validation Checklist

**Purpose:** Comprehensive validation plan for SCALAR extraction from 01_second_brain to ~/SCALAR
**Status:** Stage 2 Deliverable
**Next Stage:** Stage 3 (Migration Execution)

---

## Testing Phases

1. [Pre-Extraction Verification](#1-pre-extraction-verification)
2. [Post-Extraction File Checks](#2-post-extraction-file-checks)
3. [Configuration Validation](#3-configuration-validation)
4. [Path Replacement Validation](#4-path-replacement-validation)
5. [Python Import Tests](#5-python-import-tests)
6. [Database Connectivity Tests](#6-database-connectivity-tests)
7. [Integration Tests](#7-integration-tests)
8. [MCP Server Tests](#8-mcp-server-tests)
9. [Obsidian Integration Tests](#9-obsidian-integration-tests)
10. [Success Criteria](#10-success-criteria)

---

## 1. Pre-Extraction Verification

**Purpose:** Verify source exists and system is ready for extraction

**Status:** ⏸️ Run before extraction

### Checklist

```bash
# [ ] Source directory exists
test -d ~/coding_projects/projects/01_second_brain/SCALAR_workflow && echo "✅ Source exists" || echo "❌ Source missing"

# [ ] Source size is correct (~30GB)
du -sh ~/coding_projects/projects/01_second_brain/SCALAR_workflow

# [ ] Target doesn't exist (prevent overwrite)
test ! -e ~/SCALAR && echo "✅ Target available" || echo "❌ Target exists (remove first)"

# [ ] Sufficient disk space (need 1GB+)
df -h ~ | awk 'NR==2 {print "Available: " $4}'

# [ ] rsync is installed
command -v rsync &> /dev/null && echo "✅ rsync available" || echo "❌ Install: sudo apt-get install rsync"

# [ ] Python 3.10+ installed
python3 --version

# [ ] Docker is running
docker ps &> /dev/null && echo "✅ Docker running" || echo "❌ Start Docker"

# [ ] Git is installed
git --version
```

**Expected Results:**
- Source exists at `~/coding_projects/projects/01_second_brain/SCALAR_workflow`
- Target ~/SCALAR does not exist
- At least 1GB free disk space
- All required tools installed

---

## 2. Post-Extraction File Checks

**Purpose:** Verify extraction completed and core files present

**Status:** ⏸️ Run after extraction script

### Checklist

```bash
cd ~/SCALAR

# [ ] Directory exists
test -d ~/SCALAR && echo "✅ ~/SCALAR exists" || echo "❌ Extraction failed"

# [ ] Size is approximately correct (~700MB)
du -sh . | awk '{print "Size: " $1}'

# [ ] Core modules extracted
test -d modules && echo "✅ modules/" || echo "❌ Missing modules/"

# [ ] Configuration files extracted
test -f requirements.txt && echo "✅ requirements.txt" || echo "❌ Missing requirements.txt"
test -f main.py && echo "✅ main.py" || echo "❌ Missing main.py"

# [ ] Tests extracted
test -d tests && echo "✅ tests/" || echo "❌ Missing tests/"

# [ ] Scripts extracted
test -d scripts && echo "✅ scripts/" || echo "❌ Missing scripts/"

# [ ] Docs extracted
test -d docs && echo "✅ docs/" || echo "❌ Missing docs/"

# [ ] Config directory extracted
test -d config && echo "✅ config/" || echo "❌ Missing config/"
test -d config/docker && echo "✅ config/docker/" || echo "❌ Missing config/docker/"

# [ ] External test files moved
test -d tests/external && echo "✅ tests/external/" || echo "❌ Missing tests/external/"

# [ ] Virtual env was NOT extracted
test ! -d venv && test ! -d venv_external_tools && echo "✅ venv excluded" || echo "❌ venv should be excluded"

# [ ] Models were NOT extracted
test ! -d models || (du -sh models | grep -qE "^[0-9]+[KM]" && echo "✅ models excluded/empty") || echo "❌ models should be excluded"

# [ ] Cache was NOT extracted
test ! -d .cache && echo "✅ .cache excluded" || echo "❌ .cache should be excluded"

# [ ] Git initialized
test -d .git && echo "✅ Git initialized" || echo "❌ Git not initialized"
```

**Expected Results:**
- ~/SCALAR directory exists with ~700MB size
- All core directories present (modules, tests, scripts, config, docs)
- Excluded directories NOT present (venv, models, cache, research_databases)
- Git repository initialized

---

## 3. Configuration Validation

**Purpose:** Verify configuration files are correct and complete

**Status:** ⏸️ Run after copying config templates

### Checklist

```bash
cd ~/SCALAR

# [ ] .env.example exists
test -f .env.example && echo "✅ .env.example" || echo "❌ Missing .env.example"

# [ ] .env created from example
test -f .env && echo "✅ .env exists" || echo "❌ Copy from .env.example"

# [ ] Required environment variables set in .env
grep -q "CONTACT_EMAIL=" .env && echo "✅ CONTACT_EMAIL" || echo "❌ Set CONTACT_EMAIL"
grep -q "POSTGRES_PASSWORD=" .env && echo "✅ POSTGRES_PASSWORD" || echo "❌ Set POSTGRES_PASSWORD"
grep -q "REDIS_PASSWORD=" .env && echo "✅ REDIS_PASSWORD" || echo "❌ Set REDIS_PASSWORD"
grep -q "JWT_SECRET_KEY=" .env && echo "✅ JWT_SECRET_KEY" || echo "❌ Set JWT_SECRET_KEY"
grep -q "ENCRYPTION_KEY=" .env && echo "✅ ENCRYPTION_KEY" || echo "❌ Set ENCRYPTION_KEY"

# [ ] GPU server configured
grep -q "GPU_SERVER_HOST=" .env && echo "✅ GPU_SERVER_HOST" || echo "❌ Set GPU_SERVER_HOST"

# [ ] config.yaml exists
test -f config/config.yaml && echo "✅ config.yaml" || echo "❌ Copy from config.yaml.template"

# [ ] docker-compose.yml exists
test -f config/docker/docker-compose.yml && echo "✅ docker-compose.yml" || echo "❌ Missing docker-compose.yml"

# [ ] .gitignore comprehensive
test -f .gitignore && wc -l .gitignore | awk '{print "✅ .gitignore (" $1 " lines)"}'

# [ ] README.md exists
test -f README.md && echo "✅ README.md" || echo "❌ Missing README.md"
```

**Expected Results:**
- All configuration files present
- .env file created and populated with required values
- GPU_SERVER_HOST points to 192.168.10.10 (or Tailscale IP)

---

## 4. Path Replacement Validation

**Purpose:** Verify hardcoded paths were replaced with environment variables

**Status:** ⏸️ Run after path replacement script

### Checklist

```bash
cd ~/SCALAR

# [ ] Path replacement script executed
python3 /tmp/scalar_path_replacement.py --execute --output /tmp/scalar_path_report.json

# [ ] No hardcoded second_brain paths remain
! grep -r "01_second_brain/SCALAR_workflow" modules/ scripts/ && echo "✅ No hardcoded second_brain paths" || echo "❌ Found hardcoded paths"

# [ ] No hardcoded Tailscale GPU IP (should use env var)
! grep -r "100.102.171.107" modules/ scripts/ config/ && echo "✅ No hardcoded Tailscale IP" || echo "❌ Found hardcoded IP"

# [ ] sys.path.append() calls removed
! grep -r "sys.path.append" modules/ && echo "✅ No sys.path.append()" || echo "❌ Found sys.path.append()"

# [ ] Environment variables used
grep -r "SCALAR_ROOT" modules/ scripts/ | head -3
grep -r "GPU_SERVER_HOST" modules/ | head -3

# [ ] Backup files created
ls -la modules/**/*.backup 2>/dev/null | head -5

# [ ] Report generated
test -f /tmp/scalar_path_report.json && echo "✅ Report exists" || echo "❌ No report"
```

**Expected Results:**
- No hardcoded absolute paths to second_brain
- No hardcoded GPU server IPs
- Environment variables used: SCALAR_ROOT, GPU_SERVER_HOST, OBSIDIAN_VAULT_PATH
- Backup files created

---

## 5. Python Import Tests

**Purpose:** Verify Python modules are importable and dependencies installed

**Status:** ⏸️ Run after venv setup

### Checklist

```bash
cd ~/SCALAR

# [ ] Virtual environment created
test -d venv && echo "✅ venv exists" || python3 -m venv venv

# [ ] Virtual environment activated
source venv/bin/activate && echo "✅ venv activated" || echo "❌ Failed to activate"

# [ ] Dependencies installed
pip install -r requirements.txt

# [ ] Core modules importable
python3 -c "from modules.config import BaseConfig; print('✅ config module')" || echo "❌ config import failed"

python3 -c "from modules.orchestration import WorkflowOrchestrator; print('✅ orchestration module')" || echo "❌ orchestration import failed"

python3 -c "from modules.collection_utils import api_client_factory; print('✅ collection_utils module')" || echo "❌ collection_utils import failed"

python3 -c "from modules.ai_research import llm_client; print('✅ ai_research module')" || echo "❌ ai_research import failed"

# [ ] Configuration loads without errors
python3 -c "from modules.config import BaseConfig; config = BaseConfig(); print('✅ Config loads')" || echo "❌ Config failed"

# [ ] No import errors in test suite
python3 -m pytest tests/ --collect-only > /tmp/scalar_test_collection.log 2>&1 && echo "✅ Tests collected" || echo "❌ Test collection failed"

# [ ] Critical dependencies installed
python3 -c "import fastapi; print('✅ fastapi')" || echo "❌ fastapi missing"
python3 -c "import pydantic; print('✅ pydantic')" || echo "❌ pydantic missing"
python3 -c "import sqlalchemy; print('✅ sqlalchemy')" || echo "❌ sqlalchemy missing"
python3 -c "import redis; print('✅ redis')" || echo "❌ redis missing"
```

**Expected Results:**
- Virtual environment created and activated
- All dependencies installed successfully
- Core modules importable without errors
- Configuration loads without errors

---

## 6. Database Connectivity Tests

**Purpose:** Verify database stack starts and is accessible

**Status:** ⏸️ Run after docker-compose up

### Checklist

```bash
cd ~/SCALAR/config/docker

# [ ] Docker containers start
docker-compose up -d

# [ ] All containers running
docker-compose ps | grep -E "Up|healthy"

# [ ] PostgreSQL accessible
docker exec scalar-postgres pg_isready -U scalar_user && echo "✅ PostgreSQL ready" || echo "❌ PostgreSQL not ready"

# [ ] Redis accessible
docker exec scalar-redis redis-cli -a "$REDIS_PASSWORD" ping && echo "✅ Redis ready" || echo "❌ Redis not ready"

# [ ] Elasticsearch accessible
curl -s -u elastic:$ELASTICSEARCH_PASSWORD http://localhost:9200/_cluster/health | grep -q "yellow\|green" && echo "✅ Elasticsearch ready" || echo "❌ Elasticsearch not ready"

# [ ] Qdrant (SCALAR) accessible
curl -s http://localhost:6333/healthz | grep -q "ok" && echo "✅ Qdrant SCALAR ready" || echo "❌ Qdrant SCALAR not ready"

# [ ] Qdrant (Obsidian) accessible
curl -s http://localhost:6334/healthz | grep -q "ok" && echo "✅ Qdrant Obsidian ready" || echo "❌ Qdrant Obsidian not ready"

# [ ] Container logs show no errors
docker-compose logs --tail=50 | grep -i error || echo "✅ No errors in logs"

# [ ] Database data directories created
test -d ~/SCALAR/data/postgres && echo "✅ Postgres data dir" || echo "❌ Missing postgres data"
test -d ~/SCALAR/data/redis && echo "✅ Redis data dir" || echo "❌ Missing redis data"
test -d ~/SCALAR/data/elasticsearch && echo "✅ Elasticsearch data dir" || echo "❌ Missing elasticsearch data"
test -d ~/SCALAR/data/qdrant && echo "✅ Qdrant data dir" || echo "❌ Missing qdrant data"
```

**Expected Results:**
- All 5 containers running (postgres, redis, elasticsearch, qdrant, qdrant-obsidian)
- All services respond to health checks
- No errors in container logs

---

## 7. Integration Tests

**Purpose:** Test external service integrations

**Status:** ⏸️ Run after database and config setup

### Checklist

```bash
cd ~/SCALAR
source venv/bin/activate

# [ ] GPU server accessible
ping -c 3 192.168.10.10 && echo "✅ GPU server reachable" || echo "❌ GPU server unreachable"

# [ ] Ollama LLM accessible
curl -s http://192.168.10.10:11434/api/tags | grep -q "models" && echo "✅ Ollama accessible" || echo "❌ Ollama not accessible"

# [ ] BioLORD embeddings accessible (if running)
curl -s http://192.168.10.10:8000/health 2>/dev/null && echo "✅ BioLORD accessible" || echo "⚠️  BioLORD not running (optional)"

# [ ] Academic APIs accessible (PubMed)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&retmax=1" | grep -q "Count" && echo "✅ PubMed API" || echo "❌ PubMed API failed"

# [ ] OpenAlex API accessible
curl -s "https://api.openalex.org/works?filter=title.search:diabetes&per-page=1" | grep -q "results" && echo "✅ OpenAlex API" || echo "❌ OpenAlex API failed"

# [ ] Database connections from Python
python3 << EOF
from modules.config import BaseConfig
config = BaseConfig()

# Test PostgreSQL
try:
    import psycopg2
    conn = psycopg2.connect(
        host=config.database.postgres.host,
        port=config.database.postgres.port,
        database=config.database.postgres.database,
        user=config.database.postgres.user,
        password=config.database.postgres.password
    )
    conn.close()
    print("✅ PostgreSQL connection")
except Exception as e:
    print(f"❌ PostgreSQL: {e}")

# Test Redis
try:
    import redis
    r = redis.Redis(
        host=config.database.redis.host,
        port=config.database.redis.port,
        password=config.database.redis.password,
        decode_responses=True
    )
    r.ping()
    print("✅ Redis connection")
except Exception as e:
    print(f"❌ Redis: {e}")
EOF
```

**Expected Results:**
- GPU server accessible on LAN
- Ollama LLM service responding
- Academic APIs (PubMed, OpenAlex) accessible
- Database connections work from Python

---

## 8. MCP Server Tests

**Purpose:** Verify MCP server integration with LibreChat

**Status:** ⏸️ Run after API server start

### Checklist

```bash
cd ~/SCALAR
source venv/bin/activate

# [ ] API server starts
python3 main.py &
API_PID=$!
sleep 5

# [ ] API health check
curl -s http://localhost:8080/health | grep -q "healthy" && echo "✅ API healthy" || echo "❌ API not healthy"

# [ ] MCP tools available
curl -s http://localhost:8080/mcp/tools | grep -q "scalar_search" && echo "✅ MCP tools available" || echo "❌ MCP tools not available"

# [ ] Test scalar_search tool
curl -s -X POST http://localhost:8080/mcp/tools/scalar_search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes"}' | grep -q "results" && echo "✅ scalar_search works" || echo "❌ scalar_search failed"

# [ ] Test extract_pico_elements tool
curl -s -X POST http://localhost:8080/mcp/tools/extract_pico_elements \
  -H "Content-Type: application/json" \
  -d '{"text": "Patients with diabetes were treated with insulin."}' && echo "✅ extract_pico works" || echo "❌ extract_pico failed"

# Stop API server
kill $API_PID 2>/dev/null
```

**Expected Results:**
- API server starts without errors
- Health check passes
- MCP tools endpoint returns tool list
- Core MCP tools (scalar_search, extract_pico) functional

---

## 9. Obsidian Integration Tests

**Purpose:** Verify Obsidian vault integration

**Status:** ⏸️ Run after symlink creation

### Checklist

```bash
cd ~/SCALAR

# [ ] Obsidian symlink exists
test -L docs/obsidian_vault && echo "✅ Symlink exists" || echo "❌ Create symlink"

# [ ] Symlink points to correct location
readlink docs/obsidian_vault | grep -q "obsidian_llm_vault" && echo "✅ Correct target" || echo "❌ Wrong target"

# [ ] Obsidian vault accessible via symlink
test -d docs/obsidian_vault && echo "✅ Vault accessible" || echo "❌ Vault not accessible"

# [ ] SCALAR directories exist in vault
test -d docs/obsidian_vault/SCALAR_METHOD_DOCUMENTATION && echo "✅ SCALAR_METHOD_DOCUMENTATION" || echo "⚠️  Directory missing"
test -d docs/obsidian_vault/SCALAR_PROJECT_EXTERNAL_LLM_OUTPUTS && echo "✅ SCALAR_PROJECT_EXTERNAL_LLM_OUTPUTS" || echo "⚠️  Directory missing"
test -d docs/obsidian_vault/SCALAR_METHOD_SEARCHES && echo "✅ SCALAR_METHOD_SEARCHES" || echo "⚠️  Directory missing"

# [ ] Vault read/write permissions
touch docs/obsidian_vault/test_scalar_write.md && rm docs/obsidian_vault/test_scalar_write.md && echo "✅ Read/write OK" || echo "❌ Permission denied"

# [ ] Python can access vault
python3 -c "
from pathlib import Path
vault = Path('docs/obsidian_vault')
assert vault.exists(), 'Vault not found'
assert vault.is_symlink(), 'Not a symlink'
print('✅ Python vault access OK')
" || echo "❌ Python vault access failed"
```

**Expected Results:**
- Symlink exists at ~/SCALAR/docs/obsidian_vault
- Points to correct Obsidian vault location
- SCALAR directories accessible via symlink
- Read/write permissions work

---

## 10. Success Criteria

**Purpose:** Final validation that extraction was successful

**Status:** ⏸️ Run after all tests pass

### Critical Criteria (Must Pass)

```bash
cd ~/SCALAR

# [ ] CRITICAL: All core imports work
python3 -c "
from modules.config import BaseConfig
from modules.orchestration import WorkflowOrchestrator
from modules.collection_utils import api_client_factory
from modules.ai_research import llm_client
print('✅ CRITICAL: All core imports work')
" || echo "❌ CRITICAL FAILURE: Imports failed"

# [ ] CRITICAL: Configuration loads
python3 -c "
from modules.config import BaseConfig
config = BaseConfig()
assert config.project.root
print('✅ CRITICAL: Configuration loads')
" || echo "❌ CRITICAL FAILURE: Config failed"

# [ ] CRITICAL: Database stack running
docker ps | grep -E "scalar-postgres|scalar-redis|scalar-elasticsearch|scalar-qdrant" | wc -l | grep -q "5" && echo "✅ CRITICAL: Database stack running" || echo "❌ CRITICAL FAILURE: Database stack incomplete"

# [ ] CRITICAL: No hardcoded paths remain
! grep -r "01_second_brain/SCALAR_workflow" modules/ scripts/ && echo "✅ CRITICAL: No hardcoded paths" || echo "❌ CRITICAL FAILURE: Hardcoded paths found"

# [ ] CRITICAL: Git repository initialized
test -d .git && git log --oneline | head -1 && echo "✅ CRITICAL: Git initialized" || echo "❌ CRITICAL FAILURE: No Git repo"
```

### Optional Criteria (Should Pass)

```bash
# [ ] OPTIONAL: Tests pass
pytest tests/ -v --tb=short && echo "✅ OPTIONAL: Tests pass" || echo "⚠️  OPTIONAL: Some tests failing"

# [ ] OPTIONAL: GPU server accessible
curl -s http://192.168.10.10:11434/api/tags && echo "✅ OPTIONAL: GPU server OK" || echo "⚠️  OPTIONAL: GPU server unavailable"

# [ ] OPTIONAL: MCP server works
curl -s http://localhost:8080/health && echo "✅ OPTIONAL: MCP server OK" || echo "⚠️  OPTIONAL: MCP server not running"

# [ ] OPTIONAL: Obsidian vault linked
test -L docs/obsidian_vault && echo "✅ OPTIONAL: Obsidian linked" || echo "⚠️  OPTIONAL: Obsidian not linked"
```

### Rollback Criteria (Extraction Failed)

**If ANY critical criterion fails, consider rolling back:**

```bash
# Rollback steps
cd ~
mv SCALAR SCALAR.failed.$(date +%Y%m%d_%H%M%S)
echo "Extraction failed, rolled back to SCALAR.failed.*"
echo "Review errors and retry extraction"
```

---

## Final Summary

**Success Definition:**
- All CRITICAL criteria pass
- At least 80% of OPTIONAL criteria pass
- Total size approximately 700MB
- No hardcoded paths
- Core functionality works (imports, config, database)

**Next Steps After Success:**
1. Apply tier1 workflow integration
2. Create first epic (e.g., "EPIC-001: Systematic review workflow validation")
3. Run complete systematic review end-to-end test
4. Document any configuration quirks or issues

---

**Created:** 2025-10-23
**Purpose:** Stage 2 testing validation plan
**Status:** Ready for Stage 3 (Migration Execution)
