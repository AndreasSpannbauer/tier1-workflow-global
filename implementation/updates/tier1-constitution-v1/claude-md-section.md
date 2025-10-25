### Constitutional Compliance

This project follows the Tier1 6-article constitution:

- **Article I**: Simplicity Imperative
- **Article II**: Anti-Abstraction Principle
- **Article III**: No Simulation Code (enforced via pre-commit hook)
- **Article IV**: Contract-First (when applicable)
- **Article V**: Integration-First Testing (when applicable)
- **Article VI**: Observable Systems

See `.claude/constitution.md` for details.

**Validation:**
```bash
# Check all articles (warnings only)
python3 tools/validate_constitutional_compliance.py

# Check specific article
python3 tools/validate_constitutional_compliance.py --article II

# Install pre-commit hook (blocks on Article III violations)
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Git Automation:**
```bash
# Auto-commit WIP before starting workflow
python3 tools/git_workflow_commit.py start --epic-id EPIC-123

# Auto-commit workflow results after completion
python3 tools/git_workflow_commit.py end --epic-id EPIC-123 --message "description"
```
