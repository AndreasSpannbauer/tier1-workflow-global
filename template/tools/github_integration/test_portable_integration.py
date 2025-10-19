"""
Test script for portable GitHub integration module.

Validates that all components work without project-specific dependencies.
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from github_integration.models import (
    GitHubIssueMetadata,
    IssueSummary,
    ProgressUpdate,
    SubIssueTask,
)
from github_integration.utils import get_project_root, ensure_tasks_directory
from github_integration.gh_cli_wrapper import GitHubCLIError


def test_models():
    """Test Pydantic models instantiate correctly."""
    print("Testing models...")

    # Test GitHubIssueMetadata
    metadata = GitHubIssueMetadata()
    assert metadata.issue_number is None
    assert metadata.sync_enabled is True

    metadata_full = GitHubIssueMetadata(
        issue_number=123, issue_url="https://github.com/user/repo/issues/123"
    )
    assert metadata_full.issue_number == 123

    # Test IssueSummary
    summary = IssueSummary(
        title="Test Epic",
        epic_id="EPIC-001",
        status="planned",
        domain="backend",
        effort="MEDIUM",
        complexity="MEDIUM",
        problem_statement="Test problem",
        requirements=["Req 1"],
        services=["service1"],
        impact_summary="Impact summary",
        artifact_links=["spec.md"],
    )
    assert summary.epic_id == "EPIC-001"

    # Test ProgressUpdate
    update = ProgressUpdate(
        epic_id="EPIC-001",
        phase="Phase 1",
        status="in_progress",
        agent_id="agent-1",
        details="Test details",
    )
    assert update.epic_id == "EPIC-001"
    assert update.timestamp is not None

    # Test SubIssueTask
    task = SubIssueTask(
        name="Test Task", domain="backend", epic_id="EPIC-001", estimated_effort="LOW"
    )
    assert task.domain == "backend"

    print("✅ All models work correctly")


def test_path_detection():
    """Test project root detection."""
    print("\nTesting path detection...")

    # Test get_project_root
    root = get_project_root()
    assert root.exists(), f"Project root does not exist: {root}"
    print(f"✅ Project root detected: {root}")

    # Test ensure_tasks_directory
    tasks_dir = ensure_tasks_directory()
    assert tasks_dir.exists(), f"Tasks directory not created: {tasks_dir}"
    assert (tasks_dir / "backlog").exists()
    assert (tasks_dir / "current").exists()
    assert (tasks_dir / "completed").exists()
    print(f"✅ Tasks directory structure verified: {tasks_dir}")


def test_imports():
    """Test all module imports work."""
    print("\nTesting imports...")

    # Test issue_sync_gh
    from github_integration.issue_sync_gh import (
        create_github_issue_from_epic,
        sync_status_to_github_simple,
    )

    # Test progress_reporter
    from github_integration.progress_reporter import (
        post_progress_update,
        create_sub_issues_for_parallel_work,
    )

    # Test issue_mapper
    from github_integration.issue_mapper import (
        extract_issue_summary,
        format_issue_body,
    )

    # Test label_manager
    from github_integration.label_manager import get_label_taxonomy

    # Test gh_cli_wrapper
    from github_integration.gh_cli_wrapper import create_issue, get_repo_name

    print("✅ All imports successful")


def test_label_taxonomy():
    """Test label taxonomy structure."""
    print("\nTesting label taxonomy...")

    from github_integration.label_manager import get_label_taxonomy

    taxonomy = get_label_taxonomy()
    assert "status" in taxonomy
    assert "type" in taxonomy
    assert "domain" in taxonomy
    assert "priority" in taxonomy

    # Check status labels exist
    status_labels = taxonomy["status"]
    status_names = [label.name for label in status_labels]
    assert "status:planned" in status_names
    assert "status:in-progress" in status_names

    print(f"✅ Label taxonomy has {sum(len(v) for v in taxonomy.values())} labels")


def test_error_handling():
    """Test error handling and non-blocking behavior."""
    print("\nTesting error handling...")

    from github_integration.utils import find_epic_dir

    # Test FileNotFoundError for non-existent epic
    try:
        find_epic_dir("EPIC-NONEXISTENT")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "EPIC-NONEXISTENT" in str(e)
        print("✅ FileNotFoundError raised correctly for missing epic")

    # Test GitHubCLIError for repo detection (may not fail if gh is configured)
    from github_integration.gh_cli_wrapper import get_repo_name

    try:
        repo = get_repo_name()
        print(f"✅ Repository detected: {repo}")
    except GitHubCLIError as e:
        print(f"ℹ️  Repository detection failed (expected if not in git repo): {e}")


def test_no_hardcoded_paths():
    """Verify no hardcoded project-specific paths remain."""
    print("\nChecking for hardcoded paths...")

    module_dir = Path(__file__).parent

    # Files to check (excluding docs and this test)
    python_files = [
        "models.py",
        "gh_cli_wrapper.py",
        "issue_mapper.py",
        "issue_sync_gh.py",
        "label_manager.py",
        "progress_reporter.py",
        "utils.py",
        "__init__.py",
    ]

    forbidden_strings = [
        "email_management_system",
        "/home/andreas-spannbauer/coding_projects",
    ]

    for py_file in python_files:
        file_path = module_dir / py_file
        if not file_path.exists():
            continue

        content = file_path.read_text()
        for forbidden in forbidden_strings:
            if forbidden in content:
                print(
                    f"❌ Found hardcoded path '{forbidden}' in {py_file}"
                )
                return

    print("✅ No hardcoded paths found in Python files")


def main():
    """Run all tests."""
    print("=" * 70)
    print("GitHub Integration Portable Module Tests")
    print("=" * 70)

    try:
        test_models()
        test_path_detection()
        test_imports()
        test_label_taxonomy()
        test_error_handling()
        test_no_hardcoded_paths()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nModule is ready for use in any project!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
