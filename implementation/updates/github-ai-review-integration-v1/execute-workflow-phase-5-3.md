### Step 5.3: Create Feature Branch and Pull Request with AI Review

```bash
echo "Creating feature branch and pull request..."
echo ""

# Generate summary from implementation results
if [ "$EXECUTION_MODE" = "parallel" ]; then
  SUMMARY="Parallel implementation completed across ${TOTAL_FILES_CREATED} new files and ${TOTAL_FILES_MODIFIED} modified files."
else
  SUMMARY="Sequential implementation completed with ${TOTAL_FILES_CREATED} new files and ${TOTAL_FILES_MODIFIED} modified files."
fi

# Create feature branch and PR using helper script
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "tools"))

from github_integration.pr_with_ai_review import create_feature_branch_and_pr

epic_id = os.environ.get("ARGUMENTS")
epic_title = os.environ.get("EPIC_TITLE")
summary = os.environ.get("SUMMARY")

result = create_feature_branch_and_pr(
    epic_id=epic_id,
    epic_title=epic_title,
    summary=summary,
    base_branch="main"
)

if result:
    print(f"\n✅ Feature branch created: {result['branch']}")
    print(f"✅ Pull request created: {result['pr_url']}")
    print(f"✅ AI review requested from @claude and @codex")

    # Save PR info for later
    with open(f".workflow/outputs/{epic_id}/pr_info.txt", "w") as f:
        f.write(f"{result['pr_url']}\n")
        f.write(f"{result['branch']}\n")
        f.write(f"{result['pr_number']}\n")

    sys.exit(0)
else:
    print("\n⚠️ PR creation failed (non-blocking)")
    sys.exit(0)
EOF

echo ""
```

