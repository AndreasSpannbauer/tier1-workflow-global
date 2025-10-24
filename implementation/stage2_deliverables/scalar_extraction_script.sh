#!/bin/bash
# SCALAR Extraction Script
# Extracts SCALAR from 01_second_brain to ~/SCALAR
# DRY RUN by default - use --execute to actually copy files

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SOURCE_DIR="${HOME}/coding_projects/projects/01_second_brain/SCALAR_workflow"
TARGET_DIR="${HOME}/SCALAR"
DRY_RUN=true
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --execute)
            DRY_RUN=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--execute] [--verbose]"
            echo ""
            echo "Options:"
            echo "  --execute   Actually perform the extraction (default: dry-run)"
            echo "  --verbose   Show detailed rsync output"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

echo "============================================================================"
echo "SCALAR Extraction Script"
echo "============================================================================"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "⚠️  DRY RUN MODE - No files will be copied"
    echo "   Use --execute to actually perform extraction"
    echo ""
fi

echo "Performing pre-flight checks..."
echo ""

# Check source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ ERROR: Source directory not found: $SOURCE_DIR"
    exit 1
fi
echo "✅ Source directory exists: $SOURCE_DIR"

# Check target doesn't exist
if [ -e "$TARGET_DIR" ]; then
    echo "❌ ERROR: Target already exists: $TARGET_DIR"
    echo "   Remove or rename it first: mv $TARGET_DIR ${TARGET_DIR}.backup"
    exit 1
fi
echo "✅ Target directory is available: $TARGET_DIR"

# Check disk space (need ~700MB + overhead)
REQUIRED_SPACE_MB=1000
AVAILABLE_SPACE_MB=$(df -BM "$HOME" | awk 'NR==2 {print $4}' | sed 's/M//')

if [ "$AVAILABLE_SPACE_MB" -lt "$REQUIRED_SPACE_MB" ]; then
    echo "❌ ERROR: Insufficient disk space"
    echo "   Required: ${REQUIRED_SPACE_MB}MB"
    echo "   Available: ${AVAILABLE_SPACE_MB}MB"
    exit 1
fi
echo "✅ Sufficient disk space: ${AVAILABLE_SPACE_MB}MB available"

# Check rsync is available
if ! command -v rsync &> /dev/null; then
    echo "❌ ERROR: rsync not found"
    echo "   Install with: sudo apt-get install rsync"
    exit 1
fi
echo "✅ rsync is available"

echo ""
echo "All pre-flight checks passed!"
echo ""

# ============================================================================
# CALCULATE SOURCE SIZE
# ============================================================================

echo "Calculating source directory size..."
SOURCE_SIZE=$(du -sh "$SOURCE_DIR" | awk '{print $1}')
echo "Source size: $SOURCE_SIZE (will be reduced by exclusions)"
echo ""

# ============================================================================
# EXTRACTION (RSYNC WITH EXCLUSIONS)
# ============================================================================

echo "============================================================================"
echo "EXTRACTION PHASE"
echo "============================================================================"
echo ""

# Rsync options
RSYNC_OPTS=(
    -av                           # Archive mode, verbose
    --progress                    # Show progress
)

if [ "$DRY_RUN" = true ]; then
    RSYNC_OPTS+=(--dry-run)
fi

if [ "$VERBOSE" = false ]; then
    RSYNC_OPTS+=(--info=progress2)  # Condensed progress
fi

# Exclusions (60% of size: ~18-20GB)
EXCLUSIONS=(
    # Virtual environments (6.1 GB)
    --exclude='venv_external_tools/'
    --exclude='venv/'
    --exclude='env/'
    --exclude='.venv/'

    # ML models (4.6 GB - re-downloadable)
    --exclude='models/'
    --exclude='*.onnx'
    --exclude='*.h5'
    --exclude='*.hdf5'
    --exclude='*.pb'
    --exclude='*.pt'
    --exclude='*.pth'
    --exclude='*.bin'  # Model binaries

    # Cache directories (976 MB)
    --exclude='.cache/'
    --exclude='__pycache__/'
    --exclude='.mypy_cache/'
    --exclude='.pytest_cache/'
    --exclude='.ruff_cache/'
    --exclude='*.pyc'
    --exclude='*.pyo'

    # Test outputs (1-2 GB)
    --exclude='test_outputs/'
    --exclude='validation_outputs/'
    --exclude='test_results/'

    # Research databases (15 GB - needs review)
    --exclude='research_databases/'

    # Logs and temporary files
    --exclude='*.log'
    --exclude='logs/'
    --exclude='.tmp/'
    --exclude='tmp/'

    # IDE and editor files
    --exclude='.vscode/'
    --exclude='.idea/'
    --exclude='*.swp'
    --exclude='*.swo'
    --exclude='.DS_Store'

    # Git (will re-init in target)
    --exclude='.git/'

    # Docker volumes
    --exclude='docker_volumes/'

    # Downloads
    --exclude='downloads/'

    # Archive
    --exclude='archive/'

    # Hidden files except .env templates
    --exclude='.*'
    --include='.env.example'
    --include='.env.template'
    --include='.gitignore'
)

echo "Rsync command:"
echo "rsync ${RSYNC_OPTS[*]} ${EXCLUSIONS[*]} $SOURCE_DIR/ $TARGET_DIR/"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "⚠️  DRY RUN - Showing what would be copied:"
    echo ""
fi

# Execute rsync
rsync "${RSYNC_OPTS[@]}" "${EXCLUSIONS[@]}" "$SOURCE_DIR/" "$TARGET_DIR/"

echo ""
echo "✅ Rsync completed"
echo ""

# ============================================================================
# POST-EXTRACTION SETUP
# ============================================================================

if [ "$DRY_RUN" = false ]; then
    echo "============================================================================"
    echo "POST-EXTRACTION SETUP"
    echo "============================================================================"
    echo ""

    # Create .gitignore
    echo "Creating .gitignore..."
    cat > "$TARGET_DIR/.gitignore" << 'EOF'
# See /tmp/scalar_config_templates/.gitignore for comprehensive version
.env
__pycache__/
*.pyc
venv/
.venv/
models/
.cache/
logs/
*.log
data/
outputs/
EOF
    echo "✅ .gitignore created"

    # Create essential directories
    echo ""
    echo "Creating essential directories..."
    mkdir -p "$TARGET_DIR"/{data,logs,outputs,models,.cache}
    echo "✅ Essential directories created"

    # Initialize Git
    echo ""
    echo "Initializing Git repository..."
    cd "$TARGET_DIR"
    git init
    git add .
    git commit -m "Initial commit: SCALAR extracted from 01_second_brain

Extracted from: $SOURCE_DIR
Extraction date: $(date)
Excluded: venv, models, cache, test outputs, research databases
Expected size: ~700MB core code

Next steps:
1. Configure .env file
2. Create Obsidian symlink
3. Run path replacement script
4. Test imports and configuration
"
    echo "✅ Git repository initialized"

    # Calculate final size
    echo ""
    echo "Calculating final size..."
    FINAL_SIZE=$(du -sh "$TARGET_DIR" | awk '{print $1}')
    echo "✅ Final size: $FINAL_SIZE"

    echo ""
    echo "============================================================================"
    echo "EXTRACTION COMPLETE"
    echo "============================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure environment:"
    echo "   cd $TARGET_DIR"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your settings"
    echo ""
    echo "2. Create Obsidian symlink:"
    echo "   ln -s ~/coding_projects/projects/01_second_brain/obsidian_llm_vault $TARGET_DIR/docs/obsidian_vault"
    echo ""
    echo "3. Run path replacement:"
    echo "   python3 /tmp/scalar_path_replacement.py --execute"
    echo ""
    echo "4. Create virtual environment:"
    echo "   cd $TARGET_DIR"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "5. Start database stack:"
    echo "   cd $TARGET_DIR/config/docker"
    echo "   docker-compose up -d"
    echo ""
    echo "6. Run tests:"
    echo "   cd $TARGET_DIR"
    echo "   pytest tests/ -v"
    echo ""

else
    echo "============================================================================"
    echo "DRY RUN COMPLETE"
    echo "============================================================================"
    echo ""
    echo "This was a dry run. No files were copied."
    echo ""
    echo "To actually perform the extraction, run:"
    echo "  $0 --execute"
    echo ""
fi
